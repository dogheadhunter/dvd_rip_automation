import subprocess
import os
import ctypes
import re # Added for filename sanitization
import requests # For Pushbullet notification

# --- USER CONFIGURATION ---
PUSHBULLET_API_KEY = "o.UqWB9szmZcPUIJVmHq5cmkRg7UmLBmil" # Your Pushbullet API Key
makemkv = r"C:\\Program Files (x86)\\MakeMKV\\makemkvcon.exe"  # Path to MakeMKV CLI
output_folder = r"C:\\Users\\doghe\\Videos\\backup"      # Updated output folder
drive_letter = "D:"                 # DVD drive letter (used for eject)
# For MakeMKV, we'll use disc:0, assuming it's the correct one as confirmed by 'info'
makemkv_drive_specifier = "disc:0" 
title_to_rip = "0"                  # Title index 0 (Main movie "Title #1")
# --- END USER CONFIGURATION ---

def send_pushbullet_notification(title: str, message: str, api_key: str):
    """
    Sends a notification via Pushbullet.
    """
    if not api_key:
        print("Pushbullet API key not configured. Skipping notification.")
        return
    try:
        data = {"type": "note", "title": title, "body": message}
        headers = {"Access-Token": api_key, "Content-Type": "application/json"}
        response = requests.post("https://api.pushbullet.com/v2/pushes", json=data, headers=headers, timeout=10)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        print(f"Pushbullet notification '{title}' sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Pushbullet notification: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in send_pushbullet_notification: {e}")

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
        print(f"Error: MakeMKV executable not found at '{makemkv}'. Please check the path.")
        return

    # Ensure output directory (including title-specific subfolder) exists
    try:
        if not os.path.exists(final_output_path):
            os.makedirs(final_output_path)
            print(f"Created output directory: {final_output_path}")
    except OSError as e:
        print(f"Error creating output directory {final_output_path}: {e}")
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
                        send_pushbullet_notification("DVD Rip Success", f"DVD '{current_disc_title if current_disc_title else 'Unknown Disc'}' ripped successfully and disc ejected from drive {drive_letter}.", PUSHBULLET_API_KEY)
                    else:
                        print(f"Failed to open or alias drive {drive_letter} for eject.")
                        send_pushbullet_notification("DVD Rip Alert", f"DVD '{current_disc_title if current_disc_title else 'Unknown Disc'}' ripped successfully, but failed to eject drive {drive_letter}.", PUSHBULLET_API_KEY)
                except Exception as e_eject:
                    print(f"Could not eject drive {drive_letter}: {e_eject}")
                    send_pushbullet_notification("DVD Rip Error", f"DVD '{current_disc_title if current_disc_title else 'Unknown Disc'}' ripped successfully, but an error occurred during eject: {e_eject}", PUSHBULLET_API_KEY)
            else:
                print("\\nRip failed. Drive will not be ejected.")
                send_pushbullet_notification("DVD Rip Failed", f"MakeMKV rip failed for '{current_disc_title if current_disc_title else 'Unknown Disc'}' with error code {proc.returncode}. Drive not ejected.", PUSHBULLET_API_KEY)

    except FileNotFoundError: # Should be caught by the os.path.exists check
        print(f"Error: MakeMKV executable not found at '{makemkv}'.")
        send_pushbullet_notification("Script Error", f"MakeMKV executable not found at '{makemkv}'.", PUSHBULLET_API_KEY)
        return
    except Exception as e:
        print(f"An error occurred during MakeMKV execution: {e}")
        send_pushbullet_notification("Script Error", f"An error occurred during MakeMKV execution: {e}", PUSHBULLET_API_KEY)
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
