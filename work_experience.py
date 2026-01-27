import pandas as pd
import time
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import re
import cli_util as cutil
from cli_util import CommonConstraints as cc

def adjust_work_experience(adjust_user_info):
    valid = {
        '1': {"desc": "View Work Experience", "func": view_work_experience}, 
        '2': {"desc": "Add Work Experience", "func": add_work_experience}, 
        '3': {"desc": "Remove Work Experience", "func": remove_work_experience}, 
        '4': {"desc": "Edit Work Experience", "func": edit_work_experience}, 
        '5': {"desc": "Return to User Info", "func": adjust_user_info}
    }
    prompt = "Would you like to add, remove, view, or edit a work experience?"

    return cutil.input_choice(prompt, valid, "Please type 1 to view work experience, 2 to add work experience, 3 to remove work experience, 4 to edit work experience, or 5 to return to user info")

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
        start_year = cutil.input_int(prompt="Enter the year you started working in this position (YYYY): ", constraint=cc.within_range(1900,2100), error_msg="Please enter a valid four-digit year (1900-2100).")
        start_month = cutil.input_int(prompt="Enter the month you started working in this position (MM): ", constraint=cc.within_range(1,12), error_msg="Please enter a valid month (01-12).")
        end_year = cutil.input_int(prompt="Enter the year you ended working in this position (YYYY): ", constraint=cc.within_range(1900,2100), error_msg="Please enter a valid four-digit year (1900-2100).")
        end_month = cutil.input_int(prompt="Enter the month you ended working in this position (MM): ", constraint=cc.within_range(1,12), error_msg="Please enter a valid month (01-12).")
        
        long_short, description_short, bullet1_long, bullet2_long, bullet3_long = work_experience_description_writer()
        
        long_short_mapping = {'S': False, 'L': True}
        
        
        work_experience_df = pd.read_csv('Stored Info/work_experience_bank.csv')
        
        new_row = pd.DataFrame(
            {'company': [company], 
             'role': [role], 
             'start_month': [start_month],
             'start_year': [start_year],
             'end_month': [end_month],
             'end_year': [end_year],
             'long_short': [long_short_mapping[long_short.upper()]],
             'description_short': [description_short],
             'bullet1_long': [bullet1_long],
             'bullet2_long': [bullet2_long],
             'bullet3_long': [bullet3_long]})
        
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

