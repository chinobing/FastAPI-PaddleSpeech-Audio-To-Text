# pull official base image
FROM python:3.8-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update
RUN apt-get -y upgrade

# install ffmpeg
RUN apt-get install -y ffmpeg

# install paddlespeech
RUN apt install -y build-essential
RUN g++ -v
RUN pip install pytest-runner -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
RUN pip install paddlespeech -i https://pypi.tuna.tsinghua.edu.cn/simple

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
