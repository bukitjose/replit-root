import subprocess
import os
import shutil
import logging
import time

logging.basicConfig(filename='recovery_log.txt', level=logging.INFO)

class RecoveryError(Exception):
    pass

def backup_file(file_path, backup_dir):
    try:
        if os.path.exists(file_path):
            shutil.copy(file_path, backup_dir)
            logging.info(f"Backed up {file_path} to {backup_dir}")
        else:
            raise RecoveryError(f"File {file_path} does not exist, skipping backup")
    except Exception as e:
        logging.error(f"Error backing up {file_path}: {e}")
        raise RecoveryError(f"Error backing up {file_path}: {e}")

def restore_file(backup_path, target_path):
    try:
        if os.path.exists(backup_path):
            shutil.copy(backup_path, target_path)
            logging.info(f"Restored {backup_path} to {target_path}")
        else:
            raise RecoveryError(f"Backup file {backup_path} does not exist, skipping restore")
    except Exception as e:
        logging.error(f"Error restoring {backup_path} to {target_path}: {e}")
        raise RecoveryError(f"Error restoring {backup_path} to {target_path}: {e}")

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        logging.info(f"Executed command: {command}\nOutput: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {command}\nError: {e}")
        raise RecoveryError(f"Error executing command: {command}\nError: {e}")

def network_diagnosis():
    try:
        result = run_command("ping -c 4 google.com")
        if result:
            logging.info("Network is reachable")
            return True
        else:
            logging.warning("Network is unreachable")
            return False
    except Exception as e:
        logging.error(f"Error performing network diagnosis: {e}")
        raise RecoveryError(f"Error performing network diagnosis: {e}")

def flash_iso_or_torrent(file_path, device):
    try:
        if os.path.exists(file_path):
            # Determine file type
            _, file_extension = os.path.splitext(file_path)
            if file_extension.lower() == ".iso":
                # Flash ISO
                logging.info(f"Flashing ISO file {file_path} to device {device}")
                subprocess.run(["dd", "if=" + file_path, "of=" + device, "bs=4M", "status=progress"])
                logging.info(f"ISO file {file_path} flashed to device {device}")
                return True
            elif file_extension.lower() == ".torrent":
                # Convert torrent to ISO and flash
                iso_path = convert_torrent_to_iso(file_path)
                logging.info(f"Converted torrent file {file_path} to ISO: {iso_path}")
                flash_iso(iso_path, device)
                logging.info(f"Torrent file {file_path} flashed to device {device}")
                return True
            else:
                raise RecoveryError(f"Unsupported file type: {file_extension}")
        else:
            raise RecoveryError(f"File {file_path} does not exist, skipping flashing")
    except Exception as e:
        logging.error(f"Error flashing file {file_path} to device {device}: {e}")
        raise RecoveryError(f"Error flashing file {file_path} to device {device}: {e}")

def convert_torrent_to_iso(torrent_path):
    # Placeholder function to simulate torrent to ISO conversion
    # In a real-world scenario, you would implement the actual conversion logic
    # For demonstration purposes, this function simply returns a dummy ISO path
    iso_path = os.path.splitext(torrent_path)[0] + ".iso"
    open(iso_path, "w").close()  # Create a dummy ISO file
    return iso_path

def flash_iso(iso_path, device):
    try:
        if os.path.exists(iso_path):
            # Fallback methods for ISO flashing (add more methods as needed)
            methods = [
                ("dd", ["dd", "if=" + iso_path, "of=" + device, "bs=4M", "status=progress"]),
                ("cp", ["cp", iso_path, device])  # Example fallback method
            ]

            for method, command in methods:
                try:
                    logging.info(f"Attempting ISO flashing using method: {method}")
                    subprocess.run(command)
                    logging.info(f"ISO file {iso_path} flashed to device {device} using method: {method}")
                    return True
                except Exception as e:
                    logging.warning(f"Error flashing ISO file {iso_path} to device {device} using method {method}: {e}")
                    continue

            raise RecoveryError(f"All ISO flashing methods failed for file {iso_path}")
        else:
            raise RecoveryError(f"ISO file {iso_path} does not exist, skipping flashing")
    except Exception as e:
        logging.error(f"Error flashing ISO file {iso_path} to device {device}: {e}")
        raise RecoveryError(f"Error flashing ISO file {iso_path} to device {device}: {e}")

def retry(func, *args, attempts=3, delay=1, **kwargs):
    for _ in range(attempts):
        try:
            return func(*args, **kwargs)
        except RecoveryError as e:
            logging.warning(f"Recovery error occurred: {e}. Retrying in {delay} seconds.")
            time.sleep(delay)
    logging.error(f"Failed after {attempts} attempts.")
    raise RecoveryError(f"Failed after {attempts} attempts.")

def main():
    print("===== Welcome to Recovery Mode =====")
    logging.info("Recovery Mode started")
    try:
        while True:
            print("\nOptions:")
            print("1. Backup file")
            print("2. Restore file")
            print("3. Run command")
            print("4. Network diagnosis")
            print("5. Flash ISO or Torrent file")
            print("6. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                file_path = input("Enter the path of the file to backup: ")
                backup_dir = input("Enter the backup directory: ")
                backup_file(file_path, backup_dir)
            elif choice == "2":
                backup_path = input("Enter the path of the backup file: ")
                target_path = input("Enter the target path for restoration: ")
                restore_file(backup_path, target_path)
            elif choice == "3":
                command = input("Enter the command to run: ")
                print(run_command(command))  # Execute the command and print the output
            elif choice == "4":
                network_diagnosis()
            elif choice == "5":
                file_path = input("Enter the path of the ISO or torrent file: ")
                device = input("Enter the device to flash the file to: ")
                if retry(flash_iso_or_torrent, file_path, device, attempts=10):
                    print("Flash successful!")
                else:
                    print("Flash failed.")
            elif choice == "6":
                print("Exiting Recovery Mode.")
                break
            else:
                print("Invalid choice. Please enter a valid option.")
    except RecoveryError as e:
        print(f"Recovery error occurred: {e}")

if __name__ == "__main__":
    main()
              
