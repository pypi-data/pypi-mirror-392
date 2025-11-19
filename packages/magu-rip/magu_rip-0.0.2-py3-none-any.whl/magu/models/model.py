def table(name: str, user: bool = False):
    def wrapper(cls):
        cls._table = name
        cls._user = user
        return cls
    return wrapper

class Model:
    def __init__(self):
        try:
            self._table
        except Exception:
            print(f"[Model] {self.__class__.__name__} has no table name defined at @table()")

    def __call__(self):
        return self.__dict__

# Descriptor para marcar atributos (como annotations, em Java)
class Column:
    def __init__(self,
                type,
                name: str = None,
                nullable: bool = True,
                unique: bool = False,
                id: bool = False,
                many_to_one: bool = False):
       self.type = type
       self.name = name
       self.nullable = nullable
       self.unique = unique
       self.id = id
       self.many_to_one = many_to_one

    def __set_name__(self, owner, name: str):
        self.name = name if not self.name else self.name
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)
    
    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
