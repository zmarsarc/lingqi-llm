# 指南


## 1. 如何通过管理员接口添加用户
如果使用默认的管理员端口8001，那么按如下方式添加用户

    POST http://host:8001/admin/user
    {
        "username": username,
        "password": password
    }

成功后可以通过如下方式查看用户列表

    GET http://host:8001/admin/users

## 2. 如何使用用户侧API
用户侧API端口默认8000，首先需要登陆拿token，使用如下方式登陆

    // 目前还是明文密码
    POST http://host:8000/app/v1/login
    {
        "username": username,
        "password": password
    }

    -->
    {
        "code": 0,
        "msg": "ok",
        "token", access_token
    }

保存这个token，在访问用户侧端口时，发送的请求头部携带此token，在http header中增加字段：

    headers:
    Authorization: Basic <access_token>

就可以访问用户侧端口了。