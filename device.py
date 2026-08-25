import time


###################################
# 공통 장비 정보
###################################

device = "SWITCH"

console = "/SERIAL COM6 /BAUD 115200"

username_admin = "admin"
password_admin = "Changeme1357!"

mgmt_vlan = 160
mgmt_port = 1
mgmt_ip = "10.100.54.12/16"

pc_ip = "10.100.249.132"


###################################
# Console 연결
###################################

def connect_console(crt):

    crt.Session.Connect(console)
    time.sleep(2)


###################################
# 관리자 로그인
###################################

def login_admin(crt):

    crt.Screen.Send("\n")
    crt.Screen.WaitForString("login")

    crt.Screen.Send(f"{username_admin}\r")
    crt.Screen.WaitForString("Password")

    crt.Screen.Send(f"{password_admin}\r")
    crt.Screen.WaitForString(f"{device}>")

    crt.Screen.Send("enable\n")
    crt.Screen.WaitForString(f"{device}#")


###################################
# Console 연결 + 관리자 로그인
###################################

def start(crt):

    connect_console(crt)
    login_admin(crt)


###################################
# Config mode 진입
###################################

def config_mode(crt):

    crt.Screen.Send("con t\n")
    crt.Screen.WaitForString(f"{device}(config)#")


###################################
# Config mode 종료
###################################

def end_config(crt):

    crt.Screen.Send("end\n")
    crt.Screen.WaitForString(f"{device}#")


###################################
# MGMT 설정
###################################

def set_mgmt(crt):

    config_mode(crt)

    crt.Screen.Send(f"vlan {mgmt_vlan}\n")
    crt.Screen.WaitForString(f"{device}(vlan-{mgmt_vlan})#")

    crt.Screen.Send(f"untagged {mgmt_port}\n")
    crt.Screen.WaitForString(f"{device}(vlan-{mgmt_vlan})#")

    crt.Screen.Send(f"ip address {mgmt_ip}\n")
    crt.Screen.WaitForString(f"{device}(vlan-{mgmt_vlan})#")

    end_config(crt)

    time.sleep(5)


###################################
# MGMT 원복
###################################

