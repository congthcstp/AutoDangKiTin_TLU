import os
import sys
import time
import json
from src.auth import internet_connection, login, get_user_info
from src.course import make_course_array
from src.register import auto_register
from src.calendar_sync import make_token, send_schedule
from src.ui import clear, menu, internet_check, schedule_menu as ui_schedule_menu

def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def main():
    ensure_folder_exists('res/')
    offline_mode = False
    if internet_connection():
        if os.path.exists("res/token.json"):
            offline_mode = internet_check()
        else:
            print("Kết nối không ổn định và không có dữ liệu từ lần chạy trước, vui lòng thử lại sau")
            sys.exit()
    
    username = input("Username: ") if not os.path.exists("res/login.json") else json.load(open("res/login.json"))["username"]
    password = input("Password: ") if not os.path.exists("res/login.json") else json.load(open("res/login.json"))["password"]
    cookies, headers = login(username, password)
    name, student_id, course_url, register_url, schedule_url = get_user_info(cookies, headers)

    while True:
        option = menu(name, student_id, offline_mode)
        if option == '1':
            clear()
            course_array, course_name_array = make_course_array(course_url, cookies, headers)
            auto_register(course_array, course_name_array, register_url, cookies, headers)
        elif option == '2' and not offline_mode:
            clear()
            cal, schedule_arr = make_token(schedule_url, cookies, headers)
            sub_option, sub_choice = ui_schedule_menu(schedule_arr)
            if sub_option == '0':
                continue
            elif sub_option == '1':
                clear()
                if 0 <= int(sub_choice) < len(schedule_arr):
                    send_schedule(cal, schedule_arr, int(sub_choice))
                    print("\nNhấn phím bất kì để tiếp tục...")
                    input()
            elif sub_option == '2':
                clear()
                for i in range(len(schedule_arr)):
                    print(i, '.', schedule_arr[i][0]['summary'])
                    send_schedule(cal, schedule_arr, i)
                    print()
                print("Nhấn phím bất kì để tiếp tục...")
                input()
            elif sub_option == '3':
                print("Đăng xuất thành công !")
                os.remove("res/token_google.json")
                time.sleep(1)
        elif option == '3' or (option == '2' and offline_mode):
            try:
                os.remove("res/login.json")
                os.remove("res/token.json")
                print("Đăng xuất thành công !")
            except:
                pass
            time.sleep(1)
        elif option == '0':
            print("Gặp lại sau !")
            sys.exit()
        else:
            print("Đối số không hợp lệ")
            time.sleep(1)

if __name__ == "__main__":
    main()