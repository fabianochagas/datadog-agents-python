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
This check verifies if the FTP service is reachable by the agent. 
It tests if the port responds and tries to log in. 
This is useful to simulate the application's function that needs to access the FTP server.

on the file wms_check_param.json you add the proper information thaa will be used by the agent 
  
{
   "smtp_mailserver_host": "smtp_mail_server_hostname",
   "smtp_mailserver_port": "587",
   "smtp_mailserver_username": "valid_email@your_server.com",
   "smtp_mailserver_password": "12345trewq",
   "imap_mailserver_host": "imap_mail_server_hostname",
   "imap_mailserver_port": "993",
   "imap_mailserver_username": "valid_email@your_server.com",
   "imap_mailserver_password": "12345trewq",
   "ucis_environment": "the tag to be used on Datadog"
}

## datadog_WMS_Check
