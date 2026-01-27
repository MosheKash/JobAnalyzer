import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
import cli_util as cutil
from cli_util import CommonConstraints as cc

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
            "job_bank.csv",
            "coursework_bank.csv",
            "projects_bank.csv",
            "skills_bank.csv",
            "work_experience_bank.csv",
            "user_info.json"
        ],
    }

    csv_headers = {
        "coursework_bank.csv": ["course_id", "course_name", "institution", "year", "semester", "grade", "description"],
        "projects_bank.csv": ["project_name", "description", "start_month", "start_year", "end_month", "end_year", "link1", "link2"],
        "skills_bank.csv": ["skill_name", "level"],
        "work_experience_bank.csv": [
            "company", 
            "role", 
            "start_month", 
            "start_year", 
            "end_month", 
            "end_year", 
            "long_short", # True for long description, False for short
            "description_short", 
            "bullet1_long", 
            "bullet2_long", 
            "bullet3_long"
        ],
        "job_bank.csv": [
                "id",
                "site",
                "job_url",
                "job_url_direct",
                "title",
                "company",
                "location",
                "date_posted",
                "job_type",
                "salary_source",
                "interval",
                "min_amount",
                "max_amount",
                "currency",
                "is_remote",
                "job_level",
                "job_function",
                "listing_type",
                "emails",
                "description",
                "company_industry",
                "company_url",
                "company_logo",
                "company_url_direct",
                "company_addresses",
                "company_num_employees",
                "company_revenue",
                "company_description",
                "skills",
                "experience_range",
                "company_rating",
                "company_reviews_count",
                "vacancy_count",
                "work_from_home_type"
            ]
    }

    json_headers = {
        "user_info.json": [
            "full_name",
            "email",
            "phone_number",
            "linkedin_url",
            "github_url",
            "portfolio_url",
            "address"
        ]
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
                
                expected_headers = csv_headers.get(item, [])
                
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

                        
                    prompt = """How would you like to proceed?
1. Load from backup
2. Remake file
3. Proceed without doing anything (not advisable)
Selection: """

                    valid = {'1': {'desc': 'Load from backup', 'func': cutil.return_self_dummy, 'args': ['1']},
                                 '2': {'desc': 'Remake file', 'func': cutil.return_self_dummy, 'args': ['2']},
                                 '3': {'desc': 'Proceed without doing anything', 'func': cutil.return_self_dummy, 'args': ['3']}}

                    result = cutil.input_choice(prompt, valid, "Please type 1 to load from a backup, 2 to remake the file, or 3 to proceed without doing anything")

                    if result == '1':
                        load_backup(item_path)
                    elif result == '2':
                        Path(item_path).unlink()
                        with open(item_path, 'w', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(expected_headers)
                    # result == 3 does nothing

            elif item_path.suffix == ".json":
                expected_headers = json_headers.get(item, [])
                
                if not item_path.exists():
                    with item_path.open("w", encoding="utf-8") as f:
                        json.dump({key: "" for key in expected_headers}, f, indent=4)
                    print(f"Created file with headers: {item_path}")
                
                with item_path.open("r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    existing_headers = list(existing_data.keys())
                
                if existing_headers != expected_headers:
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
                    prompt = """How would you like to proceed?
1. Load from backup
2. Remake file
3. Proceed without doing anything (not advisable)
Selection: """
                    valid = {'1': {'desc': 'Load from backup', 'func': cutil.return_self_dummy, 'args': ['1']},
                                 '2': {'desc': 'Remake file', 'func': cutil.return_self_dummy, 'args': ['2']},
                                 '3': {'desc': 'Proceed without doing anything', 'func': cutil.return_self_dummy, 'args': ['3']}}
                    result = cutil.input_choice(prompt, valid, "Please type 1 to load from a backup, 2 to remake the file, or 3 to proceed without doing anything")

                    if result == '1':
                        load_backup(item_path)
                    elif result == '2':
                        Path(item_path).unlink()
                        with item_path.open("w", encoding="utf-8") as f:
                            json.dump({key: "" for key in expected_headers}, f, indent=4)
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