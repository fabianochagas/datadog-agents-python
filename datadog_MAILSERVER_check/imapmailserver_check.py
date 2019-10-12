# the following try/except block will make the custom check compatible with any Agent version
try:
    # first, try to import the base class from old versions of the Agent...
    from checks import AgentCheck
except ImportError:
    # ...if the above failed, the check is running in Agent version 6 or later
    from datadog_checks.checks import AgentCheck

# content of the special variable __version__ will be shown in the Agent status page
__version__ = "1.0.0"

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

import logging
import sys
from logging.handlers import RotatingFileHandler

logFile = '/var/log/datadog/IMAP-Check.log'
log_formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=10, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger('imap_logger')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

import json
import imaplib

class HelloCheck(AgentCheck):# it can be any name, actually
    def check(self, instance):
        try:
            # Read parameters from json file 
            with open('/etc/datadog-agent/checks.d/mailserver_param.json') as json_data:    
                data = json.load(json_data)

            app_log.info('-----------------')
            app_log.info('Process starting!')
            app_log.info('Loading parameters from JSON ...')
            imap_mailserver_host = str(data["imap_mailserver_host"])
            imap_mailserver_port = str(data["imap_mailserver_port"] )
            imap_mailserver_username = str(data["imap_mailserver_username"])
            imap_mailserver_password = str(data["imap_mailserver_password"] )
            ucis_environment = str(data["ucis_environment"] )

            app_log.info('IMAP Host: ' + imap_mailserver_host)
            app_log.info('IMAP Port: ' + imap_mailserver_port)
            app_log.info('IMAP User: ' + imap_mailserver_username)
            app_log.info('UCIS Environment: ' + ucis_environment)

            app_log.info('Connecting to the IMAP server ...')
            connection = imaplib.IMAP4_SSL(imap_mailserver_host,imap_mailserver_port)#, timeout=10)
            app_log.info('Connected! Loggin in now ...')
            connection.login(imap_mailserver_username, imap_mailserver_password)
            app_log.info('Logged in!')
            connection.logout()
            app_log.info('Test completed, releasing the connection to the IMAP server now.')
            check_status = CheckStatus.OK
            check_message = "Connection to the IMAP mail server successful"
            statsd.service_check(check_name='imapserver_check', status=check_status, message=check_message)
            self.gauge('imapserver_check.server_reached', 0, tags=['product:ucis','environment:' + ucis_environment,'role:application'])
            self.gauge('imapserver_check.logging_in', 0, tags=['product:ucis','environment:' + ucis_environment,'role:application'])


        except Exception as error:
            if 'LOGIN failed' in str(error):
                app_log.warn ('Warning - IMAP authentication went wrong. Most probably the server refused the username/password combination provided.. %s\nURL: %s', error, imap_mailserver_host)
                app_log.warn ('Warning - The test passed because the server is responding.')
                connection.logout()
                check_status = CheckStatus.WARNING
                check_message = "The IMAP mail server is listening but the credentials for this test are wrong."
                statsd.service_check(check_name='imapserver_check', status=check_status, message=check_message)
                self.gauge('imapserver_check.server_reached', 0, tags=['product:ucis','environment:' + ucis_environment,'role:application'])
                self.gauge('imapserver_check.logging_in', 1, tags=['product:ucis','environment:' + ucis_environment,'role:application'])
            else:
                app_log.error ('ERROR - Server not responding Data not retrieved because %s\nURL: %s', error, imap_mailserver_host)
                check_status = CheckStatus.CRITICAL
                check_message = 'ERROR - Server not responding Data not retrieved because ->'+ error
                statsd.service_check(check_name='imapserver_check', status=check_status, message=check_message)
                self.gauge('imapserver_check.server_reached', 1, tags=['product:ucis','environment:' + ucis_environment,'role:application'])
                self.gauge('imapserver_check.logging_in', 1, tags=['product:ucis','environment:' + ucis_environment,'role:application'])
    
        finally:
            app_log.info('Process completed!')
            app_log.info('------------------')

def main():
	# Launch the function that checks the mail server availability
		mailserver_check()

if (__name__ == '__main__'):
	main()

