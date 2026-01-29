'''
###################################
화면캡쳐, 전체 line 읽기, 시험부분 line만 추출, 검증판단 부분
###################################
'''


import time
import mss
import os
import pygetwindow as gw

result_file = r"C:\Users\ehh74_0i1\OneDrive\바탕 화면\2025 업무\_2025.04.03_보안기능시험_자동화\securitytest_result.txt"
device = "SWITCH"
#prompt_config = f"{device}(config)# "

####화면 캡쳐####
dest = r"C:\Users\ehh74_0i1\OneDrive\바탕 화면\2025 업무\_2025.04.03_보안기능시험_자동화"
def capture_range(i):
    with mss.mss() as sct:

        monitor = sct.monitors[3]

        region = {
             "top": monitor["top"]+367,
             "left": monitor["left"]+162,
             "width": 803,
             "height": 1088}
    
        screenshot = sct.grab(region)         
        filename = os.path.join(dest, f"TEST_{i}.png")
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=filename)

####전체 line 읽기
all_lines = []
def read_all():
    crt.Screen.Synchronous = True
    global all_lines
    all_lines = []

    for row in range(1, crt.Screen.Rows + 1):
        line = crt.Screen.Get(row, 1, row, crt.Screen.Columns).rstrip()
        if line.strip() != "":
            all_lines.append(line)

    crt.Screen.Synchronous = False


####시험부분 line만 추출
def select(all_lines, start_from, end_to):
    crt.Screen.Synchronous = True
    final_line = []
    capture = False

    for line in all_lines:
        if start_from in line:
            capture = True
            final_line.append(line)
            continue     

        if capture:
            final_line.append(line)
            if end_to in line:
                break   
    
    final = "\n".join(final_line)

    crt.Screen.Synchronous = False
    return final

#검증 판단 부분
def verify(name, find_line, True_count):
    crt.Screen.Synchronous = True
    
    read_all()

    final = select(all_lines, f"HS4148# start_{name}", f"HS4148# finish_{name}")
    j = 0

    for judge in final.splitlines():
        if find_line in judge:
            j = j+1

    if j == True_count:
        result = f"TEST_{name} : True"
        with open(result_file, "a") as f:
            f.write(result + "\n")
            f.write("output: "+ final + "\n")   

    else : 
        result = f"TEST_{name} : False"
        with open(result_file, "a") as f:
            f.write(result + "\n")
            f.write("output: "+ final + "\n")     

    crt.Screen.Synchronous = False

#config mode 진입
def config_mode():
    crt.Screen.Synchronous = True

    crt.Screen.Send("conf t\n")
    crt.Screen.WaitForString(f"{device}(config)# ")

    crt.Screen.Synchronous = False



#Console, Telnet, SSH 접속
def start(protocol, ip, username, password):
    if protocol == "Console":
        crt.Session.Connect("/SERIAL COM6 /BAUD 115200")
        time.sleep(2)
        crt.Screen.Send("\n")
        crt.Screen.WaitForString("Username")

    elif protocol == "Telnet":
        crt.Session.Connect(f"/TELNET {ip}")

    if protocol == "SSH":
        crt.Session.Connect(f"/SSH2 {username}@{ip} /PASSWORD {password}")