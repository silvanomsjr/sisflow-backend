import json
from utils.sistemConfig import getCoordinatorName

# Formats a json string received from mysql db. Works with empty values
def getFormatedMySQLJSON(mysqlJSON):
  
  if not mysqlJSON:
    return ''
  
  if isinstance(mysqlJSON, str):
    return json.loads(mysqlJSON)
  
  return json.loads(mysqlJSON.decode("utf-8"))

# Return a profile object from user token
def getUserTokenProfile(userToken, profileAcronym):

  if not userToken or not userToken["profiles"]:
    return None
  
  for profile in userToken["profiles"]:
    if profile["profile_acronym"] == profileAcronym:
      return profile
  
  return None

# PARSER - get parser token substring
def getParserSubstring(str):
  
  substrStart = str.find("[[[")
  if substrStart == -1:
    return None
  
  substrEnd = str.find("]]]",substrStart)
  if substrEnd == -1:
    print("# Warning, Error while parsing an string, parser not closed")
    return None

  return str[substrStart:substrEnd+3]

# PARSER - parses a given string changing text options based on user data
def sistemStrParser(str, studentData=None, advisorData=None):

  studentProfile = None

  if not str:
    return None
  
  if studentData:
    studentProfile = getUserTokenProfile(studentData, "STU")
  if advisorData:
    advisorProfile = getUserTokenProfile(studentData, "ADV")
  
  substrP = getParserSubstring(str)
  while substrP:
    command = substrP.replace("[[[",'').replace("]]]",'').strip()

    # single attributes parsing
    # put names
    if "studentName" in command:
      str = str.replace(substrP, studentData.get("user_name") if studentData else "")
    elif "advisorName" in command:
      str = str.replace(substrP, advisorData.get("user_name") if advisorData else "")
    elif "coordinatorName" in command:
      str = str.replace(substrP, getCoordinatorName())
    
    # put student matricula
    elif "studentMatricula" in command:
      str = str.replace(substrP, studentProfile.get("matricula") if studentProfile else "")
    
    # put student course
    elif "studentCourse" in command:
      str = str.replace(substrP, studentProfile.get("course") if studentProfile else "")
    
    # put advisor siape
    elif "advisorSiape" in command:
      str = str.replace(substrP, advisorProfile.get("siape") if advisorProfile else "")
      
    # conditional parsing
    elif ":::" in command:
      
      # gender differences
      if "ifStudentMale?" in command:
        str = str.replace(substrP, command.replace("ifStudentMale?",'').split(":::")[ 0 if studentData["gender"] == 'M' else 1 ])
      if "ifAdvisorMale?" in command:
        str = str.replace(substrP, command.replace("ifAdvisorMale?",'').split(":::")[ 0 if advisorData["gender"] == 'M' else 1 ])

      # course differences, works only with students
      if "ifBCCStudent?" in command:
        if studentProfile and studentProfile["course"]:
          str = str.replace(substrP, command.replace("ifBCCStudent?",'').split(":::")[ 0 if studentProfile["course"] == "BCC" else 1 ])
        else:
          str = str.replace(substrP, '')
      
    # avoid loops when not configured correctly
    else:
      str = str.replace(substrP, '')

    substrP = getParserSubstring(str)
  
  return str