import httpx
import urllib.parse
import json
import os
import time
from datetime import datetime

login_url = "https://sinhvien1.tlu.edu.vn:443/education/oauth/token"
info_url = "https://sinhvien1.tlu.edu.vn:443/education/api/student/getstudentbylogin"
semester_url = "https://sinhvien1.tlu.edu.vn:443/education/api/semester/semester_info"
course_url = ""

username = ""
password = ""
login_data = ""
name = ""
student_id = ""

starttime = 0
endtime = 0

cookies = ""
headers = ""

def main():
    internet_check()
    login_option()
    user_info()
    menu()

def internet_connection():
    try:
        response = httpx.get("https://sinhvien1.tlu.edu.vn:443", timeout=5)
        return 0
    except httpx.ConnectTimeout:
        return 1
    except httpx.ConnectError:
        return 2

def internet_check():
    if internet_connection() == 1:
        print("Connection timeout")
        exit()
    elif internet_connection() == 2:
        print("Please check your internet connection and try again !")
        exit()

def login():
    global username, password, login_data
    username = input("Username: ")
    password = input("Password: ")
    login_data = {"client_id": "education_client", "grant_type": "password", "username": username, "password": password, "client_secret": "password"}
    r = httpx.post(login_url, data=login_data)
    if 'error' in r.text:
        print("Password or username is incorrect !\n")
        main()
    elif '502 Bad Gateway' in r.text:
        print("Bad gateway at server, please try again !")
        exit()
    else:
        print("Login successful !")
        time.sleep(1)
        os.system('clear')
        cookies_renew(r)

def login_option():
    os.system('clear')
    print("Login option:\n")
    print("1. Manual login")
    print("2. Login with JSON file\n")
    option = input("Option: ")
    if option == '1':
        os.system('clear')
        login()
    elif option == '2':
        os.system('clear')
        json_login()

def make_login_json():
    login = {
        "username": username,
        "password": password
    }
    if os.path.exists("login.json"):
        os.remove("login.json")
    with open("login.json", "w") as outfile:
        json.dump(login, outfile)
    print("Successful !")
    time.sleep(1)
    os.system('clear')
    menu()

def json_login():
    global username, password, login_data
    if os.path.exists("login.json") == False:
        print("You don't have a JSON login file !")
        time.sleep(1)
        main()
    f = open("login.json")
    login = json.load(f)
    username = login['username']
    password = login['password']
    login_data = {"client_id": "education_client", "grant_type": "password", "username": username, "password": password, "client_secret": "password"}
    r = httpx.post(login_url, data=login_data)
    if 'error' in r.text:
        print("Password or username is incorrect !\n")
        main()
    elif '502 Bad Gateway' in r.text:
        print("Bad gateway at server, please try again !")
        exit()
    else:
        print("Login successful !")
        time.sleep(1)
        os.system('clear')
        cookies_renew(r)

def user_info():
    global student_id, name, course_url
    r = httpx.get(info_url, headers=headers, cookies=cookies)
    name = json.loads(r.text)['displayName']
    student_id = json.loads(r.text)['id']
    r2 = httpx.get(semester_url, headers=headers, cookies=cookies)
    course_url = "https://sinhvien1.tlu.edu.vn:443/education/api/cs_reg_mongo/findByPeriod/" + str(student_id) + "/" + str(json.loads(r2.text)['semesterRegisterPeriods'][0]['id'])
        
def cookies_renew(r):
    global cookies, headers
    cookies = {"token": urllib.parse.quote_plus(r.text)}
    access_token = "Bearer " + json.loads(r.text)['access_token']
    headers = {"Authorization" : access_token}

def menu():
    print("Welcome back, " + name)
    print("Your id is: " + str(student_id))
    print("\n")
    print("1. Course register")
    print("2. List all course and ID")
    print("3. Auto register")
    print("4. Create a login JSON")
    print("0. Exit")
    option = input("\nOption: ")
    if option == '1':
        os.system('clear')
        course_register()
    elif option == '2':
        os.system('clear')
        course_list()
    elif option == '3':
        os.system('clear')
        auto_register()
    elif option == '4':
        make_login_json()
    elif option == '0':
        print("See you again !")
        exit()
    else:
        print("Invalid argument")
        time.sleep(1)
        menu()

