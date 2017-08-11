"""
操作Role这张表,可以查看,添加或者删除一条service
"""

from sanic.views import HTTPMethodView
from sanic.response import json
from auth_center.model import Role
from auth_center.decorator.auth_check import authorized


class RoleListSource(HTTPMethodView):
    """操作Role这张表
    """
    decorators = [authorized()]

    async def get(self, request):
        """直接查看Role中的全部内容,如果有参数service_name,则检查该service_name是否存在
        """
        if request.args.get("service_name") is None:
            if (request.app.name not in request.args['_roles']):
                return json({"message":"没有权限查看"},401)
            else:
                roles = await Role.select()
                return json({"rolelist": [{"servicename": role.service_name} for role in roles]})
        else:
            try:
                role = await Role.get(Role.service_name == request.args.get("service_name"))
            except Exception as e:
                pass
            else:
                pass


    async def post(self, request):
        """为Role表添加新的成员,使用inser_many,传入的必须为一个名为roles的列表,每个元素包含rolename
        """
        if (request.app.name not in request.args['_roles']):
            return json({"message":"没有权限添加内容"},401)
        else:
            iq = Role.insert_many(request.json["roles"])
            try:
                result = await iq.execute()
            except Exception as e:
                return json({"message":"数据库错误","error":e.message},500))
            else:
                if result:
                    return json({
                        "result": True
                    })
                else:
                    return json({
                        "result": False
                    })

    async def delete(self, request):
        """在Role表中删除rolename为name的权限
        """
        if (request.app.name not in request.args['_roles']):
            return json({"message":"没有权限删除内容"},401)
        else:
            name = request.json["name"]
            dq = Role.delete().where(role.service_name == name)
            try:
                nr = await dq
            except Exception as e:
                return json({"message":"数据库错误","error":e.message},500))
            else:
                if result:
                    return json({
                        "result": True
                    })
                else:
                    return json({
                        "result": False
                    })
