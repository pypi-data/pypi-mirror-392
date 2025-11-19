from magu.core.server import run_server
from magu.controllers.controller import *
from magu.models.model import *
from magu.repositories.repository import MariaDBRepository
from magu.database.database import MySQLDatabase as mysql

@table(name="tabela")
class RestModel(Model):
    def __init__(self):
        super().__init__()

    id = Column(int, id=True)
    name = Column(str)
    age = Column(int)

@request_mapping("/")
class RootController(Controller):
    def __init__(self):
        super().__init__()

    @get_mapping("/")
    def get_root(self):
        return {"root": "root"}


@request_mapping("/a")
class RestController(Controller):
    def __init__(self):
        super().__init__()

    @get_mapping()
    def get(self):
        return self.rep.find_all()

    @post_mapping()
    def post(self):
        mod = RestModel()
        mod.name = "delicia"
        mod.age = 1
        return self.rep.save(mod)

    @get_mapping("/{id}")
    def get_one(self):
        return self.rep.find_by_id(self.pk)

    @get_mapping("/a/{id}")
    def get_a(self):
        return self.rep.find_by_id(id)

    @put_mapping("/{id}")
    def patch(self):
        mod = RestModel()
        mod.name = "Enzo"
        mod.age = 17
        return self.rep.update(self.pk, mod)
    
cont = RestController()
root = RootController()

if __name__ == '__main__':
    run_server()
