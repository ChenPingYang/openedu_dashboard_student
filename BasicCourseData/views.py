from django.shortcuts import render
import cookiegetter
from use_function import namedtuplefetchall, getChooseDate
from django.db import connections


def basic_course_data_view(request):
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
                            data.append(rs.start_date)
                            data.append(rs.end_date)
                            coursedata.append(data.copy())

                to_render['result'] = coursedata
                # 設定日期範圍下拉式選單，預設值為1
                to_render['select'] = 1
                to_render['finalUpdate'] = '最後資料更新時間 : ' + finalUpdate_Student
                to_render['studentName'] = studentName

            to_render['IsLogin'] = 1
            print('teacher')
            return render(request, '1_BasicCourseData.html', to_render)

        else:
            print('not login')
            to_render['IsLogin'] = 2
            return render(request, 'noLogin.html', to_render)

    if request.method == 'POST':
        to_render = {}
        # 要傳給html的資料
        coursedata = []
        courseId = []

        # 學生擁有的課程
        studentsCourse = []

        islogin = cookiegetter.isLogined(request)
        if islogin:
            userEmail = cookiegetter.getEmail(request)
            userID = cookiegetter.getUserIDByEmail(userEmail)
            choose = request.GET.get('choose', False)
            S_startDate = request.GET.get('startDate', False)
            D_userChooseStartDate = getChooseDate(choose, S_startDate)

            if choose is None:
                to_render['select'] = 1
                to_render['selectStartDate'] = S_startDate
            else:
                to_render['select'] = choose
                to_render['selectStartDate'] = '年/月/日'

            with connections['ResultDB'].cursor() as cursor:
                # 取得統計日期，方式是取得最後一筆資料，此筆資料的統計日期就是最新日期
                cursor.execute("select * from student_total_data0912")
                result = namedtuplefetchall(cursor)
                finalUpdate_Student = result[-1].run_date

                cursor.execute("select * from course_total_data_v2")
                result = namedtuplefetchall(cursor)
                finalUpdate_course = result[-1].統計日期

                # 依據使用者選擇的日期，取得資料
                cursor.execute(
                    "SELECT course_id,name "
                    "FROM student_total_data0912 "
                    "WHERE run_date = %s and user_id = %s", [finalUpdate_Student, userID]
                )
                result = namedtuplefetchall(cursor)

                studentName = None
                for rs in result:
                    courseId.append(rs.course_id)
                    studentName = rs.name

                cursor.execute(
                    "SELECT * "
                    "FROM course_total_data_v2 "
                    "WHERE 統計日期 = %s AND start_date > %s", [finalUpdate_course, D_userChooseStartDate]
                )
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
                            data.append(rs.start_date)
                            data.append(rs.end_date)
                            coursedata.append(data.copy())

                to_render['result'] = coursedata
                to_render['select'] = 1
                to_render['finalUpdate'] = '最後資料更新時間 : ' + finalUpdate_Student
                to_render['studentName'] = studentName

            to_render['IsLogin'] = 1
            return render(request, '1_BasicCourseData.html', to_render)

        else:
            to_render['IsLogin'] = 2
            return render(request, 'noLogin.html', to_render)