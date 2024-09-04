import base64
import os
from dotenv import load_dotenv
import requests
import pickle
from bs4 import BeautifulSoup
import tabulate

load_dotenv()


def login():
    print("Login Again...")
    login_data = {
        "Anthem_UpdatePage": True,
        "__EVENTTARGET": "ctl34",
        "__EVENTARGUMENT": None,
        "__VIEWSTATE": "",
        "__VIEWSTATEGENERATOR": "F82B3F21",
        "__EVENTVALIDATION": "",
        "UserCode": os.getenv("USER_CODE"),
        "KeyCode": os.getenv("KEY_CODE"),
        "txtUsercode": None,
        "txtNationalsms": None,
        "txtEmail": None,
        "txtNationalCode": None,
        "txtUserCodeQues": None,
        "txtNationalCodeQues": None,
        "txtFirstName": None,
        "txtLastName": None,
        "txtEnglishFirstName": None,
        "txtEnglishLastName": None,
        "txtNationalCodeReg": None,
        "txtIdentityReg": None,
        "drpGender": None,
        "drpNationalty": None,
        "txtEmailReg": None,
        "txtMobile": None,
        "txtPhone": None,
        "drpUserType": None,
        "txtUser": None,
        "txtPass": None,
        "txtRePass": None,
        "txtQuestionReg": None,
        "txtAnswerReg": None,
        "txtApplicant": None,
        "txtNational": None,
        "txtRegGuest": None,
    }
    login_res = requests.post("https://amoozesh.ustmb.ac.ir/SamaWeb/login.aspx?Anthem_CallBack=true", data=login_data)

    if login_res.status_code == 200:
        cookie = {
            ".ASPXAUTH": login_res.cookies[".ASPXAUTH"],
            "ASP.NET_SessionId": login_res.cookies["ASP.NET_SessionId"],
            "Menu": None,
            "SL_G_WPT_TO": "en",
        }
        second_login_res = requests.head("https://amoozesh.ustmb.ac.ir/SamaWeb/LoginWithUser.aspx", cookies=cookie)
        cookie = {
            "ASP.NET_SessionId": login_res.cookies["ASP.NET_SessionId"],
            ".ASPXAUTH": second_login_res.cookies[".ASPXAUTH"],
            "Menu": None,
            "SL_G_WPT_TO": "en",
        }
        with open("cache.txt", "wb") as cache_file:
            cache_file.write(pickle.dumps(cookie))
        return cookie
    else:
        raise ValueError("some problem in login!")


def get_cookies_from_cache():
    with open("cache.txt", "rb") as file:
        return pickle.load(file)


def get_student_image_with_cookies(cookies: dict):
    try:
        response = requests.get(
            "https://amoozesh.ustmb.ac.ir/SamaWeb/StudentPicture.ashx",
            cookies=cookies
        )
        return response
    except:
        raise ConnectionError


def request_to_url_with_cache_or_login(url: str, method: str, data: dict | None = None):
    try:
        cookies = get_cookies_from_cache()
        response = requests.request(method, url, cookies=cookies,
                                    data=data)  # => It return error if there is a problem to request
        soup: BeautifulSoup = BeautifulSoup(response.content.decode("utf-8"), 'html.parser')

        if "ورود به سیستم آموزش" in soup.title.string:
            # The cookie in cache.txt is no longer valid.
            print("# The cookie in cache.txt is no longer valid.")
            cookies = login()
            response = requests.request(method, url, cookies=cookies, data=data)
            title = BeautifulSoup(response.content.decode("utf-8")).title.string
            if "ورود به سیستم آموزش" in title:
                # it is the site's issue.
                raise ConnectionError
        else:
            # The cookie in cache.txt is still valid.
            print("# The cookie in cache.txt is still valid.")
            pass
        return {
            "status": "OK",
            "response": response,
            "cookies": cookies
        }
    except:
        print("مشکلی در برقراری ارتباط با سایت وجود دارد!")
        raise ConnectionError


def main_page():
    cookies = login()
    res = requests.get("https://amoozesh.ustmb.ac.ir/SamaWeb/Index.aspx", cookies=cookies)
    with open("../eawiyrfweb.html", "w", encoding="utf-8") as file:
        file.write(res.content.decode("utf-8"))


# main_page()

