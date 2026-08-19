import time
import paramiko
from xtelnet import Telnet_Session
from openpyxl import load_workbook
from datetime import datetime

# 결과 파일
file_path = r"C:\Git\script_security_project\RESULT\securitytest_result.xlsx"
save_path = file_path

# 장비 정보
device = "SWITCH"
console = "/SERIAL COM6 /BAUD 115200"
ip = "192.168.100.22"

username_admin = "admin"
password_admin = "Changeme1357!"

username_admin2 = "admin2"
password_admin2 = "Changeme1357!\r"

######################################
# 결과 excel에 기록 #

wb = load_workbook(file_path)
sheet1 = wb["RESULT"]
sheet2 = wb["LOG"]

def get_next_row(sheet):
    for row in range(sheet.max_row, 0, -1):
        if any(cell.value for cell in sheet[row]):
            return row +1
    return 1


#############################################################
# 선행 : telnet, ssh enable, username admin2, user1 생성 #

def system_enable(ip):

    telnet = Telnet_Session()
    telnet.enable_debug
    telnet.connect(ip, username=username_admin, password=password_admin, timeout=10)
    telnet.execute("enable\n")
    telnet.execute("con t\n")
    telnet.execute("system enable-ssh\n")
    telnet.execute("system enable-telnet\n")
    # telnet.execute("feature telnet\n")
    # telnet.execute("feature ssh\n")
    telnet.execute("end\n")
    telnet.execute("exit\n")


def make_user(ip, username, privilege):

    telnet = Telnet_Session()
    telnet.connect(ip, username=username_admin, password=password_admin, timeout=10)
    telnet.execute("enable\n")
    telnet.execute("con t\n")
    telnet.execute(f"username {username} password {privilege}\r")
    #telnet.execute(f"username {username} privilege {privilege} password\r")
    time.sleep(1)
    telnet.execute("Changeme1357!\r")
    time.sleep(0.5)
    telnet.execute("Changeme1357!\r")
    time.sleep(0.5)
    telnet.execute("end\n")
    telnet.execute("exit\n")

##################################################
# 차단 시간 지정 #
def set_login_time(ip, login_time):

    telnet = Telnet_Session()
    telnet.connect(ip, username=username_admin, password=f"{password_admin}\r", timeout=10)

    telnet.execute("enable\n")
    telnet.execute("con t\n")

    telnet.execute(f"user login lockout-time {login_time}\r")
    time.sleep(1)
    telnet.execute("end")
    telnet.close

##################################################
# 차단 횟수 지정 #
def set_login_times(ip, login_times):

    telnet = Telnet_Session()
    telnet.connect(ip, username=username_admin, password=f"{password_admin}\r", timeout=10)

    telnet.execute("enable\n")
    telnet.execute("con t\n")

    telnet.execute(f"user login tries-before-disconnect {login_times}\r")
    time.sleep(1)
    telnet.execute("end")
    telnet.close   

##################################################
# 차단 count 확인하기 #

def check_count_and_judge(ip, test_name, fail_log, result_log, judge_count_input):
    j = 0
    count_result = False
    result = "N/A"
    log = []

    telnet = Telnet_Session()
    telnet.connect(ip, username=username_admin2, password=f"{password_admin2}\r", timeout=10)
    telnet.execute("enable\n")
    output = telnet.execute('show syslog\n', timeout=10)
    syslog = output.splitlines()[:50]
    time.sleep(2)
    telnet.execute("q\n")

    for line in syslog:
        if fail_log in line:
            j += 1
            log.append(line)  ##리스트로 만드는것##

        if result_log in line:
            count_result = True
            log.append(line)

    if count_result:
        if j == judge_count_input:
            result = "PASS"
        else:
            result = "FAIL"
        
    print(j)
    final = "\n".join(log)
    print(final)
    
    row1 = get_next_row(sheet1)
    row2 = get_next_row(sheet2)

    sheet1.cell(row=row1, column=2, value=test_name)
    sheet1.cell(row=row1, column=3, value=result)
    sheet1.cell(row=row1, column=4, value=j)

    sheet2.cell(row=row2, column=2, value=test_name)
    sheet2.cell(row=row2, column=3, value=final)

    wb.save(save_path)


