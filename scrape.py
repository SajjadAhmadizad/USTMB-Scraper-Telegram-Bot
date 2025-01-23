import base64
import datetime
import os
import hashlib
import re
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

from tables import Student, StudentSession, create_engine, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
Session = sessionmaker(bind=engine)
session = Session()

load_dotenv()


def convert_to_persian_numbers(text):
    english_to_persian = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    return text.translate(english_to_persian)


import tabulate


def rtl_tabulate(data, headers):
    reversed_data = [row[::-1] for row in data]
    reversed_headers = headers[::-1]

    table = tabulate.tabulate(reversed_data, reversed_headers)

    lines = table.split('\n')

    return '\n'.join(lines)


def login(student: Student):
    std, student_session = student
    login_data = {
        "Anthem_UpdatePage": True,
        "__EVENTTARGET": "ctl34",
        "__EVENTARGUMENT": None,
        "__VIEWSTATE": "",
        "__VIEWSTATEGENERATOR": "F82B3F21",
        "__EVENTVALIDATION": "",
        "UserCode": std.student_code,
        "KeyCode": hashlib.md5(str(std.national_code).encode()).hexdigest(),
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
    print("Login Again...")
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
        print(second_login_res.headers)

        # Add this session in database for user
        if student_session:
            student_session.ASPXAUTH = cookie[".ASPXAUTH"]
            student_session.NET_SessionId = cookie["ASP.NET_SessionId"]
            student_session.expires_at = datetime.datetime.now()  # TODO: add expires_at
        else:
            new_session = StudentSession(
                student_id=std.id,
                NET_SessionId=cookie["ASP.NET_SessionId"],
                ASPXAUTH=cookie[".ASPXAUTH"],
                Menu="main",
                expires_at=datetime.datetime.now()  # TODO: add expires_at
            )
            session.add(new_session)
        session.commit()

        return cookie
    else:
        raise ValueError("some problem in login!")


def get_student_image_with_cookies(cookies: dict):
    try:
        response = requests.get(
            "https://amoozesh.ustmb.ac.ir/SamaWeb/StudentPicture.ashx",
            cookies=cookies
        )
        return response
    except:
        raise ConnectionError


def request_to_url_with_cookie_or_login(url: str, method: str, user_id: int, data: dict | None = None):
    try:
        student = session.query(
            Student, StudentSession
        ).join(
            StudentSession, Student.id == StudentSession.student_id, isouter=True
        ).filter(
            Student.telegram_id == user_id
        ).first()

        std, student_session = student
        if student_session:
            cookies = {
                'ASP.NET_SessionId': student_session.NET_SessionId,
                '.ASPXAUTH': student_session.ASPXAUTH,
                'Menu': None,
                'SL_G_WPT_TO': 'en'
            }
        else:
            # There isn't any session for this student
            cookies = {}
        response = requests.request(
            method,
            url,
            cookies=cookies,
            data=data
        )  # => It return error if there is a problem to request
        soup: BeautifulSoup = BeautifulSoup(response.content.decode("utf-8"), 'html.parser')

        if "ورود به سیستم آموزش" in soup.title.string:
            # The cookie in database is no longer valid or there isn't any cookie.
            print("# The cookie in database is no longer valid or there isn't any cookie.")
            print(std.id, std.telegram_id)
            cookies = login(student)
            response = requests.request(method, url, cookies=cookies, data=data)
            title = BeautifulSoup(response.content.decode("utf-8")).title.string
            if "ورود به سیستم آموزش" in title:
                # it is the site's issue.
                raise ConnectionError
        else:
            # The cookie in db is still valid.
            print("# The cookie in db is still valid.")
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
    cookies = login(student="")
    res = requests.get("https://amoozesh.ustmb.ac.ir/SamaWeb/Index.aspx", cookies=cookies)
    with open("../eawiyrfweb.html", "w", encoding="utf-8") as file:
        file.write(res.content.decode("utf-8"))


def get_lessons(lesson: str, user_id: int, lesson_status: str | None = None, page_number: str | None = None):
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
        response: dict = request_to_url_with_cookie_or_login(
            "https://amoozesh.ustmb.ac.ir/SamaWeb/LessonReport.asp",
            "post",
            user_id,
            payload
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


def get_my_courses_in_this_semester(user_id: int):
    try:
        response = request_to_url_with_cookie_or_login(
            "https://amoozesh.ustmb.ac.ir/SamaWeb/TermStudentLessons.asp",
            "post",
            user_id
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
        "strStudentCode": session.query(Student.student_code).filter(Student.telegram_id == user_id).scalar()
    }
    print(payload)
    try:
        response = request_to_url_with_cookie_or_login(
            "https://amoozesh.ustmb.ac.ir/SamaWeb/WorkBookPrintTerm.asp",
            "post",
            user_id,
            payload
        )  # => If there is a problem in the request to https://amoozesh.ustmb.ac.ir, it returns ConnectionError

        student_image = get_student_image_with_cookies(
            response.get("cookies")
        )  # => If there is a problem getting student image, it returns ConnectionError

        soup: BeautifulSoup = BeautifulSoup(response.get("response").content.decode("utf-8"), 'html.parser')
        student_img = soup.find_all("img")[1]
        uni_logo = soup.find_all("img")[0]
        student_img["src"] = 'data:image/jpeg;base64,' + base64.b64encode(student_image.content).decode('utf-8')
        uni_logo["src"] = "https://amoozesh.ustmb.ac.ir/SamaWeb/Images/UniversityPicture.png"

        for script_tag in soup.find_all("script"):
            # Remove script tags on the page
            script_tag.extract()

        file_address = f"data/{user_id}.html"
        os.makedirs(os.path.dirname(file_address), exist_ok=True)
        with open(file_address, "wb") as file:
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


def get_lesson_temporary_work_report(user_id: int):
    try:
        res = request_to_url_with_cookie_or_login(
            "https://amoozesh.ustmb.ac.ir/SamaWeb/TemproryTermWorkBookReport.asp",
            "get",
            user_id
        )
        soup: BeautifulSoup = BeautifulSoup(res.get("response").content.decode("utf-8"), 'html.parser')
        table = soup.find("table", attrs={
            "border": "1",
            "cellpadding": "1",
            "bordercolor": "#C0C0C0",
            "style": "border-collapse: collapse",
            "cellspacing": "0",
            "width": "90%"
        })

        data = [data.text for data in table.select("tr td font")]
        data = [data[num:num + 7] for num in range(0, len(data), 7)]

        return tabulate.tabulate(data[1:], headers=data[0])
    except ConnectionError:
        return ""


def get_work_report(user_id: int):
    try:
        res = request_to_url_with_cookie_or_login(
            "https://amoozesh.ustmb.ac.ir/SamaWeb/WorkBookRequest.asp",
            "get",
            user_id
        )
        answer = ""
        soup: BeautifulSoup = BeautifulSoup(res.get("response").content.decode("utf-8"), 'html.parser')
        rows = soup.find_all('div', attrs={"class": "tab-pane"})
        header = "کددرس,نام درس,واحد,نمره,وضعیت"
        for div in rows:
            semester = div.find_next().select("font")[0].text
            ans = []
            li = re.findall("size=\"2\">(.*?)<", str(div.find_all("font")[6]).replace("\n", " "))
            while "" in li:
                li[li.index("")] = "گ.ن"
            for i in range(0, len(li), 5):
                ans.append(li[i:i + 5])
            yield {"semester": semester, "data": rtl_tabulate(ans, header.split(","))}
    except ConnectionError:
        return ""
