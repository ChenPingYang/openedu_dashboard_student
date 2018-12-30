# coding=utf-8

from django.shortcuts import render
import pymysql
from django.conf import settings
from django.db import DatabaseError, connections
from use_function import namedtuplefetchall
import json

# Create your views here.

_COOKIE_NAME_OPENEDU_USER_INFO = 'openedu-user-info'
_COOKIE_NAME_EDX_USER_INFO = 'edx-user-info'


def get_connection():
    with connections['OpenEduDB'].cursor() as cursor:
        return cursor


# 取得Email，有則回傳Email；否則回傳None
def getEmail(request):
    email = None
    if request.COOKIES is not None:
        for key, value in request.COOKIES.items():
            cookie_name = key
            if cookie_name == _COOKIE_NAME_OPENEDU_USER_INFO or cookie_name == _COOKIE_NAME_EDX_USER_INFO:
                username = value
                username = username.replace('054 ', ', ')
                dict_ = dict(username)
                email = getUserEmailByUserName(dict_['username'])

    return email


# 確認是否已經登入
def isLogined(request):
    if request.COOKIES is not None:
        for key in request.COOKIES.keys():
            cookiename = key
            if cookiename == _COOKIE_NAME_OPENEDU_USER_INFO or cookiename == _COOKIE_NAME_EDX_USER_INFO:
                return True
    return False


# 透過Userid取得Email
def getUserEmailById(userid):
    # edxapp.auth_user
    sql = 'SELECT email FROM auth_user WHERE id = %s'
    cursor = get_connection()
    try:
        cursor.execute(sql, userid)
        result = namedtuplefetchall(cursor)
        email = result[-1].email
        return email

    except DatabaseError:
        print('Error')

    finally:
        cursor.close()

    return None


# 透過UserName來取得email
def getUserEmailByUserName(username):
    # edxapp.auth_user
    sql = 'SELECT email FROM auth_user WHERE username = %s'
    cursor = get_connection()
    try:
        cursor.execute(sql, username)
        result = namedtuplefetchall(cursor)
        email = result[-1].enail
        return email
    except DatabaseError:
        print('Error')
    finally:
        cursor.close()

    return None


# 透過Email取得UserID
def getUserIDByEmail(email):
    # edxapp.auth_user
    sql = 'SELECT id FROM auth_user WHERE email = %s'
    cursor = get_connection()

    try:
        cursor.execute(sql, email)
        result = namedtuplefetchall(cursor)
        userid = result[-1].id
        # 測試用 記得刪除
        userID = '7692'
        return userid
    except Exception:
        print('Error')
    finally:
        cursor.close()
    return None


# 判斷是否是老師
def isTeacher(userid):
    # edxapp.student_courseaccessrole
    sql = 'SELECT id FROM student_courseaccessrole WHERE role = "instructor" AND user_id = %s'
    cursor = get_connection()

    try:
        cursor.execute(sql, userid)
        result = namedtuplefetchall(cursor)
        if result is not None:
            isteacher = True
            return isteacher
    except DatabaseError:
        print('Error')
    finally:
        cursor.close()

    return None


# 取得老師開的課
def get_Teacher_Courses(userid):
    # edxapp.student_courseaccessrole
    connection = None
    sql = 'SELECT course_id FROM student_courseaccessrole WHERE role = "instructor" AND user_id = %s'
    cursor = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, userid)
        result = namedtuplefetchall(cursor)
        return result
    except Exception:
        print('Error')
    finally:
        cursor.close()

    return None

