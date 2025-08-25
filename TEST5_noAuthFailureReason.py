import time
from openpyxl import load_workbook

device = "HL7301"

def start(protocol, ip, username, password):
    if protocol == "Console":
        crt.Session.Connect("/SERIAL COM6 /BAUD 115200")
    elif protocol == "Telnet":
        crt.Session.Connect(f"/TELNET {ip}")
    time.sleep(1)
    crt.Screen.Send(f"{username}\r")
    time.sleep(1)
    crt.Screen.Send(f"{password}\r")
    crt.Screen.WaitForString(f"{device}>")
    crt.Screen.Send("enable\n")  

    if protocol == "SSH":
        crt.Session.Connect(f"/SSH2 {username}@{ip} /PASSWORD {password}")
        crt.Screen.WaitForString(f"{device}>")
        crt.Screen.Send("enable\n")


#start("Console", "192.168.73.2", "admin", "Changeme1357!")
#start("Telnet", "192.168.73.2", "admin", "Changeme1357!")
#start("SSH", "192.168.73.2", "admin", "Changeme1357!")
