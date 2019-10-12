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

logFile = '/var/log/datadog/SMTP-Check.log'
log_formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=10, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger('smtp_logger')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

import json
import smtplib

class HelloCheck(AgentCheck):# it can be any name, actually
    def check(self, instance):
        try:
            # Read parameters from json file 
            with open('/etc/datadog-agent/checks.d/mailserver_param.json') as json_data:    
                data = json.load(json_data)

            app_log.info('-----------------')
            app_log.info('Process starting!')
            app_log.info('Loading parameters from JSON ...')
            smtp_mailserver_host = str(data["smtp_mailserver_host"])
            smtp_mailserver_port = str(data["smtp_mailserver_port"] )
            smtp_mailserver_username = str(data["smtp_mailserver_username"])
            smtp_mailserver_password = str(data["smtp_mailserver_password"])
            ucis_environment = str(data["ucis_environment"] )

            app_log.info('SMTP Host: ' + smtp_mailserver_host)
            app_log.info('SMTP Port: ' + smtp_mailserver_port)
            app_log.info('SMTP User: ' + smtp_mailserver_username)
            app_log.info('UCIS Environment: ' + ucis_environment)

            # Connecting to the SMTP server to check the availability
            app_log.info('Connecting to the SMTP server ...')
            connection = smtplib.SMTP(smtp_mailserver_host,smtp_mailserver_port)#, timeout=10)
            app_log.info('Connected! Logging in now ...')
            connection.starttls()
            connection.login(smtp_mailserver_username, smtp_mailserver_password)
            app_log.info('Logged in!')
            connection.quit()

            check_status = CheckStatus.OK
            check_message = "Connection to the SMTP mail server successful"
            statsd.service_check(check_name='smtpserver_check', status=check_status, message=check_message)
            app_log.info("Test completed, releasing the connection to the IMAP server now.")
            self.gauge('smtpserver_check.server_reached', 0, tags=['product:ucis','environment:' + ucis_environment,'role:application'])
            self.gauge('smtpserver_check.logging_in', 0, tags=['product:ucis','environment:' + ucis_environment,'role:application'])

        except smtplib.SMTPAuthenticationError as error:
            app_log.warn ("Warning - SMTP authentication went wrong. Most probably the server did not accept the username/password combination provided.. ")
            app_log.warn ("Warning - The test passed because the server is responding.")
            connection.quit()
            check_status = CheckStatus.WARNING
            check_message = "Warning - SMTP authentication went wrong. The test passed because the server is responding. Most probably the server did not accept the username/password combination provided.. -> " + error
            statsd.service_check(check_name='smtpserver_check', status=check_status, message=check_message)
            self.gauge('smtpserver_check.server_reached', 0, tags=['product:ucis','environment:' + ucis_environment,'role:application'])
            self.gauge('smtpserver_check.logging_in', 1, tags=['product:ucis','environment:' + ucis_environment,'role:application'])

        except smtplib.SMTPConnectError as error:
            app_log.error ("ERROR - Error occurred during establishment of a connection with the server. " + error)
            check_status = CheckStatus.CRITICAL
            check_message = "ERROR - Error occurred during establishment of a connection with the server. -> " + error
            statsd.service_check(check_name='smtpserver_check', status=check_status, message=check_message)
            self.gauge('smtpserver_check.server_reached', 1, tags=['product:ucis','environment:' + ucis_environment,'role:application'])
            self.gauge('smtpserver_check.match', 1, tags=['product:ucis','environment:' + ucis_environment,'role:application'])

        except Exception as error:
            app_log.error ("ERROR - Server not responding Data not retrieved because of -> " + error)
            check_status = CheckStatus.CRITICAL
            check_message = "ERROR - Server not responding Data not retrieved because of -> " + error
            statsd.service_check(check_name='smtpserver_check', status=check_status, message=check_message)
            self.gauge('smtpserver_check.server_reached', 1, tags=['product:ucis','environment:' + ucis_environment,'role:application'])
            self.gauge('smtpserver_check.logging_in', 1, tags=['product:ucis','environment:' + ucis_environment,'role:application'])
    
        finally:
            app_log.info('Process completed!')
            app_log.info('------------------')

def main():
	# Launch the function that checks the mail server availability
		mailserver_check()

if (__name__ == '__main__'):
	main()


