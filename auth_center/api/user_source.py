from sanic.views import HTTPMethodView
from sanic.response import json
from sanic.exceptions import abort
from auth_center.exception import SourceNotFound, DatabaseError
from auth_center.model import User, Role
from auth_center.decorator.auth_check import authorized


class UserRoleSource(HTTPMethodView):
    """操作单个用户中的权限
    """
    decorators = [authorized()]

    async def get(self, request, _id):
        """获取用户当前的权限信息"""
        try:
            user = await User.get(User._id == _id)
        except:
            raise SourceNotFound("can not find the user")
        if request.args['_username'] != user.username and (request.app.name not in request.args['_roles']):
            raise SourceNotFound("you do not have permission to see other's infomation")
        else:
            return json({
                "username": user.username,
                "roles": [i.rolename for i in await user.roles]
            })

    async def post(self, request, _id):
        """为用户添加权限
        """
        if request.app.name not in request.args['_roles']:
            raise SourceNotFound("you do not have permission to add role")
        else:
            try:
                user = await User.get(User._id == _id)
            except:
                raise SourceNotFound("can not find the user")

            else:
                try:
                    role = await Role.get(Role.rolename == request.json["rolename"])
                except:
                    raise SourceNotFound("can not find the rolename")
                else:
                    try:
                        result = await user.roles.add(role)
                    except:
                        return json({
                            "result": False
                        })
                    else:
                        return json({
                            "result": True
                        })

    async def delete(self, request, _id):
        """为用户删除权限
        """
        if request.app.name not in request.args['_roles']:
            raise SourceNotFound("you do not have permission to add role")
        else:
            try:
                user = await User.get(User._id == _id)
            except:
                raise SourceNotFound("can not find the user")

            else:
                try:
                    role = await Role.get(Role.rolename == request.json["rolename"])
                except:
                    raise SourceNotFound("can not find the rolename")
                else:
                    try:
                        result = await user.roles.remove(role)
                    except:
                        return json({
                            "result": False
                        })
                    else:
                        return json({
                            "result": result
                        })
        return json('I am delete method')


class UserListSource(HTTPMethodView):
    """操作User这张表
    """
    async def options(self, request):
        return json({'message':'ok'})
    @authorized()
    async def get(self, request):
        """直接查看User中的全部内容,可以添加参数name查看username为name的用户信息
        """
        if (request.app.name not in request.args['_roles']):
            raise SourceNotFound("you do not have permission to see other's infomation")
        else:
            name = request.args.get("name")
            if name:
                try:
                    user = await User.get(User.username == name)
                except:
                    raise SourceNotFound("can not find the user")
                else:
                    users = [user]
            else:
                users = await User.select()
            return json({"userlist": [
                {"_id": str(user._id),
                 "username": user.username,
                 "main_email":user.main_email,
                 "roles": [i.rolename for i in await user.roles]} for user in users]
            })

    async def post(self, request):
        """为User表添加新的成员,使用inser_many,传入的必须为一个名为users的列表,每个元素包含username和password和main_email
        """
        if (request.app.name not in request.args['_roles']):
            raise SourceNotFound("you do not have permission to see other's infomation")
        else:
            iq = User.insert_many([{"_id": uuid.uuid4(),
                                    "username": i["username"],
                                    'password':i['password'],
                                    "main_email":i['main_email']
                                    } for i in request.json["users"]])
            try:
                result = await iq.execute()
            except Exception as e:
                raise DatabaseError(e.message)
            else:
                if result:
                    return json({
                        "result": True
                    })
                else:
                    return json({
                        "result": False
                    })
    @authorized()
    async def delete(self, request):
        """在User表中删除username为name的用户
        """
        if (request.app.name not in request.args['_roles']):
            raise SourceNotFound("you do not have permission to see other's infomation")
        else:
            name = request.json["name"]
            dq = User.delete().where(User.username == name)
            try:
                nr = await dq
            except Exception as e:
                raise DatabaseError(e.message)
            else:
                if result:
                    return json({
                        "result": True
                    })
                else:
                    return json({
                        "result": False
                    })

class UserPasswordSource(HTTPMethodView):
    """操作单个用户中的密码
    """
    decorators = [authorized()]

    async def post(self, request, _id):
        """为用户修改password,需要传入一个{"token":xxx}
        """

        token = request.json["token"]
        try:
            token_info = request.app.serializer.loads(token,request.app.config['TOKEN_TIME'])
        except SignatureExpired as e:
            raise SourceNotFound("token is out of date")
        source = token_info["source"]
        now_id = token_info["_id"]
        new_password = token_info["new_password"]
        if _id != now_id or source != type(self).__name__:
            raise SourceNotFound("you do not have permission to update email")
        else:
            try:
                user = await User.get(User._id == _id)
            except:
                raise SourceNotFound("can not find the user")
            else:
                try:
                    user.password = new_password
                    result = await user.save()
                except Exception as e:
                    print(e)
                    return json({
                        "result": False
                    })
                else:
                    return json({
                        "result": True
                    })


class UserEmailSource(HTTPMethodView):
    """操作单个用户中的email
    """
    decorators = [authorized()]

    async def post(self, request, _id):
        """为用户修改email,需要传入一个{"token":xxx}
        """

        token = request.json["token"]
        try:
            token_info = request.app.serializer.loads(token,request.app.config['TOKEN_TIME'])
        except SignatureExpired as e:
            raise SourceNotFound("token is out of date")
        source = token_info["source"]
        now_id = token_info["_id"]
        new_email = token_info["new_email"]
        if _id != now_id or source != type(self).__name__:
            raise SourceNotFound("you do not have permission to update email")
        else:
            try:
                user = await User.get(User._id == _id)
            except:
                raise SourceNotFound("can not find the user")
            else:
                try:
                    user.main_email = new_email
                    result = await user.save()
                except Exception as e:
                    print(e)
                    return json({
                        "result": False
                    })
                else:
                    return json({
                        "result": True
                    })
