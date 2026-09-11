from fastapi import FastAPI
from src.routers.admin import ScooterAdmin, StationAdmin, StaffAdmin
from src.routers.user import ScooterUser, authorization
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from contextlib import asynccontextmanager

from src.database import engine
from src.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server Start")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "http://localhost:3000",   
    "http://127.0.0.1:3000",
    "http://localhost:5173",     
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(StationAdmin.admin_router)
app.include_router(ScooterAdmin.admin_router)
app.include_router(StaffAdmin.admin_router)
app.include_router(ScooterUser.router)
app.include_router(authorization.router)

@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}
