## 说明
模仿博客园：https://www.cnblogs.com
做的博客系统

## 运行环境

| Project | Status | Description |
|---------|--------|-------------|
| python          | 3.5.4 | 在这个版本以及以上都可以 |
| django                | 2.0.7 | 2.x版本都可以 |
| bs4                | 0.0.1 | pip3安装最新版本 |
| Pillow                | 5.2.0 | pip3安装最新版本 |

## 功能

| 路径 | 功能 | 技术说明 |
|---------|--------|-------------|
| /login/          | 登录 | ajax+验证码+用户认证组件+session |
| /zhuce/          | 注册 | form组件+ajax |
| /index/                | 首页 | Bootstrap+分页组件 |
| /username/                | 个人站点 | 分类展示(聚合和分组)+inclusion_tag |
| /username/category...                | 左侧分类展示 | 聚合和分组+inclusion_tag |
| /username/articles/article_id                | 文章详情 | 事务+F查询+评论+推荐和反对 |
| /backend/                | 后台管理 | 富文本编辑器kindeditor+bs4模块+中间件验证登录 |

## 运行方式

使用Pycharm直接运行即可，
或者使用命令
`python manage.py runserver`

## 表关系
本项目涉及8个表，表关系包含一对一，一对多，多对多！
表关系图如下：

![Image text](https://github.com/py3study/cnblog/表关系.png)

图中箭头开始的英文字母表示关联字段

按照箭头方向查询，表示正向查询，否则为反向查询

## 效果
前端：

![Image text](https://github.com/py3study/cnblog/前端.png)

后端：

![Image text](https://github.com/py3study/cnblog/后端.png)

Copyright (c) 2018-present, xiao You