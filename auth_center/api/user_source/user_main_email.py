from sanic.views import HTTPMethodView
from sanic.response import json
from sanic.exceptions import abort
from auth_center.model import User, Role
from auth_center.decorator.auth_check import authorized

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
            return json({"message":"token is out of date"},401)

        source = token_info["source"]
        now_id = token_info["_id"]
        new_email = token_info["new_email"]
        if _id != now_id or source != type(self).__name__:
            return json({"message":"you do not have permission to update email"},401)

        else:
            try:
                user = await User.get(User._id == _id)
            except:
                return json({"message":"can not find the user"},401)

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
