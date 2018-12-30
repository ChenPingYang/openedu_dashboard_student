from django.shortcuts import render
from django.db import connections
from use_function import namedtuplefetchall
import cookiegetter


def suggested_courses_view(request):
    request.encoding = 'utf-8'
    to_render = {}
    data = []
    output = []
    if request.method == 'GET':
        to_render = suggest_course(request)

    return render(request, 'SuggestedCourses.html', to_render)


def suggested_courses_v1_view(request):
    request.encoding = 'utf-8'

    if request.method == 'GET':
        to_render = {}
        coursedata = []
        courseId = []
        studentsCourse = []

        islogin = cookiegetter.isLogined(request)
        islogin = True

        if islogin:
            userEmail = cookiegetter.getEmail(request)
            userID = cookiegetter.getUserIDByEmail(userEmail)

            userID = '43394'

            with connections['ResultDB'].cursor() as cursor:
                # 取得統計日期，方式是取得最後一筆資料，此筆資料的統計日期就是最新日期
                cursor.execute("SELECT max(run_date) as day FROM student_total_data0912")
                result = namedtuplefetchall(cursor)
                finalUpdate_Student = result[-1].day

                cursor.execute("SELECT max(統計日期) as day FROM course_total_data_v2")
                result = namedtuplefetchall(cursor)
                finalUpdate_course = result[-1].day

                # 取得學生擁有的課程的資料
                cursor.execute("SELECT course_id,name "
                               "FROM student_total_data0912 "
                               "WHERE run_date = %s and user_id = %s", [finalUpdate_Student, userID])
                result = namedtuplefetchall(cursor)

                studentName = None
                for rs in result:
                    courseId.append(rs.course_id)
                    studentName = rs.name

                cursor.execute("select * from course_total_data_v2 where 統計日期 = %s", [finalUpdate_course])
                result = namedtuplefetchall(cursor)
                data = []
                for rs in result:
                    for i in range(len(courseId)):
                        if rs.course_id == courseId[i]:
                            data.clear()
                            data.append(rs.課程代碼)
                            data.append(rs.course_id)
                            data.append(rs.course_name)
                            data.append(rs.註冊人數)
                            coursedata.append(data.copy())

                to_render['User_course'] = coursedata
                # 設定日期範圍下拉式選單，預設值為1
                to_render['select'] = 1
                to_render['finalUpdate'] = '最後資料更新時間 : ' + finalUpdate_Student
                to_render['studentName'] = studentName

            to_render['IsLogin'] = 1
            print('teacher')
            return render(request, 'SuggestedCourses_v1.html', to_render)

        else:
            print('not login')
            to_render['IsLogin'] = 2
            return render(request, 'noLogin.html', to_render)


def suggest_course(request):
    request.encoding = 'utf-8'
    to_render = {}
    data = []
    output = []

    with connections['ResultDB'].cursor() as cursor:

        # course_id = 'course-v1:FCUx+2015015+201512'
        course = request.GET.get('course', '')
        course_id = course.replace(' ', '+')

        # 搜尋所有修同一課程之學生所修課資料
        cursor.execute(
            "SELECT course_id "
            "FROM student_total_data0912 "
            "WHERE user_id in (SELECT user_id FROM student_total_data0912 WHERE course_id = %s)", [course_id]
        )
        courses = namedtuplefetchall(cursor)

        # 課程資料
        cursor.execute(
            "SELECT distinct(course_id), course_name,課程代碼, 註冊人數 "
            "FROM course_total_data_v2 "
            "WHERE 統計日期='2018-12-18'"
        )
        course_data = namedtuplefetchall(cursor)

        student_count = {}
        for course in courses:
            if course.course_id in student_count:
                student_count[course.course_id] += 1
            else:
                student_count[course.course_id] = 1

        # 排序
        student_count = dict(sorted(student_count.items(), key=lambda x: x[1], reverse=True))

        temp = []
        c = 0
        for key, value in student_count.items():
            temp.clear()
            check = ExistorNot(key, course_data)

            if key == course_id:
                pass
            elif c < 5:
                if check is not None:
                    temp.append(check[0])
                    temp.append(check[1])
                    temp.append(check[2])
                    temp.append(check[3])
                    output.append(temp.copy())
                    c += 1

            else:
                break

        cursor.execute("SELECT course_name "
                       "FROM course_total_data_v2 "
                       "WHERE course_id = %s and 統計日期='2018-12-18'", [course_id])
        result = namedtuplefetchall(cursor)

        CourseName = result[-1].course_name

        to_render['data'] = output
        to_render['CourseName'] = CourseName

        return to_render


def ExistorNot(cid, course_data):
    exist = None
    for cd in course_data:
        if cd.course_id == cid:
            exist = [cd.課程代碼, cd.course_id, cd.course_name, cd.註冊人數]
            break

    return exist
