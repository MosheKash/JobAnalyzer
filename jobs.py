import pandas as pd
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from jobspy import scrape_jobs
from datetime import date, datetime
import cli_util as cutil
from cli_util import CommonConstraints as cc

def add_job(main_menu):
    valid = {
        '1': {"desc": "Job Search", "func": job_scraper}, 
        '2': {"desc": "Custom Job Description", "func": custom_job_description}, 
        '3': {"desc": "Return to Main Menu", "func": main_menu}
    }
    prompt = "Would you like to perform a job search across job boards, input a custom job description, or return to the main menu?"
    
    return cutil.input_choice(prompt, valid, "Please type 1 to perform a job search, 2 to input a custom job description, or 3 to return to the main menu")

def job_scraper():
    print("Please wait, initializing searcher...")
    
    autocomplete_model = ChatOllama(model="gemma3:1b")
    
    while True:
        search_query = input("Enter the job title or keywords to search for: ")
        location = input("Enter the location for the job search (or leave blank for remote): ")
        num_results = cutil.input_int(prompt="Enter the number of job listings to retrieve: ", constraint=cc.positive_integer, error_msg="Please enter a positive integer for the number of job listings.")
        distance = cutil.input_int(prompt="Enter the maximum distance from the location in miles (or leave blank for no limit): ", constraint=cc.non_negative_integer, error_msg="Please enter a non-negative integer or leave blank for no limit.", empty_allowed=True)
        job_type = cutil.input_str(prompt="Enter the job type (fulltime, parttime, internship, contract) (or leave blank for any): ", constraint=cc.is_in_set({'fulltime', 'parttime', 'internship', 'contract', ''}), error_msg="Please enter 'fulltime', 'parttime', 'internship', 'contract', or leave blank for any.")
        remote = cutil.input_str(prompt="Should the job be remote? (y/n) (or leave blank for any): ", constraint=cc.is_in_set({'y', 'n', ''}), error_msg="Please enter 'y' for yes, 'n' for no, or leave blank for any.")
        
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
        min_salary = cutil.input_int(prompt="Enter the minimum salary amount: ", constraint=cc.non_negative_integer, error_msg="Please enter a non-negative salary or leave blank.", empty_allowed=True)
        max_salary = cutil.input_int(prompt="Enter the maximum salary amount: ", constraint=cc.non_negative_integer, error_msg="Please enter a non-negative salary or leave blank.", empty_allowed=True)
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

