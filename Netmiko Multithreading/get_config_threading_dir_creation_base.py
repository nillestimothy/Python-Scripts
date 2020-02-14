from simplecrypt import encrypt, decrypt
from pprint import pprint
from netmiko import ConnectHandler
from time import time
from datetime import datetime
import os
import json

import threading

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
    pprint( devices )

    return devices

#------------------------------------------------------------------------------
def read_device_creds( device_creds_filename, key ):

    print ('\n... getting credentials ...\n')
    with open( device_creds_filename, 'rb') as device_creds_file:
        device_creds_json = decrypt( key, device_creds_file.read() )

    device_creds_list = json.loads( device_creds_json.decode('utf-8'))

    print ('\n----- device_creds ----------------------')

    # convert to dictionary of lists using dictionary comprehension
    device_creds = { dev[0]:dev for dev in device_creds_list }
    pprint( device_creds )

    return device_creds

#------------------------------------------------------------------------------
def config_worker( device, creds ):

    #---- Connect to the device ----
    if   device['type'] == 'junos-srx': device_type = 'juniper'
    elif device['type'] == 'cisco-ios': device_type = 'cisco_ios'
    elif device['type'] == 'cisco-xr':  device_type = 'cisco_xr'
    else:                               device_type = 'cisco_ios'    # attempt Cisco IOS as default

    print ('---- Connecting to device {0}, username={1}, password={2}'.format( device['ipaddr'],
                                                                                creds[1], creds[2] ))

    #---- Connect to the device
    session = ConnectHandler( device_type=device_type, ip=device['ipaddr'],
                                                       username=creds[1], password=creds[2] )
    
    if device_type == 'juniper':
        #---- Use CLI command to get configuration data from device
        print ('---- Getting configuration from device')
        session.send_command('configure terminal')
        showrun = session.send_command('show configuration')

    if device_type == 'cisco_ios':
        #---- Use CLI command to get configuration data from device
        print ('---- Getting configuration from device')
        showver = session.send_command("show version", use_textfsm=True)
        showrun = session.send_command("show run")
    
    if device_type == 'cisco_xr':
        #---- Use CLI command to get configuration data from device
        print ('---- Getting configuration from device')
        showrun = session.send_command('show configuration running-config')


    #---- Write out configuration information to file
    hostname = showver[0]['hostname']
    filelocation = ("/home/nillest/Documents/Backups/" + "/" + hostname)
    filename = hostname + "_" + dt_string + ".txt"
    #---- File Creation Error Handling
    if not os.path.exists(filelocation):
            os.mkdir(filelocation)
            print(filelocation , " Created ")
    else:
            print(filelocation , " already exists ")

    output_file_location = "/home/nillest/Documents/Backups/" + hostname + "/" + filename
    output_file = open(output_file_location, "w")
    output_file.write(showrun)
    output_file.close()
    print(hostname + " has been backed up to " + output_file_location + "\n")

    session.disconnect()

    return


#==============================================================================
# ---- Main: Get Configuration
#==============================================================================

devices = read_devices( 'devices-file' )
creds   = read_device_creds( 'encrypted-device-creds', 'cisco' )

starting_time = time()
now = datetime.now()
dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

config_threads_list = []
for ipaddr,device in devices.items():

    print ('Creating thread for: ', device)
    config_threads_list.append( threading.Thread( target=config_worker, args=(device, creds[ipaddr] ) ) )

print ('\n---- Begin get config threading ----\n')
for config_thread in config_threads_list:
    config_thread.start()

for config_thread in config_threads_list:
    config_thread.join()

print ('\n---- End get config threading, elapsed time=', time() - starting_time)