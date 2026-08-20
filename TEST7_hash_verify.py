import time
import re
from openpyxl import load_workbook

# 결과 파일
file_path = r"C:\Git\script_security_project\RESULT\securitytest_result.xlsx"
save_path = file_path

# 장비 정보
device = "SWITCH"
console = "/SERIAL COM6 /BAUD 115200"

# 기존 관리자 계정
username_admin = "admin"
password_admin = "Changeme1357!"

# 시험 계정
same_user = "same_user"
admin2 = "admin2"

test_users = [
    "test1",
    "test2",
    "test3"
]

# 시험 비밀번호
test_password = "Changeme1357#!"

# 동일 비밀번호 재설정을 위한 임시 비밀번호
temp_password = "Changeme1357!#"


###################################
# Excel
###################################

wb = load_workbook(file_path)
sheet1 = wb["RESULT"]
sheet2 = wb["LOG"]


def get_next_row(sheet):
    for row in range(sheet.max_row, 0, -1):
        if any(cell.value for cell in sheet[row]):
            return row + 1
    return 1


###################################
# 전체 화면 읽기
###################################

all_lines = []


def read_all():

    global all_lines
    all_lines = []

    num_rows = 300
    num_cols = 300

    for row in range(1, num_rows + 1):

        line = crt.Screen.Get(
            row,
            1,
            row,
            num_cols
        ).rstrip()

        if line.strip() != "":
            all_lines.append(line)


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

    final = "\n".join(final_line)

    return final


###################################
# RESULT / LOG 저장
###################################

def save_result(test_name, result, judge_value, final):

    row1 = get_next_row(sheet1)
    row2 = get_next_row(sheet2)

    sheet1.cell(
        row=row1,
        column=2,
        value=test_name
    )

    sheet1.cell(
        row=row1,
        column=3,
        value=result
    )

    sheet1.cell(
        row=row1,
        column=4,
        value=judge_value
    )

    sheet2.cell(
        row=row2,
        column=2,
        value=test_name
    )

    sheet2.cell(
        row=row2,
        column=3,
        value=final
    )

    wb.save(save_path)


###################################
# 장비 접속
###################################

def start():

    crt.Session.Connect(console)

    time.sleep(2)

    crt.Screen.Send("\n")
    crt.Screen.WaitForString("login")
    crt.Screen.Send(f"{username_admin}\r")
    crt.Screen.WaitForString("Password")
    crt.Screen.Send(f"{password_admin}\r")
    crt.Screen.WaitForString(f"{device}>")
    crt.Screen.Send("enable\n")
    crt.Screen.WaitForString(f"{device}#")


###################################
# config mode
###################################

def config_mode():
    crt.Screen.Send("con t\n")
    crt.Screen.WaitForString(f"{device}(config)#")


###################################
# 사용자 비밀번호 설정
###################################

def set_user_password(username, privilege, password):

    crt.Screen.Send(f"username {username} password {privilege}\n")
    crt.Screen.WaitForString("Password")
    crt.Screen.Send(f"{password}\r")
    crt.Screen.WaitForString("Please enter it again")
    crt.Screen.Send(f"{password}\r")
    crt.Screen.WaitForString(f"{device}(config)#")


###################################
# Enable 비밀번호 설정
###################################

def set_enable_password(username, password):
    crt.Screen.Send(f"enable {username} password\n")
    crt.Screen.WaitForString("Enable Password")
    crt.Screen.Send(f"{password}\r")
    crt.Screen.WaitForString("Please enter it again")
    crt.Screen.Send(f"{password}\r")
    crt.Screen.WaitForString(f"{device}(config)#")


###################################
# Hash 추출
###################################

def extract_hash(line):
    match = re.search(r"\$5\$[^$\s]+\$[^\s]+",line)

    if match:
        return match.group(0)

    return None


##########################################################################
# TEST7
# 1.5.1 비밀번호 저장
##########################################################################


##################################################
# TEST7-01
# 동일 계정 동일 비밀번호 재설정 시
# Hash 변경 확인
##################################################

