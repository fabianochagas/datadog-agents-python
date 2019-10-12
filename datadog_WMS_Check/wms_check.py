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

import socket
from checkJSONSchema import compare_json_schema
import requests
import json
import httplib

# For logging:
import logging
import sys
from logging.handlers import RotatingFileHandler

logFile = '/var/log/datadog/WMS_Check.log'
log_formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=10, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger('wms_logger')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

class HelloCheck(AgentCheck): # It can be any name, actually
  def check(self, instance):
    try:
        app_log.info('-----------------')
        app_log.info('Process starting!')
        app_log.info('Loading parameters from JSON ...')
        # Read parameters from json file 
        with open('/etc/datadog-agent/checks.d/wms_check_param.json') as json_data:    
            data = json.load(json_data)

        wms_host = data["wms_api_host"] 
        wms_port = data["wms_api_port"] 
        wms_path = data["path"] 
        wms_querystring_name = data["querystring_name"] 
        wms_querystring_value = data["querystring_value"] 
        wms_ucis_environment = data["ucis_environment"] 

        app_log.info('Host: ' + wms_host)
        app_log.info('Port: ' + wms_port)
        app_log.info('Path: ' + wms_path)
        app_log.info('Querystring name: ' + wms_querystring_name)
        app_log.info('Querystring value: ' + wms_querystring_value)
        app_log.info('Environment: ' + wms_ucis_environment)

        # Setting up variables to be used on the API request
        querystring = {}
        querystring[wms_querystring_name] = wms_querystring_value

        headers = {
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "",
            'accept-encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
            }
        headers['Host']=wms_host + ':' + wms_port
        payload = ""

        # To check it there is http service is up
        url_api = 'http://' + wms_host + ':' + wms_port + wms_path
        app_log.info('URL API: ' + url_api)
        app_log.info('Check server response ...')
        connection = httplib.HTTPConnection(wms_host, timeout = 5 )
        connection.request("GET", "/")
        response = connection.getresponse()

        if response.status != "200":
            app_log.info('Server answered ... checking the WMS api now ... ')
            self.gauge('wms_check.connection', 0, tags=['product:ucis','environment:' + wms_ucis_environment,'role:application'])

            # To check if the JSON sent back from WMS matches the schema 
            myResponse = requests.request("GET", url_api, headers=headers, data=payload, params=querystring)
            app_log.info(json.loads(myResponse.text))
            if compare_json_schema(json.loads(myResponse.text)):
                app_log.info("JSON schema response from WMS API matches!")
                self.gauge('wms_check.schema_match', 0, tags=['product:ucis','environment:' + wms_ucis_environment,'role:application'])
                check_status = CheckStatus.OK
                check_message = "Connection to the WMS server successful"
                statsd.service_check(check_name='wms_check', status=check_status, message=check_message)
            else:
                app_log.error("JSON schema response from WMS API DOESN'T MATCH! --- ERROR ---")
                self.gauge('wms_check.schema_match', 1, tags=['product:ucis','environment:' + wms_ucis_environment,'role:application'])
                check_status = CheckStatus.CRITICAL
                check_message = "JSON schema response from WMS API DOESN'T MATCH! --- ERROR ---"
                statsd.service_check(check_name='wms_check', status=check_status, message=check_message)
        else:
            # If the response is not 200 terminate the check. An alert will be raised
            app_log.error("Server doesn't answer ... terminating validation ... ")
            app_log.error(http)
            self.gauge('wms_check.connection', 1, tags=['product:ucis','environment:' + wms_ucis_environment,'role:application'])
            check_status = CheckStatus.CRITICAL
            check_message = "WMS Server unreachable --- CRITICAL ---"
            statsd.service_check(check_name='wms_check', status=check_status, message=check_message)
                
    except httplib.HTTPException as error:
        app_log.error ('Data not retrieved because %s\nURL: %s', error, wms_host)
        self.gauge('wms_check.connection', 1, tags=['product:ucis','environment:' + wms_ucis_environment,'role:application'])
        check_status = CheckStatus.CRITICAL
        check_message = 'Data not retrieved because ->' + error
        statsd.service_check(check_name='wms_check', status=check_status, message=check_message)
    except Exception as error:
        app_log.error ('Data not retrieved because %s\nURL: %s', error, wms_host)
        self.gauge('wms_check.connection', 1, tags=['product:ucis','environment:' + wms_ucis_environment,'role:application'])
        check_status = CheckStatus.CRITICAL
        check_message = 'Data not retrieved because ->' + error
        statsd.service_check(check_name='wms_check', status=check_status, message=check_message)
    finally: 
        app_log.info('Process completed!')
        app_log.info('------------------')


def main():
        # compare first struct against second
                check()

if (__name__ == '__main__'):
        main()

