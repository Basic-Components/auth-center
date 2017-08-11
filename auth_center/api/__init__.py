from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import abort
from sanic.exceptions import NotFound,Unauthorized
from itsdangerous import SignatureExpired
from sanic_cors import cross_origin

api = Blueprint('api')

from .user_source import UserRoleSource, UserListSource, UserPasswordSource,UserEmailSource
from .role_source import RoleListSource

#UserRoleSource.decorators.append(cross_origin(api))
#UserListSource.decorators.append(cross_origin(api))
#UserPasswordSource.decorators.append(cross_origin(api))
#UserEmailSource.decorators.append(cross_origin(api))
#RoleListSource.decorators.append(cross_origin(api))

api.add_route(UserRoleSource.as_view(), '/user_role/<_id>')
api.add_route(UserPasswordSource.as_view(), '/user_password/<_id>')
api.add_route(UserEmailSource.as_view(), '/user_email/<_id>')
api.add_route(UserListSource.as_view(), '/users')
api.add_route(RoleListSource.as_view(), '/roles')
