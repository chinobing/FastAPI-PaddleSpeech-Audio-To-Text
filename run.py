#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__ChinoBing__'
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from pstext import application

app = FastAPI(
    title='FastAPI PaddleSpeech Audio To Text Docs',
    description='FastAPI PaddleSpeech Audio To Text API接口文档，项目代码：https://github.com/chinobing/FastAPI-PaddleSpeech-Audio-To-Text',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redocs',
)

# mount表示将某个目录下一个完全独立的应用挂载过来，这个不会在API交互文档中显示
app.mount(path='/static', app=StaticFiles(directory='./pstext/static'), name='static')  # .mount()不要在分路由APIRouter().mount()调用，模板会报错


app.include_router(application, tags=['paddlespeech audio to text'])

if __name__ == '__main__':
    uvicorn.run('run:app', host='0.0.0.0', port=8000, workers=4)
