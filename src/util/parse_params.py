"""
Wrap parameters parsing
Because flask_restful reqparse is ugly

Reused from flask-api-starter-kit
"""
from functools import wraps
from flask_restful import reqparse
from . import syssecurity

def parse_params_with_user_authentication(name="Authorization", location="headers", type=str, required=True, 
    help="Required. Bearer with jwt given by server in user autentication", accepted_profiles=None, reqparse_arguments=None):
    """
    Uses Authorization param in request Bearer to make a JWT authentication
    Use the list accepted_profiles to choose which profiles are allowed
    Forward all params without formating, use it before parse_params if needed
    """
    
    def parse(func):
        """ Wrapper """

        @wraps(func)
        def resource_verb(*args, **kwargs):
            """ Decorated function """

            parser = reqparse.RequestParser()
            # add authorization bearer with JWT argument
            parser.add_argument(reqparse.Argument(name, location=location, type=type, required=required, help=help))
            # add other arguments
            if reqparse_arguments:
                for argument in reqparse_arguments:
                    parser.add_argument(argument)
            # parse all arguments
            parsed_reqparse_arguments = parser.parse_args()
            
            # checks if user is allowed and get jwt data
            acess_allowed, error_message, jwt_data = syssecurity.is_auth_token_valid(
                parsed_reqparse_arguments[name], allowed_profiles_acronyms=accepted_profiles)
            if not acess_allowed:
                return error_message, 401

            # create dictionary with the jwt_data field
            parsed_dict = {key: value for key, value in parsed_reqparse_arguments.items() if key is not name}
            parsed_dict['jwt_data'] = jwt_data

            # update decorated function kwargs with the new dictionary
            kwargs.update(parsed_dict)
            return func(*args, **kwargs)

        return resource_verb

    return parse

def parse_params(*arguments):
    """
    Parse the parameters
    Forward them to the wrapped function as named parameters
    """

    def parse(func):
        """ Wrapper """

        @wraps(func)
        def resource_verb(*args, **kwargs):
            """ Decorated function """

            parser = reqparse.RequestParser()
            for argument in arguments:
                parser.add_argument(argument)
            kwargs.update(parser.parse_args())
            return func(*args, **kwargs)

        return resource_verb

    return parse