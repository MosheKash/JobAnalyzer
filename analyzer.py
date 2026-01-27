import pandas as pd
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import time
import coursework as cw
import skills as sk
import projects as pro
import work_experience as we
import jobs
import analyzer_util as autil
import cli_util as cutil

# General Overview:

# 1. Ask for a job description, ideally a LinkedIn/Handshake/Indeed link that I then scrape for data
# 2. Have access to a LaTeX document that is basically a super-resume, which it can comment out sections as necessary. Not sure if I should use a LLM directly, or maybe a genetic algorithm similar to knapsack problem guided via LLM
# 3. Have access to a spreadsheet/csv that details every skill that is relevant to me, plus a competency factor that says how competent I am. This competency factor should only be visible to me and the algorithm, not to employers
# 4. Have access to all courses I ever took, all projects I ever built
# 5. Based off of all this info, build me a resume that is the best for for this job
# 6. Write me a cover letter based off of this job

def main_menu():
    valid = {
        '1': {"desc": "Adjust User Info", "func": adjust_user_info}, 
        '2': {"desc": "Analyze Job", "func": analyze_job}
    }
    prompt = """
    
Welcome to JobAnalyzer! This script is written and maintained by Moshe Kashlinsky.
To get started, please pick an option from the menu below:
    """

    return cutil.input_choice(prompt, valid, "Please type 1 to adjust user info, or 2 to analyze a job")

def adjust_user_info():
    valid = {
        '1': {"desc": "Skills", "func": sk.adjust_skills, "args": [adjust_user_info]}, 
        '2': {"desc": "Coursework", "func": cw.adjust_coursework, "args": [adjust_user_info]}, 
        '3': {"desc": "Projects", "func": pro.adjust_projects, "args": [adjust_user_info]}, 
        '4': {"desc": "Work Experience", "func": we.adjust_work_experience, "args": [adjust_user_info]}, 
        '5': {"desc": "Return to Main Menu", "func": main_menu}
    }
    prompt = "Would you like to adjust your skills, coursework, projects, work experience, or return to the main menu?"
    
    return cutil.input_choice(prompt, valid, "Please type 1 to adjust skills, 2 to adjust coursework, 3 to adjust projects, 4 to adjust work experience, or 5 to return to the main menu")

def analyze_job():
    valid = {
        '1': {"desc": "Add Job", "func": jobs.add_job, "args": [main_menu]}, 
        '2': {"desc": "Create Resume", "func": create_resume}, 
        '3': {"desc": "Create Cover Letter", "func": create_cover_letter}
    }
    prompt = "Would you like to input a new job, create a resume or a cover letter?"
    
    return cutil.input_choice(prompt, valid, "Please type 1 to add a job, 2 to create a resume, or 3 to create a cover letter")

def create_resume():
    job_df = pd.read_csv('Stored Info/job_bank.csv')
    if job_df.empty:
        print("No jobs found in the job bank. Please add a job first.")
        return analyze_job()
    
    print("\n"+"-"*30)
    print("Here are the jobs currently stored in your job bank:")
    print(job_df[['title', 'company', 'location']])
    print("-" * 30 + "\n")

    job_index = input(
        "Enter the job index you would like to create a resume for "
        "(or type back to return to analyze job menu): "
    )

    if job_index.lower() == "back":
        return analyze_job()

    try:
        job_index = int(job_index)
        selected_job = job_df.loc[job_index]
    except (ValueError, KeyError):
        print("Invalid job index.")
        return create_resume()
    
    job_description = selected_job.iloc[0]['description']
    
    print(f"\nCreating resume for job: {selected_job.iloc[0]['title']} at {selected_job.iloc[0]['company']}\n")
    
    resume_outline = create_resume_ai(job_description)
    
    print("\n" + "-"*30)
    print("Resume Outline Created:\n")
    print(resume_outline)
    print("-"*30 + "\n")
    
    return analyze_job()

