from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .config import UPLOAD_DIR

# Création de l'application FastAPI
app = FastAPI(
    title="RAG Document Analyzer",
    description="API pour l'analyse de documents avec RAG",
    version="1.0.0",
    docs_url="/api/docs",  # Modifié pour inclure /api/
    redoc_url="/api/redoc"  # Modifié pour inclure /api/
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "RAG Document Analyzer API. Accédez à /api/docs pour la documentation."}

# Nettoyage au shutdown
@app.on_event("shutdown")
async def cleanup():
    import shutil
    try:
        shutil.rmtree(UPLOAD_DIR)
    except Exception as e:
        print(f"Erreur lors du nettoyage: {str(e)}")
