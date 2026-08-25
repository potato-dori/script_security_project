
### python 3.13.2
### This script is based on equipment of REALTAK Chipset ###

import time
import sys

sys.path.append(r"C:\Git\script_security_project")

import device
import result


##########################################################################
# TEST2 : 1.2.1 비밀번호 보안성 기준
##########################################################################

pw_list_combi = [
        "024681357A",
        "ADGJLQETUa",
        "adgjlqetu!",
        "024681357!",
        "ADGJLQETUla!",
        "024681357Aa",
        "024681357A!",
        "024681357a!"
                ]

repeated_pw_list = [
        "AAAKTC12!",
        "aaaktc12!",
        "KTC111!",
        "KTCktc!!!"
        ]

consecutive_pw_list = [
        "ASDFktc1!",
        "asdfKTC1!",
        "KTC1234!#",
        "LKJHktc1!",
        "lkjhKTC1!",
        "KTC4321!#"
    ]


##########################################################################
# 초기 Admin Password 입력 대기
##########################################################################

def make_admin():

    crt.Screen.Send("\n")

    crt.Screen.WaitForString(
        "Enter admin account password : "
    )


##########################################################################
# 현재 화면에서 특정 문자열 개수 확인
##########################################################################

def get_message_count(find_line):

    all_lines = result.read_all(crt)

    count = 0

    for line in all_lines:

        if find_line in line:
            count += 1

    return count


##########################################################################
# 초기 Admin Password 조합 시험
##########################################################################

def TEST2_PW_combi(test_pw, find_line):

    make_admin()

    before_count = get_message_count(find_line)

    for pw in test_pw:

        time.sleep(2)

        crt.Screen.Send(f"{pw}\r")
        crt.Screen.WaitForString("Enter admin account password : ")

    time.sleep(1)

    # 시험 종료 후 메시지 개수
    after_count = get_message_count(find_line)

    # 이번 시험에서 증가한 개수
    judge_count = after_count - before_count

    # 현재 화면 전체 로그
    final = "\n".join(
        result.read_all(crt)
    )

    return judge_count, final


##########################################################################
# 최초 관리자 admin 계정 생성
##########################################################################

def make_init_admin():

    make_admin()

    crt.Screen.Send(device.password_admin)
    time.sleep(0.5)
    crt.Screen.Send("\r")

    crt.Screen.WaitForString("Please enter it again")

    crt.Screen.Send(device.password_admin)
    time.sleep(0.5)
    crt.Screen.Send("\r")

    crt.Screen.WaitForString("SWITCH login:")
    crt.Screen.Send("\n")


##########################################################################
# 판정
##########################################################################

def pw_verify(test_name, expected_count, actual_count, final):

    if actual_count == expected_count:
        test_result = "PASS"

    else:
        test_result = "FAIL"

    judge_value = (
        f"Count={actual_count}, "
        f"Expected={expected_count}"
    )

    result.save_result(
        test_name,
        test_result,
        judge_value,
        final
    )





##########################################################################
# Console 연결
##########################################################################

device.connect_console(crt)
time.sleep(1)


##########################################################################
# 비밀번호 조합 미충족
##########################################################################

test_name = "TEST2_PW_combi_init"

find_line = "% Your password must contain a minimum of 9 characters included with at least"
actual_count, final = TEST2_PW_combi(pw_list_combi,find_line)

pw_verify(
    test_name,
    8,
    actual_count,
    final
)

time.sleep(1)

crt.Screen.Send("\r")


##########################################################################
# 동일 문자 반복
##########################################################################

test_name = "TEST2_PW_repeated_init"

find_line = "% Passwords should not have the same characters or numbers in succession."
actual_count, final = TEST2_PW_combi(repeated_pw_list, find_line)

pw_verify(
    test_name,
    4,
    actual_count,
    final
)

time.sleep(1)

crt.Screen.Send("\r")


##########################################################################
# 연속 문자
##########################################################################

test_name = "TEST2_PW_consecutive_init"

find_line = "% Passwords should not have the consecutive characters or numbers in succession."
actual_count, final = TEST2_PW_combi(consecutive_pw_list,find_line)

pw_verify(
    test_name,
    6,
    actual_count,
    final
)

time.sleep(1)

crt.Screen.Send("\r")


##########################################################################
# 초기 admin 계정 생성
##########################################################################

make_init_admin()


##########################################################################
# Console 종료
##########################################################################

device.disconnect_console(crt)


