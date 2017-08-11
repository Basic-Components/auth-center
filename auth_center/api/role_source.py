from sanic.views import HTTPMethodView
from sanic.response import json
from sanic.exceptions import abort
from auth_center.exception import SourceNotFound, DatabaseError
from auth_center.model import Role
from auth_center.decorator.auth_check import authorized


class RoleListSource(HTTPMethodView):
    """操作Role这张表
    """
    decorators = [authorized()]
    async def get(self, request):
        """直接查看Role中的全部内容
        """
        if (request.app.name not in request.args['_roles']):
            raise SourceNotFound("you do not have permission to see other's infomation")
        else:
            roles = await Role.select()
            return json({"rolelist":[{"rolename":role.rolename} for role in roles]})

    async def post(self, request):
        """为Role表添加新的成员,使用inser_many,传入的必须为一个名为roles的列表,每个元素包含rolename
        """
        if (request.app.name not in request.args['_roles']):
            raise SourceNotFound("you do not have permission to see other's infomation")
        else:
            iq = Role.insert_many(request.json["roles"])
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


    async def delete(self,request):
        """在Role表中删除rolename为name的权限
        """
        if (request.app.name not in request.args['_roles']):
            raise SourceNotFound("you do not have permission to see other's infomation")
        else:
            name = request.json["name"]
            dq = Role.delete().where(Role.rolename==name)
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
