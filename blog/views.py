from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from blog.models import Article, UserInfo, Blog, Category, Tag, ArticleUpDown, Comment, Article2Tag
from django.db.models import Sum, Avg, Max, Min, Count
from django.db.models import F
import json
from django.http import JsonResponse
from django.db import transaction
from cnblog import settings  # 导入settings。注意:cnblog为项目名
import os
from bs4 import BeautifulSoup
from blog.form import UserForm
from utils.code import check_code
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# def page_html(request,data):
#     try:
#         page_num = int(request.GET.get('page', 1))
#     except Exception:
#         page_num = 1
#
#     return Pagination(page_num, len(data))

def code(request):
    """
    生成图片验证码
    :param request:
    :return:
    """
    img,random_code = check_code()
    request.session['random_code'] = random_code
    from io import BytesIO
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())

# Create your views here.
def login(request):  # 登录
    if request.method == "POST":
        username = request.POST.get("user")
        pwd = request.POST.get("pwd")
        code = request.POST.get('code')
        response = {"state": False}
        if code.upper() != request.session['random_code'].upper():
            response["msg"] = '验证码错误!'
            return HttpResponse(json.dumps(response))
            # return render(request, 'login.html', {'msg': '验证码错误'})
        # 用户验证成功,返回user对象,否则返回None
        user = auth.authenticate(username=username, password=pwd)

        if user:
            # 查询当前用户对象
            user_obj = UserInfo.objects.filter(username=username).first()
            # 增加session
            request.session['is_login'] = True
            request.session['user'] = username
            # 更新最后登录时间
            request.session['last_time'] = str(user_obj.last_login)
            user_obj.save()

            # 登录,注册session
            # 全局变量 request.user=当前登陆对象(session中)
            auth.login(request, user)
            # return redirect("/index/")
            response["state"] = True

        response["msg"] = '用户名或者密码错误!'
        return HttpResponse(json.dumps(response))

    return render(request, "login.html")

#装饰器，用来判断用户是否登录
def required_login(func):
    def inner(*args,**kwargs):
        request = args[0]  # 响应请求
        if request.session.get("is_login"): #判断登录状态,如果为True
            return func(*args,**kwargs)  # 执行视图函数
        else:
            if request.is_ajax():  # 此时未登录，判断ajax请求
                #返回一个json信息，并指定url
                return HttpResponse(json.dumps({"state":False,'url':'/login/'}))

            return render(request,"no_login.html")
            #return redirect("/login/")  # 302重定向

    return inner

def index(request):  # 首页
    article_list = Article.objects.all()  # 查询所有文章
    paginator = Paginator(article_list, 3)  # 每页显示2条

    # 异常判断
    try:
        # 当前页码，如果取不到page参数，默认为1
        current_num = int(request.GET.get("page", 1))  # 当前页码
        article_list = paginator.page(current_num)  # 获取当前页码的数据
    except Exception:  # 出现异常时
        article_list = paginator.page(1)  # 强制更新为第一页
        current_num = 1

    #  如果页数十分多时，换另外一种显示方式
    if paginator.num_pages > 9:  # 一般网页展示11页,左5页,右5页,加上当前页,共11页
        if current_num - 4 < 1:  # 如果前5页小于1时
            pageRange = range(1, 9)  # 页码的列表:范围是初始状态
        elif current_num + 4 > paginator.num_pages:  # 如果后5页大于总页数时
            # 页码的列表:范围是(当前页-5,总页数+1)。因为range顾头不顾尾,需要加1
            pageRange = range(current_num - 4, paginator.num_pages + 1)
        else:
            # 页码的列表:后5页正常时,页码范围是(当前页-5,当前页+6)。注意不是+5,因为range顾头不顾尾！
            pageRange = range(current_num - 4, current_num + 5)
    else:
        pageRange = paginator.page_range  # 页码的列表

    return render(request, "index.html", {"article_list": article_list,"paginator": paginator, "current_num": current_num,"pageRange":pageRange})

def logout(request):  # 注销
    auth.logout(request)
    return redirect("/index/")

def zhuce(request):  # 注册
    if request.method == "POST":
        # 将post数据传给UserForm
        form = UserForm(request.POST)

    else:  # 默认是get请求(地址栏输入访问时)
        form = UserForm()  # 没有表单数据的form
    return render(request, "zhuce.html", {"form": form})


