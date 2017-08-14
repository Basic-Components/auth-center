from sanic.views import HTTPMethodView
from sanic.response import json
from sanic.exceptions import abort
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
            return json({"message":"can not find the user"},401)

        if request.args['_username'] != user.username and (request.app.name not in request.args['_roles']):
            return json({"message":"you do not have permission to see other's infomation"},401)
        else:
            return json({
                "username": user.username,
                "roles": [i.rolename for i in await user.roles]
            })

    async def post(self, request, _id):
        """为用户添加权限
        """
        if request.app.name not in request.args['_roles']:
            return json({"message":"you do not have permission to add role"},401)
        else:
            try:
                user = await User.get(User._id == _id)
            except:
                return json({"message":"can not find the user"},401)
            else:
                try:
                    role = await Role.get(role.service_name == request.json["rolename"])
                except:
                    return json({"message":"can not find the rolename"},401)
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
            return json({"message":"you do not have permission to add role"},401)

        else:
            try:
                user = await User.get(User._id == _id)
            except:
                return json({"message":"can not find the user"},401)

            else:
                try:
                    role = await Role.get(role.service_name == request.json["rolename"])
                except:
                    return json({"message":"can not find the rolename"},401)
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
