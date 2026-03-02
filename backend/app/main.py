from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import auth, projects, issues, comments

Base.metadata.create_all(bind=engine)

app = FastAPI(title="IssueHub", version="1.0.0", description="A lightweight bug tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(issues.router)
app.include_router(comments.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
