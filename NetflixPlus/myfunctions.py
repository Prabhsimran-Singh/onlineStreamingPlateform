import smtplib
import string
from datetime import date, timedelta, datetime
from pyexpat import model
from random import randint

from Tools.demo import vector
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from email.message import EmailMessage
from django.core.files.storage import FileSystemStorage
from django.shortcuts import *
from django.http import *
import pymysql
from django.views.decorators.csrf import csrf_exempt
import calendar

def find(string):
    ob = SentimentIntensityAnalyzer()
    result = ob.polarity_scores(string)

    if result['compound'] >= 0 :
        return 1
    else:
        return -1

@csrf_exempt
def addreview(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")

    review = request.POST["txtdescription"]
    viewtype = request.POST["type"]
    id = request.POST["id"]
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    review = review.rstrip()
    review = review.lstrip()
    nature = find(review)
    s = "SELECT  * FROM `userreview`  "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    if cr.rowcount == 0:
        s = "INSERT INTO `userreview`( `userid`, `id`, `type`, `review`, `nature`) VALUES (%s,%s,%s,%s,%s)"
        val = (str(request.session["userid"]), str(id), viewtype, review, str(nature))
        cr = conn.cursor()
        cr.execute(s,val)
        conn.commit()

    flag = "true"
    for r in result1:

        if int(r[2]) == int(id) and int(r[1]) == int(request.session["userid"] and r[3] == "movie"):

            return redirect(request.META.get('HTTP_REFERER'))
            break
        elif int(r[2]) == int(id) and int(r[1]) == int(request.session["userid"] and r[3] == "show"):

            return redirect(request.META.get('HTTP_REFERER'))
            break
        else:
            flag = "false"

    if flag == "false":
        s = "INSERT INTO `userreview`( `userid`, `id`, `type`, `review`, `nature`) VALUES (%s,%s,%s,%s,%s)"
        val = (str(request.session["userid"]), str(id), viewtype, review, str(nature))
        cr = conn.cursor()
        cr.execute(s, val)
        conn.commit()

    return redirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
def editreview(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")

    review = request.POST["txtdescription"]
    viewtype = request.POST["type"]
    id = request.POST["id"]
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    review = review.rstrip()
    review = review.lstrip()
    nature = find(review)
    s = "SELECT  * FROM `userreview`  "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    for r in result1:



        if int(r[2]) == int(id) and int(r[1]) == int(request.session["userid"]) and r[3] == str(viewtype) :

            s = "UPDATE `userreview` SET `review`=%s, `nature`=%s WHERE `reviewid`='" + str(r[0]) + "'"
            val = ( review, str(nature))
            cr = conn.cursor()
            cr.execute(s,val)
            conn.commit()
            return redirect(request.META.get('HTTP_REFERER'))



    return redirect(request.META.get('HTTP_REFERER'))


def deletereview(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    id = request.GET["reviewid"]
    s = "DELETE FROM `userreview` WHERE `reviewid`='" + id + "'"

    cr = conn.cursor()
    cr.execute(s)
    conn.commit()
    return redirect(request.META.get('HTTP_REFERER'))


def home_page(request):
    return render(request, "startpage.html")


def page_1_2(request):
    return render(request, "page_1.1.html")


@csrf_exempt
def page_3(request):
    plan = request.POST["txtplan"];
    request.session["userplan"] = plan
    return render(request, "page_create_account.html", {"d": " "})


@csrf_exempt
def page_4(request):
    if not "userplan" in request.session:
        return HttpResponseRedirect("page3")
    email = request.POST["txtemail"]
    request.session["username"] = request.POST["txtname"]
    request.session["userphone"] = request.POST["txtphone"]
    request.session["useremail"] = email
    request.session["userpassword"] = request.POST["txtpassword"]

    planname = request.session["userplan"]
    amount = ""
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    s = "SELECT * FROM `user` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    for r in result:
        if (r[3] == email):
            return render(request, 'page_create_account.html', {"d": "User already exists. Kindly use Sign In"});
            break;

    s = "SELECT * FROM `plans` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    for r in result:
        if (r[1] == planname):
            amount = r[2]
            break;

    return render(request, "userpayment.html", {"d": amount})


@csrf_exempt
def user_payment(request):
    if not "username" in request.session:
        return HttpResponseRedirect("page3")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    name = request.session["username"]
    phone = request.session["userphone"]
    email = request.session["useremail"]
    password = request.session["userpassword"]

    cardname = request.POST["txtname"]
    cardnumber = request.POST["txtcardnumber"]
    cardcode = request.POST["txtcode"]
    carddate = request.POST["txtdate"]
    userid = ""
    paymentid = ""
    planid = ""
    amount = ""
    today = date.today()

    days_in_month = calendar.monthrange(today.year, today.month)[1]
    enddate = today + timedelta(days=days_in_month)

    planname = request.session["userplan"]

    s1 = "INSERT INTO `user`( `Name`, `Phone`, `Email`, `Password`) VALUES ('" + name + "','" + phone + "','" + email + "','" + password + "')"
    cr1 = conn.cursor()
    cr1.execute(s1)
    conn.commit()

    s = "SELECT * FROM `user` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    for r in result:
        if (r[3] == email):
            userid = r[0]
            request.session["userid"]=r[0]

            break;

    s1 = "INSERT INTO `paymentdetails`( `userid`, `Cardholder name`, `Cardexpdate`, `Cardnumber`, `Threedigitnumber`) VALUES ('" + str(
        userid) + "','" + cardname + "','" + carddate + "','" + cardnumber + "','" + cardcode + "')"
    cr1 = conn.cursor()
    cr1.execute(s1)
    conn.commit()

    s = "SELECT * FROM `paymentdetails` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    for r in result:
        if (r[1] == userid):
            paymentid = r[0]
            break;

    s = "SELECT * FROM `plans` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    for r in result:
        if (r[1] == planname):
            planid = r[0]
            amount = r[2]
            break;

    s1 = "INSERT INTO `subscriptions`(`planid`, `userid`, `paymentid`, `startdate`, `enddate`, `amountpaid`, `amountbalance`, `status`) VALUES ('" + str(
        planid) + "','" + str(userid) + "','" + str(paymentid) + "','" + str(today) + "','" + str(
        enddate) + "','" + amount + "',0,'1')"
    cr1 = conn.cursor()
    cr1.execute(s1)
    conn.commit()

    s = "SELECT  `movieid`,`Movie name`, `Genres`, `Language`, `Image` FROM `movies`  ORDER BY `Movie name` ASC "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    l = []
    e = {}
    for r in result:
        if r[0] == 19:
            e = {"movieid": r[0], "moviename": r[1], "genre": r[2], "language": r[3]}
        d = {"movieid": r[0], "moviename": r[1], "genre": r[2], "language": r[3], "image": r[4]}
        l.append(d)

    s = "  SELECT DISTINCT `Genres` FROM `movies` ORDER BY `Genres` DESC"
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    return render(request, 'usermain.html', {"d": l, "e": e, "g": result});


def user_main(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    s = "SELECT  `movieid`,`Movie name`, `Genres`, `Language`, `Image` FROM `movies`  ORDER BY `Movie name` ASC "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    l = []
    e = {}
    for r in result:
        if r[0] == 19:
            e = {"movieid": r[0], "moviename": r[1], "genre": r[2], "language": r[3]}
        d = {"movieid": r[0], "moviename": r[1], "genre": r[2], "language": r[3], "image": r[4]}
        l.append(d)

    s = "  SELECT DISTINCT `Genres` FROM `movies` ORDER BY `Genres` DESC"
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    return render(request, 'usermain.html', {"d": l, "e": e, "g": result});


def user_movieview(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    movieid = request.GET["movieid"]
    s = "SELECT  * FROM `userreview`  "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    review = ""
    reviewid = 0
    d=[]
    if cr.rowcount == 0:
        y = 1
    else:
        flag = "false"
        for r in result1:
            if int(r[2]) == int(movieid) and r[3] == "movie":
                if int(r[5]) == 1:
                    value="Positive"
                else:
                    value = "Negative"

                f={"review":r[4],"nature":value}
                d.append(f)
            if int(r[2]) == int(movieid) and int(r[1]) == int(request.session["userid"]) and r[3] == "movie":
                reviewid = r[0]
                y = 2
                review = r[4]
                flag = "true"


        if flag == "false":
            y = 1


    s = "SELECT COUNT(nature) FROM `userreview` WHERE `id`='" + str(movieid) + "' AND nature=1 AND type='movie'"
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    r = result[0]
    pos = r[0]
    s = "SELECT COUNT(nature) FROM `userreview` WHERE `id`='" + str(movieid) + "' AND nature='-1' AND type='movie'"
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    r = result[0]
    neg = r[0]
    if pos > neg:
        state = "Positive"
    elif pos == 0 and neg == 0:
        state = "N/A"
    elif pos == neg:
        state = "Mixed"
    else:
        state = "Negative"
    s = "SELECT  * FROM `movies`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    e = {}
    for r in result:
        if r[0] == int(movieid):
            e = {"movieid": r[0], "moviename": r[1], "genre": r[2], "language": r[3], "Runtime": r[4], "Image": r[5],
                 "cast": r[6], "director": r[7], "link1": r[8], "description": r[9], "coverimage": r[10]}
            break

    return render(request, 'user_movieview.html', {"d": e, "t": y, "y": review, "reviewid": reviewid,"totalreviews":d,"smartreview":state});


def user_moviewatch(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    movieid = request.GET["movieid"]

    s = "SELECT  * FROM `movies`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    print("values")

    e = {}
    for r in result:
        if r[0] == int(movieid):
            e = {"movieid": r[0], "moviename": r[1], "genre": r[2], "language": r[3], "Runtime": r[4], "Image": r[5],
                 "cast": r[6], "director": r[7], "link1": r[8], "description": r[9], "coverimage": r[10]}
            break

    return render(request, 'user_moviewatch.html', {"d": e});


def user_main_tvshows(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    s = "SELECT  `showid`,`Show name`, `Genres`, `Language`, `Image` FROM `tvshows`  ORDER BY `Show name` ASC "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    l = []
    e = {}
    for r in result:
        if r[0] == 1:
            e = {"showid": r[0], "showname": r[1], "genre": r[2], "language": r[3]}
        d = {"showid": r[0], "showname": r[1], "genre": r[2], "language": r[3], "image": r[4]}
        l.append(d)

    s = "  SELECT DISTINCT `Genres` FROM `tvshows` ORDER BY `Genres` DESC"
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    return render(request, 'usermain_tvshows.html', {"d": l, "e": e, "g": result});


def user_showview(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    showid = request.GET["showid"]

    s = "SELECT  * FROM `userreview`  "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    review = ""
    reviewid = 0
    d=[]
    if cr.rowcount == 0:
        y = 1
    else:
        flag = "false"
        for r in result1:
            if int(r[2]) == int(showid) and r[3] == "show":
                if int(r[5]) == 1:
                    value = "Positive"
                else:
                    value = "Negative"

                f = {"review": r[4], "nature": value}
                d.append(f)
            if int(r[2]) == int(showid) and int(r[1]) == int(request.session["userid"]) and r[3] == "show":
                reviewid = r[0]
                y = 2
                review = r[4]
                flag = "true"


        if flag == "false":
            y = 1

    s="SELECT COUNT(nature) FROM `userreview` WHERE `id`='"+str(showid)+"' AND nature=1 AND type='show'"
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    r=result[0]
    pos=r[0]
    s = "SELECT COUNT(nature) FROM `userreview` WHERE `id`='" + str(showid) + "' AND nature='-1' AND type='show'"
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    r = result[0]
    neg = r[0]
    if pos>neg:
        state="Positive"
    elif pos==0 and neg ==0:
        state = "N/A"
    elif pos == neg:
        state = "Mixed"
    else:
        state = "Negative"

    s = "SELECT  * FROM `tvshows`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    e = {}
    for r in result:
        if r[0] == int(showid):
            e = {"showid": r[0], "showname": r[1], "genre": r[2], "language": r[3], "Runtime": r[4], "Image": r[5],
                 "cast": r[6], "director": r[7], "link1": r[8], "description": r[9], "coverimage": r[10]}
            break
    print(d)
    return render(request, 'user_showview.html', {"d": e, "t": y, "y": review, "reviewid": reviewid,"totalreviews":d,"smartreview":state});


def user_showwatch(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    showid = request.GET["showid"]
    s = "SELECT  * FROM `tvshows`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    e = {}
    for r in result:
        if r[0] == int(showid):
            e = {"showid": r[0], "showname": r[1], "genre": r[2], "language": r[3], "Runtime": r[4], "Image": r[5],
                 "cast": r[6], "director": r[7], "link1": r[8], "description": r[9], "coverimage": r[10]}
            break

    return render(request, 'user_showwatch.html', {"d": e});


@csrf_exempt
def user_login(request):
    email = request.POST["txtemail"]
    password = request.POST["txtpassword"]
    planid = 0
    flag = False
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT `subscriptionid`,`enddate` FROM `subscriptions` WHERE `status`=1 "
    cr = conn.cursor()
    cr.execute(s)
    result4 = cr.fetchall()

    today = date.today()

    for r in result4:
        expiry_temp = datetime.strptime(r[1], '%Y-%m-%d').date()
        if expiry_temp < today:
            s = "UPDATE `subscriptions` SET `status`=2 WHERE `subscriptionid`='" + str(r[0]) + "' "
            cr = conn.cursor()
            cr.execute(s)
            conn.commit()

    s = "SELECT * FROM `user` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    today = date.today()
    for r in result:
        if (r[3] == email and r[4] == password):
            request.session["useremail"] = email
            request.session["userid"] = r[0]
            print(request.session["userid"])

            s = "SELECT COUNT(userid) FROM `useronline` WHERE userid='" + str(r[0]) + "' and online=1 "
            cr = conn.cursor()
            cr.execute(s)
            result1 = cr.fetchall()

            s = "SELECT subscriptions.userid, planid,plans.id,plans.`Screens you can watch on at the same time`,`status` FROM subscriptions,plans WHERE subscriptions.userid='" + str(
                r[0]) + "' and plans.id=subscriptions.planid and `status`=1"
            cr = conn.cursor()
            cr.execute(s)
            result2 = cr.fetchall()
            screens = 0

            if cr.rowcount == 0:
                s = "SELECT subscriptions.userid, planid,plans.id,plans.`Screens you can watch on at the same time`,`status`,`subscriptionid` FROM subscriptions,plans WHERE subscriptions.userid='" + str(
                    r[0]) + "' and plans.id=subscriptions.planid and `status`=3"
                cr1 = conn.cursor()
                cr1.execute(s)
                result3 = cr1.fetchall()

                if cr1.rowcount !=0 :
                    d = {"msg": "Your account has been deactivated"}
                    return render(request, "signin.html", {"ar": d})
                else:
                    s1 = "SELECT subscriptions.userid, planid,plans.id,plans.`Screens you can watch on at the same time`,`status`,`subscriptionid` FROM subscriptions,plans WHERE subscriptions.userid='" + str(
                        r[0]) + "' and plans.id=subscriptions.planid and `status`=2"
                    cr1 = conn.cursor()
                    cr1.execute(s1)
                    result4 = cr1.fetchall()

                    t = result4[0]
                    request.session["subscriptionreniew"]=1
                    request.session["subscriptionid"] =t[5]
                    d = {"msg": "Your subscription expired"}
                    request.session["plan"]="Basic"
                    return render(request, "signin.html", {"ar": d})

            for i in result2:
                screens = i[3]

            for t in result1:
                if int(t[0]) < int(screens):
                    flag = True

            if (flag):
                s = "INSERT INTO `useronline`( `userid`, `online`,`date`) VALUES ('" + str(r[0]) + "',1,'" + str(
                    today) + "')"
                cr = conn.cursor()
                cr.execute(s)
                conn.commit()

                s = "SELECT  `movieid`,`Movie name`, `Genres`, `Language`, `Image` FROM `movies`  ORDER BY `Movie name` ASC "
                cr = conn.cursor()
                cr.execute(s)
                result = cr.fetchall()
                l = []
                e = {}
                for r in result:
                    if r[0] == 19:
                        e = {"movieid": r[0], "moviename": r[1], "genre": r[2], "language": r[3]}
                    d = {"movieid": r[0], "moviename": r[1], "genre": r[2], "language": r[3], "image": r[4]}
                    l.append(d)

                s = "  SELECT DISTINCT `Genres` FROM `movies` ORDER BY `Genres` DESC"
                cr = conn.cursor()
                cr.execute(s)
                result = cr.fetchall()

                return HttpResponseRedirect("usermain");
            else:
                d = {"msg": "Online Screen Limit Exceded"}
                return render(request, "signin.html", {"ar": d})
        else:
            flag1 = "false"

    if flag1 == "false":
        d = {"msg": "Incorrect Email/Password"}
        return render(request, "signin.html", {"ar": d})

def validate_plan(request):
    plan = request.GET["plan"]
    request.session["plan"]=plan
    return HttpResponse("Success!")

def usersubscriptionrenew(request):
    if not "subscriptionreniew" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT * FROM `paymentdetails` WHERE `userid`='"+str(request.session["userid"])+"' "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    plan=request.session["plan"]

    s = "SELECT `Monthly price`,`id` FROM `plans` WHERE `type`='" + plan + "' "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    g=result1[0]
    t=g[0]
    request.session["planid"]=g[1]
    request.session["planprice"] = g[0]
    for r in result:
        d={"cardname":r[2],"cardexp":r[3],"cardnumber":r[4],"cardcvv":r[5],"plan":plan}
    return render(request,"usersubscriptionrenew.html",{"ar":d,"d":t})

@csrf_exempt
def usersubscriptionrenewpayment(request):
    if not "subscriptionreniew" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    today = date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    enddate = today + timedelta(days=days_in_month)

    s = "UPDATE `subscriptions` SET `planid`='"+str(request.session["planid"])+"',`amountpaid`='"+str(request.session["planprice"])+"',`enddate`='"+str(enddate)+"',`startdate`='"+str(today)+"',`status`=1 WHERE `subscriptionid`='"+str(request.session["subscriptionid"])+"' "
    cr = conn.cursor()
    cr.execute(s)
    conn.commit()
    del request.session["planid"]
    del request.session["planprice"]
    del request.session["subscriptionid"]
    del request.session["subscriptionreniew"]
    return HttpResponseRedirect("signin")

def user_logout(request):
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "UPDATE `useronline` SET `online`=0 where `userid`='" + str(
        request.session["userid"]) + "' and `online`=1 ORDER BY `id` DESC LIMIT 1"
    cr = conn.cursor()
    cr.execute(s)
    conn.commit()
    del request.session["userid"]
    d = {"msg": " "}
    return render(request, "signin.html", {"ar": d})


def user_forgetpassword(request):
    g = {"msg": " "}
    return render(request, "user_forgetpassword.html", {"d": g})


def user_generateotp(request):
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT * FROM `user` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    email = request.POST["txtemail"]

    flag="true"
    for r in result:

        if r[3] == email:
            request.session["useridpassword"] = r[0]
            otp = randint(100000, 999999)
            s1 = "UPDATE `user` SET `otp`='" + str(otp) + "'where `userid`='" + str(r[0]) + "'"
            cr1 = conn.cursor()
            cr1.execute(s1)
            conn.commit()
            connection = smtplib.SMTP('smtp.gmail.com', 587)
            connection.starttls()
            connection.login("testhellotesthello1@gmail.com", "hellotest1")

            # message to be sent
            msg = EmailMessage()

            msg.set_content("We have received an request to change your password\nYou otp is : " + str(otp))

            msg['Subject'] = 'Reset Password'
            msg['From'] = "Netflix Plus Security Team"
            msg['To'] = r[3]
            # sending the mail
            connection.send_message(msg)

            # terminating the session
            connection.quit()
            return render(request, 'user_enterotp.html');
        else:
           flag="false"

    if flag == "false":
        g = {"msg": "Email NOT registered"}
        return render(request, 'user_forgetpassword.html', {"d": g});


def user_changepassword(request):
    if not "useridpassword" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT * FROM `user` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    otp = request.POST["txtotp"]
    password = request.POST["txtpassword"]
    flag="true"
    for r in result:
        if int(r[0]) == request.session["useridpassword"]:

            if int(otp) == int(r[5]):

                s1 = "UPDATE `user` SET `otp`= 0,`Password`='" + password + "' where `userid`='" + str(r[0]) + "'"
                cr1 = conn.cursor()
                cr1.execute(s1)
                conn.commit()
                del request.session["useridpassword"]

                connection = smtplib.SMTP('smtp.gmail.com', 587)
                connection.starttls()
                connection.login("testhellotesthello1@gmail.com", "hellotest1")

                # message to be sent
                msg = EmailMessage()

                msg.set_content("Your Password has been successfully changed")

                msg['Subject'] = 'Reset Password'
                msg['From'] = "Netflix Plus Security Team"
                msg['To'] = r[3]
                # sending the mail
                connection.send_message(msg)

                # terminating the session
                connection.quit()
                return HttpResponseRedirect("signin")

            else:
               flag="false"

    if flag=="false":
        g = {"msg": "Incorrect Otp"}
        return render(request, 'user_enterotp.html', {"d": g});


def user_profile(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")

    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    s = "SELECT  * FROM `user`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT * FROM `plans` "
    cr = conn.cursor()
    cr.execute(s)
    result3 = cr.fetchall()
    r1 = result3[0]
    amountp1 = r1[2]
    r1 = result3[1]
    amountp2 = r1[2]
    r1 = result3[2]
    amountp3 = r1[2]

    s = "SELECT subscriptions.userid,subscriptionid,enddate,status,amountpaid, planid,plans.id,plans.type,status FROM subscriptions,plans WHERE subscriptions.userid='" + str(
        request.session["userid"]) + "' and plans.id=subscriptions.planid and status=1"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    for i in result1:
        planname = i[7]
        subid = i[1]
        balance = i[4]
        enddate = i[2]
        status = i[3]
    e = {}
    request.session["subid"] = subid
    for r in result:
        if int(r[0]) == request.session["userid"]:
            e = {"name": r[1], "phone": r[2], "email": r[3], "plan": planname, "subscriptionid": subid,
                 "balance": balance, "enddate": enddate, "status": status, "price1": amountp1, "price2": amountp2,
                 "price3": amountp3}
            break
    g = {"msg": " "}
    return render(request, 'user_profile.html', {"d": e, "t": 0, "i": g, "js": 0, "k": 0});


@csrf_exempt
def generateotp(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")

    oldpassword = request.POST["txtoldpassword"]
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT  * FROM `user`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    s = "SELECT * FROM `plans` "
    cr = conn.cursor()
    cr.execute(s)
    result3 = cr.fetchall()
    r1 = result3[0]
    amountp1 = r1[2]
    r1 = result3[1]
    amountp2 = r1[2]
    r1 = result3[2]
    amountp3 = r1[2]
    e={}
    flag = "true"
    for r in result:

        if int(r[0]) == request.session["userid"]:
            e = {"name": r[1], "phone": r[2], "email": r[3], "price1": amountp1, "price2": amountp2, "price3": amountp3}
            if oldpassword == r[4]:
                otp = randint(100000, 999999)
                s1 = "UPDATE `user` SET `otp`='" + str(otp) + "'where `userid`='" + str(r[0]) + "'"
                cr1 = conn.cursor()
                cr1.execute(s1)
                conn.commit()

                connection = smtplib.SMTP('smtp.gmail.com', 587)
                connection.starttls()
                connection.login("testhellotesthello1@gmail.com", "hellotest1")

                # message to be sent
                msg = EmailMessage()

                msg.set_content("We have received an request to change your password\nYou otp is : " + str(otp))

                msg['Subject'] = 'Reset Password'
                msg['From'] = "Netflix Plus Security Team"
                msg['To'] = r[3]
                # sending the mail
                connection.send_message(msg)

                # terminating the session
                connection.quit()
                flag="true"
                break
            else:
               flag="false"

    if flag=="false":
        g = {"msg": "Incorrect Password"}
        return render(request, 'user_profile.html', {"d": e, "t": 0, "i": g, "js": 1, "k": 0});
    g = {"msg": " "}
    return render(request, 'user_profile.html', {"d": e, "t": 1, "i": g, "js": 1, "k": 0});


@csrf_exempt
def changepassword(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")

    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT  * FROM `user`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT * FROM `plans` "
    cr = conn.cursor()
    cr.execute(s)
    result3 = cr.fetchall()
    r1 = result3[0]
    amountp1 = r1[2]
    r1 = result3[1]
    amountp2 = r1[2]
    r1 = result3[2]
    amountp3 = r1[2]
    flag = "true"
    otp = request.POST["txtotp"]
    password = request.POST["txtnewpassword"]
    for r in result:
        if int(r[0]) == request.session["userid"]:
            e = {"name": r[1], "phone": r[2], "email": r[3], "price1": amountp1, "price2": amountp2, "price3": amountp3}
            if int(otp) == int(r[5]):

                s1 = "UPDATE `user` SET `otp`= 0,`Password`='" + password + "' where `userid`='" + str(r[0]) + "'"
                cr1 = conn.cursor()
                cr1.execute(s1)
                conn.commit()
                flag="true"
            else:
                flag="false"
                break
    if flag=="false":
        g = {"msg": "Incorrect Otp"}
        return render(request, 'user_profile.html', {"d": e, "t": 1, "i": g, "js": 1, "k": 0});

    g = {"msg": " ", "msg2": "Password change successful"}
    return render(request, 'user_profile.html', {"d": e, "t": 0, "i": g, "js": 0, "k": 1});


@csrf_exempt
def subscription(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT  * FROM `user`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT subscriptions.userid,subscriptionid,enddate,status,amountpaid, planid,plans.id,plans.type FROM subscriptions,plans WHERE subscriptions.userid='" + str(
        request.session["userid"]) + "' and plans.id=subscriptions.planid"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    s = "SELECT * FROM `plans` "
    cr = conn.cursor()
    cr.execute(s)
    result3 = cr.fetchall()
    r1 = result3[0]
    amountp1 = r1[2]
    r1 = result3[1]
    amountp2 = r1[2]
    r1 = result3[2]
    amountp3 = r1[2]

    for i in result1:
        planname = i[7]
        subid = i[1]
        balance = i[4]
        enddate = i[2]
        status = i[3]
    e = {}

    for r in result:
        if int(r[0]) == request.session["userid"]:
            e = {"name": r[1], "phone": r[2], "email": r[3], "plan": planname, "subscriptionid": subid,
                 "balance": balance, "enddate": enddate, "status": status, "price1": amountp1, "price2": amountp2,
                 "price3": amountp3}
            break
    g = {"msg": " "}
    return render(request, 'user_profile.html', {"d": e, "t": 3, "i": g, "js": 2, "k": 0});


@csrf_exempt
def subscriptions_renew(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")

    subscription = request.session["subid"]
    plan = request.POST["txtplan"]
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT  * FROM `user`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT `paymentid`, `userid`, `Cardholder name`, `Cardexpdate`, `Cardnumber`, `Threedigitnumber` FROM `paymentdetails` WHERE `userid`='" + str(
        request.session["userid"]) + "'"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    for i in result1:
        Cardholdername = i[2]
        Cardexpdate = i[3]
        Cardnumber = i[4]
        Threedigitnumber = i[5]

    e = {}

    s = "SELECT * FROM `plans` "
    cr = conn.cursor()
    cr.execute(s)
    result3 = cr.fetchall()
    for y in result3:
        if str(y[1]) == str(plan):
            amount = y[2]
            break

    r1 = result3[0]
    amountp1 = r1[2]
    r1 = result3[1]
    amountp2 = r1[2]
    r1 = result3[2]
    amountp3 = r1[2]

    for r in result:
        if int(r[0]) == request.session["userid"]:
            e = {"name": r[1], "phone": r[2], "email": r[3], "plan": plan, "subscriptionid": subscription,
                 "amount": amount, "cardexpdate": Cardexpdate, "cardname": Cardholdername, "cardnumber": Cardnumber,
                 "cvv": Threedigitnumber, "price1": amountp1, "price2": amountp2,
                 "price3": amountp3}
            break
    g = {"msg": " "}
    return render(request, 'user_profile.html', {"d": e, "t": 4, "i": g, "js": 2, "k": 0});


def subscriptions_pay(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")

    subscription = request.session["subid"]
    plan = request.POST["txtplan"]
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT  * FROM `user`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT * FROM `plans` "
    cr = conn.cursor()
    cr.execute(s)
    result3 = cr.fetchall()

    for y in result3:
        if str(y[1]) == str(plan):
            amount = y[2]
            planid = y[0]
            break

    r1 = result3[0]
    amountp1 = r1[2]
    r1 = result3[1]
    amountp2 = r1[2]
    r1 = result3[2]
    amountp3 = r1[2]

    s = "SELECT `paymentid`, `userid`, `Cardholder name`, `Cardexpdate`, `Cardnumber`, `Threedigitnumber` FROM `paymentdetails` WHERE `userid`='" + str(
        request.session["userid"]) + "'"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    for i in result1:
        paymentid = i[0]
        Cardholdername = i[2]
        Cardexpdate = i[3]
        Cardnumber = i[4]
        Threedigitnumber = i[5]

    today = date.today()

    days_in_month = calendar.monthrange(today.year, today.month)[1]
    enddate = today + timedelta(days=days_in_month)
    s1 = "UPDATE `subscriptions` SET `status`=0 where `userid`='" + str(request.session["userid"]) + "'"
    cr1 = conn.cursor()
    cr1.execute(s1)
    conn.commit()

    s1 = "INSERT INTO `subscriptions`(`planid`, `userid`, `paymentid`, `startdate`, `enddate`, `amountpaid`, `amountbalance`, `status`) VALUES ('" + str(
        planid) + "','" + str(request.session["userid"]) + "','" + str(paymentid) + "','" + str(today) + "','" + str(
        enddate) + "','" + amount + "',0,'1')"
    cr1 = conn.cursor()
    cr1.execute(s1)
    conn.commit()

    for r in result:
        if int(r[0]) == request.session["userid"]:
            e = {"name": r[1], "phone": r[2], "email": r[3], "plan": plan, "subscriptionid": subscription,
                 "balance": amount, "enddate": enddate, "status": 1, "price1": amountp1, "price2": amountp2,
                 "price3": amountp3}
            break
    g = {"msg": "", "msg2": "Subscription Renewed "}
    return render(request, 'user_profile.html', {"d": e, "t": 0, "i": g, "js": 0, "k": 2});


def page_2(request):
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT  `Monthly price`, `HD available`, `Ultra HD available`, `Watch on your laptop and TV`, `Watch on your mobile phone and tablet`, `Screens you can watch on at the same time`, `Unlimited movies and TV shows`, `Smart Reviews`, `Cancel anytime` FROM `plans`"
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    #  lt = []
    # a='A'

    #  for i in result:
    #      count = 1;
    #     lt1=[]
    #     for j in i:
    #          lt1.append(a+str(count))
    #         count+=1
    #      lt.append(lt1)
    #    a = chr(ord(a) + 1)

    # data=zip(lt,result)
    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'plans' and COLUMN_NAME NOT In ('id','type') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    return render(request, 'page_plans.html', {"d": result, "e": result1});


def sign_in(request):
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT `subscriptionid`,`enddate` FROM `subscriptions` WHERE `status`=1 "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    print(result1)
    today = date.today()

    for r in result1:
        expiry_temp = datetime.strptime(r[1], '%Y-%m-%d').date()
        if  expiry_temp < today:
            s = "UPDATE `subscriptions` SET `status`=2 WHERE `subscriptionid`='"+str(r[0])+"' "
            cr = conn.cursor()
            cr.execute(s)
            conn.commit()

    return render(request, "signin.html")


def admin_login(request):
    d = {"msg": " "}
    return render(request, "admin_login.html", {"ar": d})


def admin_logout(request):
    d = {"msg": " "}
    del request.session["adminname"]
    return render(request, "admin_login.html", {"ar": d})


@csrf_exempt
def admin_1(request):
    email = request.POST["txtemail"]
    password = request.POST["txtpassword"]
    request.session["adminname"] = email
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT * FROM admin "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    flag = "false"
    for r in result:
        if (r[1] == email and r[2] == password):
            flag = "true"
            break

        else:
            flag = "false"

    if flag == "true":
        d = {"msg": email}
        return HttpResponseRedirect("adminmain")
    else:
        d = {"msg": "Incorrect Email/Password"}
        return render(request, "admin_login.html", {"ar": d})


def admin_main(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT COUNT(online) FROM `useronline` where `online`=1"
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    s = "SELECT  COUNT(DISTINCT Genres) FROM `movies` "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    s = "SELECT  COUNT(DISTINCT Genres) FROM `tvshows` "
    cr = conn.cursor()
    cr.execute(s)
    result2 = cr.fetchall()
    s = "SELECT COUNT(`Movie name`) FROM `movies` "
    cr = conn.cursor()
    cr.execute(s)
    result3 = cr.fetchall()
    s = "SELECT COUNT(`Show name`) FROM `tvshows` "
    cr = conn.cursor()
    cr.execute(s)
    result4 = cr.fetchall()

    s = "SELECT COUNT(`status`) FROM `subscriptions` where `status`=1 "
    cr = conn.cursor()
    cr.execute(s)
    result5 = cr.fetchall()
    s = "SELECT COUNT(`userid`) FROM `user` "
    cr = conn.cursor()
    cr.execute(s)
    result6 = cr.fetchall()

    return render(request, "admin_main.html",
                  {"ar": d, "user": result[0], "movies": result3[0], "tvshows": result4[0], "Gmovies": result1[0],
                   "Gtvshows": result2[0], "subs": result5[0], "users": result6[0]})


def movie_details(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    d = {"msg": request.session["adminname"]}
    s = "SELECT  `Movie name`, `Genres`, `Language`, `Runtime (minutes)`,`Image`, `Cast`, `Director`, `Link`,`Description`,`Cover Image` FROM `movies` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'movies' and COLUMN_NAME NOT In ('movieid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    return render(request, "moviedetails.html", {"ar": d, "d": result, "e": result1})


def movie_add(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    s = "SELECT  `Movie name`, `Genres`, `Language`, `Runtime (minutes)`,`Image`, `Cast`, `Director`, `Link`,`Description`,`Cover Image` FROM `movies` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'movies' and COLUMN_NAME NOT In ('movieid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    f = {"msg": " "}
    return render(request, "movieadd.html", {"ar": d, "d": result, "e": result1, "l": f})


@csrf_exempt
def movieadd_data(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    moviename = request.POST["txtmoviename"]
    genre = request.POST["txtgenre"]
    language = request.POST["txtlanguage"]
    runtime = request.POST["txtruntime"]
    filename = request.FILES["txtfile"]
    coverimage = request.FILES["txtcoverfile"]
    cast = request.POST["txtcast"]
    director = request.POST["txtdirector"]
    link1 = request.POST["txtlink"]
    description = request.POST["txtdescription"]

    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    s = "SELECT  `Movie name`, `Genres`, `Language`, `Runtime (minutes)`,`Image`, `Cast`, `Director`, `Link`,`Description`,`Cover Image` FROM `movies`"
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'movies' and COLUMN_NAME NOT In ('movieid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    name = link1 + "IMG" + ".jpeg"
    coverimagename = link1 + "COVERIMG" + ".jpeg"
    for r in result:

        if r[0] == moviename:
            f = {"msg": "Movie already exists in the database"}
            return render(request, "movieadd.html", {"d": result, "e": result1, "l": f})

    s1 = "INSERT INTO `movies` (`Movie name`, `Genres`, `Language`, `Runtime (minutes)`,`Image`, `Cast`,`Director`,`Link`,`Description`,`Cover Image`) VALUES('" + moviename + "','" + genre + "','" + language + "','" + runtime + "','" + name + "','" + cast + "','" + director + "','" + link1 + "','" + description + "','" + coverimagename + "')"
    cr1 = conn.cursor()
    cr1.execute(s1)
    conn.commit()

    s2 = "SELECT  `Movie name`, `Genres`, `Language`, `Runtime (minutes)`,`Image`, `Cast`, `Director`, `Link`,`Description`,`Cover Image` FROM `movies` "
    cr2 = conn.cursor()
    cr2.execute(s2)
    result2 = cr2.fetchall()

    fs = FileSystemStorage()
    fs.save(name, filename)
    f = {"msg": " "}
    fs = FileSystemStorage()
    fs.save(coverimagename, coverimage)
    f = {"msg": " "}
    return render(request, "movieadd.html", {"ar": d, "d": result2, "e": result1, "l": f})


def movie_edit(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    s = "SELECT  * FROM `movies` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'movies' and COLUMN_NAME NOT In ('movieid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    f = {"msg": " "}
    return render(request, "movieedit.html", {"ar": d, "d": result, "e": result1, "l": f})


@csrf_exempt
def movieedit_data(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    movieid = request.GET["movieid"]

    s = "SELECT  * FROM `movies` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    dic = {}
    moviename = ""
    for r in result:

        if r[0] == int(movieid):
            dic = {"movieid": movieid, "moviename": r[1], "genre": r[2], "language": r[3], "runtime": r[4],
                   "filename": r[5], "cast": r[6], "director": r[7], "link1": r[8], "description": r[9],
                   "coverimage": r[10]}
            break

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'movies' and COLUMN_NAME NOT In ('movieid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    return render(request, "movieeditdata.html", {"ar": d, "d": result, "d1": dic, "e": result1, })


@csrf_exempt
def movieedit_data_save(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    movieid = request.POST["txtmovieid1"]
    moviename = request.POST["txtmoviename"]
    genre = request.POST["txtgenre"]
    language = request.POST["txtlanguage"]
    runtime = request.POST["txtruntime"]

    cast = request.POST["txtcast"]
    director = request.POST["txtdirector"]
    link1 = request.POST["txtlink"]
    description = request.POST["txtdescription"]

    name = ""
    covername = ""

    if str(request.FILES.get('txtfile', False)) == "False":
        name = request.POST["txtfiletxt"]
    else:
        filename = request.FILES["txtfile"]
        name = link1 + "IMG" + ".jpeg"
        fs = FileSystemStorage()
        fs.save(name, filename)

    if str(request.FILES.get('txtcoverfile', False)) == "False":
        covername = request.POST["txtcoverfiletxt"]
    else:
        filename = request.FILES["txtcoverfile"]
        covername = link1 + "COVERIMG" + ".jpeg"
        fs = FileSystemStorage()
        fs.save(covername, filename)

    s1 = "UPDATE `movies` SET  `Movie name` = '" + moviename + "', `Genres` = '" + genre + "', `Language` = '" + language + "', `Runtime (minutes)` = '" + runtime + "', `Image` = '" + name + "',`cast` = '" + cast + "', `Director` = '" + director + "', `Link` = '" + link1 + "',`Description`='" + description + "',`Cover Image`='" + covername + "' WHERE `movieid` = '" + movieid + "'"
    cr1 = conn.cursor()
    cr1.execute(s1)
    conn.commit()

    s = "SELECT  * FROM `movies` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'movies' and COLUMN_NAME NOT In ('movieid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    dic = {"movieid": " ", "moviename": " ", "genre": " ", "language": " ", "runtime": " ", "filename": " ",
           "cast": " ", "director": " ", "link1": " ", "description": " ", "coverimage": " "}

    return render(request, "movieeditdata.html", {"ar": d, "d": result, "d1": dic, "e": result1, })


def movie_delete(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    d = {"msg": request.session["adminname"]}
    movieid = request.GET["movieid"]
    name = request.GET["file"]
    covername = request.GET["coverfile"]

    fs = FileSystemStorage()
    fs.delete(name)
    fs.delete(covername)

    s1 = "DELETE FROM `movies` WHERE `movieid`='" + str(movieid) + "'"
    cr1 = conn.cursor()
    cr1.execute(s1)
    conn.commit()

    s = "SELECT  * FROM `movies` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'movies' and COLUMN_NAME NOT In ('movieid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    dic = {"movieid": " ", "moviename": " ", "genre": " ", "language": " ", "runtime": " ", "filename": " ",
           "cast": " ", "director": " ", "link1": " ", "description": " ", "coverimage": " "}

    return render(request, "movieeditdata.html", {"ar": d, "d": result, "d1": dic, "e": result1, })


def admin_userdetails(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    s = "SELECT `userid`, `Name`, `Phone`, `Email`, `otp` FROM `user` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'user' AND table_schema = 'netflixplus' and COLUMN_NAME NOT In ('password','userid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    f = {"msg": " "}
    return render(request, "admin_userdetails.html", {"ar": d, "d": result, "e": result1, "l": f})


def admin_userdetailedit(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    dd = {"msg": request.session["adminname"]}
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    userid = request.GET["userid"]

    s = "SELECT  * FROM `user` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    dic = {}

    for r in result:

        if r[0] == int(userid):
            dic = {"userid": userid, "username": r[1], "phone": r[2], "email": r[3], "otp": r[5], }
            break
    s = "SELECT  * FROM `paymentdetails` "
    cr = conn.cursor()
    cr.execute(s)
    result2 = cr.fetchall()
    dic1 = {}

    for r in result2:

        if r[1] == int(userid):
            dic1 = {"cardname": r[2], "cardexpdate": r[3], "cardnumber": r[4], "payid": r[0]}
            break

    s = "SELECT `subscriptionid`,`enddate` FROM `subscriptions` WHERE `status`=1 "
    cr = conn.cursor()
    cr.execute(s)
    result5 = cr.fetchall()

    today = date.today()

    for r in result5:
        expiry_temp = datetime.strptime(r[1], '%Y-%m-%d').date()
        if expiry_temp < today:
            s = "UPDATE `subscriptions` SET `status`=2 WHERE `subscriptionid`='" + str(r[0]) + "' "
            cr = conn.cursor()
            cr.execute(s)
            conn.commit()

    s = "SELECT  * FROM `subscriptions` "
    cr = conn.cursor()
    cr.execute(s)
    result2 = cr.fetchall()
    dic3 = {}

    for r in result2:

        if r[2] == int(userid) and int(r[8]) == 1:
            subid=r[0]
            planid = r[1]
            startdate = r[4]
            enddate = r[5]
            amount = r[6]
            status = r[8]
            break

        elif r[2] == int(userid) and int(r[8]) == 0:
            subid = r[0]
            planid = r[1]
            startdate = r[4]
            enddate = r[5]
            amount = r[6]
            status = r[8]

        elif r[2] == int(userid) and int(r[8]) == 2:
            subid = r[0]
            planid = r[1]
            startdate = r[4]
            enddate = r[5]
            amount = r[6]
            status = r[8]
            break

        elif r[2] == int(userid) and int(r[8]) == 3:
            subid = r[0]
            planid = r[1]
            startdate = r[4]
            enddate = r[5]
            amount = r[6]
            status = r[8]
            break

    s = "SELECT  * FROM `plans` "
    cr = conn.cursor()
    cr.execute(s)
    result2 = cr.fetchall()

    for r in result2:

        if r[0] == int(planid):
            planname = r[1]
            break
    if int(status) == 1:
        state = "Activated"
    elif int(status) == 3:
        state = "Deactivated"
    else:
        state = "Subscription Inactive"
    dic2 = {"subid":subid,"plan": planname, "startdate": startdate, "enddate": enddate, "amount": amount, "state": state}

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'user' AND table_schema = 'netflixplus' and COLUMN_NAME NOT In ('password','userid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    return render(request, "admin_userdetailedit.html",
                  {"ar": dd, "d": result, "d1": dic, "d2": dic1, "d3": dic2, "e": result1})


@csrf_exempt
def admin_userdetails_save(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    dd = {"msg": request.session["adminname"]}

    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    userid = request.POST["txtuserid"]
    phone = request.POST["txtphone"]
    otp = request.POST["txtotp"]
    s = "UPDATE `user` SET `Phone`='" + phone + "',`otp`='" + otp + "' WHERE `userid`='" + userid + "' "
    cr = conn.cursor()
    cr.execute(s)
    conn.commit()

    return HttpResponseRedirect("adminuserdetails")


def admin_user_delete(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    dd = {"msg": request.session["adminname"]}

    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    subid = request.GET["subid"]
    print("subid:")
    print(subid)
    s = "UPDATE `subscriptions` SET `status`=3 WHERE `subscriptionid`='" + subid + "' "
    cr = conn.cursor()
    cr.execute(s)
    conn.commit()

    return HttpResponseRedirect("adminuserdetails")

def admin_user_activate(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    dd = {"msg": request.session["adminname"]}

    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    subid = request.GET["subid"]
    print("subid:")
    print(subid)
    s = "UPDATE `subscriptions` SET `status`=1 WHERE `subscriptionid`='" + subid + "' "
    cr = conn.cursor()
    cr.execute(s)
    conn.commit()

    return HttpResponseRedirect("adminuserdetails")


def admin_plans(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    dd = {"msg": request.session["adminname"]}

    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    s = "SELECT * FROM `plans` "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    d = result1[0]
    e = {"price": d[2], "hd": d[3], "uhd": d[4], "watchlaptop": d[5], "watchmobile": d[6], "screenlimit": d[7],
         "unlimitedshows": d[8], "smartreviews": d[9], "cancelanytime": d[10]}
    d = result1[1]
    e1 = {"price": d[2], "hd": d[3], "uhd": d[4], "watchlaptop": d[5], "watchmobile": d[6], "screenlimit": d[7],
          "unlimitedshows": d[8], "smartreviews": d[9], "cancelanytime": d[10]}
    d = result1[2]
    e2 = {"price": d[2], "hd": d[3], "uhd": d[4], "watchlaptop": d[5], "watchmobile": d[6], "screenlimit": d[7],
          "unlimitedshows": d[8], "smartreviews": d[9], "cancelanytime": d[10]}

    return render(request, "admin_plans.html", {"ar": dd, "d1": e, "d2": e1, "d3": e2})


@csrf_exempt
def admin_plans_save(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    dd = {"msg": request.session["adminname"]}

    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    txtprice = request.POST["txtprice"]
    txthd = request.POST["txthd"]
    txtuhd = request.POST["txtuhd"]
    txtwatchlaptop = request.POST["txtwatchlaptop"]
    txtwatchmobile = request.POST["txtwatchmobile"]
    txtscreenlimit = request.POST["txtscreenlimit"]
    txtunlimitedshows = request.POST["txtunlimitedshows"]
    txtsmartreview = request.POST["txtsmartreview"]
    txtcancel = request.POST["txtcancel"]

    txtprice1 = request.POST["txtprice1"]
    txthd1 = request.POST["txthd1"]
    txtuhd1 = request.POST["txtuhd1"]
    txtwatchlaptop1 = request.POST["txtwatchlaptop1"]
    txtwatchmobile1 = request.POST["txtwatchmobile1"]
    txtscreenlimit1 = request.POST["txtscreenlimit1"]
    txtunlimitedshows1 = request.POST["txtunlimitedshows1"]
    txtsmartreview1 = request.POST["txtsmartreview1"]
    txtcancel1 = request.POST["txtcancel1"]

    txtprice2 = request.POST["txtprice2"]
    txthd2 = request.POST["txthd2"]
    txtuhd2 = request.POST["txtuhd2"]
    txtwatchlaptop2 = request.POST["txtwatchlaptop2"]
    txtwatchmobile2 = request.POST["txtwatchmobile2"]
    txtscreenlimit2 = request.POST["txtscreenlimit2"]
    txtunlimitedshows2 = request.POST["txtunlimitedshows2"]
    txtsmartreview2 = request.POST["txtsmartreview2"]
    txtcancel2 = request.POST["txtcancel2"]

    s = "UPDATE `plans` SET `Monthly price`='" + txtprice + "',`HD available`='" + txthd + "',`Ultra HD available`='" + txtuhd + "',`Watch on your laptop and TV`='" + txtwatchlaptop + "',`Watch on your mobile phone and tablet`='" + txtwatchmobile + "',`Screens you can watch on at the same time`='" + txtscreenlimit + "',`Unlimited movies and TV shows`='" + txtunlimitedshows + "',`Smart Reviews`='" + txtsmartreview + "',`Cancel anytime`='" + txtcancel + "' WHERE id=1"
    cr = conn.cursor()
    cr.execute(s)
    conn.commit()

    s = "UPDATE `plans` SET `Monthly price`='" + txtprice1 + "',`HD available`='" + txthd1 + "',`Ultra HD available`='" + txtuhd1 + "',`Watch on your laptop and TV`='" + txtwatchlaptop1 + "',`Watch on your mobile phone and tablet`='" + txtwatchmobile1 + "',`Screens you can watch on at the same time`='" + txtscreenlimit1 + "',`Unlimited movies and TV shows`='" + txtunlimitedshows1 + "',`Smart Reviews`='" + txtsmartreview1 + "',`Cancel anytime`='" + txtcancel1 + "' WHERE id=2"
    cr = conn.cursor()
    cr.execute(s)
    conn.commit()

    s = "UPDATE `plans` SET `Monthly price`='" + txtprice2 + "',`HD available`='" + txthd2 + "',`Ultra HD available`='" + txtuhd2 + "',`Watch on your laptop and TV`='" + txtwatchlaptop2 + "',`Watch on your mobile phone and tablet`='" + txtwatchmobile2 + "',`Screens you can watch on at the same time`='" + txtscreenlimit2 + "',`Unlimited movies and TV shows`='" + txtunlimitedshows2 + "',`Smart Reviews`='" + txtsmartreview2 + "',`Cancel anytime`='" + txtcancel2 + "' WHERE id=3"
    cr = conn.cursor()
    cr.execute(s)
    conn.commit()

    s = "SELECT * FROM `plans` "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    d = result1[0]
    e = {"price": d[2], "hd": d[3], "uhd": d[4], "watchlaptop": d[5], "watchmobile": d[6], "screenlimit": d[7],
         "unlimitedshows": d[8], "smartreviews": d[9], "cancelanytime": d[10]}
    d = result1[1]
    e1 = {"price": d[2], "hd": d[3], "uhd": d[4], "watchlaptop": d[5], "watchmobile": d[6], "screenlimit": d[7],
          "unlimitedshows": d[8], "smartreviews": d[9], "cancelanytime": d[10]}
    d = result1[2]
    e2 = {"price": d[2], "hd": d[3], "uhd": d[4], "watchlaptop": d[5], "watchmobile": d[6], "screenlimit": d[7],
          "unlimitedshows": d[8], "smartreviews": d[9], "cancelanytime": d[10]}

    return render(request, "admin_plans.html", {"ar": dd, "d1": e, "d2": e1, "d3": e2});


def admin_changepassword(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")

    d = {"msg": request.session["adminname"]}

    return render(request, "admin_changepassword.html", {"ar": d});


@csrf_exempt
def admin_changepassword_save(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    d = {"msg": request.session["adminname"]}
    oldpassword = request.POST["txtoldpassword"]
    newpassword = request.POST["txtnewpassword"]

    s = "SELECT * FROM `admin` "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    for r in result1:
        if r[2] == oldpassword and r[1] == request.session["adminname"]:
            s = "UPDATE `admin` SET  `password` ='" + newpassword + "' WHERE `adminid`='" + str(r[0]) + "'"
            cr = conn.cursor()
            cr.execute(s)
            conn.commit()
            l = {"msg": " "}
            f = {"msg": "Password changed successfull"}
        else:
            l = {"msg": "Old password incorrect"}
            f = {"msg": ""}

    return render(request, "admin_changepassword.html", {"ar": d, "t": l, "g": f});


def admin_addadmin(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")

    d = {"msg": request.session["adminname"]}

    return render(request, "admin_addadmin.html", {"ar": d});


@csrf_exempt
def admin_addadmin_save(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")

    d = {"msg": request.session["adminname"]}
    oldpassword = request.POST["txtpassword"]
    newadminname = request.POST["txtnewadminname"]
    newpassword = request.POST["txtnewadminpassword"]
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT * FROM `admin` "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    for r in result1:
        if r[2] == oldpassword and r[1] == request.session["adminname"]:
            s = "INSERT INTO `admin` (`username`,`password`) VALUES('" + newadminname + "','" + newpassword + "')"
            cr = conn.cursor()
            cr.execute(s)
            conn.commit()
            l = {"msg": " "}
            f = {"msg": "New admin ADDED successfull"}
        else:
            l = {"msg": "Incorrect Password"}
            f = {"msg": ""}

    return render(request, "admin_addadmin.html", {"ar": d, "t": l, "g": f});


def admin_editadmin(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT `username` FROM `admin` "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    d = {"msg": request.session["adminname"]}

    return render(request, "admin_editadmin.html", {"ar": d, "data": result1});


@csrf_exempt
def admin_editadmin_save(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")

    d = {"msg": request.session["adminname"]}
    oldpassword = request.POST["txtpassword"]
    newadminname = request.POST["txtnewadminname"]
    newpassword = request.POST["txtnewadminpassword"]
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT `username` FROM `admin` "
    cr = conn.cursor()
    cr.execute(s)
    result2 = cr.fetchall()

    s = "SELECT * FROM `admin` "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    for r in result1:
        if r[2] == oldpassword and r[1] == request.session["adminname"]:
            for r in result1:
                if r[1] == newadminname and r[2] == newpassword:

                    l = {"msg": " "}
                    l1 = {"msg": " "}
                    f = {"msg": "Edit successfull"}
                    request.session["securedelete"] = 1
                    request.session["adminuserid"] = r[0]
                    return HttpResponseRedirect("admin_deladmin")
                else:
                    l1 = {"msg": "Incorrect Password"}
                    l = {"msg": " "}
                    f = {"msg": " "}
            break
        else:
            l = {"msg": "Incorrect Password"}
            l1 = {"msg": " "}
            f = {"msg": " "}

    return render(request, "admin_editadmin.html", {"ar": d, "t": l, "t1": l1, "g": f, "data": result2});


def admin_deladmin(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    if not "securedelete" in request.session:
        return HttpResponseRedirect("admin_addadmin")
    d = {"msg": request.session["adminname"]}
    del request.session["securedelete"]
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT * FROM `admin` "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    for r in result1:
        if r[0] == int(request.session["adminuserid"]):
            admin = {"id": r[0], "name": r[1]}

    return render(request, "admin_editadmin_view.html", {"ar": d, "l": admin});


@csrf_exempt
def admin_deladmin_del(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    adminid = request.POST["txtadminid"]
    adminname = request.POST["txtadminname"]

    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "DELETE FROM `admin` where `adminid`='" + adminid + "'"
    cr = conn.cursor()
    cr.execute(s)
    conn.commit()
    if adminname == str(request.session["adminname"]):
        del request.session["adminname"]
    return HttpResponseRedirect("admin_editadmin")


def test(request):
    return render(request, "test.html")


def tvshow_details(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    d = {"msg": request.session["adminname"]}
    s = "SELECT  `Show name`, `Genres`, `Language`, `Seasons`,`Image`, `Cast`, `Based on`, `Link`,`Description`,`Cover Image` FROM `tvshows` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tvshows' and COLUMN_NAME NOT In ('showid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    return render(request, "tvshowdetails.html", {"ar": d, "d": result, "e": result1})


def tvshow_add(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    d = {"msg": request.session["adminname"]}
    s = "SELECT  `Show name`, `Genres`, `Language`, `Seasons`,`Image`, `Cast`, `Based on`, `Link`,`Description`,`Cover Image` FROM `tvshows` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tvshows' and COLUMN_NAME NOT In ('showid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    f = {"msg": " "}
    return render(request, "tvshowadd.html", {"ar": d, "d": result, "e": result1, "l": f})


@csrf_exempt
def tvshowadd_data(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    tvshowname = request.POST["txttvshowname"]
    genre = request.POST["txtgenre"]
    language = request.POST["txtlanguage"]
    runtime = request.POST["txtruntime"]
    filename = request.FILES["txtfile"]
    coverimage = request.FILES["txtcoverfile"]
    cast = request.POST["txtcast"]
    director = request.POST["txtdirector"]
    link1 = request.POST["txtlink"]
    description = request.POST["txtdescription"]

    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    s = "SELECT  `Show name`, `Genres`, `Language`, `Seasons`,`Image`, `Cast`, `Based on`, `Link`,`Description`,`Cover Image` FROM `tvshows`"
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tvshows' and COLUMN_NAME NOT In ('showid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    name = "TV" + link1 + "IMG" + ".jpeg"
    coverimagename = "TV" + link1 + "COVERIMG" + ".jpeg"
    for r in result:

        if r[0] == tvshowname:
            f = {"msg": "TV Show already exists in the database"}
            return render(request, "tvshowadd.html", {"ar": d, "d": result, "e": result1, "l": f})

    s1 = "INSERT INTO `tvshows` (`Show name`, `Genres`, `Language`, `Seasons`,`Image`, `Cast`,`Based on`,`Link`,`Description`,`Cover Image`) VALUES('" + tvshowname + "','" + genre + "','" + language + "','" + runtime + "','" + name + "','" + cast + "','" + director + "','" + link1 + "','" + description + "','" + coverimagename + "')"
    cr1 = conn.cursor()
    cr1.execute(s1)
    conn.commit()

    s2 = "SELECT  `Show name`, `Genres`, `Language`, `Seasons`,`Image`, `Cast`, `Based on`, `Link`,`Description`,`Cover Image` FROM `tvshows` "
    cr2 = conn.cursor()
    cr2.execute(s2)
    result2 = cr2.fetchall()

    fs = FileSystemStorage()
    fs.save(name, filename)
    f = {"msg": " "}

    fs = FileSystemStorage()
    fs.save(coverimagename, coverimage)
    f = {"msg": " "}
    return render(request, "tvshowadd.html", {"ar": d, "d": result2, "e": result1, "l": f})


def tvshow_edit(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    s = "SELECT  * FROM `tvshows` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tvshows' and COLUMN_NAME NOT In ('showid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    f = {"msg": " "}
    return render(request, "tvshowedit.html", {"ar": d, "d": result, "e": result1, "l": f})


@csrf_exempt
def tvshowedit_data(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    tvshowid = request.GET["tvshowid"]

    s = "SELECT  * FROM `tvshows` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    dic = {}
    tvshowname = ""
    for r in result:

        if r[0] == int(tvshowid):
            dic = {"tvshowid": tvshowid, "tvshowname": r[1], "genre": r[2], "language": r[3], "runtime": r[4],
                   "filename": r[5], "cast": r[6], "director": r[7], "link1": r[8], "description": r[9],
                   "coverimage": r[10]}
            break

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tvshows' and COLUMN_NAME NOT In ('showid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    return render(request, "tvshoweditdata.html", {"ar": d, "d": result, "d1": dic, "e": result1})


@csrf_exempt
def tvshowedit_data_save(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    tvshowid = request.POST["txttvshowid"]
    tvshowname = request.POST["txttvshowname"]
    genre = request.POST["txtgenre"]
    language = request.POST["txtlanguage"]
    runtime = request.POST["txtruntime"]

    cast = request.POST["txtcast"]
    director = request.POST["txtdirector"]
    link1 = request.POST["txtlink"]
    description = request.POST["txtdescription"]

    name = ""
    covername = ""

    if str(request.FILES.get('txtfile', False)) == "False":
        name = request.POST["txtfiletxt"]
    else:
        filename = request.FILES["txtfile"]
        name = "TV" + link1 + "IMG" + ".jpeg"
        fs = FileSystemStorage()
        fs.delete(name)
        fs.save(name, filename)

    if str(request.FILES.get('txtcoverfile', False)) == "False":
        covername = request.POST["txtcoverfiletxt"]
    else:
        filename = request.FILES["txtcoverfile"]
        covername = "TV" + link1 + "COVERIMG" + ".jpeg"
        fs = FileSystemStorage()
        fs.delete(covername)
        fs.save(covername, filename)

    s1 = "UPDATE `tvshows` SET  `Show name` = '" + tvshowname + "', `Genres` = '" + genre + "', `Language` = '" + language + "', `Seasons` = '" + runtime + "', `Image` = '" + name + "',`cast` = '" + cast + "', `Based on` = '" + director + "', `Link` = '" + link1 + "',`Description`='" + description + "',`Cover Image`='" + covername + "' WHERE `showid` = '" + tvshowid + "'"
    cr1 = conn.cursor()
    cr1.execute(s1)
    conn.commit()

    s = "SELECT  * FROM `tvshows` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tvshows' and COLUMN_NAME NOT In ('showid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    dic = {"tvshowid": " ", "tvshowname": " ", "genre": " ", "language": " ", "runtime": " ", "filename": " ",
           "cast": " ", "director": " ", "link1": " ", "description": " ", "coverimage": " "}

    return render(request, "tvshoweditdata.html", {"ar": d, "d": result, "d1": dic, "e": result1, })


def tvshow_delete(request):
    if not "adminname" in request.session:
        return HttpResponseRedirect("admin_login")
    d = {"msg": request.session["adminname"]}
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")

    tvshowid = request.GET["showid"]
    name = request.GET["file"]
    covername = request.GET["coverfile"]

    fs = FileSystemStorage()
    fs.delete(name)
    fs.delete(covername)

    s1 = "DELETE FROM `tvshows` WHERE `showid`='" + str(tvshowid) + "'"
    cr1 = conn.cursor()
    cr1.execute(s1)
    conn.commit()

    s = "SELECT  * FROM `tvshows` "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    s = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tvshows' and COLUMN_NAME NOT In ('showid') ORDER BY ORDINAL_POSITION"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    dic = {"tvshowid": " ", "tvshowname": " ", "genre": " ", "language": " ", "runtime": " ", "filename": " ",
           "cast": " ", "director": " ", "link1": " ", "description": " ", "coverimage": " "}

    return render(request, "tvshoweditdata.html", {"ar": d, "d": result, "d1": dic, "e": result1, })


def user_mylist(request):
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    movieid = request.GET["movieid"]

    s = "SELECT  * FROM `movies`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    for r in result:
        if int(r[0]) == int(movieid):
            name = r[1]
            break

    s = "SELECT  * FROM `mylist`  "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    if cr.rowcount == 0:
        s = "INSERT INTO `mylist`( `userid`, `movieid`, `moviename`) VALUES ('" + str(
            request.session["userid"]) + "','" + str(movieid) + "','" + name + "')"
        cr = conn.cursor()
        cr.execute(s)
        conn.commit()

    flag = "true"
    for r in result1:

        if int(r[2]) == int(movieid) and int(r[1]) == int(request.session["userid"]):

            return redirect(request.META.get('HTTP_REFERER'))

            break
        else:
            flag = "false"

    if flag == "false":
        s = "INSERT INTO `mylist`( `userid`, `movieid`, `moviename`) VALUES ('" + str(
            request.session["userid"]) + "','" + str(movieid) + "','" + name + "')"
        cr = conn.cursor()
        cr.execute(s)
        conn.commit()
        print("in else")

    return redirect(request.META.get('HTTP_REFERER'))


def user_mylisttv(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    showid = request.GET["showid"]

    s = "SELECT  * FROM `tvshows`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    for r in result:
        if int(r[0]) == int(showid):
            name = r[1]
            break

    s = "SELECT  * FROM `mylisttv`  "
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    if cr.rowcount == 0:
        print("in list")
        s = "INSERT INTO `mylisttv`( `userid`, `showid`, `showname`) VALUES ('" + str(
            request.session["userid"]) + "','" + str(showid) + "','" + name + "')"
        cr = conn.cursor()
        cr.execute(s)
        conn.commit()

    flag = "true"
    for r in result1:

        if int(r[2]) == int(showid) and int(r[1]) == int(request.session["userid"]):

            return redirect(request.META.get('HTTP_REFERER'))

            break
        else:
            flag = "false"

    if flag == "false":
        s = "INSERT INTO `mylisttv`( `userid`, `showid`, `showname`) VALUES ('" + str(
            request.session["userid"]) + "','" + str(showid) + "','" + name + "')"
        cr = conn.cursor()
        cr.execute(s)
        conn.commit()

    return redirect(request.META.get('HTTP_REFERER'))


def usermylist_page(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT  * FROM `user`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    for r in result:
        if int(r[0]) == request.session["userid"]:
            e = {"name": r[1]}

    s = "SELECT  `moviename`,`movieid` FROM `mylist` where `userid`='" + str(request.session["userid"]) + "'"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    t = []
    for r in result1:
        d = {"name": r[0], "id": r[1], "url": "usermovieview?movieid", "type": "movie"}
        t.append(d)

    s = "SELECT  `showname`,`showid` FROM `mylisttv` where `userid`='" + str(request.session["userid"]) + "'"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    for r in result1:
        d = {"name": r[0], "id": r[1], "url": "usershowview?showid", "type": "show"}
        t.append(d)

    if len(t) == 0:
        i = {"msg": "Add Movies and Shows to Your List by clicking 'My List'"}
    else:
        i = {"msg": " "}
    return render(request, "user_mylistpage.html", {"d": e, "e": t, "ar": i})


def user_mylistdelete(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    s = "SELECT  * FROM `user`  "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    for r in result:
        if int(r[0]) == request.session["userid"]:
            e = {"name": r[1]}

    id = request.GET["id"]
    type = request.GET["type"]

    if type == "show":
        s = "DELETE FROM `mylisttv` where `userid`='" + str(request.session["userid"]) + "' AND `showid`='" + id + "'"
        cr = conn.cursor()
        cr.execute(s)
        conn.commit()

    if type == "movie":
        s = "DELETE FROM `mylist` where `userid`='" + str(request.session["userid"]) + "' AND `movieid`='" + id + "'"
        cr = conn.cursor()
        cr.execute(s)
        conn.commit()

    s = "SELECT  `moviename`,`movieid` FROM `mylist` where `userid`='" + str(request.session["userid"]) + "'"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()
    t = []
    for r in result1:
        d = {"name": r[0], "id": r[1], "url": "usermovieview?movieid", "type": "movie"}
        t.append(d)

    s = "SELECT  `showname`,`showid` FROM `mylisttv` where `userid`='" + str(request.session["userid"]) + "'"
    cr = conn.cursor()
    cr.execute(s)
    result1 = cr.fetchall()

    for r in result1:
        d = {"name": r[0], "id": r[1], "url": "usershowview?showid", "type": "show"}
        t.append(d)

    if len(t) == 0:
        i = {"msg": "Add Movies and Shows to Your List by clicking 'My List'"}
    else:
        i = {"msg": " "}
    return render(request, "user_mylistpage.html", {"d": e, "e": t, "ar": i})


def user_search(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    k = {"msg": ""}
    return render(request, "user_search.html", {"d": "", "k": "0", "l": k})


@csrf_exempt
def user_search_button(request):
    if not "userid" in request.session:
        return HttpResponseRedirect("signin")
    conn = pymysql.Connect("127.0.0.1", "root", "", "netflixplus")
    name = request.POST["txtsearch"]
    fname = "%" + name + "%"
    s = "SELECT  `movieid`,`Movie name`, `Image` FROM `movies`  WHERE `Movie name` LIKE '" + fname + "' "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()
    l = []
    p = {"searchtext": name}
    for r in result:
        d = {"id": r[0], "name": r[1], "image": r[2], "link": "usermovieview?movieid"}
        l.append(d)

    if len(l) == 0:
        k = {"msg": "No result found"}
    else:
        k = {"msg": " "}

    s = "SELECT  `showid`,`Show name`, `Image` FROM `tvshows`  WHERE `Show name` LIKE '" + fname + "' "
    cr = conn.cursor()
    cr.execute(s)
    result = cr.fetchall()

    for r in result:
        d = {"id": r[0], "name": r[1], "image": r[2], "link": "usershowview?showid"}
        l.append(d)

    if len(l) == 0:
        k = {"msg": "No result found"}
    else:
        k = {"msg": " "}
    return render(request, "user_search.html", {"d": l, "k": "1", "l": k, "p": p})
