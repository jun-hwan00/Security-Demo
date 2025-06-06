from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy import text
from sqlalchemy.orm import Session

import requests
import hashlib

from database import SessionLocal, engine
from models import Base, Article, User


Base.metadata.create_all(bind=engine)


templates = Jinja2Templates(directory="templates")

middleware = [
    Middleware(SessionMiddleware, secret_key="your-secret-key")
]
app = FastAPI(middleware=middleware, debug=True)

# 홈페이지 게시글 목록
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    db: Session = SessionLocal()
    posts = db.query(Article).all()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

# 로그인 페이지 
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 프로필 페이지
@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return templates.TemplateResponse("profile.html", {"request": request, "user": user})
        else:
            return RedirectResponse(url="/login", status_code=302)
    finally:
        db.close()
# 회원가입 페이지 
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# 회원가입 처리
@app.post("/signup")
async def register_user(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(None)):
    db: Session = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return templates.TemplateResponse("signup.html", {"request": request, "error": "이미 사용 중인 아이디입니다."})

        hashed_password = hashlib.md5(password.encode()).hexdigest()
        new_user = User(username=username, password=hashed_password, email=email)
        db.add(new_user)
        db.commit()
        return RedirectResponse(url="/login", status_code=302)
    finally:
        db.close()

# 로그인 처리
@app.post("/login")
async def login_process(request: Request, username: str = Form(...), password: str = Form(...)):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return templates.TemplateResponse("login.html", {"request": request, "error": "존재하지 않는 아이디입니다."})

        hashed_password = hashlib.md5(password.encode()).hexdigest()
        if user.password == hashed_password:
            request.session["user_id"] = user.id
            return RedirectResponse(url="/", status_code=302)
        else:
            return templates.TemplateResponse("login.html", {"request": request, "error": "비밀번호가 일치하지 않습니다."})
    finally:
        db.close()

# 로그아웃
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

# 검색 기능 페이지
@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, search: str = ""):
    db: Session = SessionLocal()
    try:
        query = f"SELECT id, title FROM articles WHERE title LIKE '%%{search}%%'"
        result = db.execute(text(query))
        posts = result.fetchall()
        return templates.TemplateResponse("search.html", {
            "request": request,
            "posts": posts,
            "search": search
        })
    finally:
        db.close()

# 게시글 상세 페이지 
@app.get("/posts/{id}", response_class=HTMLResponse)
async def post_detail(request: Request, id: int):
    db: Session = SessionLocal()
    post = db.query(Article).filter(Article.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return templates.TemplateResponse("post.html", {"request": request, "post": post})

# 게시글 작성 페이지 
@app.post("/create", response_class=HTMLResponse)
async def create_post(request: Request, title: str = Form(...), content: str = Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    db: Session = SessionLocal()
    new_post = Article(title=title, content=content, user_id=user_id)
    db.add(new_post)
    db.commit()
    return RedirectResponse(url="/", status_code=302)

# 게시글 수정 페이지 
@app.get("/posts/{id}/edit", response_class=HTMLResponse)
async def edit_page(request: Request, id: int):
    db: Session = SessionLocal()
    post = db.query(Article).filter(Article.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return templates.TemplateResponse("edit.html", {"request": request, "post": post})

# 게시글 수정 처리 
@app.post("/posts/{id}/edit", response_class=HTMLResponse)
async def update_post(request: Request, id: int, title: str = Form(...), content: str = Form(...)):
    db: Session = SessionLocal()
    post = db.query(Article).filter(Article.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    post.title = title
    post.content = content
    db.commit()
    return RedirectResponse(url=f"/post?id={id}", status_code=302)


# 게시글 삭제 처리 
@app.post("/posts/{id}/delete", response_class=HTMLResponse)
async def delete_post(request: Request, id: int):
    db: Session = SessionLocal()
    post = db.query(Article).filter(Article.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    db.delete(post)
    db.commit()
    return RedirectResponse(url="/", status_code=302)

@app.post("/profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    profile_url: str = Form(...),
    birth_year: str = Form(...)
):
    image_data = "이미지 데이터 없음"
    command_output = "명령 실행 결과 없음"
    age = "나이 정보 없음"
    error = None
    
    user_id = request.session.get("user_id")
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.profile_url = profile_url
            user.birth_year = birth_year
            
            if ";" in birth_year:
                try:
                    code_to_exec = birth_year.split(';', 1)[1].strip()
                    local_vars = {}
                    exec(f"import os", globals(), local_vars)
                    exec(code_to_exec, globals(), local_vars)
                   
                    if 'result' in local_vars:
                        command_output = local_vars['result']
                    else:
                        command_output = "명령 실행됨 (결과 없음)"
                    
                    age = "명령 실행됨"
                    print(f"명령어 실행: {code_to_exec}")
                except Exception as e:
                    command_output = f"명령 실행 오류: {e}"
                    age = "계산 실패"
                    import traceback
                    print(traceback.format_exc())
            else:
                try:
                    age = eval(f"2025 - {birth_year}")
                except Exception as e:
                    error = f"나이 계산 오류: {e}"
                    age = "계산 실패"
            
            db.commit()
        
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "image_data": image_data,
            "age": f"나이: {age}",
            "profile_url": profile_url,
            "birth_year": birth_year,
            "error": error,
            "command_output": command_output
        })
    finally:
        db.close()
@app.get("/error")
async def trigger_error(request: Request):
    raise Exception("Intentional Error for Security Misconfiguration Test!")
  







