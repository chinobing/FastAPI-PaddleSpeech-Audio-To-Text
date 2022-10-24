#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__ChinoBing__'

from datetime import datetime
from pydantic import BaseModel


class CreateAudioData(BaseModel):
    title: str
    size: str
    extension: str
    progress: float

class ReadAudioData(CreateAudioData):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CreateAudioSegment(BaseModel):
    segment_title: str
    segment_content: str
    complete: bool = False

class ReadAudioSegment(CreateAudioSegment):
    id: int

    class Config:
        orm_mode = True
