"""
操作Role这张表,可以查看,添加或者删除一条service
"""

from sanic.views import HTTPMethodView
from sanic.response import json
from App.model import Role
from App.decorator import authorized, role_check


class RoleListSource(HTTPMethodView):
    """操作Role这张表
    """
    decorators = [role_check(),authorized()]

    async def get(self, request):
        """直接查看Role中的全部内容,如果有参数service_name,则检查该service_name是否存在
        """
        if request.args.get("service_name") is None:
            roles = await Role.select()
            return json({"message":{
                "rolelist": [{"servicename": role.service_name} for role in roles]}
                })
        else:

            role = await Role.get(Role.service_name == request.args.get("service_name"))
            print(role)
            return json({"message":True})



    async def post(self, request):
        """为Role表添加新的成员,使用inser_many,传入的必须为一个名为roles的列表,每个元素包含service_name
        """
        iq = Role.insert_many(request.json["roles"])
        try:
            result = await iq.execute()
        except Exception as e:
            return json({"message":"数据库错误","error":str(e)},500)
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
        """在Role表中删除service_name为name的权限
        """

        name = request.json["service_name"]
        dq = Role.delete().where(Role.service_name == name)
        try:
            nr = await dq
        except Exception as e:
            return json({"message":"数据库错误","error":e.message},500)
        else:
            if nr:
                return json({
                    "result": True
                })
            else:
                return json({
                    "result": False
                })
