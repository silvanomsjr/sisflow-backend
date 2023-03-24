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
def sistemStrParser(str, studentData):

  if not str:
    return None
  
  substrP = getParserSubstring(str)
  while substrP:
    command = substrP.replace("[[[",'').replace("]]]",'').strip()

    # put user name
    if "userName" in command:
      str = str.replace(substrP, studentData["user_name"])
    
    # put coordinator name
    if "coordinatorName" in command:
      str = str.replace(substrP, getCoordinatorName())

    # gender differences
    if "ifMale?" in command:
      str = str.replace(substrP, command.replace("ifMale?",'').split(":::")[ 0 if studentData["gender"] == 'M' else 1 ])

    # course differences, works only users with student profiles
    if "ifBCC?" in command:
      
      studentProfile = getUserTokenProfile(studentData, "STU")

      if studentProfile and studentProfile["course"]:
        str = str.replace(substrP, command.replace("ifBCC?",'').split(":::")[ 0 if studentProfile["course"] == "BCC" else 1 ])
      else:
        str = str.replace(substrP, '')
    
    # avoid loops when not configured correctly
    else:
      str = str.replace(substrP, '')

    substrP = getParserSubstring(str)
  
  return str