def TEST7_same_user_hash():

    crt.Screen.Send(f"{test_name}_start\n")
    time.sleep(1)


    ###################################
    # same_user 최초 생성
    # Changeme1357#
    ###################################

    config_mode()
    set_user_password(same_user,"admin",test_password)
    crt.Screen.Send("end\n")
    crt.Screen.WaitForString(f"{device}#")


    # 첫 번째 Hash 확인
    crt.Screen.Send(f"show running-configuration |include {same_user}\n")
    time.sleep(1)

    ###################################
    # 비밀번호 변경
    # Changeme1357!
    ###################################

    config_mode()
    set_user_password(same_user,"admin",temp_password)
    crt.Screen.Send("end\n")
    crt.Screen.WaitForString(f"{device}#")


    # 두 번째 Hash 확인
    crt.Screen.Send(f"show running-configuration |include {same_user}\n")
    time.sleep(1)

    ###################################
    # 최초 비밀번호로 다시 변경
    # Changeme1357#
    ###################################

    config_mode()
    set_user_password(same_user,"admin",test_password)
    crt.Screen.Send("end\n")
    crt.Screen.WaitForString(f"{device}#")

    # 세 번째 Hash 확인
    crt.Screen.Send(f"show running-configuration |include {same_user}\n")
    time.sleep(1)
    crt.Screen.Send(f"{test_name}_end\n")
    time.sleep(1)


##################################################
# 동일 계정 Hash 판정
##################################################

def TEST7_same_user_verify():
    read_all()
    final = select(all_lines,
        f"{test_name}_start",
        f"{test_name}_end")

    hash_list = []

    for line in final.splitlines():

        if (
            f"username {same_user}" in line
            and "encrypted-password" in line
        ):

            hash_value = extract_hash(line)

            if hash_value is not None:
                hash_list.append(hash_value)


    ###################################
    # 첫 번째 Hash와 세 번째 Hash 비교
    #
    # Hash1 : Changeme1357#
    # Hash2 : Changeme1357!
    # Hash3 : Changeme1357#
    ###################################

    if len(hash_list) >= 3:

        first_hash = hash_list[0]
        third_hash = hash_list[2]

        if first_hash != third_hash:
            result = "PASS"
        else:
            result = "FAIL"

        judge_value = (
            f"Hash1 != Hash3 : "
            f"{first_hash != third_hash}"
        )

    else:

        result = "FAIL"

        judge_value = (
            f"Hash Count={len(hash_list)}"
        )


    save_result(
        test_name,
        result,
        judge_value,
        final
    )


##################################################
# TEST7-02
# 다른 계정에 동일 비밀번호 설정 시
# Hash 값 상이 확인
##################################################

def TEST7_different_user_hash():

    crt.Screen.Send(f"{test_name}_start\n")
    time.sleep(1)
    config_mode()


    ###################################
    # test1 / test2 / test3 생성
    #
    # 모두 동일한 비밀번호
    # Changeme1357#
    ###################################

    for username in test_users:

        set_user_password(
            username,
            "admin",
            test_password
        )

    crt.Screen.Send("end\n")
    crt.Screen.WaitForString(f"{device}#")


    # test 계정 전체 확인
    crt.Screen.Send("show running-configuration |include test\n")
    time.sleep(1)

    crt.Screen.Send(f"{test_name}_end\n")
    time.sleep(1)


##################################################
# 다른 계정 Hash 판정
##################################################

def TEST7_different_user_verify():

    read_all()

    final = select(
        all_lines,
        f"{test_name}_start",
        f"{test_name}_end"
    )

    hash_list = []


    ###################################
    # test1 / test2 / test3
    # 각 Hash 추출
    ###################################

    for username in test_users:

        for line in final.splitlines():

            if (
                f"username {username}" in line
                and "encrypted-password" in line
            ):

                hash_value = extract_hash(line)

                if hash_value is not None:
                    hash_list.append(hash_value)

                break


    ###################################
    # Hash 3개가 모두 서로 다른지 확인
    ###################################

    unique_hash_count = len(set(hash_list))

    if (
        len(hash_list) == 3
        and unique_hash_count == 3
    ):
        result = "PASS"

    else:
        result = "FAIL"


    judge_value = (
        f"Hash Count={len(hash_list)}, "
        f"Unique Hash={unique_hash_count}"
    )


    save_result(
        test_name,
        result,
        judge_value,
        final
    )


##################################################
# TEST7-03
# 운영모드 변경용 비밀번호를
# 동일 비밀번호로 재설정 시
# Hash 변경 확인
##################################################

