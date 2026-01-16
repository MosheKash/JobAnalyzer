from pylatex import Document, Section, Command, Package, NoEscape, Itemize
from pylatex.base_classes import Environment, Arguments
from pylatex.utils import escape_latex
import json
from pathlib import Path

class JobLong(Environment):
    """Custom environment for job entries with bullet points"""
    _latex_name = 'joblong'
    packages = []
    
    def __init__(self, job_title, date_range):
        super().__init__(arguments=Arguments(job_title, date_range))

class JobShort(Environment):
    """Custom environment for short job entries"""
    _latex_name = 'jobshort'
    packages = []
    
    def __init__(self, job_title, date_range):
        super().__init__(arguments=Arguments(job_title, date_range))

class ProjectEntry(Environment):
    """Custom tabularx environment for project entries"""
    _latex_name = 'tabularx'
    packages = []
    
    def __init__(self):
        super().__init__(arguments=Arguments(NoEscape(r'\linewidth'), NoEscape('@{}l r@{}')))

def create_resume_latex(work_experience, projects, skills, coursework, education):
    """
    Format:
    
    work_experience: list of dicts with keys: company, role, start_date, end_date, type (long or short), description based off of type
    projects: list of dicts with keys: project_name, description, start_date, end_date, link1, link2
    skills: dict of dicts with keys: skill_name, level. Looks like {category 1: [{skill_name: , level: }, ...], category 2: [...], ...}
    coursework: list of dicts with keys: course_name, institution, year, semester, grade, description
    education: list of dicts with keys: institution, degree, field_of_study, start_date, end_date, description. Sorted by end_date descending
    
    """
    
    PROJECT_ROOT = Path(__file__).parent

    # Path to Stored Info/user_info.json
    USER_INFO_PATH = PROJECT_ROOT / "Stored Info" / "user_info.json"

    # Read JSON
    with USER_INFO_PATH.open("r", encoding="utf-8") as f:
        user_info = json.load(f)

    # Extract values
    name = user_info["name"]
    github = user_info["github"]
    linkedin = user_info["linkedin"]
    email = user_info["email"]
    phone = user_info["phone_number"]
    
    # Document setup with geometry
    geometry_options = {"margin": "0.9in"}
    doc = Document(documentclass='article', 
                   document_options=['a4paper', '12pt'],
                   geometry_options=geometry_options)
    
    # Add packages
    doc.packages.append(Package('url'))
    doc.packages.append(Package('parskip'))
    doc.packages.append(Package('color'))
    doc.packages.append(Package('graphicx'))
    doc.packages.append(Package('xcolor', options=['usenames', 'dvipsnames']))
    doc.packages.append(Package('tabularx'))
    doc.packages.append(Package('enumitem'))
    doc.packages.append(Package('supertabular'))
    doc.packages.append(Package('titlesec'))
    doc.packages.append(Package('multicol'))
    doc.packages.append(Package('multirow'))
    doc.packages.append(Package('hyperref', options=['unicode', 'draft=false']))
    doc.packages.append(Package('fontawesome5'))
    
    # Add preamble configurations
    doc.preamble.append(Command('definecolor', arguments=['linkcolour', 'rgb', '0,0.2,0.6']))
    doc.preamble.append(Command('hypersetup', 'colorlinks,breaklinks,urlcolor=linkcolour,linkcolor=linkcolour'))
    
    # Custom column type
    doc.preamble.append(NoEscape(r'\newcolumntype{C}{>{\centering\arraybackslash}X}'))
    
    # Custom section formatting
    doc.preamble.append(NoEscape(r'\titleformat{\section}{\Large\scshape\raggedright}{}{0em}{}[\titlerule]'))
    doc.preamble.append(NoEscape(r'\titlespacing{\section}{0pt}{10pt}{10pt}'))
    
    # Define custom environments
    doc.preamble.append(NoEscape(r'''
\newenvironment{jobshort}[2]
    {
    \begin{tabularx}{\linewidth}{@{}l X r@{}}
    \textbf{#1} & \hfill &  #2 \\[3.75pt]
    \end{tabularx}
    }
    {
    }

\newenvironment{joblong}[2]
    {
    \begin{tabularx}{\linewidth}{@{}l X r@{}}
    \textbf{#1} & \hfill &  #2 \\[3.75pt]
    \end{tabularx}
    \begin{minipage}[t]{\linewidth}
    \begin{itemize}[nosep,after=\strut, leftmargin=1em, itemsep=3pt,label=--]
    }
    {
    \end{itemize}
    \end{minipage}    
    }
'''))
    
    # Set page style
    doc.preamble.append(Command('pagestyle', 'empty'))
    
    # Header with name and contact info
    doc.append(NoEscape(rf'''
\begin{{tabularx}}{{\linewidth}}{{@{{}} C @{{}}}}
\Huge{{{escape_latex(name)}}} \\[7.5pt]
\raisebox{{-0.05\height}}\faLinkedin\ {escape_latex(linkedin)} \ $|$ \ 
\raisebox{{-0.05\height}}\faEnvelope \ {escape_latex(email)} \ $|$ \ 
\raisebox{{-0.05\height}}\faMobile \ {escape_latex(phone)} \ $|$ \
\raisebox{{-0.05\height}}\faGithub \ {escape_latex(github)}\\
\end{{tabularx}}
'''))
    
    # Work Experience Section
    if work_experience != []:
        with doc.create(Section('Work Experience')):
            for job_dict in work_experience:
                if job_dict["type"] == "long":
                    with doc.create(JobLong(f"{job_dict['role']}, {job_dict['company']}", f"{job_dict['start_date']} -- {job_dict['end_date']}")):
                        for item in job_dict['description']:
                            doc.append(NoEscape(rf'\item {escape_latex(item)}'))
                else:
                    with doc.create(JobShort(f"{job_dict['role']}, {job_dict['company']}", f"{job_dict['start_date']} -- {job_dict['end_date']}")):
                        doc.append(NoEscape(rf'\noindent {escape_latex(job_dict["description"])}'))
                doc.append(NoEscape('\n'))
    
    # Projects Section
    if projects != []:
        with doc.create(Section('Projects')):
            doc.append(Command('small'))
            for project_dict in projects:
                with doc.create(ProjectEntry()):
                    doc.append(NoEscape('\n'))
                    doc.append(NoEscape(rf'\textbf{{{escape_latex(project_dict["project_name"])}}} & \hfill \textbf{{{escape_latex(project_dict["start_date"])} -- {escape_latex(project_dict["end_date"])}}} \\[3.75pt]'))
                    doc.append(NoEscape(rf'\multicolumn{{2}}{{@{{}}X@{{}}}}{{{escape_latex(project_dict["description"])}}} \\'))
                    doc.append(NoEscape('\n'))
                doc.append(NoEscape('\n'))
        
    # Education Section
    with doc.create(Section('Education')):
        for degree in education:
            doc.append(NoEscape(r'\noindent'))
            doc.append(NoEscape(rf'\textbf{{{escape_latex(degree["institution"])}}} \hfill {escape_latex(degree["start_date"])} -- {escape_latex(degree["end_date"])}'))
            doc.append(NoEscape('\n\n'))
            doc.append(NoEscape(r'\vspace{-2.5mm}'))
            doc.append(NoEscape('\n\n'))
            doc.append(NoEscape(r'\noindent'))
            doc.append(NoEscape(rf'\textbf{{Degree:}} {escape_latex(degree["degree"])} in {escape_latex(degree["field_of_study"])}'))
            doc.append(NoEscape('\n'))
            doc.append(NoEscape(r'\hfill'))
            doc.append(NoEscape('\n'))
            doc.append(NoEscape(rf'\textbf{{GPA: {escape_latex(degree["gpa"])}}} \\[2pt]'))
            if degree.get("minor", ""):
                doc.append(NoEscape(rf'\textbf{{Minor:}} {escape_latex(degree["minor"])}'))
    
    # Skills Section
    if skills != {}:
        with doc.create(Section('Skills')):
            with doc.create(Itemize(options=NoEscape(r'itemsep 1pt, parskip 1pt, parsep 0pt'))) as itemize:
                for skill_category in skills:
                    itemize.add_item(NoEscape(rf'\textbf{{{escape_latex(skill_category)}}}: {escape_latex(", ".join([skill["skill_name"] for skill in skills[skill_category]]))}'))
    
    if coursework != []:
        with doc.create(Section('Relevant Coursework')):
            with doc.create(Itemize(options=NoEscape(r'itemsep 1pt, parskip 1pt, parsep 0pt'))) as itemize:
                for course_dict in coursework:
                    itemize.add_item(NoEscape(rf'\textbf{{{escape_latex(course_dict["course_name"])}}} ({escape_latex(course_dict["institution"])}, {escape_latex(course_dict["year"])} {escape_latex(course_dict["semester"])}, Recieved a {escape_latex(course_dict["grade"])}): {escape_latex(course_dict["description"])}'))
    
    # Footer
    doc.append(NoEscape(r'\center{\small\textbf{References Available Upon Request}}'))
    
    return doc

