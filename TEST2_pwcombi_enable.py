
### python 3.13.2
### This script is based on equipment of REALTAK Chipset ###  

import time
import sys

sys.path.append(r"C:\Git\script_security_project")

import device
import result


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


##########################################################################
# Enable Password 입력
##########################################################################

def make_enable():

    time.sleep(1)
    crt.Screen.Send("enable admin2 password\n")
    crt.Screen.WaitForString("Enable Password")


##########################################################################
# Enable Password 조합 시험
##########################################################################

def TEST2_PW_enable(pw_case):

    crt.Screen.Send(f"{test_name}_start\n")

    time.sleep(1)
    device.config_mode(crt)

    for pw in pw_case:
        make_enable()

        crt.Screen.Send(f"{pw}\r")
        time.sleep(0.3)

        crt.Screen.Send("\n")
        crt.Screen.WaitForString(f"{device.device}(config)# ")    

    time.sleep(1)
    device.end_config(crt)

    crt.Screen.Send("show running-configuration |include admin2\n")
    #crt.Screen.Send("show running-config |include enable password\n")
    
    crt.Screen.WaitForString(f"{device.device}#")
    crt.Screen.Send(f"{test_name}_end\n")
    time.sleep(1)


##########################################################################
# 판정
##########################################################################

def pw_verify(judge_count, find_line):

    final = result.test_part(
        crt,
        f"{device.device}# {test_name}_start",
        f"{device.device}# {test_name}_end"
    )

    j=0

    for judge in final.splitlines():

        if find_line in judge:
            j += 1

    if j == judge_count:
        test_result = "PASS"

    else:
        test_result = "FAIL"

    judge_value = f"Count={j}, Expected={judge_count}"

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
# admin2 사용자 생성
##########################################################################

#device.create_user(crt, "admin2", "admin", "Changeme1357!")


##########################################################################
# 조합 미충족
##########################################################################

test_name = "TEST2_PW_combi_enable1"
TEST2_PW_enable(combi_pw_list1)
pw_verify(4, "% Your password must contain a minimum of 9 characters included with at least")


##########################################################################
# 조합 미충족
##########################################################################

test_name = "TEST2_PW_combi_enable2"
TEST2_PW_enable(combi_pw_list2)
pw_verify(4, "% Your password must contain a minimum of 9 characters included with at least")


##########################################################################
# 동일 문자 반복
##########################################################################

test_name = "TEST2_PW_repeated_enable"
TEST2_PW_enable(repeated_pw_list)
pw_verify(4, "% Passwords should not have the same characters or numbers in succession.")


##########################################################################
# 연속 문자
##########################################################################

test_name = "TEST2_PW_consecutive_enable1"
TEST2_PW_enable(consecutive_pw_list1)
pw_verify(3, "% Passwords should not have the consecutive characters or numbers in succession.")


##########################################################################
# 역순 연속 문자
##########################################################################

test_name = "TEST2_PW_consecutive_enable2"
TEST2_PW_enable(consecutive_pw_list2)
pw_verify(3, "% Passwords should not have the consecutive characters or numbers in succession.")


###################################
# admin2 계정 삭제
###################################

device.delete_user(crt, "admin2")


##########################################################################
# 로그아웃 + Console 종료
##########################################################################

device.close(crt)