def zhuce_ajax(request):  # 注册ajax请求处理
    if request.method == "POST":  # 判断POST请求
        print(request.POST)
        form = UserForm(request.POST)  # 将post数据传给自定义类
        result = {"state": False, "name": "", "pwd": "", "r_pwd": ""}
        # print(1)
        if form.is_valid():
            # print(2)
            name = request.POST.get("name")
            pwd = request.POST.get("pwd")
            # 创建普通用户
            ret = UserInfo.objects.create_user(username=name, password=pwd)
            if ret:
                result["state"] = True
            return HttpResponse(json.dumps(result, ensure_ascii=False))
        else:
            print(form.errors)
            if form.errors:  # 判断有错误信息的情况下
                if form.errors.get("name"):
                    result["name"] = form.errors.get("name")[0]
                if form.errors.get("pwd"):
                    result["pwd"] = form.errors.get("pwd")[0]
                if form.errors.get("r_pwd"):
                    result["r_pwd"] = form.errors.get("r_pwd")[0]

                g_error = form.errors.get("__all__")  # 接收全局钩子错误信息
                if g_error:  # 判断有错误信息的情况下
                    g_error = g_error[0]  # 取第一个错误信息
                    result["r_pwd"] = g_error

                return HttpResponse(json.dumps(result, ensure_ascii=False))


# def query_current_site(request,username):  # 查询当前站点的博客标题
#     # 查询当前站点的用户对象
#     user = UserInfo.objects.filter(username=username).first()
#     if not user:
#         return render(request, "not_found.html")
#
#     # 查询当前站点对象
#     blog = user.blog
#     return blog

def homesite(request, username, **kwargs):  # 个人站点主页
    print("kwargs", kwargs)
    print(request.path)

    # 查询当前站点的用户对象
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, "not_found.html")
    # 查询当前站点对象
    blog = user.blog

    # 查询当前用户发布的所有文章
    if not kwargs:
        article_list = Article.objects.filter(user__username=username)
    else:
        condition = kwargs.get("condition")
        params = kwargs.get("params")
        # 判断分类、随笔、归档
        if condition == "category":
            # 查询当前分类的文章列表
            article_list = Article.objects.filter(user__username=username).filter(category__title=params)
        elif condition == "tag":
            # 查询当前标签的文章列表
            article_list = Article.objects.filter(user__username=username).filter(tags__title=params)
        else:
            # 查询当前归档的文章列表
            year, month = params.split("/")
            article_list = Article.objects.filter(user__username=username).filter(create_time__year=year,
                                                                                  create_time__month=month)
    return render(request, "homesite.html", {"blog": blog, "username": username, "article_list": article_list})


def article_detail(request, username, article_id):  # 文章详情
    # 查询当前站点的用户对象
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, "not_found.html")
    # 查询当前站点对象
    blog = user.blog

    # 查询指定id的文章
    article_obj = Article.objects.filter(pk=article_id).first()
    # 当前用户id
    user_id = UserInfo.objects.filter(username=username).first().nid

    comment_list = Comment.objects.filter(article_id=article_id)
    dict = {"blog": blog,
            "username": username,
            'article_obj': article_obj,
            "user_id": user_id,
            "comment_list": comment_list,
            }

    return render(request, 'article_detail.html', dict)

@required_login
def digg(request):  # 点赞和踩灭
    print(request.POST)
    if request.method == "POST":
        # ajax发送的过来的true和false是字符串，使用json反序列化得到布尔值
        is_up = json.loads(request.POST.get("is_up"))
        article_id = request.POST.get("article_id")
        user_id = request.user.pk

        response = {"state": True, "msg": None}  # 初始状态
        # 判断当前登录用户是否对这篇文章做过点赞或者踩灭操作
        obj = ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
        if obj:
            response["state"] = False  # 更改状态
            response["handled"] = obj.is_up  # 获取之前的操作,返回true或者false
            print(obj.is_up)
        else:
            with transaction.atomic():  # 使用事务
                # 插入一条记录
                new_obj = ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
                if is_up:  # 判断为推荐
                    Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
                else:  # 反对
                    Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)

        return JsonResponse(response)

    else:
        return HttpResponse("非法请求")

@required_login
def comment(request):  # 用户评论
    print(request.POST)
    if request.method == "POST":
        # 获取数据
        user_id = request.user.pk
        article_id = request.POST.get("article_id")
        content = request.POST.get("content")
        pid = request.POST.get("pid")
        # 生成评论对象
        with transaction.atomic():  # 增加事务
            # 评论表增加一条记录
            comment = Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                             parent_comment_id=pid)
            # 当前文章的评论数加1
            Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

        response = {"state": False}  # 初始状态

        if comment.user_id:  # 判断返回值
            response = {"state": True}

        # 响应体增加3个变量
        response["timer"] = comment.create_time.strftime("%Y-%m-%d %X")
        response["content"] = comment.content
        response["user"] = request.user.username

        return JsonResponse(response)  # 返回json对象

    else:
        return HttpResponse("非法请求")

