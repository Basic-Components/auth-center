# auth-center
restful的认证中心服务,用于维护一个用户的登录注册中心,同时维护其可用服务的列表,使用peewee和sanic

# 版本

v 0.0.1-alpha

# 数据库设计

用户只维护

+ `_id` uuid4生成的id,这是每个user的唯一主键标识
+ `username` 用户名,同样要求唯一
+ `password` 密码
+ `main_email` 注册的主email,要求唯一
+ `ctime` 创建时间

权限则维护

+ `service_name` 拥有使用权限的服务名,

用户与权限是多对多关系


ip地址维护

+ `ip` 访问的ip地址
+ `country` 访问ip指向的国家
+ `city` 访问ip指向的城市
+ `ctime` 第一次使用的时间
+ `utime` 最后一次使用的时间
+ `count` 使用的次数

用户与ip地址是1对多关系

user-agents维护,header中的`user-agents`

+ `type` 分为mobile,tablet,pc,bot,api
+ `browser` 访问的浏览器信息
+ `os` 系统
+ `device` 设备
+ `ctime` 第一次使用的时间
+ `utime` 最后一次使用的时间
+ `count` 使用的次数

用户与user-agents是1对多关系

# 结构

这个服务包括4个部分

+ 验证api部分,用于外部客户端获取登录token(无需验证)
+ 验证码部分,用于生成验证码
+ 资源api部分,用于外部客户端访问操作内部数据库
+ 安全中心服务,用于提供密码修改(需验证),密码丢失后找回(无需验证)
+ 管理员后台(需本服务权限验证)

# 统一的传递标准

接口的请求和返回都是json,内容必然会有`message`字段识别成功与否的是http状态码

+ 如果成功状态码为200
+ 如果认证失败则状态码为401
+ 如果数据库连接有问题,则状态码为500

页面则返回为html,使用jinjia2渲染

# 接口

## 认证接口

前缀:`/auth`,接口包括

+ `POST /`

    input:
    + username
    + password

    output:
    + message,token




+ `POST /logout`

    header:
    + Authorization,token

    output:
    + message:ok


+ `POST /signup`

    input:
    + username
    + password
    + main_email
    + captcha_id 验证码编号
    + captcha_code 验证码内容

    output:
    + message,bool


+ `POST /signup/ajax/username`

    input:
    + username

    output:
    + message str
    + result bool

+ `POST /signup/ajax/main_email`

    input:
    + main_email

    output:
    + message str
    + result bool



## 验证码接口

前缀:`/captcha`,接口包括

+ `POST /`

    output:
    + message,(captcha_id,pic_base64)

## 登录
