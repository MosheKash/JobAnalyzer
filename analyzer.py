from pathlib import Path
import csv
from datetime import datetime
import shutil
import pandas as pd
from jobspy import scrape_jobs
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from datetime import date

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
    valid = {'1': adjust_skills, '2': adjust_coursework, '3': adjust_projects, '4': adjust_work_experience, '5': main_menu}
    print("Would you like to adjust your skills, coursework, projects, work experience, or return to the main menu?\n")
    print("1. Skills")
    print("2. Coursework")
    print("3. Projects")
    print("4. Work Experience")
    print("5. Return to Main Menu\n")
    while True:
        result = input("Selection: ")
        if result in valid:
            return valid[result]()
        print("Invalid input. Please type 1 to adjust skills, 2 to adjust coursework, 3 to adjust projects, 4 to adjust work experience, or 5 to return to the main menu")

def adjust_skills():
    valid = {'1': view_skills, '2': add_skill, '3': remove_skill, '4': edit_skill, '5': adjust_user_info}
    print("Would you like to add, remove, view, or edit a skill?\n")
    print("1. View Skills")
    print("2. Add Skill")
    print("3. Remove Skill")
    print("4. Edit Skill")
    print("5. Return to User Info\n")
    while True:
        result = input("Selection: ")
        if result in valid:
            return valid[result]()
        else:
            print("Invalid input. Please type 1 to view skills, 2 to add a skill, 3 to remove a skill, 4 to edit a skill, or 5 to return to user info")

def view_skills():
    skills_df = pd.read_csv('Stored Info/skills_bank.csv')
    print("\n" + "-"*30)
    print(skills_df)
    print("-"*30 + "\n")
    adjust_skills()

def add_skill():
    while True:
        skill_name = input("Enter the name of the skill (Type back to return to adjusting skills menu): ")
        if skill_name.lower() == "back":
            adjust_skills()
            return
        
        level = input("Enter the level of proficiency as an integer from 1-10, 1 being Beginner to 10 being Master: ")
        
        new_row = pd.DataFrame({'skill_name': [skill_name], 'level': [int(level)]})
        
        if skill_name.strip() == "" or not level.isdigit() or not (1 <= int(level) <= 10):
            print("Invalid input. Skill name cannot be empty and level must be an integer between 1 and 10.")
            continue
        
        if skill_name in pd.read_csv('Stored Info/skills_bank.csv')['skill_name'].values:
            print(f"Skill '{skill_name}' already exists. Please enter a different skill.")
            continue
        
        skills_df = pd.read_csv('Stored Info/skills_bank.csv')
        skills_df = pd.concat([skills_df, new_row], ignore_index=True)
        
        skills_df.to_csv('Stored Info/skills_bank.csv', index=False)
        print(f"Skill '{skill_name}' added successfully.\n")

def remove_skill():
    while True:
        skills_df = pd.read_csv('Stored Info/skills_bank.csv')
        
        skill_to_remove = input("Enter the name of the skill to remove (Type back to return to adjusting skills menu): ")
        
        if skill_to_remove.lower() == "back":
            adjust_skills()
            return
        
        if skill_to_remove in skills_df['skill_name'].values:
            skills_df = skills_df[skills_df['skill_name'] != skill_to_remove]
            skills_df.to_csv('Stored Info/skills_bank.csv', index=False)
            print(f"Skill '{skill_to_remove}' removed successfully.")
        else:
            print(f"Skill '{skill_to_remove}' not found.")

