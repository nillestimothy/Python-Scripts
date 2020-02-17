from pprint import pprint
from netmiko import ConnectHandler
from time import time
from datetime import datetime
import getpass
import os
import threading
import json

#---- Set Environment Variable for NTC Templates
os.environ ['NET_TEXTFSM'] = "C:\\Users\\yamah\\AppData\\Local\Programs\\Python\\Python38-32\\Lib\\site-packages\\ntc_templates\\templates"


#------------------------------------------------------------------------------
def read_devices( devices_filename ):

    devices = {}  # create our dictionary for storing devices and their info

    with open( devices_filename ) as devices_file:

        for device_line in devices_file:

            device_info = device_line.strip().split(',')  #extract device info from line

            device = {'ipaddr': device_info[0],
                      'type':   device_info[1],
                      'name':   device_info[2]}  # create dictionary of device objects ...

            devices[device['ipaddr']] = device  # store our device in the devices dictionary
                                                # note the key for devices dictionary entries is ipaddr

    print ('\n----- devices --------------------------')
    print( devices )

    return devices

#------------------------------------------------------------------------------

def config_worker( device, user, PASSWORD ):

    #---- Connect to the device ----
    if   device['type'] == 'junos-srx': device_type = 'juniper'
    elif device['type'] == 'cisco-ios': device_type = 'cisco_ios'
    elif device['type'] == 'cisco-xr':  device_type = 'cisco_xr'
    else:                               device_type = 'cisco_ios'    # attempt Cisco IOS as default

    print ('---- Connecting to devices')

    #---- Connect to the device
    session = ConnectHandler( device_type=device_type, ip=device['ipaddr'], username=user, password=PASSWORD )

    if device_type == 'juniper':
        #---- Use CLI command to get configuration data from device
        print ('---- Getting configuration from device')
        session.send_command('configure terminal')
        showrun = session.send_command('show configuration')

    if device_type == 'cisco_ios':
        #---- Use CLI command to get configuration data from device
        print ('---- Getting configuration from device')
        session.save_config()
        showver = session.send_command("show version", use_textfsm=True)
        showrun = session.send_command("show run")

    if device_type == 'cisco_xr':
        #---- Use CLI command to get configuration data from device
        print ('---- Getting configuration from device')
        showrun = session.send_command('show configuration running-config')



    #----Write out configuration information to file and save in directory

    hostname = showver[0]['hostname']
    filelocation = ("D:\\Python Scripts\\Backups\\" + "\\" + hostname)
    filename = hostname + "_" + dt_string + ".cfg"
    if not os.path.exists(filelocation):
            os.mkdir(filelocation)
            print(filelocation , " Created ")
    else:
            print(filelocation , " already exists ")

    outFileName = "D:\\Python Scripts\\Backups\\" + hostname + "\\" + filename
    outFile = open(outFileName, "w")
    outFile.write(showrun)
    outFile.close()
    print(hostname + " has been backed up to " + outFileName + "\n")


    session.disconnect()

    return


#==============================================================================
# ---- Main: Get Configuration
#==============================================================================

devices = read_devices( 'D:\\Python Scripts\\Device Backup\\Netmiko Multithreading-Windows\\devices-file' )
user = input('Give me your Username: ')
PASSWORD = getpass.getpass('Give me your Password: ')

starting_time = time()
now = datetime.now()
dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")


config_threads_list = []
for ipaddr,device in devices.items():

    print ('Creating thread for: ', device)
    config_threads_list.append( threading.Thread( target=config_worker, args=(device, user, PASSWORD ) ) )

print ('\n---- Begin get config threading ----\n')
for config_thread in config_threads_list:
    config_thread.start()

for config_thread in config_threads_list:
    config_thread.join()

print ('\n---- End get config threading, elapsed time=', time() - starting_time)
