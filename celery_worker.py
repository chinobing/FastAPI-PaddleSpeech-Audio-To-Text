#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__ChinoBing__'
import os
import paddle
from celery import Celery
from pstext import crud
from pathlib import Path
from paddlespeech.cli.asr.infer import ASRExecutor

audio_save_path = Path("./audio")
audio_output_path = audio_save_path / "output"


capp = Celery(__name__)
capp.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
capp.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

asr_executor = ASRExecutor()


@capp.task(name="_create_task")
def create_task(title: str, audio_id:int):
    file_path = audio_output_path / title
    filelist = os.listdir(file_path)
    # 保证读取按照文件的顺序
    filelist.sort(key=lambda x: int(os.path.splitext(x)[0]))
    # 遍历输出每一个文件的名字和类型
    for file in filelist:
        text = "file"
        text = asr_executor(
            audio_file=file_path / file,
            device=paddle.get_device(), force_yes=True) # force_yes参数需要注意

        crud.update_audio_segment(audio_id = audio_id, segment_title = file, segment_content = text)
        crud.update_audio(audio_id = audio_id)


