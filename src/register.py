import httpx
import json
import threading
import time
from datetime import datetime

def valid_time_checking():
    with open("res/all_course.json", encoding="utf8") as f:
        time_get = json.load(f)
    starttime = time_get['courseRegisterViewObject']['startDate']
    endtime = time_get['courseRegisterViewObject']['endDate']
    str_starttime = datetime.fromtimestamp(starttime / 1000)
    str_endtime = datetime.fromtimestamp(endtime / 1000)
    current_time = datetime.fromtimestamp(int(time.time()))
    print("Hiện tại:     ", current_time)
    print("Bắt đầu:      ", str_starttime)
    print("Kết thúc:     ", str_endtime, '\n')
    if current_time >= str_endtime:
        print("Đã hết thời gian đăng kí!")
        time.sleep(3)
        return False
    else:
        for x in range(int(starttime/1000) - int(time.time()) - 5, 0, -1):
            sec = x % 60
            min = int(x/60) % 60
            hrs = x / 3600
            times = f"{int(hrs):02}:{min:02}:{sec:02}"
            print("Bắt đầu chế độ tự động, " + times + " còn lại.", end='\r')
            time.sleep(1)
        return True

def send_request(val, i, register_url, cookies, headers, thread_check):
    try:
        r = httpx.post(register_url, headers=headers, cookies=cookies, json=val[i], verify=False)
        response = json.loads(r.text)
        if response['status'] == 0:
            print(response['message'])
            thread_check[i] = 'True'
        elif response['status'] == -9:
            thread_check[i] = 'Error'
        else:
            print(response['message'])
            thread_check[i] = 'False'
    except Exception as err:
        print(err)
        thread_check[i] = 'Error'

def auto_send_request(val, course_array, register_url, cookies, headers):
    thread_check = ['' for _ in range(len(course_array[val]))]
    for i in range(len(course_array[val])):
        thread = threading.Thread(target=send_request, args=(course_array[val], i, register_url, cookies, headers, thread_check))
        thread.start()
    print("Số thread hiện tại: ", len(course_array[val]))
    while True:
        if 'True' in thread_check:
            return True
        elif '' not in thread_check:
            if 'Error' in thread_check:
                for i in range(len(thread_check)):
                    if thread_check[i] == 'Error':
                        thread_check[i] = ''
                        thread = threading.Thread(target=send_request, args=(course_array[val], i, register_url, cookies, headers, thread_check))
                        thread.start()
            else:
                return False
        time.sleep(0.1)

def auto_register(course_array, course_name_array, register_url, cookies, headers):
    for i in range(len(course_array)):
        print(i, '.', course_name_array[i], '\n')
    option = input("Chọn môn để đăng kí (nhập 'all' để chọn tất cả)\nBạn có thể nhập nhiều môn 1 lúc bằng dấu cách: ")
    opt_list = option.split()
    print("Đang tiến hành đăng kí, vui lòng đợi...\n")
    time.sleep(2)
    print("Tips: Chỉ nên chọn những môn thực sự quan trọng vì quá trình đăng kí sẽ rất lâu.\nÀ quên, môn nào nhập trước đăng kí trước nhé :3\n")
    time.sleep(2)
    if not valid_time_checking():
        return
    for opt in opt_list:
        if opt == 'all':
            for j in range(len(course_array)):
                if auto_send_request(j, course_array, register_url, cookies, headers):
                    print("\nThành công: " + course_name_array[j])
                else:
                    print("\nKhông thành công: " + course_name_array[j])
        elif 0 <= int(opt) < len(course_array):
            if auto_send_request(int(opt), course_array, register_url, cookies, headers):
                print("\nThành công: " + course_name_array[int(opt)])
            else:
                print("\nKhông thành công: " + course_name_array[int(opt)])
    print("\nNhấn phím bất kì để tiếp tục...")
    input()