def edit_skill():
    while True:
        skills_df = pd.read_csv('Stored Info/skills_bank.csv')
        
        skill_to_edit = input("Enter the name of the skill to edit (Type back to return to adjusting skills menu): ")
        
        if skill_to_edit.lower() == "back":
            adjust_skills()
            return
        
        if skill_to_edit in skills_df['skill_name'].values:
            new_level = input(f"Enter the new level for '{skill_to_edit}' as an integer from 1-10: ")
            if not new_level.isdigit() or not (1 <= int(new_level) <= 10):
                print("Invalid input. Level must be an integer between 1 and 10.")
                continue
            
            skills_df.loc[skills_df['skill_name'] == skill_to_edit, 'level'] = int(new_level)
            skills_df.to_csv('Stored Info/skills_bank.csv', index=False)
            print(f"Skill '{skill_to_edit}' updated successfully.")
        else:
            print(f"Skill '{skill_to_edit}' not found.")

def adjust_coursework():
    valid = {'1': view_coursework, '2': add_coursework, '3': remove_coursework, '4': edit_coursework, '5': adjust_user_info}
    print("Would you like to add, remove, view, or edit a skill?\n")
    print("1. View Coursework")
    print("2. Add Coursework")
    print("3. Remove Coursework")
    print("4. Edit Coursework")
    print("5. Return to User Info\n")
    
    while True:
        result = input("Selection: ")
        if result in valid:
            return valid[result]()
        else:
            print("Invalid input. Please type 1 to view coursework, 2 to add coursework, 3 to remove coursework, 4 to edit coursework, or 5 to return to user info")

def view_coursework():
    coursework_df = pd.read_csv('Stored Info/coursework_bank.csv')
    print("\n" + "-"*30)
    print(coursework_df)
    print("-"*30 + "\n")
    adjust_coursework()

def add_coursework():
    while True:
        course_id = input("Enter the course ID (Type back to return to adjusting coursework menu): ")
        if course_id.lower() == "back":
            adjust_coursework()
            return
        
        course_name = input("Enter the course name: ")
        institution = input("Enter the institution: ")
        year = input("Enter the year: ")
        semester = input("Enter the semester (F for fall, S for spring, W for winter, SU for summer, O for other): ")
        grade = input("Enter the grade you recieved for this course: ")
        description = input("Enter a brief description of the course: ")
        
        if course_id.strip() == "" or course_name.strip() == "" or institution.strip() == "" or year.strip() == "" or grade.strip() == "" or description.strip() == "":
            print("Invalid input. None of the fields can be empty.")
            continue
        
        if course_id in pd.read_csv('Stored Info/coursework_bank.csv')['course_id'].values:
            print(f"Course with ID '{course_id}' already exists. Please enter a different course ID.")
            continue
        
        if semester not in {'F', 'S', 'W', 'SU', 'O'}:
            print("Invalid input. Semester must be one of the following: F, S, W, SU, O.")
            continue
        
        semester = semester.upper()
        
        coursework_df = pd.read_csv('Stored Info/coursework_bank.csv')
        
        new_row = pd.DataFrame(
            {'course_id': [course_id], 
             'course_name': [course_name], 
             'institution': [institution], 
             'year': [year], 
             'grade': [grade], 
             'description': [description]})
        
        coursework_df = pd.concat([coursework_df, new_row], ignore_index=True)
        coursework_df.to_csv('Stored Info/coursework_bank.csv', index=False)
        print(f"Course '{course_id}' added successfully.\n")

def remove_coursework():
    while True:
        coursework_df = pd.read_csv('Stored Info/coursework_bank.csv')
        
        course_to_remove = input("Enter the course ID to remove (Type back to return to adjusting coursework menu): ")
        
        if course_to_remove.lower() == "back":
            adjust_coursework()
            return
        
        if course_to_remove in coursework_df['course_id'].values:
            coursework_df = coursework_df[coursework_df['course_id'] != course_to_remove]
            coursework_df.to_csv('Stored Info/coursework_bank.csv', index=False)
            print(f"Course '{course_to_remove}' removed successfully.")
        else:
            print(f"Course with ID '{course_to_remove}' not found.")

