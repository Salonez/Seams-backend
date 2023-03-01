from functools import wraps
from flask import request

from src.error import AccessError, InputError
from src.helpers import verify_jwt_session_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if request.method == 'GET':
            token = request.args.get('token')

        if request.method in ['POST', 'PUT', 'DELETE']:
            # jwt is passed in the request header
            json_body = request.get_json()

            if json_body is None:
                raise AccessError(description='Did not provide a json payload')
        
            if 'token' in json_body:
                token = json_body['token']

        if not token:
            raise AccessError(description='Token is missing')
  
        auth_user_id = verify_jwt_session_token(token)
        if auth_user_id is None:
            raise AccessError(description='Token is invalid')

        # returns the current logged in users contex to the routes
        return  f(auth_user_id, *args, **kwargs)
  
    return decorated