@required_login
def backend(request):  # 后台管理首页
    user = request.user
    # 当前用户文章列表
    article_list = Article.objects.filter(user=user)
    # 因为是在templates的下一层，所以需要指定目录backend
    return render(request, "backend/backend.html", {"user": user, "article_list": article_list})

@required_login
def add_article(request):  # 添加文章
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        user = request.user
        cate_pk = request.POST.get("cate")
        tags_pk_list = request.POST.getlist("tags")
        print(tags_pk_list)
        # 使用BeautifulSoup过滤html标签
        soup = BeautifulSoup(content, "html.parser")
        # 文章过滤：
        for tag in soup.find_all():
            print(tag.name)
            if tag.name in ["script", ]:  # 包含script标签时
                tag.decompose()

        # 切片文章文本
        desc = soup.text[0:150]  # 文章描述
        # 插入到Article表,注意content=str(soup)
        article_obj = Article.objects.create(title=title, content=str(soup), user=user, category_id=cate_pk, desc=desc)

        for tag_pk in tags_pk_list:  # 插入关系表
            print(tag_pk)
            # 由于是中间模型，只能安装普通表查询才行
            ret = Article2Tag.objects.create(article_id=article_obj.pk, tag_id=tag_pk)
            print(ret)

        return redirect("/backend/")  # 跳转后台首页

    else:
        # print(request.user)
        # print(request.user.blog)
        blog = request.user.blog
        # 当前用户所有分类列表
        cate_list = Category.objects.filter(blog=blog)
        # 当前用户所有标签列表
        tags = Tag.objects.filter(blog=blog)
        dict = {
            "blog": blog,
            "cate_list": cate_list,
            "tags": tags,
        }

    return render(request, "backend/add_article.html", dict)

@required_login
def upload(request):  #上传文件
    print(request.FILES)
    obj = request.FILES.get("upload_img")  # 获取文件对象
    name = obj.name  # 文件名
    # 文件存储的绝对路径
    path = os.path.join(settings.BASE_DIR, "static", "upload", name)
    with open(path, "wb") as f:
        for line in obj:  # 遍历文件对象
            f.write(line)  # 写入文件

    # 必须返回这2个key
    res = {
        # 为0表示没有错误,如果有错误,设置为1。增加一个key为message,用来显示指定的错误
        "error": 0,
        # 图片访问路径，必须能够直接访问到
        "url": "/static/upload/" + name
    }

    return HttpResponse(json.dumps(res))  # 必须返回Json

@required_login
def delete_article(request):  # 删除文章
    print(request.POST)
    response = {"state": False}
    if request.method == "POST":
        id = request.POST.get("id")
        # print(id)
        #删除这篇文章的所有tag关系
        Article2Tag.objects.filter(article_id=id).delete()

        # 再删除文章
        ret = Article.objects.filter(pk=id).delete()  # 返回元组
        print(ret)

        if ret[0]:  # 取值为1的情况下
            response['state'] = True
        else:  # 取值为0的情况下
            response['state'] = False
            response['msg'] = "删除失败!"

    response['msg'] = "非法请求!"
    return HttpResponse(json.dumps(response))

@required_login
def modify_article(request, id):  # 修改文章
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        # user = request.user
        create_time = request.POST.get("create_time")
        comment_count = request.POST.get("comment_count")
        up_count = request.POST.get("comment_count")
        down_count = request.POST.get("down_count")
        cate_pk = request.POST.get("cate")
        tags_pk_list = request.POST.getlist("tags")
        # print(tags_pk_list)
        # 使用BeautifulSoup过滤html标签
        soup = BeautifulSoup(content, "html.parser")
        # 文章过滤：
        for tag in soup.find_all():
            # print(tag.name)
            if tag.name in ["script", ]:  # 包含script标签时
                tag.decompose()

        # 切片文章文本
        desc = soup.text[0:150]  # 文章描述
        # 更新到Article表,注意content=str(soup)
        res = Article.objects.filter(pk=id).update(title=title, content=str(soup), create_time=create_time,
                                             comment_count=comment_count, up_count=up_count, down_count=down_count,
                                             category_id=cate_pk, desc=desc)

        # print(tags_pk_list)
        # 由于是中间模型，只能安装普通表查询才行
        Article2Tag.objects.filter(article_id=id).delete()  # 删除当前文章所有标签
        for tag_pk in tags_pk_list:  # 插入关系表
            # print(tag_pk)
            Article2Tag.objects.create(article_id=id, tag_id=tag_pk)  # 添加关系


        if res:
            return redirect("/backend/")  # 跳转后台首页

    article = Article.objects.filter(pk=id).first()  # 默认当前文章对象
    # 当前用户所有分类
    cate_list = Category.objects.filter(blog=request.user.blog)
    # 当前用户所有标签
    tags = Tag.objects.filter(blog_id=request.user.blog.pk)
    # 从关系表中获取标签的tag_id 列表，一个文章对应多个标签
    tag_list = []  # 这个列表是为了做选中效果
    for i in Article2Tag.objects.filter(article_id=id).values("tag_id"):
        tag_list.append(i['tag_id'])

    # print(tag_list)

    return render(request, "backend/modify_article.html",
                  {"article": article, "cate_list": cate_list, "tags": tags,"tag_list":tag_list})

