from use_function import namedtuplefetchall, getChooseDate
from django.db import connections


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
            "SELECT distinct(course_id), course_name,課程代碼 FROM course_total_data_v2"
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
            if c < 5:
                if check is not None:
                    temp.append(check[0])
                    temp.append(check[1])
                    temp.append(check[2])
                    temp.append(value)
                    output.append(temp.copy())
                    c += 1

            else:
                break

        cursor.execute("SELECT course_name FROM course_total_data_v2 WHERE course_id = %s", [course_id])
        result = namedtuplefetchall(cursor)

        CourseName = result[-1].course_name

        to_render['data'] = output
        to_render['CourseName'] = CourseName

        return to_render


def ExistorNot(cid, course_data):
    exist = None
    for cd in course_data:
        if cd.course_id == cid:
            exist = [cd.課程代碼, cd.course_id, cd.course_name]
            break

    return exist
