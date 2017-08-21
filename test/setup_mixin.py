import sys
sys.path.insert(0, 'auth-center.pyz')
from App import create_app
from conf import env_factory
app = create_app(env_factory('local'))

class SetUpAPPMixin: 
    @classmethod
    def setUpClass(cls):
        cls.app = app
