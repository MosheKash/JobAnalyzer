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
        print("Invalid input. Please type 1 to adjust user info, and 2 to analyze a job")

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
        print("Invalid input. Please type 1 to adjust skills, 2 to adjust coursework, and 3 to adjust projects")

def adjust_skills():
    pass

def adjust_coursework():
    pass

def adjust_projects():
    pass

def analyze_job():
    pass

def create_resume():
    pass

def create_cover_letter():
    pass

def init_check(): # check to make sure all necessary folders and files are made
    pass

if __name__ == "__main__":
    init_check()
    main_menu()