def work_experience_description_writer():
    long_short = cutil.input_str(prompt="Would you like to input a shorter description, or a longer one? (Type S for short, L for long): ", constraint=cc.is_in_set({'S','L'}), error_msg="Please type S for short description or L for long description.")
    if long_short.upper() == "S":
        description_short = input("Enter a brief description of your responsibilities and achievements: ")
        bullet1_long = ""
        bullet2_long = ""
        bullet3_long = ""
    
    elif long_short.upper() == "L":
        description_short = ""
        method = cutil.input_yes_no(prompt="You will now input three bullet points that describe your responsibilities and achievements. Would you like to have AI help you generate them? (y/n): ")
        
        if method.upper() == "A":
            print("Loading assistant...")
            generate_bullets_prompt = """
            
            You are an expert career coach. A client has provided you with a brief description of their responsibilities and achievements at a previous job.
            Based off of this description, generate three concise bullet points that effectively highlight their key contributions and accomplishments in that role.
            Make sure to use action verbs and quantify achievements where possible.
            
            Brief Description: {description_short}
            
            Make sure to respond in the following format. If you do not respond in this exact format, the program will not be able to parse your response:
            
            Bullet Point 1: ...
            Bullet Point 2: ...
            Bullet Point 3: ...
            
            """
            refine_bullets_prompt = """
            
            You are an expert career coach. A client has provided you with a brief description of their responsibilities and achievements at a previous job.
            In your previous correspondence with the client, you generated three bullet points based off of this description that best highlight their key contributions and accomplishments in that role.
            
            The client has now provided the following feedback based off of the bullet points you generated: {user_feedback}
            
            Your original bullet points are as follows: {original_bullets}
            
            The client's initial description of the job is as follows: {description_short}
            
            Please refine and improve the original bullet points based off of the client's feedback, ensuring that they effectively highlight the client's key contributions and accomplishments in that role.
            
            Make sure to respond in the following format, not deviating from it at all. No bolding, or extra parts to your response. If you do not respond in this exact format, the program will not be able to parse your response:
            
            Bullet Point 1: ...
            Bullet Point 2: ...
            Bullet Point 3: ...
            
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
            prompt = ChatPromptTemplate.from_template(generate_bullets_prompt)
            chain = prompt | generative_model
            print(f"Chain creation took: {time.time() - t2:.2f}s")
            
            user_desc = input("Please write a bit about the job you did, focusing on your responsibilities and achievements. The AI will take this answer and help streamline it.\n>>> ")
            
            inputs = {"description_short": user_desc}
            
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
            
            bullet_pattern = r"[\s\S]*?Bullet Point 1:\s*([^\n]*)\n[\s\S]*?Bullet Point 2:\s*([^\n]*)\n[\s\S]*?Bullet Point 3:\s*([^\n]*)[\s\S]*"
            
            match = re.search(bullet_pattern, summary_text, re.DOTALL)
            if match:
                bp1, bp2, bp3 = match.groups()
            else:
                print("Error: Unable to parse bullet points from the model's response. Going to restart process now. Please try again.")
                return work_experience_description_writer()
            
            summary_text = f"Bullet Point 1: {bp1.strip()}\nBullet Point 2: {bp2.strip()}\nBullet Point 3: {bp3.strip()}" # this whole thing is to combat hallucinations
            
            followup_prompt = ChatPromptTemplate.from_template(refine_bullets_prompt)
            followup_chain = followup_prompt | generative_model
            
            while True: # fix formatting here, we want it to match previous messages
                user_input = input("\nAsk a followup question (or type 'exit' to quit) >>> ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q', '']:
                    print("Finalizing bullet points...")
                    break
                
                followup_inputs = {
                    "user_feedback": user_input,
                    "original_bullets": summary_text,
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
                
                bullet_pattern = r"[\s\S]*?Bullet Point 1:\s*([^\n]*)\n[\s\S]*?Bullet Point 2:\s*([^\n]*)\n[\s\S]*?Bullet Point 3:\s*([^\n]*)[\s\S]*"
            
                match = re.search(bullet_pattern, summary_text, re.DOTALL)
                if match:
                    bp1, bp2, bp3 = match.groups()
                else:
                    print("Error: Unable to parse bullet points from the model's response. Going to restart process now. Please try again.")
                    continue
                
                summary_text = f"Bullet Point 1: {bp1.strip()}\nBullet Point 2: {bp2.strip()}\nBullet Point 3: {bp3.strip()}"
            
            bullet1_long = bp1.strip()
            bullet2_long = bp2.strip()
            bullet3_long = bp3.strip()
            
        elif method.upper() == "M":
            bullet1_long = input("Give a quick description of your responsibilities and achievements (1/3): ")
            bullet2_long = input("Give a quick description of your responsibilities and achievements (2/3): ")
            bullet3_long = input("Give a quick description of your responsibilities and achievements (3/3): ")
        
    return long_short, description_short, bullet1_long, bullet2_long, bullet3_long

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
                start_year = cutil.input_int(prompt="Enter the new year you started working in this position (YYYY): ", constraint=cc.within_range(1900,2100), error_msg="Please enter a valid four-digit year (1900-2100).")
                start_month = cutil.input_int(prompt="Enter the new month you started working in this position (MM): ", constraint=cc.within_range(1,12), error_msg="Please enter a valid month (01-12).")
                end_year = cutil.input_int(prompt="Enter the new year you ended working in this position (YYYY): ", constraint=cc.within_range(1900,2100), error_msg="Please enter a valid four-digit year (1900-2100).")
                end_month = cutil.input_int(prompt="Enter the new month you ended working in this position (MM): ", constraint=cc.within_range(1,12), error_msg="Please enter a valid month (01-12).")
                long_short, description_short, bullet1_long, bullet2_long, bullet3_long = work_experience_description_writer()
                
                long_short_mapping = {'S': False, 'L': True}
                
                work_experience_df.loc[(work_experience_df['company'] == company_to_edit) & (work_experience_df['role'] == chosen_role), 
                                       ['role', 'start_month', 'start_year', 'end_month', 'end_year', 'long_short', 'description_short', 'bullet1_long', 'bullet2_long', 'bullet3_long']] = [
                                           role, start_month, start_year, end_month, end_year, long_short_mapping[long_short.upper()], description_short, bullet1_long, bullet2_long, bullet3_long]
                work_experience_df.to_csv('Stored Info/work_experience_bank.csv', index=False)
                print(f"Work experience as '{chosen_role}' at '{company_to_edit}' updated successfully.")
            else:
                print(f"Role '{chosen_role}' not found at '{company_to_edit}'.")
        else:
            print(f"No work experiences found at '{company_to_edit}'.")
