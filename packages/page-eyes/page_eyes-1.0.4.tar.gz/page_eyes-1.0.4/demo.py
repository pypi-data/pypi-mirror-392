#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : aidenmo
# @Email : aidenmo@tencent.com
# @Time : 2025/11/19 12:05
import sys
from contextvars import Context
from loguru import logger
logger.remove()

logger.add(sys.stdout,
           level='DEBUG',
           enqueue=True,
           format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                  "<level>{level: <8}</level> | "
                  "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                  "<green>{extra[trace_id]}</green> - <level>{message}</level>")
from loguru._logger import context
import loguru
l = getattr(loguru, '_logger')
current_extras = context.get()
with logger.contextualize(trace_id='abc'):
    from loguru._logger import context
    current_extras = context.get()
    trace = logger
    try:
        print(1)
        a = 0
        b= 2
        a - a - 1/logger
    except Exception as e:
        logger.exception(e)