import subprocess
import os
import ctypes
import re # Added for sanitizing filenames
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
    """Removes or replaces characters that are invalid in Windows filenames."""
    # Remove characters that are outright forbidden
    filename = re.sub(r'[\\/:*?"<>|]', "", filename)
    # Replace other problematic characters (optional, can be expanded)
    filename = filename.replace("\\r", "").replace("\\n", "").strip()
    # Prevent empty filenames
    if not filename:
        filename = "Untitled_Disc"
    return filename

def get_disc_title(makemkv_exe, drive_specifier):
    """Gets the disc title using makemkvcon info."""
    # print(f"Attempting to get disc title for {drive_specifier}...") # Optional: for debugging
    try:
        command = [makemkv_exe, "-r", "info", f"disc:{drive_specifier.split(':')[-1]}"] # Ensure correct disc index format
        # print(f"Running info command: {' '.join(command)}") # Optional: for debugging
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, universal_newlines=True)
        
        disc_title = "Untitled_Disc" # Default title
        for line in proc.stdout:
            # print(f"Info line: {line.strip()}") # Optional: for debugging
            if line.startswith("TINFO:") and ",2,0," in line: # TINFO:disc_index,2,0,"Disc Title"
                match = re.search(r'TINFO:\d+,2,0,"(.*?)"', line)
                if match:
                    disc_title = match.group(1)
                    # print(f"Found disc title: {disc_title}") # Optional: for debugging
                    break # Found the main disc title
        proc.wait()
        if proc.returncode != 0:
            # print(f"MakeMKV info command failed with code {proc.returncode}") # Optional: for debugging
            send_sms(f"Failed to get disc title for {drive_specifier}. Error: {proc.returncode}")
            return "Untitled_Disc" # Return default on error
        return sanitize_filename(disc_title)
    except Exception as e:
        # print(f"Error getting disc title: {e}") # Optional: for debugging
        send_sms(f"Exception while getting disc title for {drive_specifier}: {e}")
        return "Untitled_Disc" # Return default on error

def rip_and_eject():
    """
    Rips a specific title from the DVD, names it by disc title, and then ejects the drive.
    """
    # print(f"Attempting to rip title {title_to_rip} from {makemkv_drive_specifier} to {output_folder}") # Original print

    if not os.path.exists(makemkv):
        print(f"Error: MakeMKV executable not found at \'{makemkv}\'. Please check the path.")
        send_sms(f"Error: MakeMKV executable not found at \'{makemkv}\'.")
        return

    # Get disc title first
    disc_title_sanitized = get_disc_title(makemkv, makemkv_drive_specifier)
    
    # Construct a unique filename for the title
    # Example: "My_Movie_Title_t0.mkv" for title 0
    output_filename = f"{disc_title_sanitized}_t{title_to_rip}.mkv"
    full_output_path = os.path.join(output_folder, output_filename)

    print(f"Attempting to rip title {title_to_rip} from {makemkv_drive_specifier} (Disc: {disc_title_sanitized}) to {full_output_path}")


    # Ensure output directory exists
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"Created output directory: {output_folder}")
    except OSError as e:
        print(f"Error creating output directory {output_folder}: {e}")
        send_sms(f"Error creating output directory {output_folder}: {e}")
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
            full_output_path # Use the full path with the new filename
        ]
        print(f"Running command: {' '.join(command)}")

        # Run MakeMKV rip command and stream output, allowing for stdin interaction
        with subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1,
            universal_newlines=True
        ) as proc:
            print("\\n--- MakeMKV Rip Output Start ---")
            for line in proc.stdout:
                print(line, end="") 
                if "already exist. Do you want to overwrite it?" in line:
                    # This check might be less frequent now with unique names, but good to keep
                    print("\\nAutomatically answering \'yes\' to overwrite prompt.\\n")
                    try:
                        proc.stdin.write('y\\n')
                        proc.stdin.flush()
                    except (IOError, BrokenPipeError) as e:
                        print(f"Error writing to MakeMKV stdin: {e}")
            print("\\n--- MakeMKV Rip Output End (stdout loop finished) ---")

            print("Waiting for MakeMKV process to terminate...")
            if proc.stdin and not proc.stdin.closed:
                try:
                    proc.stdin.close()
                except IOError as e:
                    print(f"Error closing MakeMKV stdin: {e}")
            
            proc.wait() 
            print(f"\\nMakeMKV rip process finished with error code: {proc.returncode}")

            if proc.returncode == 0:
                print(f"\\nRip successful: {output_filename}. Attempting to eject drive...")
                send_sms(f"DVD rip successful: {output_filename}. Disc ejected from drive {drive_letter}.") # Updated SMS
                try:
                    drive_alias = f"dvddrive{drive_letter.replace(':', '')}"
                    open_command = f"open {drive_letter} type CDAudio alias {drive_alias}"
                    eject_command = f"set {drive_alias} door open"
                    close_alias_command = f"close {drive_alias}"

                    if ctypes.windll.WINMM.mciSendStringW(open_command, None, 0, None) == 0:
                        ctypes.windll.WINMM.mciSendStringW(eject_command, None, 0, None)
                        ctypes.windll.WINMM.mciSendStringW(close_alias_command, None, 0, None)
                        print(f"Eject command sent to drive {drive_letter}.")
                        # SMS already sent above with filename
                    else:
                        print(f"Failed to open or alias drive {drive_letter} for eject.")
                        send_sms(f"DVD rip successful: {output_filename}, but failed to eject drive {drive_letter}.") 
                except Exception as e_eject:
                    print(f"Could not eject drive {drive_letter}: {e_eject}")
                    send_sms(f"DVD rip successful: {output_filename}, but an error occurred during eject: {e_eject}") 
            else:
                print(f"\\nRip failed for {output_filename}. Drive will not be ejected.")
                send_sms(f"MakeMKV rip failed for {output_filename} (disc: {disc_title_sanitized}) with error code {proc.returncode}. Drive not ejected.") # Updated SMS

    except FileNotFoundError: 
        print(f"Error: MakeMKV executable not found at \'{makemkv}\'.")
        # SMS already sent by initial check
        return
    except Exception as e:
        print(f"An error occurred during MakeMKV execution for {disc_title_sanitized}: {e}")
        send_sms(f"An error occurred for {disc_title_sanitized} during MakeMKV execution: {e}") 
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
