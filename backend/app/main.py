from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import admin, auth, categories, documents, providers, reviews
from app.core.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception(_: Request, exc: Exception):
    if settings.environment == "development":
        return JSONResponse(status_code=500, content={"success": False, "message": str(exc)})
    return JSONResponse(status_code=500, content={"success": False, "message": "Internal server error"})


@app.get("/api/health")
def health():
    return {"success": True, "message": "LSPD API is healthy"}


app.include_router(auth.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(providers.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
