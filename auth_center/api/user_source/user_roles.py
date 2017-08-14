from sanic.views import HTTPMethodView
from sanic.response import json
from sanic.exceptions import abort
from auth_center.model import User, Role
from auth_center.decorator import authorized, role_check

class UserRoleSource(HTTPMethodView):
    """操作单个用户中的权限
    """
    decorators = [role_check(),authorized()]

    async def get(self, request, _id):
        """获取用户当前的权限信息"""
        try:
            user = await User.get(User._id == _id)
        except:
            return json({"message":"找不到对应用户"},401)

        if request.args['auth_id'] != user._id :
            return json({"message":"无权限查看"},401)
        else:
            return json({
                "username": user.username,
                "roles": [i.rolename for i in await user.roles]
            })

    async def post(self, request, _id):
        """为用户添加权限
        """

        try:
            user = await User.get(User._id == _id)
        except:
            return json({"message":"找不到用户"},401)
        else:
            try:
                role = await Role.get(role.service_name == request.json["service_name"])
            except:
                return json({"message":"找不到想要添加的服务权限"},401)
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

        try:
            user = await User.get(User._id == _id)
        except:
            return json({"message":"找不到用户"},401)

        else:
            try:
                role = await Role.get(role.service_name == request.json["service_name"])
            except:
                return json({"message":"找不到想要删除的服务权限"},401)
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
