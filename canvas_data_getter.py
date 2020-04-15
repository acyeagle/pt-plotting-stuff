
from canvasapi import Canvas

### API sorcery ###

API_URL = ""
API_KEY = ""
# Connect to the course
canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course()

### Note on data format ###

"""
Data is formatted as the following:

the_data = {'section_name' : 'ENGR 216-501',
            'prof_name' : 'Cahill',
            'section_pts' : ['jane doe', ...],
            'assignments' : [   {'assignment_name' : 'HW1',
                                 'graders' : ['jane doe', ...],     <--- Indices line up
                                 'ammount_graded' : [4, ...]        <--- with these indices
                                },
                                {'assignment_name' : 'HW2',
                                 'graders' : ['jane doe', ...]
                                 'ammount_graded' : [11, ...]
                                }, 
                                ...
                            ]
            }    
"""

### Functions to fetch Sections ###

def get_prof_sections(prof):
    """ Takes the prof. name as a string. 
    Returns a list of the actual Section objects for the given PT.
    """
    prof_id = course.get_users(search_term=prof)[0].id
    sections = []
    for section in course.get_sections():
        enrollments = section.get_enrollments(type=['TeacherEnrollment'])
        for entry in enrollments:
            if entry.user_id == prof_id:
                sections.append(section)
                break
    return sections

def get_pt_sections(pt):
    """ Takes the PT name as a string. 
    Returns a list of the actual Section objects for the given PT.
    """
    pt_id = course.get_users(search_term=pt)[0].id
    sections = []
    for section in course.get_sections():
        enrollments = section.get_enrollments(type=['TaEnrollment'])
        for entry in enrollments:
            if entry.user_id == pt_id:
                sections.append(section)
                break
    return sections

def get_all_sections():
    """ Returns a all the actual Section objects.
    """
    sections = course.get_sections()
    return list(sections)
    
def get_sections(section_names):
    """ Take a list of sections names as strings.
    Returns a list of the actual Section objects.
    """
    sections = []
    for name in section_names:
        section = course.get_sections(search_term=name)
        sections.append(section[0])
    return sections
    
### The workhorse function to get the data for a given section. ###

def get_the_data(section):
    """ Takes a Section object. 
    Returns all of the grade info for this section as a custom data object. 
    """
    # Setup the dictionary to return
    section_data = {}
    section_data['name'] = section.name
    section_data['prof_name'] = _get_prof_name(section)
    # Get a list of all of the PTs for this section (as names)
    enrollments = section.get_enrollments()
    pts = [entry.user['name'] for entry in enrollments \
              if entry.type == 'TaEnrollment']
    student_ids = [entry.user['id'] for entry in enrollments \
                   if entry.type == 'StudentEnrollment']
    section_data['section_pts'] = pts
    # Iterate through assignments
    assignment_data = []
    for entry in course.get_assignments():
        print(f"On assignment {entry.name}...")
        # Initial fetch
        graders, graded_ammount = _get_grader_breakdown(entry, student_ids)
        # If blank (wrong section), skip
        if graders:      
            # Make sure every PT has an entry
            for pt in pts:
                if pt not in graders:
                    graders.append(pt)
                    graded_ammount.append(0)
            # Create the entry for the individual assignment
            data_entry = {}
            data_entry['assignment_name'] = entry.name
            data_entry['graders'] = graders
            data_entry['ammount_graded'] = graded_ammount
            assignment_data.append(data_entry)
    # Pack up and return
    section_data['assignments'] = assignment_data
    return section_data
    
### Helper functions for get_the_data ###

def _get_prof_name(section):
    """ Returns the prof. for a given section as a string.
    """
    enrollments = section.get_enrollments(type=['TeacherEnrollment'])
    try:
        name = enrollments[0].user['name']
    except IndexError:
        name = 'None'
    return name
   
def _get_grader_breakdown(assignment, student_ids):
    """ For a given Assignment, function returns two lists:
    - a list of graders
    - a corresponding list of how many submissions each grader graded
    """
    subs = assignment.get_submissions(include=['submission_history'])
    breakdown = {}
    for submission in subs:
        submission = submission.attributes
        # Check if it is for this section
        if submission['user_id'] in student_ids:
            # If the most recent submission isn't the one that is graded,
            # go get the earlier sub.
            if not submission['grade_matches_current_submission']:
                for entry in submission['submission_history']:
                    if entry['grade_matches_current_submission']:
                        submission = entry
            # Check ungraded
            if submission['workflow_state'] == 'submitted':
                grader = 'Ungraded'
            # Check unsubmitted
            elif submission['workflow_state'] == 'unsubmitted': 
                grader = 'Unsubmitted'
            # Else get grader
            elif submission['workflow_state'] == 'graded':
                grader = course.get_user(submission['grader_id']).name
            else:
                raise ValueError(f"Unhandled workflow_state: \
                                 {submission['workflow_state']}")
            # Increment
            breakdown[grader] = breakdown.get(grader, 0) + 1
    # Return two lists
    graders = list(breakdown.keys())
    graded = [breakdown[entry] for entry in graders]
    return graders, graded