def TEST7_enable_hash():

    crt.Screen.Send(f"{test_name}_start\n")
    time.sleep(1)

    ###################################
    # admin2 계정 생성
    ###################################

    config_mode()
    set_user_password(
        admin2,
        "admin",
        test_password
    )


    ###################################
    # 첫 번째 Enable 비밀번호
    # Changeme1357#
    ###################################

    set_enable_password(admin2,test_password)
    crt.Screen.Send("end\n")
    crt.Screen.WaitForString(f"{device}#")


    # 첫 번째 Hash 확인
    crt.Screen.Send("show running-configuration |include enable\n")
    time.sleep(1)


    ###################################
    # Enable 비밀번호 변경
    # Changeme1357!
    ###################################

    config_mode()
    set_enable_password(admin2,temp_password)
    crt.Screen.Send("end\n")
    crt.Screen.WaitForString(f"{device}#")


    # 두 번째 Hash 확인
    crt.Screen.Send("show running-configuration |include enable\n")
    time.sleep(1)


    ###################################
    # 최초 비밀번호로 다시 변경
    # Changeme1357#
    ###################################

    config_mode()
    set_enable_password(admin2,test_password)
    crt.Screen.Send("end\n")
    crt.Screen.WaitForString(f"{device}#")


    # 세 번째 Hash 확인
    crt.Screen.Send("show running-configuration |include enable\n")
    time.sleep(1)

    
    crt.Screen.Send(f"{test_name}_end\n")
    time.sleep(1)



##################################################
# Enable Hash 판정
##################################################

def TEST7_enable_verify():

    read_all()

    final = select(
        all_lines,
        f"{test_name}_start",
        f"{test_name}_end"
    )

    hash_list = []


    for line in final.splitlines():

        if (
            f"enable {admin2} encrypted-password" in line
        ):

            hash_value = extract_hash(line)

            if hash_value is not None:
                hash_list.append(hash_value)


    ###################################
    # 첫 번째 Hash와 세 번째 Hash 비교
    #
    # Hash1 : Changeme1357#
    # Hash2 : Changeme1357!
    # Hash3 : Changeme1357#
    ###################################

    if len(hash_list) >= 3:

        first_hash = hash_list[0]
        third_hash = hash_list[2]

        if first_hash != third_hash:
            result = "PASS"
        else:
            result = "FAIL"

        judge_value = (f"Hash1 != Hash3 : "f"{first_hash != third_hash}")

    else:

        result = "FAIL"

        judge_value = (
            f"Hash Count={len(hash_list)}"
        )


    save_result(
        test_name,
        result,
        judge_value,
        final
    )


##########################################################################
# 시험 계정 삭제
##########################################################################

def cleanup():

    config_mode()

    crt.Screen.Send(f"no username {admin2}\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    for username in test_users:
        crt.Screen.Send(f"no username {username}\n")
        crt.Screen.WaitForString(f"{device}(config)#")

    crt.Screen.Send(f"no username {same_user}\n")
    crt.Screen.WaitForString(f"{device}(config)#")

    crt.Screen.Send("end\n")
    crt.Screen.WaitForString(f"{device}#")


##########################################################################
# Console 종료
##########################################################################

def disconnect():
    crt.Screen.Send("exit\n")
    crt.Screen.WaitForString("login")

    time.sleep(1)
    crt.Session.Disconnect()



##########################################################################
# 실행
##########################################################################

start()

##################################################
# TEST7-01
# 동일 계정 동일 비밀번호 Hash 변경
##################################################

test_name = "TEST7_PW_same_user_hash"
TEST7_same_user_hash()
TEST7_same_user_verify()


##################################################
# TEST7-02
# 다른 계정 동일 비밀번호 Hash 상이
##################################################

test_name = "TEST7_PW_different_user_hash"
TEST7_different_user_hash()
TEST7_different_user_verify()


##################################################
# TEST7-03
# 운영모드 동일 비밀번호 Hash 변경
##################################################

test_name = "TEST7_PW_enable_hash"
TEST7_enable_hash()
TEST7_enable_verify()


##################################################
# 시험용 계정 삭제
##################################################

cleanup()


##################################################
# 장비 로그아웃 및 Console 연결 종료
##################################################

disconnect()