from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from routers import items

app = FastAPI(
    title="FastAPI App",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(items.router)

@app.get("/")
async def root():
    return {
        "message": "FastAPI 서버가 정상적으로 실행 중입니다",
        "docs": "http://localhost:8080/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host = "127.0.0.1",
        port = 8012,
        reload = True
    )