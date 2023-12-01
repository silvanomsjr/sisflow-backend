"""
Server Flask

The app starts here
"""
from datetime import datetime, timedelta
from flask import Flask
from flask.blueprints import Blueprint
from flask_cors import CORS

import env
import logging
import routes
import sqlalchemy
import time

sqlalchemy

from models import db
from util import db_check_create, sysconf, syssecurity, syssmtpserver, sysscheduler

# configurates logger
logging.basicConfig(level=logging.NOTSET)

# creates tables before starting the server
db_check_create()

# creates the Flask server for the API
server = Flask(__name__)

# configures its CORS enabling authorization headers for bearer jwt authentication
CORS(
    server,
    origins='*',
    headers=["Content-Type", "Authorization"],
    expose_headers="Authorization"
)

# enable debug mode based on .env
server.debug = env.DEBUG

# starts database
server.config["SQLALCHEMY_DATABASE_URI"] = env.DB_URI
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = env.SQLALCHEMY_TRACK_MODIFICATIONS
db.init_app(server)
db.app = server

# wait for app context to avoid database not initialized problems
with server.app_context():

    # load sistem configurations
    sysconf.load_sys_config()

    # load JWT authentication keys
    private_key_Path, public_key_Path = sysconf.get_key_files_path()
    syssecurity.load_keys(private_key_Path, public_key_Path)

    # start smtp server and wait its async loading for a maximum of 10 seconds
    syssmtpserver.start(env.SMTP_HOST, env.SMTP_PORT, env.SMTP_LOGIN, env.SMTP_PASSWORD)
    logging.info("Awaiting 20 seconds System for Smtp thread start...")
    for i in range(0, 20):
        time.sleep(1)
        if syssmtpserver and syssmtpserver.server_ready:
            break
        elif i == 9:
            logging.warning("Error: System Smtp thread not responding")
            exit()
    
    # start scheduler
    sysscheduler.start(server, syssmtpserver)

    # For scheduler testing
    def test():
        seconds = [0, -10, 20, 5, 2, 7, 15, 15, 19, 1]
        id = 0
        for second in seconds:
            id += 1
            sysscheduler.add_mail(id, datetime.now()+timedelta(0, second),
            'test@ufu.br', f'test with {second} seconds', f'this has sended by event scheduler with {second} timestamp seconds')
        sysscheduler.remove_event(4)
        sysscheduler.print_events()
    
    #test()

# register server route decoupled blueprints
for blueprint in vars(routes).values():
    if isinstance(blueprint, Blueprint):
        server.register_blueprint(blueprint)

# starts the app
if __name__ == "__main__":
    server.run(host=env.HOST, port=env.PORT)