def get_lessons(lesson: str, lesson_status=None, page_number=None):
    if lesson.isdigit():
        lesson = int(lesson)
    payload = {
        "LessonType": "0",
        "Completed": lesson_status,
        "Search": "LessonNameSelect" if type(lesson) == str else "LessonCodeSelect",
        "SearchPattern": lesson,
        "PageNum": page_number
    }
    try:
        response: dict = request_to_url_with_cache_or_login(
            "https://amoozesh.ustmb.ac.ir/SamaWeb/LessonReport.asp",
            "post",
            payload,
            # user_id
        )  # => If there is a problem in the request to https://amoozesh.ustmb.ac.ir, it returns ConnectionError

        soup: BeautifulSoup = BeautifulSoup(response.get("response").content.decode("utf-8"), 'html.parser')
        pages = soup.find_all("select", attrs={"name": "PageNum"})
        if pages:
            # There are other pages
            page_numbers = [num.text for num in pages[0].find_all("option")]
            print(page_numbers)
        else:
            # There aren't other pages
            page_numbers = [1]
            not_found_text = soup.find("font", attrs={"face": "IRANSans", "size": "2", "color": "maroon"})
            if not_found_text:
                # If this tag exists, it means that no lessons were found
                raise IndexError
        yield {
            "status": "Pages",
            "message": f"تعداد صفحات یافت شده : {len(page_numbers)}"
        }
    except ConnectionError:
        # There is a problem to request
        yield {
            "status": "Error",
            "message": "مشکلی در برقراری ارتباط با سایت وجود دارد!"
        }
        return
    except IndexError:
        # There is no page
        yield {
            "status": "NotFound",
            "message": "چیزی پیدا نکردم!"
        }
        print("چیزی پیدا نکردم!")
        return

    for page in page_numbers:
        if page != 1:
            req = requests.post(
                "https://amoozesh.ustmb.ac.ir/SamaWeb/LessonReport.asp",
                cookies=response.get("cookies"),
                data=payload | {"PageNum": page}
            )
            soup: BeautifulSoup = BeautifulSoup(req.content.decode("utf-8"), 'html.parser')

        table = soup.find("table", attrs={"bordercolor": "#C0C0C0"})
        rows = table.select("tr td span")
        data = [list(map(lambda span: span.text, rows[num:num + 2])) for num in range(0, len(rows), 2)]
        data = [data[num:num + 40] for num in range(0, len(data), 40)]

        lessons = f" صفحه {page} از  {page_numbers[-1]}\n"

        for lesson in data:
            for s in lesson:
                lessons += f"\n-{s[0]} {s[1]}"

        if len(lessons) > 4096:
            before = lessons[0:4097]
            after = lessons[4098::]
            lessons = [before, after]
        yield {
            "status": "Found",
            "message": lessons
        }


def get_my_courses_in_this_semester():
    try:
        response = request_to_url_with_cache_or_login(
            "https://amoozesh.ustmb.ac.ir/SamaWeb/TermStudentLessons.asp",
            "post",
            # user_id
        )  # => If there is a problem in the request to https://amoozesh.ustmb.ac.ir, it returns ConnectionError
    except ConnectionError:
        return "مشکلی در برقراری ارتباط با سایت وجود دارد!"

    soup: BeautifulSoup = BeautifulSoup(response.get("response").content.decode("utf-8"), 'html.parser')
    table = soup.find_all("table", attrs={"id": "Main"})[0]
    th = [th.string for th in table.find_all("th") if th.string not in ["وضعیت درس", "نظر سنجی", "غیبت"]]

    td = [td.string.strip() for td in table.find_all("td") if
          td.string is not None and td.string.strip() != "بررسی نشده"]
    list_ = [td[i:i + 5:] for i in range(0, len(td), 5)]
    table = tabulate.tabulate(list_, headers=th)
    return table


def get_unit_confirmation(user_id: int | None = None):
    payload = {
        "strTermCode": os.environ.get("TERM_CODE"),
        "strStudentCode": os.environ.get("USER_CODE")
    }
    try:
        response = request_to_url_with_cache_or_login(
            "https://amoozesh.ustmb.ac.ir/SamaWeb/WorkBookPrintTerm.asp",
            "post",
            payload,
            # user_id
        )  # => If there is a problem in the request to https://amoozesh.ustmb.ac.ir, it returns ConnectionError

        student_image = get_student_image_with_cookies(
            response.get("cookies"),
            # user_id
        )  # => If there is a problem getting student image, it returns ConnectionError

        soup: BeautifulSoup = BeautifulSoup(response.get("response").content.decode("utf-8"), 'html.parser')
        student_img = soup.find_all("img")[1]
        uni_logo = soup.find_all("img")[0]
        student_img["src"] = 'data:image/jpeg;base64,' + base64.b64encode(student_image.content).decode('utf-8')
        uni_logo["src"] = "https://amoozesh.ustmb.ac.ir/SamaWeb/Images/UniversityPicture.png"

        for script_tag in soup.find_all("script"):
            # Remove script tags on the page
            script_tag.extract()

        with open(file_address := f"../data/{user_id}.html", "wb") as file:
            file.write(soup.encode())
            return {
                "status": "OK",
                "file_address": file_address
            }
    except ConnectionError:
        return {
            "status": "Error",
            "message": "مشکلی در برقراری ارتباط با سایت وجود دارد!"
        }


def get_lesson_temporary_work_report():
    try:
        res = request_to_url_with_cache_or_login(
            "https://amoozesh.ustmb.ac.ir/SamaWeb/TemproryTermWorkBookReport.asp",
            "get"
        )
        soup: BeautifulSoup = BeautifulSoup(res.get("response").content.decode("utf-8"), 'html.parser')
        table = soup.find("table", attrs={"border": "1", "cellpadding": "1", "bordercolor": "#C0C0C0",
                                          "style": "border-collapse: collapse", "cellspacing": "0", "width": "90%"})

        data = [data.text for data in table.select("tr td font")]
        data = [data[num:num + 7] for num in range(0, len(data), 7)]

        return tabulate.tabulate(data[1:], headers=data[0])
    except ConnectionError:
        return ""


def invalid():
    with open("TelegramBot/cache.txt", "wb") as file:
        file.write(pickle.dumps({"a": "aa"}))


# invalid()
from pickle import FALSE