@required_login
def add_category(request):  # 添加分类
    if request.method == "POST":
        cate = request.POST.get("cate")
        response = {"state":False}
        if Category.objects.filter(title=cate).exists():  # 判断当前用户分类是否存在
            response["msg"] = "分类标题已经存在!"
        else:
            # 查询当前用户的站点
            user = UserInfo.objects.filter(username=request.user.username).first()
            # 增加分类
            ret = Category.objects.create(title=cate,blog=user.blog)
            if ret:
                response["state"] = True

        return JsonResponse(response)  # 返回Json对象

    # 当前用户所有分类
    cate_list = Category.objects.filter(blog=request.user.blog)

    return render(request, "backend/add_category.html",{"cate_list":cate_list})

@required_login
def manage_category(request):  # 管理分类
    # 当前用户所有分类
    category_list = Category.objects.filter(blog=request.user.blog)

    return render(request, "backend/manage_category.html", {"category_list": category_list})

@required_login
def delete_category(request):  # 删除分类
    print(request.POST)
    response = {"state": False}
    if request.method == "POST":
        id = request.POST.get("id")
        # print(id)
        #将所有文章分类为此id的,值设置为空
        Article.objects.filter(category_id=id).update(category_id=None)

        # 再删除分类
        ret = Category.objects.filter(pk=id).delete()  # 返回元组
        print(ret)

        if ret[0]:  # 取值为1的情况下
            response['state'] = True
        else:  # 取值为0的情况下
            response['state'] = False
            response['msg'] = "删除失败!"

    response['msg'] = "非法请求!"

    return JsonResponse(response)

@required_login
def modify_category(request,id):  # 修改分类
    if request.method == "POST":
        cate = request.POST.get("cate")
        ret = Category.objects.filter(pk=id).update(title=cate)
        response = {"state": False}
        if ret:
            response["state"] = True

        return JsonResponse(response)

    category = Category.objects.filter(pk=id).first()
    return render(request, "backend/modify_category.html", {"category": category})

@required_login
def add_tag(request):  # 添加标签
    if request.method == "POST":
        tag = request.POST.get("tag")
        response = {"state":False}
        if Tag.objects.filter(title=tag).exists():  # 判断当前用户标签是否存在
            response["msg"] = "标签名称已经存在!"
        else:
            # 查询当前用户的站点
            user = UserInfo.objects.filter(username=request.user.username).first()
            # 增加标签
            ret = Tag.objects.create(title=tag,blog=user.blog)
            if ret:
                response["state"] = True

        return JsonResponse(response)  # 返回Json对象

    # 当前用户所有标签
    tag_list = Tag.objects.filter(blog=request.user.blog)

    return render(request, "backend/add_tag.html",{"tag_list":tag_list})

@required_login
def manage_tag(request):  # 管理标签
    # 当前用户所有标签
    tag_list = Tag.objects.filter(blog_id=request.user.blog.pk)

    return render(request, "backend/manage_tag.html", {"tag_list": tag_list})

@required_login
def delete_tag(request):  # 删除标签
    print(request.POST)
    response = {"state": False}
    if request.method == "POST":
        id = request.POST.get("id")
        # print(id)
        #将关系表中标签为此id的删除掉
        Article2Tag.objects.filter(tag_id=id).delete()

        # 再删除标签
        ret = Tag.objects.filter(pk=id).delete()  # 返回元组
        print(ret)

        if ret[0]:  # 取值为1的情况下
            response['state'] = True
        else:  # 取值为0的情况下
            response['state'] = False
            response['msg'] = "删除失败!"

    response['msg'] = "非法请求!"

    return JsonResponse(response)

@required_login
def modify_tag(request,id):  # 修改标签
    if request.method == "POST":
        print(request.POST)
        tag = request.POST.get("tag")
        ret = Tag.objects.filter(pk=id).update(title=tag)
        response = {"state": False}
        if ret:
            response["state"] = True

        return JsonResponse(response)

    tag = Tag.objects.filter(pk=id).first()
    return render(request, "backend/modify_tag.html", {"tag": tag})