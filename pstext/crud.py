#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__ChinoBing__'
from sqlalchemy.orm import Session
from pstext import models, schemas
from pstext.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_audio_segment_data(db:Session, audio_id: int):
    return db.query(models.Data).filter(models.Data.audio_id == audio_id).all()

def get_audio_by_title(db:Session, title: str):
    return db.query(models.Audio).filter(models.Audio.title == title).first()

def get_data(db: Session, title: str = None, skip : int = 0, limit: int = 10):
    if title:
        return db.query(models.Audio).filter(models.Audio.title.like('%'+title+'%')).all()
    return db.query(models.Audio).offset(skip).limit(limit).all()

def create_audio_info(db: Session, data : schemas.CreateAudioData):
    db_audio = models.Audio(**data)
    db.add(db_audio)
    db.commit()
    db.refresh(db_audio)
    return db_audio

# update audio conversion progress
def update_audio(audio_id: int, db: Session=next(get_db())):
    #get audio segment progress counts
    complete = db.query(models.Data).filter(models.Data.audio_id == audio_id).filter(models.Data.complete == 1).count()
    incomplete = db.query(models.Data).filter(models.Data.audio_id == audio_id).filter(
        models.Data.complete == 0).count()
    total = complete + incomplete
    progress = round(complete / total, 2)

    # get audio data
    db_audio = db.query(models.Audio).filter(models.Audio.id == audio_id).first()
    db_audio.progress = progress
    db.commit()

def delete_audio(db: Session, audio_id: int):
    db_audio = db.query(models.Audio).filter(models.Audio.id == audio_id).first()
    db_audio_segment = db.query(models.Data).filter(models.Data.audio_id == audio_id).delete()
    if db_audio:
        db.delete(db_audio)
        db.commit()

        filename = f"{db_audio.title}.{db_audio.extension}"
        return filename
    else:
        return None

def create_audio_segment(db: Session, data : schemas.CreateAudioSegment, audio_id: int):
    db_data = models.Data(**data, audio_id=audio_id)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

# update audio segment conversion staus
def update_audio_segment(audio_id: int, segment_title: str, segment_content: str,db: Session=next(get_db())):
    db_audio = db.query(models.Data).filter(models.Data.audio_id == audio_id). \
        filter(models.Data.segment_title == segment_title).first()
    db_audio.complete = not db_audio.complete
    db_audio.segment_content = segment_content
    db.commit()



