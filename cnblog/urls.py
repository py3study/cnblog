"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path,re_path

from blog import  views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('', views.index),
    path('index/', views.index),
    path('logout/', views.logout),
    path('code/', views.code),
    #注册
    path('zhuce/', views.zhuce),
    path('zhuce_ajax/', views.zhuce_ajax),

    #点赞或者踩灭
    path('digg/', views.digg),
    # 评论
    path('comment/', views.comment),
    # 后台管理
    path('backend/', views.backend),
    # 文章管理
    path('backend/add_article/', views.add_article),
    re_path('backend/modify_article/(?P<id>\d+)', views.modify_article),
    path('backend/delete_article/', views.delete_article),
    # 上传文件
    path('upload/', views.upload),

    #分类管理
    path('backend/add_category/', views.add_category),
    path('backend/manage_category/', views.manage_category),
    path('backend/delete_category/', views.delete_category),
    re_path('backend/modify_category/(?P<id>\d+)', views.modify_category),

    #标签管理
    path('backend/add_tag/', views.add_tag),
    path('backend/manage_tag/', views.manage_tag),
    path('backend/delete_tag/', views.delete_tag),
    re_path('backend/modify_tag/(?P<id>\d+)', views.modify_tag),

    #评论管理
    path('backend/manage_comment/', views.manage_comment),
    path('backend/delete_comment/', views.delete_comment),

    #文章详情
    re_path('(?P<username>\w+)/articles/(?P<article_id>\d+)/$', views.article_detail),
    # 跳转
    re_path('(?P<username>\w+)/(?P<condition>category|tag|achrive)/(?P<params>.*)/$', views.homesite),
    # 个人站点
    re_path('(?P<username>\w+)/$', views.homesite),
]