def course_list():
    r = httpx.get(course_url, headers=headers, cookies=cookies)
    course_list = json.loads(r.text)
    course_length = len(course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'])
    for i in range(course_length):
        if course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][0]['subCourseSubjects'] is not None:
            subcourse_length = len(course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][0]['subCourseSubjects'])
            for j in range(subcourse_length):
                sub_display_name = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][0]['subCourseSubjects'][j]['displayName']
                sub_display_id = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][0]['subCourseSubjects'][j]['id']
                sub_start_date = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][0]['subCourseSubjects'][j]['timetables'][0]['startDate']
                sub_end_date = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][0]['subCourseSubjects'][j]['timetables'][0]['endDate']
                sub_start_hour = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][0]['subCourseSubjects'][j]['timetables'][0]['startHour']['startString']
                sub_end_hour = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][0]['subCourseSubjects'][j]['timetables'][0]['endHour']['endString']
                sub_week_index = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][0]['subCourseSubjects'][j]['timetables'][0]['weekIndex']
                print(sub_display_name, '(' ,sub_display_id,')')
                print(str(datetime.fromtimestamp(sub_start_date / 1000))[0:10], "->", str(datetime.fromtimestamp(sub_end_date / 1000))[0:10], end='')
                print(' ||', week_index_c(sub_week_index), end='')
                print(" ||" , sub_start_hour, "->", sub_end_hour)   
        else:
            courseSubjectDtos_length = len(course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'])
            for k in range(courseSubjectDtos_length):
                display_name = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][k]['displayName']
                display_id = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][k]['id']
                start_date = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][k]['timetables'][0]['startDate']
                end_date = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][k]['timetables'][0]['endDate']
                start_hour = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][k]['timetables'][0]['startHour']['startString']
                end_hour = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][k]['timetables'][0]['endHour']['endString']
                week_index = course_list['courseRegisterViewObject']['listSubjectRegistrationDtos'][i]['courseSubjectDtos'][k]['timetables'][0]['weekIndex']
                print(display_name, '(' ,display_id , ')')
                print(str(datetime.fromtimestamp(start_date / 1000))[0:10], "->", str(datetime.fromtimestamp(end_date / 1000))[0:10], end='')
                print(' ||', week_index_c(week_index), end='')
                print(" ||", start_hour, "->", end_hour)
        print('')
    print("Press any key to continue...")
    input()
    os.system('clear')
    menu()

def course_register():
    print("Not done yet !")
    exit()

def auto_register():
    global starttime, endtime
    r = httpx.get(course_url, headers=headers, cookies=cookies)
    time_get = json.loads(r.text)
    starttime = time_get['courseRegisterViewObject']['startDate']
    endtime = time_get['courseRegisterViewObject']['endDate']
    print("Current time: ", datetime.fromtimestamp(int(time.time())))
    print("Start date:   ", datetime.fromtimestamp(starttime / 1000))
    print("End date:     ", datetime.fromtimestamp(endtime / 1000), '\n')
    option = input("Do you want to register automatic ? [Y/n]")
    if option == 'Y' or option == 'y':
        os.system('clear')
        countdown()
    elif option == 'n' or option == 'N':
        os.system('clear')
        menu()
    else:
        print("Invalid argument")
        time.sleep(1)
        auto_register()

def countdown():
    for x in range(int(starttime/1000) - int(time.time()), 0, -1):
        sec = x % 60
        min = int(x/60) % 60
        hrs = x / 3600
        times = f"{int(hrs):02}:{min:02}:{sec:02}"
        print("Schedule started, " + times + " remaining.", end='\r')
        time.sleep(1)

def week_index_c(x):
    if x == 1:
        return "Sun"
    elif x == 2:
        return "Mon"
    elif x == 3:
        return "Tue"
    elif x == 4:
        return "Wed"
    elif x == 5:
        return "Thu"
    elif x == 6:
        return "Fri"
    elif x == 7:
        return "Sat"

main()