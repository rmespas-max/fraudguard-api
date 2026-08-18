from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.interfaces.router import router as transactions_router

app = FastAPI(
    title="FraudGuard API",
    description="Real-time transaction fraud analysis engine",
    version="1.0.0"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check():
    return {
        "status": "healthy",
        "service": "fraudguard-api"
    }


# Include routers
app.include_router(transactions_router)
