import decimal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import namedtuple
from django.db import connections
from django.db import DatabaseError
import math
import json


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def getRegisteredPersonsAndCourseCodeByCourseID(courseID):
    output = [None for i in range(2)]
    with connections['ResultDB'].cursor() as cursor:
        cursor.execute("select 註冊人數,course_id,課程代碼 from course_total_data_v2 WHERE course_id = %s", [courseID])
        result = namedtuplefetchall(cursor)

        for rs in result:
            if rs.course_id == courseID:
                output[0] = rs.註冊人數
                output[1] = rs.課程代碼
    return output


def getCourseIDByCourseCode(CourseCode):
    courseID = ''
    with connections['ResultDB'].cursor() as cursor:
        cursor.execute("select 課程代碼,course_id from course_total_data_v2 ")
        result = namedtuplefetchall(cursor)

        for rs in result:
            if rs.課程代碼 == CourseCode:
                courseID = rs.course_id

    return courseID


def getChooseDate(choose, S_startDate):
    now = datetime.today()
    if choose is not None:
        if choose == 'A':
            now = now + relativedelta(months = -1)
        elif choose == 'B':
            now = now + relativedelta(months = -6)
        elif choose == 'C':
            now = now + relativedelta(years = -1)
        elif choose == 'D':
            now = now + relativedelta(years = -20)
        return now.strftime('%Y-%m-%d')

    else:
        S_startDate = datetime.strptime(S_startDate, '%Y-%m-%d')
        return S_startDate.strftime('%Y-%m-%d')


def getListAvg(data):
    sum_ = 0
    for i in range(len(data) - 1):
        sum_ = sum_ + data[i]

    return sum_/len(data)


# admin和instructor兩個版本中的removeExtremumInt()及removeExtremumDouble()是差不多的，故結合成為removeExtremum()
def removeExtremumInt(data):
    absoluteDistance = []
    newData = []
    count = 0

    # 取得中位數
    if len(data) % 2 == 1:
        Median = data[(len(data)+1)/2]
    else:
        Median = (data[len(data)/2] + data[len(data)/2+1]) / 2

    number = []
    # 取得所有資料與中位數的距離絕對值
    for i in range(len(data)):
        number.clear()
        number.append(i)
        number.append(abs(Median - data[i]))
        absoluteDistance.append(number)

    # 排序
    absoluteDistance.sort(key=lambda x: x[1])

    # 取得所有資料與中位數的距離絕對值的中位數
    if len(absoluteDistance) % 2 == 1:
        MAD = absoluteDistance[int((len(absoluteDistance)+1)/2)][1]
    else:
        MAD = (absoluteDistance[int(len(absoluteDistance)/2)][1] + absoluteDistance[int(len(absoluteDistance)/2+1)][1])/2

    # 若MAD為零，抓一個最小的值取代MAD
    if MAD == 0:
        for i in range(len(absoluteDistance)):
            if data[i] != 0:
                MAD = absoluteDistance[i][1]
                break

    # 判斷Z分數，大於2.24移除
    for i in range(len(data)):
        Z = absoluteDistance[i][1] / (MAD/0.6745)
        if Z < 2.24:
            newData.append(data[absoluteDistance[i][0]])
            if count < absoluteDistance[i][0]:
                count = absoluteDistance[i][0]

    # 排序
    newData.sort()

    return newData


# admin和instructor兩個版本中的removeExtremumInt()及removeExtremumDouble()是差不多的，故結合成為removeExtremum()
def removeExtremumDouble(data):
    absoluteDistance = []
    newData = []
    count = 0
    existvalue = False

    for i in range(len(data)):
        if data[i] != 0:
            existvalue = True

    if existvalue is False:
        return data

    data.sort()

    # 取得中位數
    if len(data) % 2 == 1:
        Median = data[int((len(data) + 1) / 2)]
    else:
        Median = (data[int(len(data) / 2)] + data[int(len(data) / 2 + 1)]) / 2

    # 取得所有資料與中位數的距離絕對值
    number = []
    for i in range(len(data)):
        number.clear()
        number.append(i)
        number.append(abs(Median - data[i]))
        absoluteDistance.append(number.copy())
    # 排序
    absoluteDistance.sort(key=lambda x: x[1])

    # 取得所有資料與中位數的距離絕對值的中位數
    if len(absoluteDistance) % 2 == 1:
        MAD = absoluteDistance[int((len(absoluteDistance) + 1) / 2)][1]
    else:
        MAD = (absoluteDistance[int(len(absoluteDistance) / 2)][1] +
               absoluteDistance[int(len(absoluteDistance) / 2 + 1)][1]) / 2

    # 若MAD為零，抓一個最小的值取代MAD
    if MAD == 0:
        for i in range(len(absoluteDistance)):
            if data[i] != 0:
                MAD = absoluteDistance[i][1]
                break

    # 判斷Z分數，大於2.24移除
    if MAD == 0:
        for i in range(len(data)):
            newData.append(data[int(absoluteDistance[i][0])])
    else:
        for i in range(len(data)):
            Z = absoluteDistance[i][1] / (MAD / 0.6745)
            if Z < 2.24:
                newData.append(data[absoluteDistance[i][0]])
                count = i

    newData.sort()
    return newData


def getStudentLastlogin2(courseID, userID):
    output = ['' for i in range(2)]
    with connections['ResultDB'].cursor() as cursor:
        cursor.execute("select last_login,login_count "
                       "from student_total_data0912 "
                       "WHERE user_id = %s AND course_id = %s", [userID, courseID])
        result = namedtuplefetchall(cursor)

        for rs in result:
            output[0] = rs.login_count
            output[1] = rs.last_login
            if output[1] is None:
                output[1] = '無登入紀錄'

    return output


def getStudentLastlogin(userid):
    # edxapp.auth_user
    with connections['OpenEduDB'].cursor() as cursor:
        cursor.execute("select date_joined from auth_user WHERE id = %s", [userid])
        result = namedtuplefetchall(cursor)

        # for test 記得刪除
        output = '2017-04-25 08:45:48.743721'
        for rs in result:
            output = rs.date_joined

    return output
