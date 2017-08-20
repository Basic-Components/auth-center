from sanic.views import HTTPMethodView
from sanic.response import json
from sanic.exceptions import abort
from App.model import User, Role
from App.decorator import authorized, role_or_self_check

class UserRoleSource(HTTPMethodView):
    """操作单个用户中的权限
    """
    decorators = [role_or_self_check(),authorized()]

    async def get(self, request, _id):
        """获取用户当前的权限信息"""
        try:
            user = await User.get(User._id == _id)
        except:
            return json({"message":"找不到对应用户"},400)

        else:
            return json({
                "username": user.username,
                "roles": [i.service_name for i in await user.roles]
            })

    async def post(self, request, _id):
        """为用户添加权限需要json传入service_name字段实现
        """
        if (request.app.name not in request.args['auth_roles']):
            return json({"message":"没有权限添加权限"},401)

        try:
            user = await User.get(User._id == _id)
        except:
            return json({"message":"找不到用户"},400)
        else:
            try:
                role = await Role.get(Role.service_name == request.json["service_name"])
            except:
                return json({"message":"找不到想要添加的服务权限"},400)
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
        if (request.app.name not in request.args['auth_roles']):
            return json({"message":"没有权限删除权限"},401)
        try:
            user = await User.get(User._id == _id)
        except:
            return json({"message":"找不到用户"},400)

        else:
            try:
                role = await Role.get(Role.service_name == request.json["service_name"])
            except Exception as e:
                print(e)
                return json({"message":"找不到想要删除的服务权限"},400)
            else:
                try:
                    result = await user.roles.remove(role)
                except:
                    return json({
                        "result": False
                    })
                else:
                    return json({
                        "result": True
                    })
