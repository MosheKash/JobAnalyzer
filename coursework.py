import pandas as pd
import cli_util as cutil

def adjust_coursework(adjust_user_info):
    valid = {
        '1': {"desc": "View Coursework", "func": view_coursework}, 
        '2': {"desc": "Add Coursework", "func": add_coursework}, 
        '3': {"desc": "Remove Coursework", "func": remove_coursework}, 
        '4': {"desc": "Edit Coursework", "func": edit_coursework}, 
        '5': {"desc": "Return to User Info", "func": adjust_user_info}
    }
    prompt = "Would you like to add, remove, view, or edit a skill?"
    
    return cutil.input_choice(prompt, valid, "Please type 1 to view coursework, 2 to add coursework, 3 to remove coursework, 4 to edit coursework, or 5 to return to user info")

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