def edit_coursework():
    while True:
        coursework_df = pd.read_csv('Stored Info/coursework_bank.csv')
        
        course_to_edit = input("Enter the course ID to edit (Type back to return to adjusting coursework menu): ")
        
        if course_to_edit.lower() == "back":
            adjust_coursework()
            return
        
        if course_to_edit in coursework_df['course_id'].values:
            course_name = input("Enter the new course name: ")
            institution = input("Enter the new institution: ")
            year = input("Enter the new year: ")
            semester = input("Enter the new semester (F for fall, S for spring, W for winter, SU for summer, O for other): ")
            grade = input("Enter the new grade you recieved for this course: ")
            description = input("Enter a brief new description of the course: ")
            
            if course_name.strip() == "" or institution.strip() == "" or year.strip() == "" or grade.strip() == "" or description.strip() == "":
                print("Invalid input. None of the fields can be empty.")
                continue
            
            if semester not in {'F', 'S', 'W', 'SU', 'O'}:
                print("Invalid input. Semester must be one of the following: F, S, W, SU, O.")
                continue
            
            semester = semester.upper()
            
            coursework_df.loc[coursework_df['course_id'] == course_to_edit, ['course_name', 'institution', 'year', 'grade', 'description']] = [course_name, institution, year, grade, description]
            coursework_df.to_csv('Stored Info/coursework_bank.csv', index=False)
            print(f"Course '{course_to_edit}' updated successfully.")
        else:
            print(f"Course with ID '{course_to_edit}' not found.")

def adjust_projects():
    valid = {'1': view_projects, '2': add_project, '3': remove_project, '4': edit_project, '5': adjust_user_info}
    print("Would you like to add, remove, view, or edit a project?\n")
    print("1. View Projects")
    print("2. Add Project")
    print("3. Remove Project")
    print("4. Edit Project")
    print("5. Return to User Info\n")
    
    while True:
        result = input("Selection: ")
        if result in valid:
            return valid[result]()
        else:
            print("Invalid input. Please type 1 to view projects, 2 to add a project, 3 to remove a project, 4 to edit a project, or 5 to return to user info")

def view_projects():
    projects_df = pd.read_csv('Stored Info/projects_bank.csv')
    print("\n" + "-"*30)
    print(projects_df)
    print("-"*30 + "\n")
    adjust_projects()
    
def add_project():
    while True:
        project_name = input("Enter the project name (Type back to return to adjusting projects menu): ")
        if project_name.lower() == "back":
            adjust_projects()
            return
        
        description = input("Enter a brief description of the project: ")
        start_date = input("Enter the start date of the project (YYYY-MM-DD): ")
        end_date = input("Enter the end date of the project (YYYY-MM-DD): ")
        link1 = input("Enter the first link related to the project (or leave blank): ")
        link2 = input("Enter the second link related to the project (or leave blank): ")
        
        if project_name.strip() == "" or description.strip() == "" or start_date.strip() == "" or end_date.strip() == "":
            print("Invalid input. Project name, description, start date, and end date cannot be empty.")
            continue
        
        start_date = pd.to_datetime(start_date, format='%Y-%m-%d', errors='coerce')
        end_date = pd.to_datetime(end_date, format='%Y-%m-%d', errors='coerce')
        
        if project_name in pd.read_csv('Stored Info/projects_bank.csv')['project_name'].values:
            print(f"Project '{project_name}' already exists. Please enter a different project name.")
            continue
        
        projects_df = pd.read_csv('Stored Info/projects_bank.csv')
        
        new_row = pd.DataFrame(
            {'project_name': [project_name], 
             'description': [description], 
             'start_date': [start_date], 
             'end_date': [end_date], 
             'link1': [link1], 
             'link2': [link2]})
        
        projects_df = pd.concat([projects_df, new_row], ignore_index=True)
        projects_df.to_csv('Stored Info/projects_bank.csv', index=False)
        print(f"Project '{project_name}' added successfully.\n")

