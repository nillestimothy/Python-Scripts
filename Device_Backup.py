from netmiko import Netmiko
from datetime import datetime
import os
import os.path
import getpass

now = datetime.now()

dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

username = input("Enter Username: ")
password = getpass.getpass()

Switch1 = {
    "host": "192.168.10.1",
    "username": username,
    "password": password,
    "device_type": "cisco_ios",
}

Switch2 = {
    "host": "192.168.0.1",
    "username": username,
    "password": password,
    "device_type": "cisco_ios",
}

Switch3 = {
    "host": "10.0.0.99",
    "username": username,
    "password": password,
    "device_type": "cisco_ios",
}

Switch4 = {
    "host": "10.0.0.101",
    "username": username,
    "password": password,
    "device_type": "cisco_ios",
}

Switch5 = {
    "host": "172.16.0.2",
    "username": username,
    "password": password,
    "device_type": "cisco_ios",
}

myswitches = [Switch1, Switch2, Switch3, Switch4, Switch5]

for x in myswitches:
    net_connect = Netmiko(**x)
    showver = net_connect.send_command("show version", use_textfsm=True)
    showrun = net_connect.send_command("show run")
    hostname = showver[0]['hostname']
    filelocation = ("D:\\Python Scripts\\Backups\\" + "\\" + hostname)
    filename = hostname + "_" + dt_string + ".txt"
    directory = hostname
    if not os.path.exists(filelocation):
            os.mkdir(filelocation)
            print(" Directory " , filelocation , " Created ")
    else:
            print(" Directory " , filelocation , " already exists ")

    outFileName = "D:\\Python Scripts\\Backups\\" + hostname + "\\" + filename
    outFile = open(outFileName, "w")
    outFile.write(showrun)
    outFile.close()
    print(hostname + " has been backed up to " + outFileName + "\n")
    #os.startfile(outFileName)
    net_connect.disconnect()
