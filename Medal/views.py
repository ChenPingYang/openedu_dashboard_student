from django.shortcuts import render
from use_function import namedtuplefetchall, getStudentLastlogin
from django.db import connections
import cookiegetter


def medal_view(request):
    request.encoding = 'utf-8'
    to_render = {}

    if request.method == 'GET':
        doGet(request)
        return render(request, 'medal.html', to_render)

    if request.method == 'POST':
        doGet(request)
        return render(request, 'medal.html', to_render)


def doGet(request):
    mode = request.GET.get('mode', None)
    course = request.GET.get('course', None)

    to_render = {}
    islogin = cookiegetter.isLogined(request)
    haveThisCourse = False

    if islogin is True:
        userEmail = cookiegetter.getEmail(request)
        userID = cookiegetter.getUserIDByEmail(userEmail)

        with connections['ResultDB'].cursor() as cursor:
            pass

        haveThisCourse = True
        if haveThisCourse is False:
            print('noHave')
            to_render['IsLogin'] = 2
            return to_render

        to_render['IsLogin'] = 1
        print('teacher')
        return to_render

    else:
        print('not login')
        to_render['IsLogin'] = 2
        return to_render

