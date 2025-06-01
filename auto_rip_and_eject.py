import subprocess
import os
import ctypes
import re # Added for filename sanitization
from sms import send_sms # Import the send_sms function

# --- USER CONFIGURATION ---
makemkv = r"C:\\Program Files (x86)\\MakeMKV\\makemkvcon.exe"  # Path to MakeMKV CLI
output_folder = r"C:\\Users\\doghe\\Videos\\backup"      # Updated output folder
drive_letter = "D:"                 # DVD drive letter (used for eject)
# For MakeMKV, we'll use disc:0, assuming it's the correct one as confirmed by 'info'
makemkv_drive_specifier = "disc:0" 
title_to_rip = "0"                  # Title index 0 (Main movie "Title #1")
# --- END USER CONFIGURATION ---

def sanitize_filename(filename):
    """
    Sanitizes a string to be a valid filename.
    Removes illegal characters and replaces spaces with underscores.
    """
    if not filename:
        return "Untitled_DVD"
    # Remove characters that are illegal in Windows filenames
    filename = re.sub(r'[\\\\\\\\/:*?"<>|]', "", filename)
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    # Truncate if too long (Windows max path is around 260, leave room for path)
    return filename[:100]

def get_disc_title(makemkv_path, drive_specifier):
    """
    Gets the title (volume label or metadata title) of the disc using makemkvcon.
    Prefers the volume label from DRV: line if available.
    """
    print(f"Attempting to get disc title for {drive_specifier}...")
    try:
        command = [makemkv_path, "-r", "info", drive_specifier]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, universal_newlines=True)
        
        disc_title_drv = None
        disc_title_cinfo = None

        output_lines = []
        for line in process.stdout:
            output_lines.append(line.strip())
            # print(f"INFO LINE: {line.strip()}") # For debugging

        process.wait() # Ensure process is finished before parsing

        for line in output_lines:
            # Try to get title from DRV: line first (e.g., DRV:0,2,999,1,"Device","TITLE","D:")
            if line.startswith("DRV:0,2,"): # Check for the specific DRV line indicating a loaded disc with info
                try:
                    parts = line.split(',', 6) # Split by comma, expecting at least 7 parts for "D:" at the end
                    if len(parts) > 5: # Title is the 6th part (index 5)
                        title_part = parts[5]
                        if title_part.startswith('\"') and title_part.endswith('\"'):
                            disc_title_drv = title_part[1:-1]
                            if disc_title_drv: # If we got a non-empty title from DRV, prioritize it
                                print(f"Found disc title (from DRV line): {disc_title_drv}")
                                return disc_title_drv 
                except Exception as e:
                    print(f"Error parsing DRV line for title: {line} - {e}")
            
            # If not found or DRV title was empty, try CINFO: line (e.g., CINFO:1,0,"METADATA_TITLE")
            if line.startswith("CINFO:1,0,"): 
                try:
                    parts = line.split(',', 2)
                    if len(parts) > 2:
                        title_part = parts[2]
                        if title_part.startswith('\"') and title_part.endswith('\"'):
                            disc_title_cinfo = title_part[1:-1]
                            # Don't return immediately, let DRV parsing complete if it hasn't found a title yet
                except Exception as e:
                    print(f"Error parsing CINFO line for title: {line.strip()} - {e}")

        # After checking all lines, decide what to return
        if disc_title_drv: # Should have been returned already if found and valid
            # This case might be redundant if the earlier return works, but as a fallback.
            print(f"Using disc title (from DRV line): {disc_title_drv}")
            return disc_title_drv
        elif disc_title_cinfo:
            print(f"Found disc title (from CINFO line): {disc_title_cinfo}")
            return disc_title_cinfo
        else:
            print("Could not determine disc title from makemkvcon info (checked DRV and CINFO).")
            return None
            
    except Exception as e:
        print(f"An error occurred while trying to get disc title: {e}")
        return None

