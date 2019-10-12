# the following try/except block will make the custom check compatible with any Agent version
try:
    # first, try to import the base class from old versions of the Agent...
    from checks import AgentCheck
except ImportError:
    # ...if the above failed, the check is running in Agent version 6 or later
    from datadog_checks.checks import AgentCheck

# content of the special variable __version__ will be shown in the Agent status page
__version__ = "1.0.0"

import socket
import ftplib
import json

# For Datadog event check
# need to install the datadog loibrary for python: 
# sudo /opt/datadog-agent/embedded/bin/pip install datadog
from datadog import statsd
from datadog.api.constants import CheckStatus
# OK = 0
# WARNING = 1
# CRITICAL = 2
# UNKNOWN = 3
# ALL = (OK, WARNING, CRITICAL, UNKNOWN)

# For logging:
import logging
import sys
from logging.handlers import RotatingFileHandler

logFile = '/var/log/datadog/FTP-Check.log'
log_formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, backupCount=10, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger('ftp_logger')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

class HelloCheck(AgentCheck):
    def check(self, instance):
        try:
            # Read parameters from json file 
            with open('/etc/datadog-agent/checks.d/ftpserver_param.json') as json_data:    
                data = json.load(json_data)

            app_log.info('-----------------')
            app_log.info('Process starting!')
            app_log.info('Loading parameters from JSON ...')
            ftpserver_host = str(data["ftpserver_host"])
            ftpserver_user = str(data["ftpserver_user"])
            ftpserver_passwd = str(data["ftpserver_passwd"])
            ucis_environment = str(data["ucis_environment"])

            app_log.info('FTP Host: ' + ftpserver_host)
            app_log.info('FTP user: ' + ftpserver_user)
            app_log.info('Environment: ' + ucis_environment)

            app_log.info('Connecting to the FTP server ...')
            ftp = ftplib.FTP(ftpserver_host)
            app_log.info('Connected! Logging in ...')
            ftp.login (ftpserver_user, ftpserver_passwd)
            self.gauge('ftp.connection', 0, tags=['product:ucis','environment:'+ucis_environment,'role:application'])

            check_status = CheckStatus.OK
            check_message = 'Ftp server is reachable and the credentials are ok!'
            statsd.service_check(check_name='ftp_check', status=check_status, message=check_message)

            app_log.info('Test completed, releasing the connection to the FTP server now.')
            ftp.quit()

        except Exception as error:
            if 'LOGIN failed' in str(error):
                app_log.warn ('Warning - FTP authentication went wrong. Most probably the server refused the username/password combination provided.. %s\nURL: %s', error, ftpserver_host)
                app_log.warn ('Warning - The test passed because the server is responding.')
                ftp.quit()
                check_status = CheckStatus.WARNING
                check_message = 'Ftp server is reachable and the credentials need to be updated!'
                statsd.service_check(check_name='ftp.availability', status=check_status, message=check_message)
                self.gauge('ftp.connection', 0, tags=['product:ucis','environment:'+ucis_environment,'role:application'])
            else:
                app_log.error ('ERROR - Server not responding Data not retrieved because %s\nURL: %s', error, ftpserver_host)
                check_status = CheckStatus.CRITICAL
                check_message = 'Ftp server check: ' + error
                statsd.service_check(check_name='ftp.availability', status=check_status, message=check_message)
                self.gauge('ftp.connection', 1, tags=['product:ucis','environment:'+ucis_environment,'role:application'])
    
        finally:
            app_log.info('Process completed!')
            app_log.info('------------------')

