#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__ChinoBing__'
import shutil
import os
import io
from pathlib import Path
import aiofiles
import ffmpeg
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, UploadFile, File, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from pydantic import FilePath
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from pstext import crud, schemas
from pstext.database import engine, Base, SessionLocal
import celery_worker

application = APIRouter()

templates = Jinja2Templates(directory='./pstext/templates')

Base.metadata.create_all(bind=engine)

audio_save_path = Path("./audio")
audio_raw_path = audio_save_path / "raw"
audio_output_path = audio_save_path / "output"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI BackgroundTasks
def bg_task(file_path: FilePath, title: str, db: Session):
    """ffmpeg task"""
    output_segment_path = audio_output_path / title
    os.makedirs(output_segment_path, exist_ok=True)
    ffmpeg.input(file_path).output(f'{output_segment_path}/%03d.wav', f='segment', segment_time='49', c='copy', ac='2', ar='16000').run()

    # update audio segement database(DATA) by looping folder
    db_audio = crud.get_audio_by_title(db=db, title=title)

    for x in output_segment_path.iterdir():
        if x.is_file():
            data = {
                "segment_title": x.name
            }
            crud.create_audio_segment(db = db, data = data, audio_id = db_audio.id)

    # run Celery task
    celery_worker.create_task.delay(title = title, audio_id = db_audio.id)


@application.post("/")
async def upload_files(background_tasks: BackgroundTasks, db: Session = Depends(get_db), file: UploadFile = File(...)):
    filename = file.filename
    title = filename.split('.')[0]
    ext = filename.split('.')[1]

    # check if uploading file existed already
    db_title = crud.get_audio_by_title(db, title=title)
    if db_title:
        raise HTTPException(status_code=400, detail="Audio already uploaded")    # 将传过来的文件保存

    # save file
    out_file_path = audio_raw_path / file.filename
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        size = "{}MB".format(round(len(content)/(1024*1024),3))
        await out_file.write(content)  # async write
    data = {"title": title,
            "size": size,
            "extension": ext
            }
    #create audio info
    result = crud.create_audio_info(db = db, data = data)
    # background tasks for ffmpeg file
    background_tasks.add_task(bg_task, out_file_path, title, db)

    return result


@application.get("/", response_model=schemas.ReadAudioData)
async def home(request: Request, title: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data = crud.get_data(db, title=title, skip=skip, limit=limit)

    return templates.TemplateResponse("home.html",
                                      {"request": request,
                                       "data": data})

@application.get("/delete/{audio_id}")
async def delete(request: Request, audio_id: int, db: Session = Depends(get_db)):
    # delete info from sqlite3 and return filename
    filename = crud.delete_audio(db, audio_id)
    if filename is not None:
        os.remove(f'{audio_raw_path}/{filename}')
        shutil.rmtree(f'{audio_output_path}/{filename[:-4]}')

    url = application.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

@application.get("/download/{audio_id}")
async def get_csv(request: Request, audio_id: int, db: Session = Depends(get_db)):
    segment_data = crud.get_audio_segment_data(db, audio_id)
    txt_all = []

    for row in segment_data:
        txt_all.append(row.segment_content)
    df = pd.DataFrame(txt_all)

    response = StreamingResponse(io.StringIO(df.to_csv(index=False)), media_type="text/csv")
    return response