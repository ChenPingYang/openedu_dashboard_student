from django.shortcuts import render
from datetime import datetime, timedelta, date
from use_function import namedtuplefetchall, getChooseDate
from django.db import connections
import cookiegetter
import json


def forum_data_view(request):
    request.encoding = 'utf-8'

    if request.method == "GET":
        to_render = {}
        islogin = cookiegetter.isLogined(request)
        list_ = []

        if islogin is True:
            userEmail = cookiegetter.getEmail(request)
            userID = cookiegetter.getUserIDByEmail(userEmail)
            if cookiegetter.isTeacher(userID):
                teachersCourse = cookiegetter.get_Teacher_Courses(userID)

                with connections['ResultDB'].cursor() as cursor:
                    # 取得最新統計日期
                    # 原Java版式搜尋course_total_data，但因為field name有問題因此改用course_total_data_v2
                    # 兩者間域名域名有些不同，如id -> course_id, 其餘包含.之域名全改為_
                    cursor.execute("SELECT 統計日期 "
                                   "FROM edxresult.course_total_data_v2")
                    result = namedtuplefetchall(cursor)
                    finalUpdate = result[-1].統計日期

                    # 取得老師擁有的課程資料
                    cursor.execute("SELECT * "
                                   "FROM edxresult.course_total_data_v2 "
                                   "WHERE 統計日期 = %s order by course_id", [finalUpdate])
                    result = namedtuplefetchall(cursor)
                    temp_site = 0
                    data = []
                    for rs in result:
                        for i in range(len(teachersCourse)):
                            if rs.course_id == teachersCourse[i]:
                                data.clear()
                                data.append(rs.課程代碼)
                                data.append(rs.course_id)
                                data.append(rs.course_name)
                                data.append(rs.討論區討論次數)
                                data.append(rs.討論區參與度)
                                list_.append(data.copy())

                    # 回傳要呈現的資料
                    to_render['result'] = list_
                    # 預設日期範圍的下拉式選單，預設值為1:-請選擇-
                    to_render['select'] = 1
                    to_render['finalUpdate'] = "最後資料更新時間 : " + finalUpdate

                to_render['IsLogin'] = 1
                print('teacher')
                return render(request, '3_ForumData.html', to_render)

            else:
                print("student")
                to_render['IsLogin'] = 2
                return render(request, '3_ForumData.html', to_render)

        else:
            print('not login')
            to_render['IsLogin'] = 2
            return render(request, '3_ForumData.html', to_render)

    if request.method == 'POST':
        to_render = {}

        list_ = []
        islogin = cookiegetter.isLogined(request)

        if islogin is True:
            userEmail = cookiegetter.getEmail(request)
            userID = cookiegetter.getUserIDByEmail(userEmail)
            if cookiegetter.isTeacher(userID):
                teachersCourse = cookiegetter.get_Teacher_Courses(userID)
                choose = request.POST.get('choose', None)  # 使用者選擇範圍
                S_startDate = request.POST.get('startDate', None)  # 使用者選擇日期
                D_userChooseStartDate = getChooseDate(choose, S_startDate)
                if choose is None:
                    to_render['select'] = 1
                    to_render['selectStartDate'] = S_startDate
                else:
                    to_render['select'] = choose
                    to_render['selectStartDate'] = '年/月/日'

                with connections['ResultDB'].cursor() as cursor:
                    # 取得統計日期，方式是取得最後一筆資料，此筆資料的統計日期就是最新日期
                    # 原Java版式搜尋course_total_data，但因為field name有問題因此改用course_total_data_v2
                    # 兩者間域名域名有些不同，如id -> course_id, 其餘包含.之域名全改為_
                    cursor.execute("select 統計日期 from course_total_data_v2")
                    result = namedtuplefetchall(cursor)
                    finalUpdate = result[-1].統計日期

                    # 依據使用者選擇的日期，取得資料
                    cursor.execute(
                        "SELECT * "
                        "FROM course_total_data_v2 "
                        "WHERE 統計日期 = %s AND start_date > %s", [finalUpdate, D_userChooseStartDate]
                    )
                    result = namedtuplefetchall(cursor)

                    data = []
                    for rs in result:
                        for i in range(len(teachersCourse)):
                            if rs.course_id == teachersCourse[i]:
                                data.clear()
                                data.append(rs.課程代碼)
                                data.append(rs.course_id)
                                data.append(rs.course_name)
                                data.append(rs.討論區討論次數)
                                data.append(rs.討論區參與度)
                                list_.append(data.copy())

                    to_render['result'] = list_
                    to_render['finalUpdate'] = '最後資料更新時間 : ' + finalUpdate

                to_render['IsLogin'] = 1
                print('teacher')
                return render(request, '3_ForumData.html', to_render)

            else:
                to_render['IsLogin'] = 2
                print('student')
                return render(request, '3_ForumData.html', to_render)

        else:
            to_render['IsLogin'] = 2
            print('not login')
            return render(request, '3_ForumData.html', to_render)


