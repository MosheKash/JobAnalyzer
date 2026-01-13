from pathlib import Path
import csv
from datetime import datetime
import shutil

# General Overview:

# 1. Ask for a job description, ideally a LinkedIn/Handshake/Indeed link that I then scrape for data
# 2. Have access to a LaTeX document that is basically a super-resume, which it can comment out sections as necessary. Not sure if I should use a LLM directly, or maybe a genetic algorithm similar to knapsack problem guided via LLM
# 3. Have access to a spreadsheet/csv that details every skill that is relevant to me, plus a competency factor that says how competent I am. This competency factor should only be visible to me and the algorithm, not to employers
# 4. Have access to all courses I ever took, all projects I ever built
# 5. Based off of all this info, build me a resume that is the best for for this job
# 6. Write me a cover letter based off of this job

def main_menu():
    valid = {'1': adjust_user_info, '2': analyze_job}
    print("Welcome to JobAnalyzer! This script is written and maintained by Moshe Kashlinsky.")
    print("To get started, please pick an option from the menu below:\n")
    print("1. Adjust User Info")
    print("2. Analyze Job\n")
    while True:
        result = input("Selection: ")
        if result in valid:
            return valid[result]()
        print("Invalid input. Please type 1 to adjust user info, or 2 to analyze a job")

def adjust_user_info():
    valid = {'1': adjust_skills, '2': adjust_coursework, '3': adjust_projects}
    print("Would you like to adjust your skills, coursework, or projects?\n")
    print("1. Skills")
    print("2. Coursework")
    print("3. Projects\n")
    while True:
        result = input("Selection: ")
        if result in valid:
            return valid[result]()
        print("Invalid input. Please type 1 to adjust skills, 2 to adjust coursework, or 3 to adjust projects")

def adjust_skills():
    pass

def adjust_coursework():
    pass

def adjust_projects():
    pass

def analyze_job():
    valid = {'1': create_resume, '2': create_cover_letter}
    print("Would you like to create a resume or a cover letter?\n")
    print("1. Create Resume")
    print("2. Create Cover Letter\n")
    while True:
        result = input("Selection: ")
        if result in valid:
            return valid[result]()
        print("Invalid input. Please type 1 to create a resume, or 2 to create a cover letter")

def create_resume():
    pass

def create_cover_letter():
    pass

def init_check(): # check to make sure all necessary folders and files are made
    print("------------------------")
    print("Performing startup check")
    print("------------------------")
    
    healthy = True
    
    base_dir = Path(".")

    structure = {
        "BACKUPS": [],
        "Outputs": [
            "Cover Letters",
            "Resumes",
        ],
        "Stored Info": [
            "Job Descriptions (Previously Applied)",
            "coursework_bank.csv",
            "projects_bank.csv",
            "skills_bank.csv",
            "work_experience_bank.csv",
        ],
    }

    headers = {
        "coursework_bank.csv": ["course_id", "course_name", "institution", "year", "grade", "description"],
        "projects_bank.csv": ["project_name", "description", "date", "link1", "link2"],
        "skills_bank.csv": ["skill_name", "level"],
        "work_experience_bank.csv": ["company", "role", "start_date", "end_date", "description"],
    }

    for folder, contents in structure.items():
        folder_path = base_dir / folder

        if not folder_path.exists():
            folder_path.mkdir(parents=True)
            print(f"Created folder: {folder_path}")

        for item in contents:
            item_path = folder_path / item

            # CSV file
            if item_path.suffix == ".csv":
                
                expected_headers = headers.get(item, [])
                
                if not item_path.exists(): # if the .csv isnt there, create a new one
                    with item_path.open("w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(expected_headers)
                    print(f"Created file with headers: {item_path}")

                with item_path.open("r", newline="", encoding="utf-8") as f: # get the existing headers to prepare for integrity check
                    reader = csv.reader(f)
                    existing_headers = next(reader, [])

                if existing_headers != expected_headers: # verify file integrity
                    healthy = False
                    print(
                        f"⚠️  Header mismatch in {item_path} ⚠️\n"
                        f"   Expected: {expected_headers}\n"
                        f"   Found:    {existing_headers}\n"
                        f"   !!! The file may be corrupted !!!\n"
                    )

                    print("How would you like to proceed?")
                    print("1. Load from backup")
                    print("2. Remake file")
                    print("3. Proceed without doing anything (not advisable)\n")
                    while True:
                        result = input("Selection: ")
                        if result in {'1', '2', '3'}:
                            break
                        print("Invalid input. Please type 1 to load from a backup, 2 to remake the file, or 3 to proceed without doing anything")

                    if result == '1':
                        load_backup(item_path)
                    elif result == '2':
                        Path(item_path).unlink()
                        with open(item_path, 'w', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(expected_headers)
                    # result == 3 does nothing

                    
            # Directory
            else:
                if not item_path.exists():
                    item_path.mkdir(parents=True)
                    print(f"Created folder: {item_path}")
        
    if healthy:
        print("Generating backup...")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = Path("BACKUPS") / timestamp
        try:
            # Create the main backup folder
            path.mkdir(parents=True, exist_ok=True)
            print(f"Successfully created: {path}")

            # List of folders to back up
            folders_to_backup = ["Outputs", "Stored Info"]

            for folder_name in folders_to_backup:
                source = Path(folder_name)
                destination = path / folder_name
                
                if source.exists():
                    # copytree creates the destination directory automatically
                    shutil.copytree(source, destination)
                    print(f"Copied {folder_name} to {destination}")
                else:
                    print(f"Warning: Source folder '{folder_name}' not found. Skipping.")

        except Exception as e:
            print(f"Error during backup process: {e}")
        
        
        
    
    print("\n----------------------")
    print("Startup Check Complete")
    print("----------------------\n")

def load_backup(item_path: Path):
    backup_dir = Path("BACKUPS")
    
    subfolders = [f for f in backup_dir.iterdir() if f.is_dir()]
    
    if not subfolders:
        print("No backups found, creating from scratch")
        
        headers = {
            "coursework_bank.csv": ["course_id", "course_name", "institution", "year", "grade", "description"],
            "projects_bank.csv": ["project_name", "description", "date", "link1", "link2"],
            "skills_bank.csv": ["skill_name", "level"],
            "work_experience_bank.csv": ["company", "role", "start_date", "end_date", "description"],
        }
        Path(item_path).unlink()
        with open(item_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers[item_path.name])
        return
    
    most_recent = max(subfolders, key=lambda f: f.name)
    backup_item = most_recent / "Stored Info" / item_path.name
    Path(item_path).unlink()
    item_path.write_bytes(backup_item.read_bytes())
    
    print(f"Replaced file {item_path.name} with its backup from {most_recent}")
    


if __name__ == "__main__":
    init_check()
    main_menu()