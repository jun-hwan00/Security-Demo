# sql injection 보안 코드

# @app.get("/search", response_class=HTMLResponse)
# async def search_page(request: Request, search: str = ""):
#     db: Session = SessionLocal()
#     try:
#         query = text("SELECT id, title FROM articles WHERE title LIKE :search_pattern")
#         result = db.execute(query, {"search_pattern": f"%{search}%"})
#         posts = result.fetchall()
#         return templates.TemplateResponse("search.html", {
#             "request": request,
#             "posts": posts,
#             "search": search
#         })
#     finally:
#         db.close()


# 게시글 수정 보안 처리 코드

# @app.post("/posts/{id}/edit", response_class=HTMLResponse)
# async def update_post(request: Request, id: int, title: str = Form(...), content: str = Form(...)):
#     user_id = request.session.get("user_id")  # 로그인 사용자 ID 확인
#     if not user_id:
#         return RedirectResponse(url="/login", status_code=302)

#     db: Session = SessionLocal()
#     post = db.query(Article).filter(Article.id == id).first()

#     if not post:
#         db.close()
#         raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

#     # 작성자 본인인지 확인
#     if post.user_id != user_id:
#         db.close()
#         return HTMLResponse(content="""
#             <script>
#             alert("해당 게시글을 수정할 권한이 없습니다.");
#             history.back();
#             </script>
#         """, status_code=403)





# 게시글 삭제 보안 처리 코드

# @app.post("/posts/{id}/delete", response_class=HTMLResponse)
# async def delete_post(request: Request, id: int):
#     user_id = request.session.get("user_id")
#     if not user_id:
#         return RedirectResponse(url="/login", status_code=302)

#     db = SessionLocal()
#     post = db.query(Article).filter(Article.id == id).first()

#     if not post:
#         db.close()
#         return HTMLResponse(content="""
#             <script>
#                 alert("게시글이 존재하지 않습니다.");
#                 history.back();
#             </script>
#         """, status_code=404)

#     if post.user_id != user_id:
#         db.close()
#         return HTMLResponse(content="""
#             <script>
#                 alert("해당 게시글을 삭제할 권한이 없습니다.");
#                 history.back();
#             </script>
#         """, status_code=403)

#     db.delete(post)
#     db.commit()
#     db.close()

#     return RedirectResponse(url="/", status_code=302)