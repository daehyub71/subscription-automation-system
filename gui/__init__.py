#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 모듈 패키지
파일명: gui/__init__.py
작성자: 청약 자동화 시스템
설명: GUI 관련 모듈들을 관리하는 패키지
"""

__version__ = "1.0.0"
__author__ = "청약 자동화 시스템"
__description__ = "tkinter 기반 GUI 모듈"

# GUI 모듈 버전 정보
GUI_VERSION = "1.0.0"
SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]

# 패키지 정보
__all__ = [
    "main_window",
    "GUI_VERSION"
]