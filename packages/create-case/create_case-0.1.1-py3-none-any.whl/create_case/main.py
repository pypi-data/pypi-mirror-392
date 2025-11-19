import os
import string
import argparse
from datetime import datetime
import getpass
import ctypes


CONFIG = {"local": ["Pictures", "Readers", "Exports"], "external": ["Extractions", "Readers"], "nas": ["Extractions", "Pictures", "Readers", "Exports"], "onedrive": ["Pictures", "Exports"]}


def list_drives():
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives


def is_external_drive(drive_path):
    DRIVE_REMOVABLE = 2
    drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
    return drive_type == DRIVE_REMOVABLE


def ask_for_drive():
    drives = list_drives()
    for idx, drv in enumerate(drives, 1):
        print(f"{idx}. {drv}")

    choice = input("Select drive: ")
    try:
        return drives[int(choice) - 1]
    except:
        print("Invalid choice")
        return None


def create_folders(base_path, folder_list):
    for folder in folder_list:
        path = os.path.join(base_path, folder)
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            print(f"Failed to create {path}: {e}")


def create_drive_case(case_folder):
    drive = ask_for_drive()
    if not drive:
        return

    if is_external_drive(drive):
        folder_list = CONFIG["external"]
    else:
        folder_list = CONFIG["local"]

    base_path = os.path.join(drive, case_folder)
    create_folders(base_path, folder_list)


def create_nas(year, case):
    base = rf"\\192.168.9.10\Case Archive\Case-Forensic\{year}\F-{year}-{case}"
    create_folders(base, CONFIG["nas"])


def create_onedrive(year, case):
    user = getpass.getuser()
    base = rf"C:\Users\{user}\OneDrive\Documents\Forensic Reports\{year}\F-{year}-{case}"
    create_folders(base, CONFIG["onedrive"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", nargs="?", type=int, default=1)
    parser.add_argument("-y", "--year", type=int, default=datetime.now().year)
    args = parser.parse_args()

    year = args.year
    case = str(args.case).zfill(3)
    case_folder_local = f"F-{year}-{case}"

    print("1. OneDrive")
    print("2. NAS")
    print("3. External Drive Scan")
    choice = input("Choose the location to create the case folder: ").strip()

    if choice == "1":
        create_onedrive(year, case)
    elif choice == "2":
        create_nas(year, case)
    elif choice == "3":
        create_drive_case(case_folder_local)
    
    print("Goodbye!")


if __name__ == "__main__":
    main()
