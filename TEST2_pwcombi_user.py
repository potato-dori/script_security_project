
### python 3.13.2
### This script is based on equipment of REALTAK Chipset ###

import time
import sys

sys.path.append(r"C:\Git\script_security_project")

import device
import result

###################################
# 시험 계정 정보
###################################

username = "admin"
privilege = "admin"

same_user = [username]


##########################################################################
# TEST1 : 1.2.1 비밀번호 보안성 기준
##########################################################################

combi_pw_list1 = [
        "024681357A",
        "ADGJLQETUa",
        "adgjlqetu!",
        "024681357!"
                ]

combi_pw_list2 = [
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

consecutive_pw_list1 = [
        "ASDFktc1!",
        "asdfKTC1!",
        "KTC1234!#"
    ]

consecutive_pw_list2 = [
        "LKJHktc1!",
        "lkjhKTC1!",
        "KTC4321!#"
    ]


###################################
# Username Password 입력
###################################

def make_user():

    crt.Screen.Send(f"username {username} password {privilege}\n")
    crt.Screen.WaitForString("Enter admin account password")
    


###################################
# Username Password 조합 시험
###################################

def TEST2_PW_user(pw_case):

    crt.Screen.Send(f"{test_name}_start\n")

    time.sleep(1)

    device.config_mode(crt)

    for pw in pw_case:

        make_user()

        crt.Screen.Send(pw)
        time.sleep(1)
        crt.Screen.Send("\r")

        crt.Screen.WaitForString(f"{device.device}(config)#")

    time.sleep(1)

    device.end_config(crt)

    crt.Screen.Send(f"show running-config |include {username}\n")
    crt.Screen.WaitForString(f"{device.device}#")
    crt.Screen.Send(f"{test_name}_end\n")

    time.sleep(1)


###################################
# 판정
###################################

def pw_verify(judge_count, find_line):

    final = result.test_part(
        crt,
        test_name + "_start",
        test_name + "_end"
    )

    j = 0

    for judge in final.splitlines():

        if find_line in judge:
            j += 1

    if j == judge_count:
        test_result = "PASS"

    else:
        test_result = "FAIL"

    judge_value = (
        f"Count={j}, "
        f"Expected={judge_count}"
    )

    result.save_result(
        test_name,
        test_result,
        judge_value,
        final
    )


##########################################################################
# 시험 시작
##########################################################################

device.start(crt)


##########################################################################
# 비밀번호 조합 미충족 1
##########################################################################

test_name = "TEST2_PW_combi_user1"
TEST2_PW_user(combi_pw_list1)
pw_verify(4, "% Your password must contain a minimum of 9 characters")


##########################################################################
# 비밀번호 조합 미충족 1
##########################################################################

test_name = "TEST2_PW_combi_user2"
TEST2_PW_user(combi_pw_list2) 
pw_verify(4, "% Your password must contain a minimum of 9 characters")


##########################################################################
# 동일 문자 반복
##########################################################################

test_name = "TEST2_PW_repeated_user"
TEST2_PW_user(repeated_pw_list)
pw_verify(4, "% Passwords should not have the same characters or numbers in succession.")


##########################################################################
# 연속 문자
##########################################################################

test_name = "TEST2_PW_consecutive_user1"
TEST2_PW_user(consecutive_pw_list1)
pw_verify(3, "% Passwords should not have the consecutive characters or numbers in succession.")


##########################################################################
# 역순 연속 문자
##########################################################################

test_name = "TEST2_PW_consecutive_user2"
TEST2_PW_user(consecutive_pw_list2)
pw_verify(3, "% Passwords should not have the consecutive characters or numbers in succession.")


##########################################################################
# Username과 동일한 Password
##########################################################################

test_name = "TEST2_PW_same_user"
TEST2_PW_user(same_user)
pw_verify(1, "% Passwords should not have contain a user name.")


###################################
# 로그아웃 + Console 종료
###################################

device.close(crt)

