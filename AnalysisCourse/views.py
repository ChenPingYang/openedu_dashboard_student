from django.shortcuts import render
from use_function import namedtuplefetchall, getCourseIDByCourseCode
from django.db import connections
import cookiegetter
import json


def analysis_course_view(request):
    request.encoding = 'utf-8'
    to_render = {}

    if request.method == 'GET':
        to_render = doGet(request)

    if request.method == 'POST':
        to_render = doGet(request)

    return render(request, 'AnalysisCourse.html', to_render)


def doGet(request):
    mode = request.GET.get('mode', False)
    course = request.GET.get('course', False)

    jsonArray_temp = []
    jsonArray_RegisteredPersons = []
    jsonArray_temp_1 = []
    jsonArray_active = []
    jsonArray_temp_2 = []
    jsonArray_answerRatio = []

    to_render = {}
    islogin = cookiegetter.isLogined(request)
    haveThisCourse = False

    if islogin:
        userEmail = cookiegetter.getEmail(request)
        userID = cookiegetter.getUserIDByEmail(userEmail)
        if cookiegetter.isTeacher(userID):
            teachersCourse = cookiegetter.get_Teacher_Courses(userID)
            for j in range(len(teachersCourse)):
                if getCourseIDByCourseCode(course) == teachersCourse[j]:
                    # 由於course_total_data裡面的欄位無法執行，於是以下的資料全改成從course_total_data_v2取出
                    with connections['ResultDB'].cursor() as cursor:
                        cursor.execute("select * from course_total_data_v2 where 課程代碼 = %s", [course])
                        result = namedtuplefetchall(cursor)

                        count = 0
                        courseCode = ''
                        courseId = ''
                        courseName = ''
                        totalRegisteredPersons = ''
                        age_17 = ''
                        age_18_25 = ''
                        age_26_ = ''
                        withDrew = ''
                        for rs in result:
                            courseCode = str(rs.課程代碼)
                            courseId = str(rs.course_id)  # 在course_total_data裡為 'id'
                            courseName = str(rs.course_name)  # 在這之下所有欄位名稱內有'_'的項目，在course_total_data裡全是'.'
                            totalRegisteredPersons = str(rs.註冊人數)
                            age_17 = str(rs.age_17)
                            age_18_25 = str(rs.age_18_25)
                            age_26_ = str(rs.age_26_)
                            withDrew = str(rs.退選人數)
                            count += 1

                        cursor.execute(
                            "SELECT count(*) as dataCount "
                            "FROM course_total_data_v2 "
                            "WHERE 課程代碼 = %s and 統計日期>=start_date and end_date>=統計日期 order by 統計日期 asc",
                            [course]
                        )
                        result = namedtuplefetchall(cursor)

                        count = result[-1].dataCount

                        RegisteredPersons = [0 for i in range(count)]
                        updateDate = ['' for i in range(count)]

                        cursor.execute(
                            "select 註冊人數 as RegisteredPersons,練習題作答率_活躍 as ActiveAnswerRatio,統計日期  as updateDate,活躍 as active,非活躍 as nonActive,練習題作答率  as answerRatio  "
                            "from course_total_data_v2 "
                            "where 課程代碼 = %s and 統計日期>=start_date and end_date>=統計日期 order by 統計日期 asc",
                            [course]
                        )
                        result = namedtuplefetchall(cursor)

                        jsonArray_temp.clear()
                        jsonArray_temp.append('日期')
                        jsonArray_temp.append('註冊人數')

                        jsonArray_temp_1.clear()
                        jsonArray_temp_1.append('日期')
                        jsonArray_temp_1.append('活躍人數')
                        jsonArray_temp_1.append('非活躍人數')

                        jsonArray_temp_2.append('日期')
                        jsonArray_temp_2.append('練習題作答率')
                        jsonArray_temp_2.append('練習題作答率_活躍')

                        jsonArray_RegisteredPersons.append(jsonArray_temp.copy())
                        jsonArray_active.append(jsonArray_temp_1.copy())
                        jsonArray_answerRatio.append(jsonArray_temp_2.copy())

                        i = 0
                        for rs in result:
                            RegisteredPersons[i] = int(rs.RegisteredPersons)
                            answerRatio = float(rs.answerRatio)
                            ActiveAnswerRatio = float(rs.ActiveAnswerRatio)
                            updateDate[i] = str(rs.updateDate)
                            active = int(rs.active)
                            nonActive = int(rs.nonActive)

                            jsonArray_temp.clear()
                            jsonArray_temp.append(updateDate[i])
                            jsonArray_temp.append(RegisteredPersons[i])
                            jsonArray_RegisteredPersons.append(jsonArray_temp.copy())

                            jsonArray_temp_1.clear()
                            jsonArray_temp_1.append(updateDate[i])
                            jsonArray_temp_1.append(active)
                            jsonArray_temp_1.append(nonActive)
                            jsonArray_active.append(jsonArray_temp_1.copy())

                            jsonArray_temp_2.clear()
                            jsonArray_temp_2.append(updateDate[i])
                            jsonArray_temp_2.append(answerRatio)
                            jsonArray_temp_2.append(ActiveAnswerRatio)
                            jsonArray_answerRatio.append(jsonArray_temp_2.copy())

                            i = i+1

                        weekChageRegisteredPersons = RegisteredPersons[count-1] - RegisteredPersons[count-2]

                        registeredPersons_Taiwan = None
                        registeredPersons_Foreign = None
                        education_master = None
                        education_Bachelo = None
                        education_Associate = None
                        education_senior = None
                        education_junior = None
                        education_primary = None
                        male = None
                        female = None

                        to_render['courseCode'] = courseCode
                        to_render['courseId'] = courseId
                        to_render['courseName'] = courseName
                        to_render['registeredPersons_Taiwan'] = registeredPersons_Taiwan
                        to_render['registeredPersons_Foreign'] = registeredPersons_Foreign
                        to_render['age_17'] = age_17
                        to_render['age_18_25'] = age_18_25
                        to_render['age_26_'] = age_26_
                        to_render['RegisteredPersons'] = RegisteredPersons
                        to_render['updateDate'] = updateDate
                        to_render['jsonArray_RegisteredPersons'] = json.dumps(jsonArray_RegisteredPersons)
                        to_render['jsonArray_active'] = json.dumps(jsonArray_active)
                        to_render['jsonArray_answerRatio'] = json.dumps(jsonArray_answerRatio)
                        to_render['weekChageRegisteredPersons'] = weekChageRegisteredPersons
                        to_render['withDrew'] = withDrew
                        to_render['education_master'] = education_master
                        to_render['education_Bachelo'] = education_Bachelo
                        to_render['education_Associate'] = education_Associate
                        to_render['education_senior'] = education_senior
                        to_render['education_junior'] = education_junior
                        to_render['education_primary'] = education_primary
                        to_render['totalRegisteredPersons'] = totalRegisteredPersons
                        to_render['mode'] = mode
                        to_render['male'] = male
                        to_render['female'] = female

                    with connections['SurveyDB'].cursor() as cursor:
                        checkBefore = False
                        checkAfter = False

                        to_render['IsLogin'] = 1
                        print('teacher')

                    haveThisCourse = True
                    break

            if haveThisCourse is False:
                print('not have')
                to_render['IsLogin'] = 2

        else:
            print('student')
            to_render['IsLogin'] = 2

    else:
        print('not login')
        to_render['IsLogin'] = 2

    return to_render









