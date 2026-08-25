import time
import sys
###################################
# 공통 모듈 경로
###################################
sys.path.append(r"C:\Git\script_security_project")
import device
import result

###################################
# 장비 정보
###################################
device_name = "SWITCH"

###################################
# SNMP 시험
###################################
groupname = "snmptest"

snmp_auth_password = "Changeme1357!"
snmp_priv_password = "Changeme1357#"


##########################################################################
# TEST8-01
# SNMP 인증 및 암호화 비밀번호 저장
##########################################################################

def TEST8_SNMP_test():

    ###################################
    # SNMP 설정
    ###################################

    device.set_snmp_v3(crt, groupname, snmp_auth_password, snmp_priv_password)
    

    ###################################
    # 여기부터 비밀번호 노출 확인
    ###################################

    crt.Screen.Send(f"{test_name}_start\n")

    time.sleep(1)

    ###################################
    # show snmp
    ###################################

    crt.Screen.Send("show snmp\n")
    crt.Screen.WaitForString(f"{device_name}#")

    ###################################
    # running-configuration
    ###################################

    crt.Screen.Send("show running-configuration |include snmp\n")
    crt.Screen.WaitForString(f"{device_name}#")

    crt.Screen.Send(f"{test_name}_end\n")

    time.sleep(1)


###################################
# SNMP 비밀번호 노출 판정
###################################

def TEST8_SNMP_verify():

    ###################################
    # 시험 구간 추출
    ###################################

    final = result.test_part(
        crt,
        f"{test_name}_start",
        f"{test_name}_end"
    )

    user_found = False

    auth_count = 0
    priv_count = 0

    ###################################
    # 결과 확인
    ###################################

    for line in final.splitlines():

        ###################################
        # SNMP User 생성 확인
        ###################################

        if f"snmp v3 user {groupname}" in line:
            user_found = True


        ###################################
        # 인증 비밀번호 노출 확인
        ###################################

        if snmp_auth_password in line:
            auth_count += 1


        ###################################
        # 암호화 비밀번호 노출 확인
        ###################################

        if snmp_priv_password in line:
            priv_count += 1      

                
    ###################################
    # 결과 판정
    ###################################

    if user_found == False:

        test_result = "FAIL"

        judge_value = "SNMP User 생성 확인되지 않음"


    elif (
        auth_count == 0
        and priv_count == 0
    ):

        test_result = "PASS"

        judge_value = (
            f"SNMP User 확인, "
            f"Auth PW={auth_count}, "
            f"Priv PW={priv_count}"
        )


    else:

        test_result = "FAIL"

        judge_value = (
            f"SNMP User 확인, "
            f"Auth PW={auth_count}, "
            f"Priv PW={priv_count}"
        )


    ###################################
    # 결과 저장
    ###################################

    result.save_result(
        test_name,
        test_result,
        judge_value,
        final
    )





##########################################################################
# 실행
##########################################################################

device.start(crt)


##################################################
# TEST8-01
# SNMP 인증 및 암호화 비밀번호 출력 확인
##################################################

test_name = "TEST8_SNMPkey_verify"

TEST8_SNMP_test()

TEST8_SNMP_verify()


##################################################
# SNMP 설정 삭제
##################################################

device.clear_snmp_v3(crt, groupname)


##################################################
# 장비 로그아웃 
##################################################

device.logout(crt)


##################################################
#Console 연결 종료
##################################################

device.disconnect_console(crt)