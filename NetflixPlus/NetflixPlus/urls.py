"""NetflixPlus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myfunctions import *
from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home_page),
    path('page1', home_page),
    path('page1.2', page_1_2),
    path('page2', page_2),
    path('page3', page_3),
    path('page4', page_4),
    path('userpayment', user_payment),
    path('usermain', user_main),
    path('usermaintvshows', user_main_tvshows),
    path('userprofile', user_profile),
    path('generateotp', generateotp),
    path('changepassword', changepassword),
    path('subscriptions', subscription),
    path('subscriptions_renew',subscriptions_renew),
    path('subscriptions_pay',subscriptions_pay),
    path('usermovieview', user_movieview),
    path('usermoviewatch', user_moviewatch),
    path('usershowview', user_showview),
    path('usershowwatch', user_showwatch),
    path('usermylist',user_mylist),
    path('usermylistpage',usermylist_page),
    path('usermylisttv',user_mylisttv),
    path('usermylistdelete',user_mylistdelete),
    path('userlogin', user_login),
    path('userlogout', user_logout),
    path('signin', sign_in),
    path('usersubscriptionrenew',usersubscriptionrenew),
    path('validate_plan',validate_plan),
    path('usersubscriptionrenewpayment',usersubscriptionrenewpayment),
    path('user_forgetpassword',user_forgetpassword),
    path('usergenerateotp',user_generateotp),
    path('userchangepassword',user_changepassword),
    path('admin_login', admin_login),
    path('admin_logout', admin_logout),
    path('admin_1', admin_1),
    path('adminmain',admin_main),
    path('admin_moviedetails', movie_details),
    path('admin_movieadd', movie_add),
    path('movieadd_data', movieadd_data),
    path('admin_movieedit', movie_edit),
    path('movieedit_data', movieedit_data),
    path('movieedit_data_save', movieedit_data_save),
    path('movie_delete', movie_delete),
    path('usersearch', user_search),
    path('usersearchbutton', user_search_button),
    path('admin_tvshowdetails', tvshow_details),
    path('admin_tvshowadd', tvshow_add),
    path('tvshowadd_data', tvshowadd_data),
    path('admin_tvshowedit', tvshow_edit),
    path('tvshowedit_data', tvshowedit_data),
    path('tvshowedit_data_save', tvshowedit_data_save),
    path('tvshow_delete', tvshow_delete),
    path('adminuserdetails', admin_userdetails),
    path('admin_userdetailedit',admin_userdetailedit),
    path('admin_userdetailssave',admin_userdetails_save),
    path('admin_userdelete',admin_user_delete),
    path('admin_useractivate',admin_user_activate),
    path('adminplans',admin_plans),
    path('admin_plans_save',admin_plans_save),
    path('admin_changepassword',admin_changepassword),
    path('admin_changepassword_save',admin_changepassword_save),
    path('admin_addadmin',admin_addadmin),
    path('admin_addadmin_save',admin_addadmin_save),
    path('admin_editadmin',admin_editadmin),
    path('admin_editadmin_save',admin_editadmin_save),
    path('admin_deladmin',admin_deladmin),
    path('admin_deladmin_del',admin_deladmin_del),
    path('addreview',addreview),
    path('reviewdelete', deletereview),
    path('editreview',editreview),
    path('test',test)

]
