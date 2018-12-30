from django.shortcuts import render
from use_function import namedtuplefetchall, getListAvg, removeExtremumDouble, getStudentLastlogin2
from django.db import connections
import cookiegetter
import json


# Create your views here.
def chart_data_view(request):
    request.encoding = 'utf-8'
    to_render = {}

    if request.method == 'GET':
        to_render = doGet(request)
        return render(request, 'detailAndChart.html', to_render)

    if request.method == 'POST':
        to_render = doGet(request)
        return render(request, 'detailAndChart.html', to_render)


def doGet(request):
    to_render = {}

    mode = request.GET.get('mode', False)
    course = request.GET.get('course', False)
    courseId = None
    endDate = None

    originalMax = ['' for i in range(5)]
    avgRadar = [0 for i in range(5)]
    avgRadar_percent = [0 for i in range(5)]
    maxRadar = [0 for i in range(5)]
    maxRadarSite = []
    RadarColumn = [0 for i in range(6)]
    RadarColumn_percent = [0 for i in range(5)]
    RadarColumnName = ['觀看次數', '觀看影片數', '討論區發文數', '問答題完成率', '問答題答對率']
    jsonArray = []
    jsonArray2 = []
    jsonArray_Charter = []
    jsonArray_watchtime = []
    jsonArray_studentgrade = []
    all_c_complete_rate = []
    all_complete_rate = []
    all_video_count = []
    all_forum_num = []
    all_watch_count = []

    islogin = cookiegetter.isLogined(request)
    haveThisCourse = False

    # 硬闖
    islogin = True
    if islogin:
        userEmail = cookiegetter.getEmail(request)
        userID = cookiegetter.getUserIDByEmail(userEmail)
        userID = '43394'
        with connections['ResultDB'].cursor() as cursor:
            # 取得課程id 課程名稱 課程統計日期
            cursor.execute(
                "SELECT start_date,統計日期,course_id,course_name "
                "FROM course_total_data_v2 "
                "WHERE 課程代碼 = %s", [course]
            )
            result = namedtuplefetchall(cursor)

            coursefinalUpdate = result[-1].統計日期
            courseid = result[-1].course_id
            courseName = result[-1].course_name
            startDate = result[-1].start_date

            # 取得學生統計日期
            cursor.execute("SELECT max(run_date) as max_date FROM student_total_data0912")
            result = namedtuplefetchall(cursor)
            studentfinalUpdate = result[-1].max_date

            # 取得每筆學生資料的平均值
            cursor.execute("SELECT watch_count,forum_num,video_count,complete_rate,c_complete_rate "
                           "FROM student_total_data0912 "
                           "WHERE course_id = %s AND run_date = %s", [courseid, studentfinalUpdate])
            result = namedtuplefetchall(cursor)

            forumtemp = completetemp = c_completetemp = videotemp = watchtemp = countpeople = 0
            forum_num = complete_rate = c_complete_rate = video_count = watch_count = 0

            for rs in result:
                watchtemp = float(rs.watch_count)
                forumtemp = float(rs.forum_num)
                videotemp = float(rs.video_count)
                completetemp = float(rs.complete_rate)
                c_completetemp = float(rs.c_complete_rate)
                watch_count = watch_count + watchtemp
                video_count = video_count + videotemp
                forum_num = forum_num + forumtemp
                complete_rate = complete_rate + completetemp
                c_complete_rate = c_complete_rate + c_completetemp
                countpeople = countpeople + 1

            watch_count = watch_count / countpeople
            video_count = video_count / countpeople
            forum_num = forum_num / countpeople
            complete_rate = complete_rate / countpeople
            c_complete_rate = c_complete_rate / countpeople

            # 取得該學生資料
            cursor.execute(
                "SELECT name,watch_count,video_count,forum_num,complete_rate,c_complete_rate "
                "FROM student_total_data0912 "
                "WHERE course_id = %s AND user_id = %s AND run_date = %s", [courseid, userID, studentfinalUpdate]
            )
            result = namedtuplefetchall(cursor)

            studentName = result[-1].name
            studentwatch_count = result[-1].watch_count
            studentvideo_count = result[-1].video_count
            studentforum_num = result[-1].forum_num
            studentcomplete_rate = result[-1].complete_rate
            studentc_complete_rate = result[-1].c_complete_rate

            courseCode = courseid
            dataFind = False
            watchvideocount = 1
            videoname = None

            # 取得該學生該課程觀看過影片名稱
            cursor.execute(
                "SELECT distinct(module_id) "
                "FROM video_watch_distinct "
                "WHERE user_id = %s and course_id = %s", [userID, courseid]
            )
            result = namedtuplefetchall(cursor)
            watchWhat = []
            for rs in result:
                watchWhat.append(rs.module_id)

            cursor.execute(
                "select sequential_name,video from course_material_data where course_id = %s", [courseid]
            )
            result = namedtuplefetchall(cursor)
            for rs in result:
                for i in range(len(watchWhat)):
                    if rs.video == watchWhat[i]:
                        jsonArray.clear()
                        watchCharter = str(rs.sequential_name)
                        jsonArray.append(watchCharter)
                        jsonArray_Charter.append(jsonArray.copy())
                        dataFind = True
                        break

            if dataFind is False:
                jsonArray.clear()
                watchCharter = '尚無觀看影片'
                jsonArray.append(watchCharter)
                jsonArray_Charter.append(jsonArray.copy())

            cursor.execute(
                "select total_grade_best,run_date "
                "from student_grade "
                "where course_id = %s AND user_id = %s order by run_date", [courseid, userID]
            )
            result = namedtuplefetchall(cursor)

            studentgrade = result[-1].total_grade_best
            graderundate = result[-1].run_date

            gradeData = []
            originalmaxgrade = 0

            # 					// 取得該課程每筆成績
            cursor.execute(
                "SELECT total_grade_best as tgb "
                "FROM student_grade "
                "WHERE course_id = %s AND run_date = %s order by total_grade_best", [courseid, graderundate]
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                gradeData.append(rs.tgb)

            maxgrade = 0
            avggrade = 0
            maxgrade = gradeData[-1]
            originalmaxgrade = gradeData[-1]
            avggrade = getListAvg(gradeData)

            chaptercount = [0 for i in range(20)]
            materialcount = [0 for i in range(20)]

            materialid = ['' for i in range(1000)]
            studentmaterialid = ['' for i in range(1000)]
            k = 0

            # 取得該課程每章節影片數
            cursor.execute(
                "SELECT count(chapter_name) as count_ch_name "
                "FROM course_material_data "
                "WHERE course_id = %s group by chapter_name order by chapter_name", [courseid]
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                chaptercount[k] = rs.count_ch_name
                k += 1

            chaptertotal = k
            k = 0

            # 取得該課程所有影片id
            cursor.execute("SELECT video "
                           "FROM course_material_data "
                           "WHERE course_id = %s order by chapter_name", [courseid])
            result = namedtuplefetchall(cursor)

            for rs in result:
                materialid[k] = rs.video
                k += 1

            numberOfQuestion = 0
            # 取得該課程測驗題數量
            cursor.execute("SELECT 測驗題數量 FROM course_total_data_v2 WHERE course_id = %s", [courseid])
            result = namedtuplefetchall(cursor)

            if len(result) != 0:
                numberOfQuestion = result[0].測驗題數量

            numberOfVideo = k

            # 取得該學生觀看過該課程
            k = 0
            cursor.execute(
                "SELECT distinct(module_id) "
                "FROM video_watch_distinct "
                "WHERE course_id = %s AND user_id = %s", [courseid, userID]
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                studentmaterialid[k] = rs.module_id
                k += 1

            studentwatch = [0 for i in range(20)]
            n = 0
            # 計算該學生該課程每章節
            for i in range(len(studentmaterialid)):
                for j in range(chaptertotal):
                    for m in range(chaptercount[j]):
                        if studentmaterialid[i] is not None and materialid[n] is not None:
                            if studentmaterialid[i] == materialid[n]:
                                studentwatch[j] += 1
                        n += 1
                n = 0

            chapterfinish = [0 for i in range(20)]
            chapterfinishcount = 0

            # 計算該學生該課程完成單元數量
            for i in range(chaptertotal):
                if studentwatch[i] == chaptercount[i]:
                    chapterfinish[i] = 1
                    chapterfinishcount += 1

            chapterpencent = 0
            chapterundonepencent = 0

            if chaptertotal != 0:
                chapterpencent = (chapterfinishcount / chaptertotal) * 100
                chapterundonepencent = ((chaptertotal - chapterfinishcount) / chaptertotal) * 100
            else:
                chapterundonepencent = 100

            encourage = [
                '學貴慎始，好的開始是成功的一半！',
                '千里之行，始於足下。好的開始是成功的一半！',
                'Keep it up. You’re on your way',
                '太棒了，學完了字詞，咱們可要一起更上一層樓囉！',
                'Constant dripping hollows the stone',
                '你超厲害！一下子就完成一半了。',
                '聚沙終會成塔，只要你願意！',
                '你怎麼如此厲害？怎樣都難不倒你！',
                '堅持是贏來勝利的不二法門，加油！',
                '鍥而不捨，金石可鏤',
                '見勝利的果實了嗎？再加把勁兒，摘下它！',
                'Stick to it! You are almost there',
                '恭喜你登頂！讓我奉上誰也帶不走的，屬於你的知識。',
            ]

            # 取得該課程資料最大值
            cursor.execute(
                "SELECT max(watch_count) as wc ,max(video_count) as vc ,max(forum_num) as fn ,max(complete_rate) as cr ,max(c_complete_rate) as ccr "
                "FROM student_total_data0912 "
                "WHERE course_id = %s AND run_date = %s", [courseid, studentfinalUpdate]
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                originalMax[0] = rs.wc
                originalMax[1] = rs.vc
                originalMax[2] = rs.fn
                originalMax[3] = rs.cr
                originalMax[4] = rs.ccr

            # 取得該課程每項資料
            cursor.execute(
                "SELECT watch_count,video_count,forum_num,complete_rate,c_complete_rate "
                "FROM student_total_data0912 "
                "WHERE course_id = %s AND run_date = %s", [courseid, studentfinalUpdate]
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                all_watch_count.append(rs.watch_count)
                all_video_count.append(rs.video_count)
                all_forum_num.append(rs.forum_num)
                all_complete_rate.append(rs.complete_rate)
                all_c_complete_rate.append(rs.c_complete_rate)

            totalCourceNumber = len(all_watch_count)

            # 取每項資料區間差距
            maxwatch = ((int(originalMax[0]) - 1) / 10 + 1)
            maxvideo = ((int(originalMax[1]) - 1) / 10 + 1)
            maxforum = ((int(originalMax[2]) - 1) / 10 + 1)
            maxcomplete = ((float(originalMax[3]) - 0.01) / 10 + 0.01)
            maxc_complete = ((float(originalMax[4]) - 0.01) / 10 + 0.01)

            maxgrade = (maxgrade - 1) / 10 + 1

            allstudentgrade = [0 for i in range(11)]
            allstudentwatch = [0 for i in range(11)]
            allstudentvideo = [0 for i in range(11)]
            allstudentforum = [0 for i in range(11)]
            allstudentcomplete = [0 for i in range(11)]
            allstudentc_complete = [0 for i in range(11)]

            # 計算每項資料區間數值
            for i in range(len(gradeData)-1, -1, -1):
                allstudentgrade[int(gradeData[i] / maxgrade)] += 1

            for i in range(len(all_watch_count)-1, -1, -1):
                allstudentwatch[int(all_watch_count[i] / maxwatch)] += 1
                allstudentvideo[int(all_video_count[i] / maxvideo)] += 1
                allstudentforum[int(all_forum_num[i] / maxforum)] += 1

                if all_complete_rate[i] >= 1:
                    allstudentcomplete[9] += 1
                else:
                    allstudentcomplete[int(all_complete_rate[i] / 0.1)] += 1

                if all_c_complete_rate[i] >= 1:
                    allstudentc_complete[9] += 1
                else:
                    allstudentc_complete[int(all_c_complete_rate[i] / 0.1)] += 1

            columnName_Grade = ['' for i in range(11)]
            columnName_Watch = ['' for i in range(11)]
            columnName_Video = ['' for i in range(11)]
            columnName_Forum = ['' for i in range(11)]
            columnName_Complete = ['' for i in range(11)]
            columnName_C_Complete = ['' for i in range(11)]

            range_ = 0

            # 命名長條圖區間值名稱
            for i in range(len(columnName_Grade)):
                columnName_Grade[i] = str(int(maxgrade) * i) + '~' + str(int(maxgrade) * (i+1) - 1)
                columnName_Watch[i] = str(int(maxwatch) * i) + '~' + str(int(maxwatch) * (i+1) - 1)
                columnName_Video[i] = str(int(maxvideo) * i) + '~' + str(int(maxvideo) * (i+1) - 1)
                columnName_Forum[i] = str(int(maxforum) * i) + '~' + str(int(maxforum) * (i+1) - 1)
                columnName_Complete[i] = str(int(range_)) + '~' + str(int(range_ + 10)) + '%'
                columnName_C_Complete[i] = str(int(range_)) + '~' + str(int(range_ + 10)) + '%'
                range_ = range_ + 10

            # 將每項資料去除極值並排序
            all_watch_count = removeExtremumDouble(all_watch_count)
            all_video_count = removeExtremumDouble(all_video_count)
            all_forum_num = removeExtremumDouble(all_forum_num)
            all_complete_rate = removeExtremumDouble(all_complete_rate)
            all_c_complete_rate = removeExtremumDouble(all_c_complete_rate)

            # 取得每項資料最大值
            if len(all_watch_count) != 0:
                maxRadar[0] = all_watch_count[-1]
                maxRadar[1] = all_video_count[-1]
                maxRadar[2] = all_forum_num[-1]
                maxRadar[3] = all_complete_rate[-1]
                maxRadar[4] = all_c_complete_rate[-1]

            # 取得每項資料平均
            avgRadar[0] = getListAvg(all_watch_count)
            avgRadar[1] = getListAvg(all_video_count)
            avgRadar[2] = getListAvg(all_forum_num)
            avgRadar[3] = getListAvg(all_complete_rate)
            avgRadar[4] = getListAvg(all_c_complete_rate)

            # 取得該學生該課程資料
            cursor.execute(
                "SELECT watch_count,video_count,forum_num,complete_rate,c_complete_rate,login_count "
                "FROM student_total_data0912 "
                "where run_date = %s AND course_id = %s AND user_id = %s", [studentfinalUpdate, courseid, userID]
            )
            result = namedtuplefetchall(cursor)

            RadarColumn[0] = result[-1].watch_count
            RadarColumn[1] = result[-1].video_count
            RadarColumn[2] = result[-1].forum_num
            RadarColumn[3] = result[-1].complete_rate
            RadarColumn[4] = result[-1].c_complete_rate
            RadarColumn[5] = result[-1].login_count

            # 登入次數
            if RadarColumn[5] >= 1:
                to_render['login_1_Img'] = 'img/login_1.png'
                to_render['login_1_GetOrNot'] = '已獲得'
                to_render['login_1_Percentage'] = '100'
            else:
                to_render['login_1_Img'] = 'img/noLogin_1.png'
                to_render['login_1_GetOrNot'] = '已登入' + str(RadarColumn[5]) + '次<br>未獲得'
                to_render['login_1_Percentage'] = '{:,.2f}'.format(RadarColumn[5] / 1 * 100)

            if RadarColumn[5] >= 5:
                to_render['login_5_Img'] = 'img/login_5.png'
                to_render['login_5_GetOrNot'] = '已獲得'
                to_render['login_5_Percentage'] = '100'
            else:
                to_render['login_5_Img'] = 'img/noLogin_5.png'
                to_render['login_5_GetOrNot'] = '已登入' + str(RadarColumn[5]) + '次<br>未獲得'
                to_render['login_5_Percentage'] = '{:,.2f}'.format(RadarColumn[5] / 5 * 100)

            if RadarColumn[5] >= 10:
                to_render['login_10_Img'] = 'img/login_10.png'
                to_render['login_10_GetOrNot'] = '已獲得'
                to_render['login_10_Percentage'] = '100'
            else:
                to_render['login_10_Img'] = 'img/noLogin_10.png'
                to_render['login_10_GetOrNot'] = '已登入' + str(RadarColumn[5]) + '次<br>未獲得'
                to_render['login_10_Percentage'] = '{:,.2f}'.format(RadarColumn[5] / 10 * 100)

            if RadarColumn[5] >= 20:
                to_render['login_20_Img'] = 'img/login_20.png'
                to_render['login_20_GetOrNot'] = '已獲得'
                to_render['login_20_Percentage'] = '100'
            else:
                to_render['login_20_Img'] = 'img/noLogin_20.png'
                to_render['login_20_GetOrNot'] = '已登入' + str(RadarColumn[5]) + '次<br>未獲得'
                to_render['login_20_Percentage'] = '{:,.2f}'.format(RadarColumn[5] / 20 * 100)

            # 觀看影片比率
            if numberOfVideo >= 1:
                to_render['numberOfVideo'] = 1

                if RadarColumn[0] >= 1:
                    to_render['watch_1_Img'] = 'img/watch_1.png'
                    to_render['watch_1_GetOrNot'] = '已獲得'
                    to_render['watch_1_Percentage'] = '100'
                else:
                    to_render['watch_1_Img'] = 'img/noWatch_1.png'
                    to_render['watch_1_GetOrNot'] = '已觀看' + str(RadarColumn[0]) + '次<br>未獲得'
                    to_render['watch_1_Percentage'] = '{:,.2f}'.format(RadarColumn[0] / 1 * 100)

                if RadarColumn[0] / numberOfVideo >= 0.2:
                    to_render['watch_20_Percentage_Img'] = 'img/watch_20_Percentage.png'
                    to_render['watch_20_Percentage_GetOrNot'] = '已獲得'
                    to_render['watch_20_Percentage_Percentage'] = '100'
                else:
                    to_render['watch_20_Percentage_Img'] = 'img/noWatch_20_Percentage.png'
                    to_render['watch_20_Percentage_GetOrNot'] = \
                        '已觀看' + '{:,.2f}'.format(RadarColumn[0] / numberOfVideo * 100) + '%<br>未獲得'
                    to_render['watch_20_Percentage_Percentage'] = \
                        '{:,.2f}'.format(((RadarColumn[0] / numberOfVideo) * 100) / 20 * 100)

                if RadarColumn[0] / numberOfVideo >= 0.5:
                    to_render['watch_50_Percentage_Img'] = 'img/watch_50_Percentage.png'
                    to_render['watch_50_Percentage_GetOrNot'] = '已獲得'
                    to_render['watch_50_Percentage_Percentage'] = '100'
                else:
                    to_render['watch_50_Percentage_Img'] = 'img/noWatch_50_Percentage.png'
                    to_render['watch_50_Percentage_GetOrNot'] = \
                        '已觀看' + '{:,.2f}'.format(RadarColumn[0] / numberOfVideo * 100) + '%<br>未獲得'
                    to_render['watch_50_Percentage_Percentage'] = \
                        '{:,.2f}'.format(((RadarColumn[0] / numberOfVideo) * 100) / 50 * 100)

                if RadarColumn[0] == numberOfVideo:
                    to_render['watch_100_Percentage_Img'] = 'img/watch_100_Percentage.png'
                    to_render['watch_100_Percentage_GetOrNot'] = '已獲得'
                    to_render['watch_100_Percentage_Percentage'] = '100'
                else:
                    to_render['watch_100_Percentage_Img'] = 'img/noWatch_100_Percentage.png'
                    to_render['watch_100_Percentage_GetOrNot'] = \
                        '已觀看' + '{:,.2f}'.format(RadarColumn[0] / numberOfVideo * 100) + '%<br>未獲得'
                    to_render['watch_100_Percentage_Percentage'] = \
                        '{:,.2f}'.format((RadarColumn[0] / numberOfVideo) * 100)

            # 討論次數
            if RadarColumn[2] >= 1:
                to_render['forum_1_Img'] = 'img/forum_1.png'
                to_render['forum_1_GetOrNot'] = '已獲得'
                to_render['forum_1_Percentage'] = '100'
            else:
                to_render['forum_1_Img'] = 'img/noForum_1.png'
                to_render['forum_1_GetOrNot'] = '已討論' + str(RadarColumn[2]) + '次<br>未獲得'
                to_render['forum_1_Percentage'] = '{:,.2f}'.format(RadarColumn[2] / 1 * 100)

            if RadarColumn[2] >= 3:
                to_render['forum_3_Img'] = 'img/forum_3.png'
                to_render['forum_3_GetOrNot'] = '已獲得'
                to_render['forum_3_Percentage'] = '100'
            else:
                to_render['forum_3_Img'] = 'img/noForum_3.png'
                to_render['forum_3_GetOrNot'] = '已討論' + str(RadarColumn[2]) + '次<br>未獲得'
                to_render['forum_3_Percentage'] = '{:,.2f}'.format(RadarColumn[2] / 3 * 100)

            if RadarColumn[2] >= 8:
                to_render['forum_8_Img'] = 'img/forum_8.png'
                to_render['forum_8_GetOrNot'] = '已獲得'
                to_render['forum_8_Percentage'] = '100'
            else:
                to_render['forum_8_Img'] = 'img/noForum_8.png'
                to_render['forum_8_GetOrNot'] = '已討論' + str(RadarColumn[2]) + '次<br>未獲得'
                to_render['forum_8_Percentage'] = '{:,.2f}'.format(RadarColumn[2] / 8 * 100)

            if RadarColumn[2] >= 15:
                to_render['forum_15_Img'] = 'img/forum_15.png'
                to_render['forum_15_GetOrNot'] = '已獲得'
                to_render['forum_15_Percentage'] = '100'
            else:
                to_render['forum_15_Img'] = 'img/noForum_15.png'
                to_render['forum_15_GetOrNot'] = '已討論' + str(RadarColumn[2]) + '次<br>未獲得'
                to_render['forum_15_Percentage'] = '{:,.2f}'.format(RadarColumn[2] / 15 * 100)

            # 作答次數
            if numberOfQuestion >= 1:
                to_render['uumberOfQuestion'] = 1

                if RadarColumn[3] > 0:
                    to_render['answer_1_Img'] = 'img/answer_1.png'
                    to_render['answer_1_GetOrNot'] = '已獲得'
                    to_render['answer_1_Percentage'] = '100'
                else:
                    to_render['answer_1_Img'] = 'img/noAnswer_1.png'
                    to_render['answer_1_GetOrNot'] = '已作答' + str(RadarColumn[3]) + '次<br>未獲得'
                    to_render['answer_1_Percentage'] = '{:,.2f}'.format(RadarColumn[3] / 1 * 100)

                if RadarColumn[3] >= 0.2:
                    to_render['answer_20_Percentage_Img'] = 'img/answer_20_Percentage.png'
                    to_render['answer_20_Percentage_GetOrNot'] = '已獲得'
                    to_render['answer_20_Percentage_Percentage'] = '100'
                else:
                    to_render['answer_20_Percentage_Img'] = 'img/noAnswer_20_Percentage.png'
                    to_render['answer_20_Percentage_GetOrNot'] = \
                        '已作答' + '{:,.2f}'.format(RadarColumn[3] * 100) + '%<br>未獲得'
                    to_render['answer_20_Percentage_Percentage'] = '{:,.2f}'.format(RadarColumn[3] / 0.2 * 100)

                if RadarColumn[3] >= 0.5:
                    to_render['answer_50_Percentage_Img'] = 'img/answer_50_Percentage.png'
                    to_render['answer_50_Percentage_GetOrNot'] = '已獲得'
                    to_render['answer_50_Percentage_Percentage'] = '100'
                else:
                    to_render['answer_50_Percentage_Img'] = 'img/noAnswer_50_Percentage.png'
                    to_render['answer_50_Percentage_GetOrNot'] = \
                        '已作答' + '{:,.2f}'.format(RadarColumn[3] * 100) + '%<br>未獲得'
                    to_render['answer_50_Percentage_Percentage'] = '{:,.2f}'.format(RadarColumn[3] / 0.5 * 100)

                if RadarColumn[3] >= 1:
                    to_render['answer_100_Percentage_Img'] = 'img/answer_100_Percentage.png'
                    to_render['answer_100_Percentage_GetOrNot'] = '已獲得'
                    to_render['answer_100_Percentage_Percentage'] = '100'
                else:
                    to_render['answer_100_Percentage_Img'] = 'img/noAnswer_100_Percentage.png'
                    to_render['answer_100_Percentage_GetOrNot'] = \
                        '已作答' + '{:,.2f}'.format(RadarColumn[3] * 100) + '%<br>未獲得'
                    to_render['answer_100_Percentage_Percentage'] = '{:,.2f}'.format(RadarColumn[3] * 100)

            # 計算雷達圖數值
            RadarData = []
            Data = ['' for i in range(5)]

            for i in range(len(avgRadar_percent)):
                if maxRadar[i] == 0:
                    RadarColumn_percent[i] = 0
                    avgRadar_percent[i] = 0
                else:
                    RadarColumn_percent[i] = RadarColumn[i] / maxRadar[i] * 100
                    avgRadar_percent[i] = avgRadar[i] / maxRadar[i] * 100
                if avgRadar_percent[i] > 100:
                    avgRadar_percent[i] = 100
                if RadarColumn_percent[i] > 100:
                    RadarColumn_percent[i] = 100

                Data[0] = RadarColumnName[i]
                Data[1] = '{:,.2f}'.format(float(originalMax[i]))
                Data[2] = '{:,.2f}'.format(float(originalMax[i]))
                Data[3] = '{:,.2f}'.format(avgRadar[i]) + '(' + '{:,.2f}'.format(avgRadar_percent[i]) + '%)'
                Data[4] = '{:,.2f}'.format(RadarColumn[i]) + '(' + '{:,.2f}'.format(RadarColumn_percent[i]) + '%)'
                RadarData.append(Data.copy())

            cursor.execute(
                "SELECT user_id "
                "FROM student_total_data0912 "
                "WHERE run_date = %s AND course_id = %s", [studentfinalUpdate, courseid]
            )
            result = namedtuplefetchall(cursor)

            studentID = [None for i in range(7000)]
            c = 0
            for rs in result:
                studentID[c] = rs.user_id
                c += 1

            courseIDcount = [0 for i in range(10000)]

            studentcourse = []
            studentcourseid = [None for i in range(10000)]

            cursor.execute(
                "SELECT count(course_id) as a,course_id "
                "FROM student_total_data0912 "
                "WHERE user_id in (SELECT user_id FROM student_total_data0912 where course_id = '" + courseid +
                "' and  run_date = '" + studentfinalUpdate + "') and run_date ='" + studentfinalUpdate +
                "' group by course_id "
            )
            result = namedtuplefetchall(cursor)

            c = 0
            for rs in result:
                studentcourseid[c] = rs.course_id
                courseIDcount[c] = rs.a
                c += 1

            recommandcourseid = [None for i in range(1000)]

            max_value = 0
            max_ptr = [0 for i in range(5)]
            s = 0
            c = 0

            for i in range(6):
                for j in range(len(courseIDcount)):
                    if courseIDcount[j] > max_value:
                        max_value = courseIDcount[j]
                        max_ptr[s] = j

                if i != 0:
                    recommandcourseid[c] = studentcourseid[max_ptr[s]]
                    courseIDcount[max_ptr[s]] = 0
                    max_value = 0
                    s += 1
                    c += 1
                else:
                    courseIDcount[max_ptr[s]] = 0
                    max_value = 0

            recommandcoursename = [None for i in range(1000)]

            for i in range(c):
                cursor.execute("SELECT course_name "
                               "FROM course_total_data_v2 "
                               "WHERE course_id = %s", [recommandcourseid[i]])
                result = namedtuplefetchall(cursor)

                recommandcoursename[i] = result[i].course_name

            # 取得該學生最後登入及登入次數
            logindata = getStudentLastlogin2(courseid, userID)
            temp4 = ['' for i in range(2)]
            temp4[0] = logindata[0]
            temp4[1] = logindata[1]

            to_render['RadarColumn'] = RadarColumn
            to_render['studentName'] = studentName
            to_render['studentgrade'] = studentgrade
            to_render['jsonArray_watchtime'] = json.dumps(jsonArray_watchtime)
            to_render['jsonArray_Charter'] = json.dumps(jsonArray_Charter)
            to_render['RadarData'] = RadarData
            to_render['course'] = course
            to_render['courseCode'] = courseCode
            to_render['courseId'] = courseId
            to_render['courseName'] = courseName
            to_render['startDate'] = startDate
            to_render['endDate'] = endDate
            to_render['temp4'] = temp4
            to_render['recommandcourseid'] = recommandcourseid
            to_render['studentID'] = studentID
            to_render['studentcourseid'] = studentcourseid
            to_render['recommandcoursename'] = recommandcoursename
            to_render['studentcourse'] = studentcourse
            to_render['chapterpencent'] = chapterpencent
            to_render['chapterundonepencent'] = chapterundonepencent

            courseNumberOfVideos = averageLengthOfVideos = numberOfTestQuestions = answerRatio = numbersOfForum = None
            numbersOfPostInForum = forumParticiPationRates = duration_week = totalRegisteredPersons = None

            to_render['courseNumberOfVideos'] = courseNumberOfVideos
            to_render['averageLengthOfVideos'] = averageLengthOfVideos
            to_render['numberOfTestQuestions'] = numberOfTestQuestions
            to_render['answerRatio'] = answerRatio
            to_render['numbersOfForum'] = numbersOfForum
            to_render['numbersOfPostInForum'] = numbersOfPostInForum
            to_render['forumParticiPationRates'] = forumParticiPationRates
            to_render['duration_week'] = duration_week
            to_render['watch_count'] = watch_count
            to_render['video_count'] = video_count
            to_render['forum_num'] = forum_num
            to_render['complete_rate'] = complete_rate
            to_render['c_complete_rate'] = c_complete_rate
            to_render['studentwatch_count'] = studentwatch_count
            to_render['studentvideo_count'] = studentvideo_count
            to_render['studentforum_num'] = studentforum_num
            to_render['studentcomplete_rate'] = studentcomplete_rate
            to_render['studentc_complete_rate'] = studentc_complete_rate
            to_render['totalRegisteredPersons'] = totalRegisteredPersons
            to_render['mode'] = mode
            to_render['originalavgwatch'] = '{:,.2f}'.format(avgRadar[0])
            to_render['originalavgvideo'] = '{:,.2f}'.format(avgRadar[1])
            to_render['originalavgforum'] = '{:,.2f}'.format(avgRadar[2])
            to_render['originalavgcomplete'] = '{:,.2f}'.format(avgRadar[3])
            to_render['originalavgc_complete'] = '{:,.2f}'.format(avgRadar[4])
            to_render['allstudentgrade'] = allstudentgrade
            to_render['allstudentwatch'] = allstudentwatch
            to_render['allstudentvideo'] = allstudentvideo
            to_render['allstudentforum'] = allstudentforum
            to_render['allstudentcomplete'] = allstudentcomplete
            to_render['allstudentc_complete'] = allstudentc_complete
            to_render['columnName_Grade'] = columnName_Grade
            to_render['columnName_Watch'] = columnName_Watch
            to_render['columnName_Video'] = columnName_Video
            to_render['columnName_Forum'] = columnName_Forum
            to_render['columnName_Complete'] = columnName_Complete
            to_render['columnName_C_Complete'] = columnName_C_Complete
            to_render['chapterfinish'] = chapterfinish
            to_render['studentmaterialid'] = len(studentmaterialid)
            to_render['studentwatch'] = studentwatch
            to_render['chaptercount'] = chaptercount
            to_render['chapterfinishcount'] = chapterfinishcount
            to_render['encourage'] = encourage
            to_render['originalmaxgrade'] = originalmaxgrade
            to_render['avggrade'] = '{:,.2f}'.format(avggrade)

            to_render['avg_watch_count'] = avgRadar_percent[0]
            to_render['avg_video_count'] = avgRadar_percent[1]
            to_render['avg_forum_num'] = avgRadar_percent[2]
            to_render['avg_complete_rate'] = avgRadar_percent[3]
            to_render['avg_c_complete_rate'] = avgRadar_percent[4]
            to_render['originalMax'] = originalMax
            to_render['student_watch_count'] = RadarColumn_percent[0]
            to_render['student_video_count'] = RadarColumn_percent[1]
            to_render['student_forum_num'] = RadarColumn_percent[2]
            to_render['student_complete_rate'] = RadarColumn_percent[3]
            to_render['student_c_complete_rate'] = RadarColumn_percent[4]
            to_render['courseid'] = courseid

        haveThisCourse = True
        if haveThisCourse is False:
            print('not have')
            to_render['IsLogin'] = 2
            return to_render

        to_render['IsLogin'] = 1
        print('teacher')
        return to_render

    else:
        print('not login')
        to_render['IsLogin'] = 2
        return to_render