def remove_project():
    while True:
        projects_df = pd.read_csv('Stored Info/projects_bank.csv')
        
        project_to_remove = input("Enter the project name to remove (Type back to return to adjusting projects menu): ")
        
        if project_to_remove.lower() == "back":
            adjust_projects()
            return
        
        if project_to_remove in projects_df['project_name'].values:
            projects_df = projects_df[projects_df['project_name'] != project_to_remove]
            projects_df.to_csv('Stored Info/projects_bank.csv', index=False)
            print(f"Project '{project_to_remove}' removed successfully.")
        else:
            print(f"Project '{project_to_remove}' not found.")

def edit_project():
    while True:
        projects_df = pd.read_csv('Stored Info/projects_bank.csv')
        
        project_to_edit = input("Enter the project name to edit (Type back to return to adjusting projects menu): ")
        
        if project_to_edit.lower() == "back":
            adjust_projects()
            return
        
        if project_to_edit in projects_df['project_name'].values:
            description = input("Enter a brief new description of the project: ")
            start_date = input("Enter the new start date of the project (YYYY-MM-DD): ")
            end_date = input("Enter the new end date of the project (YYYY-MM-DD): ")
            link1 = input("Enter the new first link related to the project (or leave blank): ")
            link2 = input("Enter the new second link related to the project (or leave blank): ")
            
            if description.strip() == "" or start_date.strip() == "" or end_date.strip() == "":
                print("Invalid input. Description, start date, and end date cannot be empty.")
                continue
            
            start_date = pd.to_datetime(start_date, format='%Y-%m-%d', errors='coerce')
            end_date = pd.to_datetime(end_date, format='%Y-%m-%d', errors='coerce')
            
            projects_df.loc[projects_df['project_name'] == project_to_edit, ['description', 'start_date', 'end_date', 'link1', 'link2']] = [description, start_date, end_date, link1, link2]
            projects_df.to_csv('Stored Info/projects_bank.csv', index=False)
            print(f"Project '{project_to_edit}' updated successfully.")
        else:
            print(f"Project '{project_to_edit}' not found.")

def adjust_work_experience():
    valid = {'1': view_work_experience, '2': add_work_experience, '3': remove_work_experience, '4': edit_work_experience, '5': adjust_user_info}
    print("Would you like to add, remove, view, or edit a work experience?\n")
    print("1. View Work Experience")
    print("2. Add Work Experience")
    print("3. Remove Work Experience")
    print("4. Edit Work Experience")
    print("5. Return to User Info\n")
    
    while True:
        result = input("Selection: ")
        if result in valid:
            return valid[result]()
        else:
            print("Invalid input. Please type 1 to view work experience, 2 to add work experience, 3 to remove work experience, 4 to edit work experience, or 5 to return to user info")

def view_work_experience():
    work_experience_df = pd.read_csv('Stored Info/work_experience_bank.csv')
    print("\n" + "-"*30)
    print(work_experience_df)
    print("-"*30 + "\n")
    adjust_work_experience()

def add_work_experience():
    while True:
        company = input("Enter the company name (Type back to return to adjusting work experience menu): ")
        if company.lower() == "back":
            adjust_work_experience()
            return
        
        role = input("Enter your role at the company: ")
        start_date = input("Enter the start date of the work experience (YYYY-MM-DD): ")
        end_date = input("Enter the end date of the work experience (YYYY-MM-DD): ")
        description = input("Enter a brief description of your responsibilities and achievements: ")
        
        if company.strip() == "" or role.strip() == "" or start_date.strip() == "" or end_date.strip() == "" or description.strip() == "":
            print("Invalid input. None of the fields can be empty.")
            continue
        
        start_date = pd.to_datetime(start_date, format='%Y-%m-%d', errors='coerce')
        end_date = pd.to_datetime(end_date, format='%Y-%m-%d', errors='coerce')
        
        work_experience_df = pd.read_csv('Stored Info/work_experience_bank.csv')
        
        new_row = pd.DataFrame(
            {'company': [company], 
             'role': [role], 
             'start_date': [start_date], 
             'end_date': [end_date], 
             'description': [description]})
        
        work_experience_df = pd.concat([work_experience_df, new_row], ignore_index=True)
        work_experience_df.to_csv('Stored Info/work_experience_bank.csv', index=False)
        print(f"Work experience at '{company}' added successfully.\n")

