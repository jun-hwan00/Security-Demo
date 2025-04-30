from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Article, User

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    db: Session = SessionLocal()
    posts = db.query(Article).all()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/post", response_class=HTMLResponse)
def post_page(request: Request):
    return templates.TemplateResponse("post.html", {"request": request})

@app.post("/create", response_class=HTMLResponse)
def create_post(request: Request, title: str = Form(...), content: str = Form(...)):
    db: Session = SessionLocal()
    new_post = Article(title=title, content=content, user_id=1)  # 사용자 연동 미구현 시 기본값
    db.add(new_post)
    db.commit()
    posts = db.query(Article).all()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})
