from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import DatabaseConfig
from routes.auth import router as auth_router
from routes.master_data import router as master_data_router
from routes.data_quality import router as data_quality_router
from routes.reports import router as reports_router
from services.auth_service import RBACService

app = FastAPI(
    title="Master Data Management System",
    description="MDM System with RBAC, Data Quality, and Reporting",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(master_data_router)
app.include_router(data_quality_router)
app.include_router(reports_router)

@app.on_event("startup")
async def startup_event():
    DatabaseConfig.init_database()
    try:
        RBACService.register_user("admin", "admin@mdm.com", "admin123", "admin")
    except:
        pass

@app.get("/")
async def root():
    return {"message": "Master Data Management System API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)