def remove_work_experience():
    while True:
        work_experience_df = pd.read_csv('Stored Info/work_experience_bank.csv')
        
        company_to_remove = input("Enter the company name to remove work experience from (Type back to return to adjusting work experience menu): ")
        
        if company_to_remove.lower() == "back":
            adjust_work_experience()
            return

        all_roles_at_company = work_experience_df[work_experience_df['company'] == company_to_remove]
        if not all_roles_at_company.empty:
            print(f"Work experiences at '{company_to_remove}':")
            print(all_roles_at_company)
            chosen_role = input("Enter the role you want to remove (or type 'all' to remove all experiences at this company): ")
            if chosen_role.lower() == 'all':
                work_experience_df = work_experience_df[work_experience_df['company'] != company_to_remove]
                work_experience_df.to_csv('Stored Info/work_experience_bank.csv', index=False)
                print(f"All work experiences at '{company_to_remove}' removed successfully.")
            elif chosen_role in all_roles_at_company['role'].values:
                work_experience_df = work_experience_df[~((work_experience_df['company'] == company_to_remove) & (work_experience_df['role'] == chosen_role))]
                work_experience_df.to_csv('Stored Info/work_experience_bank.csv', index=False)
                print(f"Work experience as '{chosen_role}' at '{company_to_remove}' removed successfully.")
            else:
                print(f"Role '{chosen_role}' not found at '{company_to_remove}'.")
        else:
            print(f"No work experiences found at '{company_to_remove}'.")

def edit_work_experience():
    while True:
        work_experience_df = pd.read_csv('Stored Info/work_experience_bank.csv')
        
        company_to_edit = input("Enter the company name to edit work experience from (Type back to return to adjusting work experience menu): ")
        
        if company_to_edit.lower() == "back":
            adjust_work_experience()
            return

        all_roles_at_company = work_experience_df[work_experience_df['company'] == company_to_edit]
        if not all_roles_at_company.empty:
            print(f"Work experiences at '{company_to_edit}':")
            print(all_roles_at_company)
            chosen_role = input("Enter the role you want to edit: ")
            if chosen_role in all_roles_at_company['role'].values:
                role = input("Enter your new role at the company: ")
                start_date = input("Enter the new start date of the work experience (YYYY-MM-DD): ")
                end_date = input("Enter the new end date of the work experience (YYYY-MM-DD): ")
                description = input("Enter a brief new description of your responsibilities and achievements: ")
                
                if role.strip() == "" or start_date.strip() == "" or end_date.strip() == "" or description.strip() == "":
                    print("Invalid input. None of the fields can be empty.")
                    continue
                
                start_date = pd.to_datetime(start_date, format='%Y-%m-%d', errors='coerce')
                end_date = pd.to_datetime(end_date, format='%Y-%m-%d', errors='coerce')
                
                work_experience_df.loc[(work_experience_df['company'] == company_to_edit) & (work_experience_df['role'] == chosen_role), ['role', 'start_date', 'end_date', 'description']] = [role, start_date, end_date, description]
                work_experience_df.to_csv('Stored Info/work_experience_bank.csv', index=False)
                print(f"Work experience as '{chosen_role}' at '{company_to_edit}' updated successfully.")
            else:
                print(f"Role '{chosen_role}' not found at '{company_to_edit}'.")
        else:
            print(f"No work experiences found at '{company_to_edit}'.")

def analyze_job():
    valid = {'1': add_job, '2': create_resume, '3': create_cover_letter}
    print("Would you like to input a new job, create a resume or a cover letter?\n")
    print("1. Add Job")
    print("2. Create Resume")
    print("3. Create Cover Letter\n")
    while True:
        result = input("Selection: ")
        if result in valid:
            return valid[result]()
        print("Invalid input. Please type 1 to add a job, 2 to create a resume, or 3 to create a cover letter")

