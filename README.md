# datadog-agents-python
This contains a couple of Datadog agents check, developed in python


## datadog_FTP_check
This check verifies if the FTP service is reachable by the agent. 
It tests if the port responds and tries to log in. 
This is useful to simulate the application's function that needs to access the FTP server.

on the file wms_check_param.json you add the proper information thaa will be used by the agent 
  
{
    "ftpserver_host": "192.168.0.28",
    "ftpserver_user": "ftp_username",
    "ftpserver_passwd": "username_pwd",
    "ucis_environment": "environment_tag"
 }
 

## datadog_JMX
This procedure to has two stepd: 
- configure the wildfly (version 10) running in #domain mode#
- configure the Datadog agent to _read_ the JMX infos exposed by the wildfly service
read the MD file instide of the folder bcs it explains all the procedure 


## datadog_MAILSERVER_check
## datadog_WMS_Check
