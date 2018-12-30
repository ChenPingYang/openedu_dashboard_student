from django.shortcuts import render
from django.db import connections, DatabaseError
from collections import namedtuple
from use_function import namedtuplefetchall


# Create your views here.
def test1_view(request):
    to_render = {}
    student_name = 0

    if request.method == 'GET':
        pass

    if request.method == 'POST':
        pass


    with connections['ResultDB'].cursor() as cursor:
        # 搜尋所有修同一課程之學生
        course_id = 'course-v1:FCUx+2015015+201512'
        cursor.execute(
            "SELECT distinct(user_id) as uid FROM edxresult.student_total_data WHERE course_id = %s", [course_id]
        )
        result = namedtuplefetchall(cursor)

        n = 0
        for rs in result:
            to_render['ttt'] = type(result)

        print(type(result))

        to_render['course_id'] = course_id
        to_render['student_name'] = student_name

    return render(request, 'test1.html', to_render)