def add_job():
    valid = {'1': job_scraper, '2': custom_job_description, '3': main_menu}
    print("Would you like to perform a job search across job boards, input a custom job description, or return to the main menu?\n")
    print("1. Job Search")
    print("2. Custom Job Description")
    print("3. Return to Main Menu\n")
    while True:
        result = input("Selection: ")
        if result in valid:
            return valid[result]()
        print("Invalid input. Please type 1 to perform a job search, 2 to input a custom job description, or 3 to return to the main menu")

def job_scraper():
    print("Please wait, initializing searcher...")
    
    autocomplete_model = ChatOllama(model="gemma3:1b")
    
    while True:
        search_query = input("Enter the job title or keywords to search for: ")
        location = input("Enter the location for the job search (or leave blank for remote): ")
        num_results = input("Enter the number of job listings to retrieve: ")
        distance = input("Enter the maximum distance from the location in miles (or leave blank for no limit): ")
        job_type = input("Enter the job type (fulltime, parttime, internship, contract) (or leave blank for any): ")
        remote = input("Should the job be remote? (y/n) (or leave blank for any): ")
        
        if not num_results.isdigit() or int(num_results) <= 0:
            print("Invalid input. Please enter a positive integer for the number of job listings.")
            continue
        
        if distance.strip() != "" and (not distance.isdigit() or int(distance) < 0):
            print("Invalid input. Please enter a non-negative integer for the distance.")
            continue
        
        if remote.lower() not in {'y', 'n', ''}:
            print("Invalid input for remote. Please enter 'y' for yes, 'n' for no, or leave blank for any.")
            continue
        
        
        if job_type.strip() != "" and job_type.lower() not in {'fulltime', 'parttime', 'internship', 'contract'}:
            print("Invalid input for job type. Please enter 'fulltime', 'parttime', 'internship', 'contract', or leave blank for any.")
            continue
        
        print("\nSearching for jobs...\n")
        
        generate_google_search_prompt = """
        Generate a concise Google search query to find job listings based on the following parameters. If the location field is blank, assume that the job is remote. Do not include anything else in your response but the query:
                
        Job Title/Keywords: {search_query}
        Location: {location}
        Distance from location (in miles, may be blank): {distance}
        Job Type (fulltime, parttime, internship, contract, may be blank): {job_type}
        """

        formatted_prompt = generate_google_search_prompt.format(
            search_query=search_query,
            location=location,
            distance=distance,
            job_type=job_type
        ).strip()

        google_search_query = autocomplete_model.invoke(formatted_prompt)
        
        print(f"Generated Google Search Query: {google_search_query.content.strip()}\n")
        
        job_listings = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "google"],
            search_query=search_query,
            location=location,
            results_wanted=int(num_results),
            distance=int(distance) if distance.strip() != "" else None,
            job_type=job_type.lower() if job_type.strip() != "" else None,
            remote=True if remote.lower() == 'y' else False if remote.lower() == 'n' else None,
            convert_to_annual=True,
            verbose=1,
            linkedin_fetch_description = True,
            google_search_term=google_search_query.content.strip()
        )
        
        job_result_df = pd.DataFrame(job_listings)
        print("RESULTS:\n" + "-"*30)
        print(job_result_df)
        print("-"*30 + "\n")
        
        job_df = pd.read_csv('Stored Info/job_bank.csv')
        job_df = pd.concat([job_df, job_result_df], ignore_index=True)
        
        job_df = job_df.drop_duplicates()
        
        path = Path("Stored Info/job_bank.csv")
        job_df.to_csv(path, index=False)
        print(f"Job search bank updated")
        
        print("\nWould you like to perform another job search? (y / anything else to return to job addition menu)")
        again = input("Selection: ")
        if again.lower() != 'y':
            return add_job()

