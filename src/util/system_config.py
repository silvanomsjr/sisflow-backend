"""
System Configuration

Has stored configurations to be reused
"""

from datetime import datetime
from pathlib import Path
from sqlalchemy import exc

import json
import logging
import os
import requests
import traceback

from repositories import ConfigRepository, ConfigsRepository

logging = logging.getLogger(__name__)

class SystemConfiguration():

    def __init__(self):
        self.coordinator_email = None
        self.coordinator_name = None
        self.key_files_path = None
        self.user_files_path = None
        self.holiday_data = None
    
    def load_sys_config(self):
        
        logging.info("Loading system configurations")
        
        self.__load_mails()
        self.__load_paths()
        self.__load_holidays()
    
    def __load_mails(self):

        if not self.coordinator_email:
            config_mail = ConfigRepository.read_config_mail(config_name="coordinator mail")

            if not config_mail:
                logging.warn("System error: Missing coordinator mail configuration")
                exit()

            self.coordinator_email = config_mail.mail
            self.coordinator_name = config_mail.mail_name

            logging.info("Mails loaded")
    
    def __load_paths(self):

        if not self.key_files_path or not self.user_files_path:
            
            root_path = os.path.abspath(os.sep)

            try:
                self.key_files_path = root_path / Path(ConfigRepository.read_config_system_path(config_name="root path key files").system_path)
                self.user_files_path = root_path / Path(ConfigRepository.read_config_system_path(config_name="root path user files").system_path)
            except Exception as e:
                logging.warn("System error: Error trying to load system file paths data", e)
                exit()

            # creates paths if not exists
            self.key_files_path.mkdir(parents=True, exist_ok=True)
            self.user_files_path.mkdir(parents=True, exist_ok=True)
            
            logging.info("Paths loaded")
    
    def __load_holidays(self):
        """ Load Holidays, not used in the monograph version, but kept for future use
            Although this solution worked when this prototype was released, it should be changed to a newer version
            with a safe way to set holidays, like using FACOM official way of loading """

        # Loads this year holidays if not configurated
        actual_year = str(datetime.today().year)
        config_year = ConfigRepository.read_config_year(actual_year)
        
        if not config_year:
            logging.info("Loading holidays from external API")
        
            holidays_res = None
            try:
                holidays_res = requests.get("https://brasilapi.com.br/api/feriados/v1/" + actual_year).json()
            except Exception as e:
                logging.warn("Error trying to load holidays from external API", e)
                exit()
        
            actual_config = ConfigRepository.create_config(config_name=f"year {str(actual_year)}")
            actual_config_year = ConfigRepository.create_config_year(config_id=actual_config.id, year=actual_year)

            for holiday in holidays_res:
                actual_config_year_holiday = ConfigRepository.create_config_year_holiday(
                    actual_config_year.year, 'API', holiday["name"], holiday["date"])
            
        self.holiday_data = ConfigsRepository.read_config_year_holidays(actual_year)

        logging.info("Holidays loaded")

    def get_key_files_path(self):
        return self.key_files_path / "private-key.pem", self.key_files_path / "public-key.pem"
    
    def get_user_file_path(self, user_file_hash):
        print(self.user_files_path, user_file_hash)
        return self.user_files_path / user_file_hash

    @staticmethod
    def get_formated_mysql_json(mysql_json):

        if not mysql_json:
            return ''
        
        if isinstance(mysql_json, str):
            return json.loads(mysql_json)
        
        return json.loads(mysql_json.decode("utf-8"))

    # Return a specific profile object from a user jwt token
    @staticmethod
    def get_user_token_profile(user_token, profile_acronym):

        if not user_token or not user_token["profiles"]:
            return None
  
        for profile in user_token["profiles"]:
            if profile["profile_acronym"] == profile_acronym:
                return profile
  
        return None

    # get a substring that starts in [[[ and finishes in ]]],
    #   used in the PARSER
    @staticmethod
    def get_parser_substring(raw_str):
    
        substr_start = raw_str.find("[[[")
        if substr_start == -1:
            return None
    
        substr_end = raw_str.find("]]]", substr_start)
        if substr_end == -1:
            logging.warn("Error while parsing an string, parser not closed")
            return None

        return raw_str[substr_start:substr_end+3]

    # PARSER - parses a given string changing text commands to user data
    def sistem_str_parser(self, raw_str, student_data=None, advisor_data=None):

        student_profile = None

        if not raw_str:
            return None
  
        if student_data:
            student_profile = SystemConfiguration.get_user_token_profile(student_data, "STU")
        if advisor_data:
            advisor_profile = SystemConfiguration.get_user_token_profile(advisor_data, "ADV")
  
        parser_substr = SystemConfiguration.get_parser_substring(raw_str)
        while parser_substr:
            command = parser_substr.replace("[[[",'').replace("]]]",'').strip()

            # single attributes parsing
            # replace command with names
            if "studentName" in command:
                raw_str = raw_str.replace(parser_substr, student_data.get("user_name") if student_data else "")
            elif "advisorName" in command:
                raw_str = raw_str.replace(parser_substr, advisor_data.get("user_name") if advisor_data else "")
            elif "coordinatorName" in command:
                raw_str = raw_str.replace(parser_substr, self.coordinator_name)
    
            # replace with matricula
            elif "studentMatricula" in command:
                raw_str = raw_str.replace(parser_substr, student_profile.get("matricula") if student_profile else "")
    
            # replace with student course
            elif "studentCourse" in command:
                raw_str = raw_str.replace(parser_substr, student_profile.get("course") if student_profile else "")
    
            # replace with advisor siape
            elif "advisorSiape" in command:
                raw_str = raw_str.replace(parser_substr, advisor_profile.get("siape") if advisor_profile else "")
      
            # conditional parsing
            elif ":::" in command:
      
                # gender differences
                if "ifStudentMale?" in command and student_data and student_data.get("gender"):
                    raw_str = raw_str.replace(parser_substr, command.replace("ifStudentMale?",'').split(":::")
                        [ 0 if student_data["gender"] == 'M' else 1 ])
                elif "ifAdvisorMale?" in command and advisor_data and advisor_data.get("gender"):
                    raw_str = raw_str.replace(parser_substr, command.replace("ifAdvisorMale?",'').split(":::")
                        [ 0 if advisor_data["gender"] == 'M' else 1 ])

                # course differences, works only with students
                elif "ifBCCStudent?" in command and student_profile and student_profile.get("course"):
                    raw_str = raw_str.replace(parser_substr, command.replace("ifBCCStudent?",'').split(":::")
                        [ 0 if student_profile["course"] == "BCC" else 1 ])
                
                # avoid loops when not configured correctly
                else:
                    raw_str = raw_str.replace(parser_substr, '')
            else:
                raw_str = raw_str.replace(parser_substr, '')

            parser_substr = SystemConfiguration.get_parser_substring(raw_str)
  
        return raw_str