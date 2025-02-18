import uvicorn

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api import utils, contacts, auth, users

from src.conf.config import settings
from src.services.limiter import limiter

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.state.limiter = limiter

origins = [
    "<http://localhost:8000>"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI!"}

if __name__ == "__main__":   

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