def custom_job_description():
    while True:
        print("\n"+"-"*30)
        print("You will be asked to input several fields. If you do not have a field, just leave it blank and press enter.")
        print("-"*30+"\n")
        
        job_url = input("Enter the job URL: ")
        title = input("Enter the job title: ")
        company = input("Enter the company name: ")
        location = input("Enter the job location: ")
        description = input("Enter the job description: ")
        skills = input("Enter the required skills (comma separated): ")
        type_of_salary = input("Enter the type of salary (e.g., hourly, yearly): ")
        min_salary = input("Enter the minimum salary amount: ")
        max_salary = input("Enter the maximum salary amount: ")
        type_of_job = input("Enter the type of job (e.g., fulltime, parttime, internship, contract): ")
        
        id = "custom"+datetime.now().strftime("%Y%m%d%H%M%S")
        
        new_job_entry = {
            "id": id,
            "site": None,
            "job_url": job_url,
            "job_url_direct": job_url,
            "title": title,
            "company": company,
            "location": location,
            "date_posted": date.today().isoformat(),
            "job_type": type_of_job,
            "salary_source": "user_input",
            "interval": type_of_salary,
            "min_amount": float(min_salary) if min_salary else None,
            "max_amount": float(max_salary) if max_salary else None,
            "currency": "USD",
            "is_remote": None,
            "job_level": None,
            "job_function": None,
            "listing_type": None,
            "emails": None,
            "description": description,
            "company_industry": None,
            "company_url": None,
            "company_logo": None,
            "company_url_direct": None,
            "company_addresses": None,
            "company_num_employees": None,
            "company_revenue": None,
            "company_description": None,
            "skills": [s.strip() for s in skills.split(",")],
            "experience_range": None,
            "company_rating": None,
            "company_reviews_count": None,
            "vacancy_count": 1,
            "work_from_home_type": None
        }
        
        job_df = pd.read_csv('Stored Info/job_bank.csv')
        job_df = pd.concat([job_df, pd.DataFrame([new_job_entry])], ignore_index=True)
        
        job_df = job_df.drop_duplicates()
            
        path = Path("Stored Info/job_bank.csv")
        job_df.to_csv(path, index=False)
        print(f"Job search bank updated")
            
        print("\nWould you like to input another job? (y / anything else to return to job addition menu)")
        again = input("Selection: ")
        if again.lower() != 'y':
            return add_job()
    
def create_resume():
    generative_model = ChatOllama(model="deepseek-r1", streaming=True, reasoning=True)
    
    # General idea is to have a latex template for a resume, where each project, skill, course and work experience is a snippet
    # that gets filled in based on the user's data and the job description. The AI will rank the user's data based on relevance to the job,
    # and then say what skills, previous work experience, projects and coursework to include in the resume.
    # A regular PY function will then take the AI generated ranking and construct the latex file, compile it to pdf, and save it to Outputs/Resumes.
    
    # maybe figure out how to implement genetic algorithms here, e.g. generate a few good resumes and then have the user pick the best one
    # then mutate that one to make a few more options, repeat until satisfied. Or have the AI do it by prompting it to improve on the previous version.

def create_cover_letter():
    
    # Similar to resume creation, but with a cover letter template. Don't think LaTeX is a good option here, but who knows. 
    # Maybe figure out how to use google docs/word templates with LLM's.
    # Maybe also figure out a way to use genetic algorithms here as well.
    
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
            "job_bank.csv",
            "coursework_bank.csv",
            "projects_bank.csv",
            "skills_bank.csv",
            "work_experience_bank.csv",
        ],
    }

    headers = {
        "coursework_bank.csv": ["course_id", "course_name", "institution", "year", "semester", "grade", "description"],
        "projects_bank.csv": ["project_name", "description", "start_date", "end_date", "link1", "link2"],
        "skills_bank.csv": ["skill_name", "level"],
        "work_experience_bank.csv": ["company", "role", "start_date", "end_date", "description"],
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