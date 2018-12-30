from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta
from use_function import namedtuplefetchall, getStudentLastlogin
from django.db import connections
import cookiegetter
import json


def index_view(request):
    request.encoding = 'utf-8'

    if request.method == "GET":
        to_render = {}
        islogin = cookiegetter.isLogined(request)

        islogin = True

        if islogin is True:
            userEmail = cookiegetter.getEmail(request)
            # userID = cookiegetter.getUserIDByEmail(userEmail)

            userID = '43394'
            with connections['ResultDB'].cursor() as cursor:
                # 取得學生統計日期
                cursor.execute("SELECT max(run_date) as max_run "
                               "FROM student_total_data0912 "
                               "WHERE user_id = %s", [userID])
                result = namedtuplefetchall(cursor)
                StudentfinalUpdate = result[-1].max_run
                to_render['finalUpdate'] = '最後資料更新時間 : ' + StudentfinalUpdate

                # 取得統計日期，方式是取得最後一筆資料，此筆資料的統計日期就是最新日期
                cursor.execute("select max(統計日期) as max_date from course_total_data_v2")
                result = namedtuplefetchall(cursor)
                CoursefinalUpdate = result[-1].max_date
                to_render['CoursefinalUpdate'] = CoursefinalUpdate

                courseData = []
                cursor.execute(
                    "SELECT (影片觀看人次_台灣 + 影片觀看人次_非台灣 + login_count)/(註冊人數+退選人數) as a,start_date,註冊人數,`course_name`,course_id,課程代碼,end_date "
                    "FROM course_total_data_v2 "
                    "WHERE course_id in (select course_id from student_total_data0912 where run_date ='"
                    + StudentfinalUpdate + "'" + " and  user_id = '" + userID + "') and 統計日期='"
                    + CoursefinalUpdate + "' order by course_id"
                )
                result = namedtuplefetchall(cursor)

                Data = ['' for i in range(9)]
                duration_week = ''
                for rs in result:
                    Data[0] = rs.course_name
                    Data[1] = rs.start_date
                    Data[2] = rs.註冊人數
                    Data[3] = rs.課程代碼

                    # 計算課程剩餘幾天
                    if rs.end_date != 'NA':
                        today = datetime.today()
                        day = (datetime.strptime(rs.end_date, '%Y-%m-%d') - today).days
                        duration_week = str(day)

                    Data[4] = duration_week

                    # 判斷課程是否已結束
                    if rs.end_date != 'NA' and datetime.strptime(rs.end_date, '%Y-%m-%d') < datetime.today():
                        # 結束
                        Data[5] = rs.course_name
                    else:
                        # 開課中
                        Data[5] = '0'

                    Data[6] = rs.end_date
                    Data[7] = rs.course_id

                    if rs.a is not None:
                        Data[8] = rs.a
                    else:
                        Data[8] = '0'

                    courseData.append(Data.copy())

                cursor.execute(
                    "SELECT watch_count,login_count,certificate,last_login,course_id as id,name "
                    "FROM student_total_data0912 "
                    "WHERE run_date = %s and  user_id = %s order by id", [StudentfinalUpdate, userID]
                )
                result = namedtuplefetchall(cursor)

                countAllCourse = 0
                countExistCourse = 0
                basiccourse = []
                selfstudycourse = []

                registerdate = getStudentLastlogin(userID)
                registerdate = datetime.strptime(str(registerdate), '%Y-%m-%d %H:%M:%S')
                to_render['date_joined'] = datetime.strftime(registerdate, '%Y-%m-%d')

                finalCourseData = ['' for i in range(12)]
                i = 0
                readyendexist = False
                endexist = False
                startexist = False
                selfstudyexist = False
                noData = 0
                studentName = ''

                for rs in result:
                    studentWatchTemp = 0
                    studentLoginTemp = 0
                    studentName = rs.name

                    if rs.id == courseData[i][7]:
                        finalCourseData[0] = courseData[i][0]
                        finalCourseData[1] = courseData[i][1]
                        finalCourseData[2] = courseData[i][2]
                        finalCourseData[3] = courseData[i][3]
                        finalCourseData[4] = courseData[i][4]
                        finalCourseData[5] = courseData[i][5]
                        finalCourseData[6] = courseData[i][6]
                        finalCourseData[7] = courseData[i][7]

                        # 若此課程為開課中，此欄為零
                        if finalCourseData[5] == '0':
                            countExistCourse += 1

                        if courseData[i][8] is not None:
                            avgcourse = float(courseData[i][8])
                        else:
                            avgcourse = 0

                        studentWatchTemp = rs.watch_count
                        studentLoginTemp = rs.login_count
                        if studentWatchTemp + studentLoginTemp < avgcourse:
                            finalCourseData[11] = '待加強'

                        finalCourseData[8] = rs.login_count
                        finalCourseData[9] = rs.last_login
                        if finalCourseData[9] is None:
                            finalCourseData[9] = '無登入紀錄'

                        if rs.certificate == 1:
                            finalCourseData[10] = '是'
                        else:
                            finalCourseData[10] = '否'

                        if finalCourseData[6] != 'NA':
                            basiccourse.append(finalCourseData.copy())
                            i += 1
                            if finalCourseData[4] != '0':
                                readyendexist = True
                            if finalCourseData[5] != '0':
                                endexist = True
                            if finalCourseData[5] == '0':
                                startexist = True
                        else:
                            selfstudycourse.append(finalCourseData.copy())
                            i += 1
                            selfstudyexist = True

                    else:
                        # 資料庫內無此課程資料
                        noData += 1

                    countAllCourse += 1

                print(selfstudycourse)

                to_render['studentName'] = studentName
                to_render['basiccourse'] = basiccourse
                to_render['selfstudycourse'] = selfstudycourse
                to_render['selfstudyexist'] = selfstudyexist
                to_render['startexist'] = startexist
                to_render['endexist'] = endexist
                to_render['readyendexist'] = readyendexist

                courseLogin = [['' for i in range(4)] for i in range(10)]
                k = 0
                cursor.execute(
                    "SELECT course_name,course_id,`課程代碼`,login_count_month "
                    "FROM course_total_data_v2 "
                    "WHERE 統計日期 = %s order by login_count_month desc", [CoursefinalUpdate]
                )
                result = namedtuplefetchall(cursor)

                for rs in result:
                    if k < 10:
                        courseLogin[k][0] = rs.course_name
                        courseLogin[k][1] = rs.course_id
                        courseLogin[k][2] = '{:,.2f}'.format(rs.login_count_month)
                        courseLogin[k][3] = rs.課程代碼
                        k += 1
                    else:
                        break

                to_render['courseLogin'] = courseLogin

                totalcourse = countAllCourse - noData
                endcourse = totalcourse - countExistCourse
                startcourse = countExistCourse

                to_render['totalcourse'] = totalcourse
                to_render['startcourse'] = startcourse
                to_render['endcourse'] = endcourse

                # print(basiccourse)


            with connections['OpenEduDB'].cursor() as cursor:
                # edxapp.auth_user
                now = datetime.strftime(datetime.today(), '%Y-%m-%d')
                cursor.execute(
                    "SELECT count(*) as number FROM auth_user where last_login > %s", [now]
                )
                result = namedtuplefetchall(cursor)

                todayLogin = result[-1].number

                to_render['todayLogin'] = todayLogin

            to_render['IsLogin'] = 1
            print('student')
            return render(request, 'index.html', to_render)

        else:
            to_render['IsLogin'] = 2
            print('not login')
            return render(request, 'noLogin.html', to_render)





