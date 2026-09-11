from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    login: str
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    login: str
    role: str
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str