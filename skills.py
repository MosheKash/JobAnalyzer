import pandas as pd
import cli_util as cutil
from cli_util import CommonConstraints as cc

def adjust_skills(adjust_user_info):
    valid = {
        '1': {"desc": "View Skills", "func": view_skills}, 
        '2': {"desc": "Add Skill", "func": add_skill}, 
        '3': {"desc": "Remove Skill", "func": remove_skill}, 
        '4': {"desc": "Edit Skill", "func": edit_skill}, 
        '5': {"desc": "Return to User Info", "func": adjust_user_info}
    }
    prompt = "Would you like to add, remove, view, or edit a skill?"

    return cutil.input_choice(prompt, valid, "Please type 1 to view skills, 2 to add a skill, 3 to remove a skill, 4 to edit a skill, or 5 to return to user info")

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
        
        level = cutil.input_int(prompt="Enter the level of proficiency as an integer from 1-10, 1 being Beginner to 10 being Master: ", constraint=cc.within_range(1,10), error_msg="Please enter an integer between 1 and 10 for the skill level.")
        
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
            new_level = cutil.input_int(prompt=f"Enter the new level for '{skill_to_edit}' as an integer from 1-10: ", constraint=cc.within_range(1,10), error_msg="Please enter an integer between 1 and 10 for the skill level.")
            skills_df.loc[skills_df['skill_name'] == skill_to_edit, 'level'] = int(new_level)
            skills_df.to_csv('Stored Info/skills_bank.csv', index=False)
            print(f"Skill '{skill_to_edit}' updated successfully.")
        else:
            print(f"Skill '{skill_to_edit}' not found.")