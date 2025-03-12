from usuario import Usuario

user = Usuario(name="name", email="email", password="pass")

def printMy(**kwargs):
    print(kwargs)
printMy(**user.model_dump())
# print(**user.model_dump())