def create_resume_ai(job_description):
    print("Loading assistant...")
    generate_resume_prompt = """
    
    You are an expert career coach. A client has provided you with a job description for a position they are interested in applying for.
    You have access to a large dataset of the client's skills, projects, coursework, and work experience.
    
    Based off of the job description, please analyze the client's datasets and determine which skills, projects, coursework, and work experience are most relevant to the job.
    Your goal is to help the client create a tailored resume that highlights their most relevant qualifications for the job.
    
    Job Description: {job_description}
    
    The client's datasets are as follows:
    
    Coursework: {coursework}
    Projects: {projects}
    Skills: {skills}
    Work Experience: {work_experience}
    
    The client would like you to select the most relevant items from each dataset to include in their resume. The resume is meant to be no longer than a single page, so please be selective in your choices.
    
    Make sure to include in your answer a python valid dictionary, where the keys are the sections of the resume, and the values are a list of the indices of the items from the datasets that you think should correspond to the dataset.
    This dictionary is essential to be included in the proper format, as the program will not function otherwise.
    For example, if you think that you want to include skills 1, 3, and 5 from the skills dataset, and projects 2 and 4 from the projects dataset, your response should look like this:
    
    {{"skills": [1, 3, 5], "projects": [2, 4], "coursework": [...], "work_experience": [...]}}
    
    """
    refine_resume_prompt = """
    
    
  
    """
    showReasoning = False
    print("The model will think for a bit to ensure a good answer. Would you like to show the thinking (May clog up terminal)? Y/N")
    
    prompt = "The model will think for a bit to ensure a good answer. Would you like to show the thinking (May clog up terminal)? Y/N"
    
    selection = cutil.input_yes_no(prompt, error_msg="Please type Y for yes or N for no")
    
    if selection:
        showReasoning = True
    else:
        print("Thinking...")
    
    t1 = time.time()
    generative_model = ChatOllama(model="deepseek-r1", streaming=True, reasoning=True)
    print(f"Model init took: {time.time() - t1:.2f}s")
    
    t2 = time.time()
    prompt = ChatPromptTemplate.from_template(generate_resume_prompt)
    chain = prompt | generative_model
    print(f"Chain creation took: {time.time() - t2:.2f}s")
    
    coursework = pd.read_csv('Stored Info/coursework_bank.csv').to_dict(orient='index')
    projects = pd.read_csv('Stored Info/projects_bank.csv').to_dict(orient='index')
    skills = pd.read_csv('Stored Info/skills_bank.csv').to_dict(orient='index')
    work_experience = pd.read_csv('Stored Info/work_experience_bank.csv').to_dict(orient='index')
    
    inputs = {"coursework": coursework, "projects": projects, "skills": skills, "work_experience": work_experience, "job_description": job_description}
    
    print("Waiting for first token...")
    t3 = time.time()
    
    print("Initializing Response (May take a bit to get started)...\n")
    first_token_received = False
    
    summary_text = ""
    
    for chunk in chain.stream(inputs):
        if not first_token_received:
            print(f"First token received after: {time.time() - t3:.2f}s")
            first_token_received = True
        # Check for reasoning (thinking) tokens
        # These are usually in additional_kwargs when reasoning=True
        reasoning = chunk.additional_kwargs.get("reasoning_content", "")
        if reasoning and showReasoning:
            print(f"\033[90m{reasoning}\033[0m", end="", flush=True)
        
        # Check for the actual answer tokens
        content = chunk.content
        if content:
            print(content, end="", flush=True)
            summary_text += content
    
    followup_prompt = ChatPromptTemplate.from_template(refine_resume_prompt)
    followup_chain = followup_prompt | generative_model
    
    while True: # fix formatting here, we want it to match previous messages
        user_input = input("\nAsk a followup question (or type 'exit' to quit) >>> ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q', '']:
            print("Finalizing bullet points...")
            break
        
        followup_inputs = {
            "user_feedback": user_input,
            "original_resume_outline": summary_text,
            "coursework": coursework, 
            "projects": projects, 
            "skills": skills, 
            "work_experience": work_experience, 
            "job_description": job_description
        }
        
        summary_text = ""
        
        for chunk in followup_chain.stream(followup_inputs):
            # Check for reasoning (thinking) tokens
            reasoning = chunk.additional_kwargs.get("reasoning_content", "")
            if reasoning and showReasoning:
                print(f"\033[90m{reasoning}\033[0m", end="", flush=True)
            
            # Check for the actual answer tokens
            content = chunk.content
            if content:
                print(content, end="", flush=True)
                summary_text += content
    
    return summary_text.strip()
    
    
    
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
    
if __name__ == "__main__":
    autil.init_check()
    main_menu()