import pandas as pd
import time
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import cli_util as cutil
from cli_util import CommonConstraints as cc

def adjust_projects(adjust_user_info):
    valid = {
        '1': {"desc": "View Projects", "func": view_projects}, 
        '2': {"desc": "Add Project", "func": add_project}, 
        '3': {"desc": "Remove Project", "func": remove_project}, 
        '4': {"desc": "Edit Project", "func": edit_project}, 
        '5': {"desc": "Return to User Info", "func": adjust_user_info}
    }
    prompt = "Would you like to add, remove, view, or edit a project?"
    
    return cutil.input_choice(prompt, valid, "Please type 1 to view projects, 2 to add a project, 3 to remove a project, 4 to edit a project, or 5 to return to user info")

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
        start_month = cutil.input_int(prompt="Enter the month you started the project (MM): ", constraint=cc.within_range(1,12), error_msg="Please enter a valid month (01-12).")
        start_year = cutil.input_int(prompt="Enter the year you started the project (YYYY): ", constraint=cc.within_range(1900,2100), error_msg="Please enter a valid four-digit year (1900-2100).")
        end_month = cutil.input_int(prompt="Enter the month you ended the project (MM): ", constraint=cc.within_range(1,12), error_msg="Please enter a valid month (01-12).")
        end_year = cutil.input_int(prompt="Enter the year you ended the project (YYYY): ", constraint=cc.within_range(1900,2100), error_msg="Please enter a valid four-digit year (1900-2100).")
        link1 = input("Enter the first link related to the project (or leave blank): ")
        link2 = input("Enter the second link related to the project (or leave blank): ")
        
        method = cutil.input_yes_no("Would you like to use AI to help generate the project description? (y/n): ")
        if method:
            description = project_description_writer()
        else:
            description = input("Enter a brief description of the project: ")
        
        if project_name in pd.read_csv('Stored Info/projects_bank.csv')['project_name'].values:
            print(f"Project '{project_name}' already exists. Please enter a different project name.")
            continue
        
        projects_df = pd.read_csv('Stored Info/projects_bank.csv')
        
        new_row = pd.DataFrame(
            {'project_name': [project_name], 
             'description': [description], 
             'start_month': [start_month],
             'start_year': [start_year],
             'end_month': [end_month],
             'end_year': [end_year],
             'link1': [link1], 
             'link2': [link2]})
        
        projects_df = pd.concat([projects_df, new_row], ignore_index=True)
        projects_df.to_csv('Stored Info/projects_bank.csv', index=False)
        print(f"Project '{project_name}' added successfully.\n")

def project_description_writer():
    print("Loading assistant...")
    generate_description_prompt = """
    
    You are an expert career coach. A client has provided you with a brief description of their responsibilities and achievements on a previous project.
    Based off of this description, help them streamline it into a brief and effective project description that highlights their key contributions and accomplishments.
    Make sure to use action verbs and quantify achievements where possible, and not make it too long or overbearing.
    
    Brief Description: {user_description}
    
    Make sure to only respond with the description of the project. Do not include any extra text or formatting. The system will not be able to parse your response if you do.
    
    """
    refine_description_prompt = """
    
    You are an expert career coach. A client has provided you with a brief description of their responsibilities and achievements on a previous project.
    In your previous correspondence with the client, you generated the following project description based off of their description of the project: {original_description}
    
    The client has now provided the following feedback based off of the description you generated: {user_feedback}
    
    The client's initial description of the project is as follows: {description_short}
    
    Please refine and improve the original project description based off of the client's feedback, ensuring that it effectively highlights the client's key contributions and accomplishments on the project.
    
    Make sure to only respond with the description of the project. Do not include any extra text or formatting. The system will not be able to parse your response if you do.
    
    """
    showReasoning = False
    selection = cutil.input_yes_no("The model will think for a bit to ensure a good answer. Would you like to show the thinking (May clog up terminal)? (y/n):")
    if selection:
        showReasoning = True
    else:
        print("Thinking...\n")
    
    
    t1 = time.time()
    generative_model = ChatOllama(model="deepseek-r1", streaming=True, reasoning=True)
    print(f"Model init took: {time.time() - t1:.2f}s")
    
    t2 = time.time()
    prompt = ChatPromptTemplate.from_template(generate_description_prompt)
    chain = prompt | generative_model
    print(f"Chain creation took: {time.time() - t2:.2f}s")
    
    user_desc = input("Please write a bit about the project you did, focusing on your responsibilities, difficulties you overcame, and achievements. The AI will take this answer and help streamline it.\n>>> ")
    
    inputs = {"user_description": user_desc}
    
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
    
    followup_prompt = ChatPromptTemplate.from_template(refine_description_prompt)
    followup_chain = followup_prompt | generative_model
    
    while True: # fix formatting here, we want it to match previous messages
        user_input = input("\nAsk a followup question (or type 'exit' to quit) >>> ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q', '']:
            print("Finalizing bullet points...")
            break
        
        followup_inputs = {
            "user_feedback": user_input,
            "original_description": summary_text,
            "description_short": user_desc
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
            method = cutil.input_yes_no("Would you like to use AI to help generate the project description? (y/n): ")
            if method:
                description = project_description_writer()
            else:
                description = input("Enter a brief description of the project: ")
            start_month = cutil.input_int(prompt="Enter the new month you started the project (MM): ", constraint=cc.within_range(1,12), error_msg="Please enter a valid month (01-12).")
            start_year = cutil.input_int(prompt="Enter the new year you started the project (YYYY): ", constraint=cc.within_range(1900,2100), error_msg="Please enter a valid four-digit year (1900-2100).")
            end_month = cutil.input_int(prompt="Enter the new month you ended the project (MM): ", constraint=cc.within_range(1,12), error_msg="Please enter a valid month (01-12).")
            end_year = cutil.input_int(prompt="Enter the new year you ended the project (YYYY): ", constraint=cc.within_range(1900,2100), error_msg="Please enter a valid four-digit year (1900-2100).")
            link1 = input("Enter the new first link related to the project (or leave blank): ")
            link2 = input("Enter the new second link related to the project (or leave blank): ")
            
            projects_df.loc[projects_df['project_name'] == project_to_edit, ['description', 'start_month', 'start_year', 'end_month', 'end_year', 'link1', 'link2']] = [description, start_month, start_year, end_month, end_year, link1, link2]
            projects_df.to_csv('Stored Info/projects_bank.csv', index=False)
            print(f"Project '{project_to_edit}' updated successfully.")
        else:
            print(f"Project '{project_to_edit}' not found.")