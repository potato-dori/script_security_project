import subprocess
import time
import os
from pywinauto import Application


###################################
# 프로그램 경로
###################################

rebex_path = r"C:\Program Files\RebexTinySftpServer-Binaries-Latest\RebexTinySftpServer.exe"
securecrt_path = r"C:\Program Files\VanDyke Software\SecureCRT\SecureCRT.exe"
script_path = r"C:\Git\script_security_project\TEST8_sshkey_verify.py"
done_file = r"C:\Git\script_security_project\TEST8_DONE.txt"


###################################
# Rebex 실행
###################################

def start_rebex():

    # Rebex 실행
    subprocess.Popen(rebex_path)

    # 프로그램이 뜰 때까지 대기
    time.sleep(2)

    # 실행된 Rebex 프로그램에 연결
    app = Application(backend="uia")
    app.connect(path=rebex_path)

    # 메인 창 가져오기
    window = app.top_window()

    # Start 버튼 클릭
    window.child_window(
        title="Start",
        control_type="Button"
    ).click_input()

    time.sleep(1)

    return app, window


###################################
# SecureCRT + TEST8 실행
###################################

def start_securecrt():

    subprocess.Popen([
        securecrt_path,
        "/SCRIPT",
        script_path
    ])


###################################
# TEST8 완료 대기
###################################

def wait_test_done():

    while True:

        if os.path.exists(done_file):
            break

        time.sleep(1)


###################################
# Rebex Stop
###################################

def stop_rebex(window):

    stop_button = window.child_window(
        title="Stop",
        control_type="Button"
    )

    if stop_button.exists():
        stop_button.click_input()

    time.sleep(1)


###################################
# Rebex 종료
###################################

def close_rebex(window):

    window.close()

    time.sleep(1)


##########################################################################
# 실행
##########################################################################

# 이전 완료 파일이 있으면 삭제
if os.path.exists(done_file):
    os.remove(done_file)


# Rebex 실행 + Start
rebex_app, rebex_window = start_rebex()


# SecureCRT + TEST8 실행
start_securecrt()


# TEST8 완료 대기
wait_test_done()


# Rebex Stop
stop_rebex(rebex_window)


# Rebex 종료
close_rebex(rebex_window)


# 완료 파일 삭제
if os.path.exists(done_file):
    os.remove(done_file)


