from fastapi import FastAPI, UploadFile, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from db import DB
from schemas import UserCreate
import shutil
import os

app = FastAPI()
db = DB()

@app.post("/api/token")
def get_token(user: UserCreate = Body()):
    db_user = db.get_user(username=user.username, password=user.password)
    print(db_user)
    if not db_user:
        token = db.generate_token()
        db.add_user(user)
        db_user = db.get_user(username=user.username)
    return JSONResponse(db_user.dict())

@app.post("/api/admin/upload")
async def upload_file(token: str, file: UploadFile):
    user = db.get_user(token=token)
    types = ["B", "kB", "MB", "GB"]
    type = 0
    file.file.seek(0, 2)
    file_size = file.file.tell()
    await file.seek(0)
    while file_size >= 1024:
        file_size = round(file_size/1024, 2)
        type += 1
    dest = os.path.join(user.folder, file.filename)
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse({
        "name": file.filename, 
        "path": dest, 
        "size": f"{file_size} {types[type]}",
        "content_type": file.content_type
        })

@app.post("/api/admin/edit")
async def edit_file(token: str, file: UploadFile):
    user = db.get_user(token=token)
    types = ["B", "kB", "MB", "GB"]
    type = 0
    file.file.seek(0, 2)
    file_size = file.file.tell()
    await file.seek(0)
    while file_size >= 1024:
        file_size = round(file_size/1024, 2)
        type += 1
    dest = os.path.join(user.folder, file.filename)
    os.remove(dest)
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse({
        "name": file.filename, 
        "path": dest, 
        "size": f"{file_size} {types[type]}",
        "content_type": file.content_type
        })

@app.post("/api/admin/read/{filename}")
async def read_file(token: str, filename: str):
    folder = db.get_user(token=token).folder
    with open(os.path.join(folder, filename), encoding="utf-8", mode="r") as f:
        content = f.read(50)
        content += "..."
    return JSONResponse({"content": content})

@app.post("/api/admin/delete/{filename}")
async def delete_file(token: str, filename: str):
    user = db.get_user(token=token)
    dest = os.path.join(user.folder, filename)
    os.remove(dest)
    return JSONResponse({
        "name": filename, 
        "path": dest
        })

for dir in os.listdir("files"):
    app.mount(f"/{dir}", StaticFiles(directory=os.path.join(os.getcwd(), "files", dir)), name=dir)