##################################################
# 차단 time 확인하기 #

def check_time_and_judge(ip, test_name, block_log, active_log, judge_time_input):
    j = 0
    count_result = False 
    result = "N/A"
    log_block = ""
    log_active = ""

    telnet = Telnet_Session()
    telnet.connect(ip, username=username_admin2, password=f"{password_admin2}\r", timeout=10)
    telnet.execute("enable\n")
    output = telnet.execute('show syslog\n', timeout=10)
    syslog = output.splitlines()[:100]
    time.sleep(2)
    telnet.execute("q\n")
    
    for line in syslog:
        if block_log in line:
            j += 1
            log_block = line

        if active_log in line:
            count_result = True  ## block_log가 있어야 active_log가 있으므로 block_log가 있는지 확인하는 것
            log_active = line

    time_block = log_block.split()[1]
    time_active = log_active.split()[1]


    #### :을 기준으로 문자열을 나눠라 => 그중 인덱스 1을 dt_block에 넣겠다
    #### 그러다보니 분끼리 상수로 계산되다보니 오류가 있음
    #dt_block = int(time_block.split(":")[1])
    #dt_active = int(time_active.split(":")[1])
    #j = dt_active - dt_block


    #datetime 객체 변환
    t_block = datetime.strptime(time_block, "%H:%M:%S")
    t_active = datetime.strptime(time_active, "%H:%M:%S")

    #시간 차이를 초로 변환 후 60으로 나눠 몇분인지 확인
    j = int((t_active - t_block).total_seconds() // 60)

    if count_result:
        if j == judge_time_input:
            result = "PASS"
        else:
            result = "FAIL"
        
    print(j)
    final = "".join(log_block+log_active)
    print(final)
    
    row1 = get_next_row(sheet1)
    row2 = get_next_row(sheet2)

    sheet1.cell(row=row1, column=2, value=test_name)
    sheet1.cell(row=row1, column=3, value=result)
    sheet1.cell(row=row1, column=4, value=j)

    sheet2.cell(row=row2, column=2, value=test_name)
    sheet2.cell(row=row2, column=3, value=final)

    wb.save(save_path)


def connect_ssh(ip, username, wrong_password):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, username=username_admin, password=password_admin,
                look_for_keys=False, allow_agent=False)

    shell = ssh.invoke_shell()
    shell.send('enable\n')
    time.sleep(1)

#connect_ssh("172.25.17.73", "admin", "Changeme1357!")

def connect_ssh_retry(ip, username, wrong_password, fail_times, delay=3):
    for i in range(1, fail_times+1):

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try :
            ssh.connect(hostname=ip, username=username, password=wrong_password,
                        look_for_keys=False, allow_agent=False)
        except Exception as e:
            print(f"로그인 실패: {e}")  

        ssh.close()
        time.sleep(delay)

def connect_telnet_retry(ip, username, wrong_password, fail_times, delay=3):
    for i in range(1, fail_times+1):

        telnet = Telnet_Session()
        telnet.enable_debug()

        try : 
            telnet.connect(
                ip, 
                username=username, 
                password=f"{wrong_password}\r", 
                port=23, 
                timeout=5,
                )
        except Exception as e:
            print(f"로그인 실패: {e}")

        telnet.destroy()
        time.sleep(delay)
        

system_enable(ip)
make_user(ip, "admin2", "admin")
make_user(ip,"user2", "guest")
set_login_time(ip, 5)
set_login_times(ip, 3)
connect_telnet_retry(ip, "user2", "wrongpw", 3)
check_count_and_judge(ip, "TEST3_pwfail_count_telnet", "User user2  on 'pts/0' login failed.", "This account(user2) will be blocked", 3)
time.sleep(330)
check_time_and_judge(ip, "TEST4_login_time", "This account(user2) will be blocked for 5 minutes", "This account(user2) has been activated", 5)
connect_ssh_retry(ip, "user3", "wrongpw", 3)
check_count_and_judge(ip, "TEST3_pwfail_count_ssh", "Failed password for user3", "%% This account(user3) has been blocked for 5 minutes", 3)