def rip_and_eject():
    """
    Rips a specific title from the DVD, names it by disc title, and then ejects the drive.
    """
    print("rip_and_eject function started...") 
    # Get disc title first
    current_disc_title = get_disc_title(makemkv, makemkv_drive_specifier)
    sanitized_disc_title = sanitize_filename(current_disc_title if current_disc_title else "Untitled_DVD")
    
    # Construct the final output path including the sanitized disc title
    # The actual MKV filename will be determined by MakeMKV (e.g., title00.mkv, title01.mkv)
    # So we create a subfolder named after the disc title.
    final_output_path = os.path.join(output_folder, sanitized_disc_title)

    print(f"Attempting to rip title {title_to_rip} from {makemkv_drive_specifier} to {final_output_path}")

    if not os.path.exists(makemkv):
        print(f"Error: MakeMKV executable not found at \'{makemkv}\'. Please check the path.")
        send_sms(f"Error: MakeMKV executable not found at \'{makemkv}\'.")
        return

    # Ensure output directory (including title-specific subfolder) exists
    try:
        if not os.path.exists(final_output_path):
            os.makedirs(final_output_path)
            print(f"Created output directory: {final_output_path}")
    except OSError as e:
        print(f"Error creating output directory {final_output_path}: {e}")
        send_sms(f"Error creating output directory {final_output_path}: {e}")
        return

    try:
        # Construct the MakeMKV command for ripping
        command = [
            makemkv,
            "-r",
            "--minlength=300", 
            "mkv",
            makemkv_drive_specifier,
            title_to_rip,
            final_output_path # Use the new path with the disc title subfolder
        ]
        print(f"Running command: {' '.join(command)}")

        # Run MakeMKV rip command and stream output
        with subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Combine stdout and stderr
            text=True,
            bufsize=1,
            universal_newlines=True
        ) as proc:
            print("\\n--- MakeMKV Rip Output Start ---")
            for line in proc.stdout:
                print(line, end="") # Print MakeMKV output directly
            print("\\n--- MakeMKV Rip Output End (stdout loop finished) ---") # Added this line

            print("Waiting for MakeMKV process to terminate...") # Added this line
            proc.wait() # Wait for the subprocess to complete
            print(f"\\nMakeMKV rip process finished with error code: {proc.returncode}")

            if proc.returncode == 0:
                print("\\nRip successful. Attempting to eject drive...")
                try:
                    drive_alias = f"dvddrive{drive_letter.replace(':', '')}"
                    open_command = f"open {drive_letter} type CDAudio alias {drive_alias}"
                    eject_command = f"set {drive_alias} door open"
                    close_alias_command = f"close {drive_alias}"

                    if ctypes.windll.WINMM.mciSendStringW(open_command, None, 0, None) == 0:
                        ctypes.windll.WINMM.mciSendStringW(eject_command, None, 0, None)
                        ctypes.windll.WINMM.mciSendStringW(close_alias_command, None, 0, None)
                        print(f"Eject command sent to drive {drive_letter}.")
                        send_sms(f"DVD rip successful and disc ejected from drive {drive_letter}.") # SMS notification
                    else:
                        print(f"Failed to open or alias drive {drive_letter} for eject.")
                        send_sms(f"DVD rip successful, but failed to eject drive {drive_letter}.") # SMS notification
                except Exception as e_eject:
                    print(f"Could not eject drive {drive_letter}: {e_eject}")
                    send_sms(f"DVD rip successful, but an error occurred during eject: {e_eject}") # SMS notification
            else:
                print("\\nRip failed. Drive will not be ejected.")
                send_sms(f"MakeMKV rip failed with error code {proc.returncode}. Drive not ejected.") # SMS notification

    except FileNotFoundError: # Should be caught by the os.path.exists check
        print(f"Error: MakeMKV executable not found at \'{makemkv}\'.")
        send_sms(f"Error: MakeMKV executable not found at \'{makemkv}\'.") # SMS notification
        return
    except Exception as e:
        print(f"An error occurred during MakeMKV execution: {e}")
        send_sms(f"An error occurred during MakeMKV execution: {e}") # SMS notification
        return

if __name__ == "__main__":
    while True:
        rip_and_eject()
        print("\\nProcess complete for the current disc.")
        user_input = input("Insert the next DVD and press Enter to continue, or type 'Q' and press Enter to quit: ")
        if user_input.strip().upper() == 'Q':
            print("Exiting script.")
            break
        print("\\nStarting process for the next disc...")
