#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__ChinoBing__'
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, func, Float
from sqlalchemy.orm import relationship

from .database import Base

class Audio(Base):
    __tablename__ = 'audio'  # 数据表的表名

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), unique=True, nullable=False, comment='音频名称')
    size = Column(String(100), comment='文件大小')
    extension = Column(String(100), comment='文件类型')
    progress = Column(Float, default=False, comment='进度')
    data = relationship('Data', back_populates='audio')  # 'Data'是关联的类名；back_populates来指定反向访问的属性名称
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')

    # __mapper_args__ = {"order_by": created_at}  # 默认是正序，倒序加上.desc()方法

    #读取数据后，显示出来的方式
    def __repr__(self):
        return f'{self.title}_{self.size}'


class Data(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    audio_id = Column(Integer, ForeignKey('audio.id'), comment='音频文件')  # ForeignKey里的字符串格式不是类名.属性名，而是表名.字段名
    audio = relationship('Audio', back_populates='data')  # 'Audio'是关联的类名；back_populates来指定反向访问的属性名称

    segment_title = Column(String(200), comment='segment后的音频名称')
    segment_content = Column(Text, comment='segment后的音频内容')
    complete = Column(Boolean, default=False, comment='segment状态')

    def __repr__(self):
        return f'{repr(self.audio_title)}'