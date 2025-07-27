from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from portfolio import router as portfolio_router
from report import router as report_router
from stock import router as stock_router
from tax import router as tax_router

app = FastAPI()

# Allow your frontend to talk to backend when local (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Serve Vite build output
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

# ✅ API routes
app.include_router(portfolio_router, prefix="/api/portfolio")
app.include_router(report_router, prefix="/api/report")
app.include_router(stock_router, prefix="/api/stock")
app.include_router(tax_router, prefix="/api/tax")