def clear_mgmt(crt):

    config_mode(crt)

    crt.Screen.Send(f"vlan {mgmt_vlan}\n")
    crt.Screen.WaitForString(f"{device}(vlan-{mgmt_vlan})#")

    crt.Screen.Send(f"no ip address {mgmt_ip}\n")
    crt.Screen.WaitForString(f"{device}(vlan-{mgmt_vlan})#")

    crt.Screen.Send(f"no untagged {mgmt_port}\n")
    crt.Screen.WaitForString(f"{device}(vlan-{mgmt_vlan})#")

    crt.Screen.Send("exit\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    crt.Screen.Send(f"no vlan {mgmt_vlan}\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# Port Speed 설정
###################################

def set_port(crt, port, speed):

    config_mode(crt)

    crt.Screen.Send(f"port {port}\n")
    crt.Screen.WaitForString(f"{device}(port[{port}])#")

    crt.Screen.Send(f"speed {speed}\n")
    crt.Screen.WaitForString(f"{device}(port[{port}])#")

    end_config(crt)
    time.sleep(5)


###################################
# 시험용 Port 원복
###################################

def restore_port(crt, port, speed):

    set_port(crt, port, speed)

    time.sleep(5)


###################################
# Port Link 확인
###################################

def check_port_link(crt, port):

    start_marker = f"PORT{port}_LINK_CHECK_start"
    end_marker = f"PORT{port}_LINK_CHECK_end"

    crt.Screen.Send(f"{start_marker}\n")

    crt.Screen.Send("show port\n")
    crt.Screen.WaitForString(f"{device}#")

    crt.Screen.Send(f"{end_marker}\n")

    time.sleep(1)

    final = read_section(
        crt,
        start_marker,
        end_marker
    )

    for line in final.splitlines():

        parts = line.split()

        if len(parts) >= 3:

            if parts[0] == str(port) and parts[2] == "up":
                print(f"Port {port} Link Up")
                return True

    print(f"Port {port} Link Down or Unknown")
    return False


###################################
# PC Ping 확인
###################################

def check_pc_ping(crt):

    crt.Screen.Send("PC_PING_CHECK_start\n")

    crt.Screen.Send(f"ping {pc_ip}\n")

    time.sleep(3)

    crt.Screen.Send("\x03")
    crt.Screen.WaitForString(f"{device}#")

    crt.Screen.Send("PC_PING_CHECK_end\n")

    time.sleep(1)

    final = read_section(
        crt,
        "PC_PING_CHECK_start",
        "PC_PING_CHECK_end"
    )

    for line in final.splitlines():

        if "packets received" in line:

            parts = line.split(",")

            if len(parts) >= 2:

                received = parts[1].split()[0]

                if int(received) > 0:
                    print("PC Ping Success")
                    return True

    print("PC Ping Fail")
    return False


###################################
# SSH Enable
###################################

def enable_ssh(crt):

    config_mode(crt)

    crt.Screen.Send("system enable-ssh\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# SSH Disable
###################################

def disable_ssh(crt):

    config_mode(crt)

    crt.Screen.Send("no system enable-ssh\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# Telnet Enable
###################################

def enable_telnet(crt):

    config_mode(crt)

    crt.Screen.Send("system enable-telnet\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# Telnet Disable
###################################

def disable_telnet(crt):

    config_mode(crt)

    crt.Screen.Send("no system enable-telnet\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# SNMP Enable
###################################

def enable_snmp(crt):

    config_mode(crt)

    crt.Screen.Send("snmp enable\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# SNMP Disable
###################################

def disable_snmp(crt):

    config_mode(crt)

    crt.Screen.Send("snmp disable\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# 사용자 계정 생성
###################################

def create_user(crt, username, privilege, password):

    config_mode(crt)

    crt.Screen.Send(f"username {username} password {privilege}\n")
    crt.Screen.WaitForString("Password")

    crt.Screen.Send(f"{password}\r")
    crt.Screen.WaitForString("Please enter it again")

    crt.Screen.Send(f"{password}\r")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# 사용자 계정 삭제
###################################

def delete_user(crt, username):

    config_mode(crt)

    crt.Screen.Send(f"no username {username}\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# Enable Password 설정
###################################

def set_enable_password(crt, username, password):

    config_mode(crt)

    crt.Screen.Send(f"enable {username} password\n")
    crt.Screen.WaitForString("Enable Password")

    crt.Screen.Send(f"{password}\r")
    crt.Screen.WaitForString("Please enter it again")

    crt.Screen.Send(f"{password}\r")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# Enable Password 삭제
###################################

def clear_enable_password(crt, username):

    config_mode(crt)

    crt.Screen.Send(f"enable {username} nopassword\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# SNMP v3 설정
###################################

def set_snmp_v3(
    crt,
    groupname,
    snmp_auth_password,
    snmp_priv_password
):

    config_mode(crt)

    crt.Screen.Send("snmp enable\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    crt.Screen.Send(f"snmp group v3g v3 {groupname}\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    crt.Screen.Send("snmp view v3v included .1\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    crt.Screen.Send(
        "snmp access v3g v3 auth "
        "read v3v write v3v notify v3v\n"
    )
    crt.Screen.WaitForString(f"{device}(config)#")

    crt.Screen.Send(
        f"snmp v3 user {groupname} "
        f"auth sha {snmp_auth_password} "
        f"priv aes {snmp_priv_password}\n"
    )
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# SNMP v3 설정 삭제
###################################

def clear_snmp_v3(crt, groupname):

    config_mode(crt)

    crt.Screen.Send(f"no snmp v3 user {groupname}\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    crt.Screen.Send("no snmp access v3g\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    crt.Screen.Send("no snmp view v3v included .1\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    crt.Screen.Send(f"no snmp group v3g v3 {groupname}\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    crt.Screen.Send("snmp disable\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    end_config(crt)


###################################
# 로그아웃
###################################

def logout(crt):

    crt.Screen.Send("exit\n")
    crt.Screen.WaitForString("login")


###################################
# Console 종료
###################################

def disconnect_console(crt):

    crt.Session.Disconnect()



##<ping 확인, ssh, telnet, snmp enable, disable 확인을 위한 코드>
###################################
# 전체 화면 읽기
###################################

def read_all(crt):

    all_lines = []

    num_rows = 500
    num_cols = 300

    for row in range(1, num_rows + 1):

        line = crt.Screen.Get(row, 1, row, num_cols).rstrip()

        if line.strip() != "":
            all_lines.append(line)

    return all_lines


###################################
# 시험 구간 추출
###################################

def select(all_lines, TEST_start, TEST_end):

    final_line = []
    capture = False

    for line in all_lines:

        if TEST_start in line:
            capture = True
            final_line.append(line)
            continue

        if capture:
            final_line.append(line)

            if TEST_end in line:
                break

    return "\n".join(final_line)


###################################
# 특정 구간 읽기
###################################

def read_section(crt, start_marker, end_marker):

    all_lines = read_all(crt)

    final = select(
        all_lines,
        start_marker,
        end_marker
    )

    return final



