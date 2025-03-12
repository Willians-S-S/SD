from pydantic import BaseModel

class Usuario(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None