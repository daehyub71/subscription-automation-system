#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스케줄러 모듈
파일명: utils/scheduler.py
작성자: 청약 자동화 시스템
설명: 일정 시간에 자동으로 시스템을 실행하는 스케줄러
"""

import threading
import time
import logging
from datetime import datetime, time as dt_time
from typing import Callable, Optional

class SystemScheduler:
    """시스템 자동 실행 스케줄러"""
    
    def __init__(self, target_function: Callable, log_callback: Optional[Callable] = None):
        """
        초기화
        Args:
            target_function (Callable): 실행할 함수
            log_callback (Optional[Callable]): 로그 콜백 함수
        """
        self.target_function = target_function
        self.log_callback = log_callback
        self.logger = logging.getLogger(__name__)
        
        # 스케줄러 상태
        self.is_running = False
        self.is_enabled = False
        self.target_time = dt_time(9, 0)  # 기본값: 09:00
        self.last_execution_date = None
        
        # 스케줄러 스레드
        self.scheduler_thread = None
        self.stop_event = threading.Event()
    
    def set_schedule(self, enabled: bool, target_time_str: str):
        """
        스케줄 설정
        Args:
            enabled (bool): 스케줄 활성화 여부
            target_time_str (str): 실행 시간 (HH:MM 형식)
        """
        try:
            self.is_enabled = enabled
            
            if enabled and target_time_str:
                # 시간 파싱
                hour, minute = map(int, target_time_str.split(':'))
                self.target_time = dt_time(hour, minute)
                
                self.log(f"📅 스케줄 설정: {'활성화' if enabled else '비활성화'} - {target_time_str}")
                
                # 스케줄러 시작
                if not self.is_running:
                    self.start_scheduler()
            else:
                self.log("📅 스케줄 비활성화")
                if self.is_running:
                    self.stop_scheduler()
                    
        except ValueError as e:
            self.log(f"❌ 스케줄 시간 형식 오류: {target_time_str} - {e}")
        except Exception as e:
            self.log(f"❌ 스케줄 설정 오류: {e}")
    
    def start_scheduler(self):
        """스케줄러 시작"""
        if self.is_running:
            self.log("⚠️ 스케줄러가 이미 실행 중입니다")
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.log(f"🚀 스케줄러 시작: 매일 {self.target_time.strftime('%H:%M')} 실행 예정")
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=2.0)
        
        self.log("⏹️ 스케줄러 중지")
    
    def _scheduler_loop(self):
        """스케줄러 메인 루프"""
        self.log("🔄 스케줄러 루프 시작")
        
        while not self.stop_event.is_set():
            try:
                if self.is_enabled:
                    current_time = datetime.now()
                    current_date = current_time.date()
                    current_time_only = current_time.time()
                    
                    # 목표 시간 체크
                    if self._should_execute(current_time_only, current_date):
                        self.log(f"⏰ 스케줄 실행 시간 도달: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        self._execute_scheduled_task()
                        self.last_execution_date = current_date
                
                # 30초마다 체크
                self.stop_event.wait(30)
                
            except Exception as e:
                self.log(f"❌ 스케줄러 루프 오류: {e}")
                time.sleep(60)  # 오류 발생 시 1분 대기
        
        self.log("🔄 스케줄러 루프 종료")
    
    def _should_execute(self, current_time: dt_time, current_date) -> bool:
        """실행 조건 체크"""
        # 이미 오늘 실행했는지 확인
        if self.last_execution_date == current_date:
            return False
        
        # 현재 시간이 목표 시간과 5분 이내인지 확인
        target_minutes = self.target_time.hour * 60 + self.target_time.minute
        current_minutes = current_time.hour * 60 + current_time.minute
        
        # 목표 시간 ± 5분 범위
        return abs(current_minutes - target_minutes) <= 5
    
    def _execute_scheduled_task(self):
        """스케줄된 작업 실행"""
        try:
            self.log("🚀 스케줄된 작업 실행 시작")
            
            # 메인 스레드에서 실행되도록 콜백 호출
            if self.target_function:
                self.target_function()
            
            self.log("✅ 스케줄된 작업 실행 완료")
            
        except Exception as e:
            self.log(f"❌ 스케줄된 작업 실행 오류: {e}")
    
    def get_status(self) -> dict:
        """스케줄러 상태 반환"""
        next_execution = None
        if self.is_enabled and self.target_time:
            today = datetime.now().date()
            next_execution_datetime = datetime.combine(today, self.target_time)
            
            # 오늘 이미 실행했거나 시간이 지났으면 내일
            if (self.last_execution_date == today or 
                datetime.now() > next_execution_datetime):
                from datetime import timedelta
                next_execution_datetime += timedelta(days=1)
            
            next_execution = next_execution_datetime.strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'is_running': self.is_running,
            'is_enabled': self.is_enabled,
            'target_time': self.target_time.strftime('%H:%M') if self.target_time else None,
            'last_execution_date': self.last_execution_date.strftime('%Y-%m-%d') if self.last_execution_date else None,
            'next_execution': next_execution
        }
    
    def log(self, message: str):
        """로그 출력"""
        self.logger.info(message)
        if self.log_callback:
            self.log_callback(message)
    
    def force_execution(self):
        """수동으로 즉시 실행"""
        self.log("🔧 수동 실행 요청")
        self._execute_scheduled_task()
    
    def get_next_execution_info(self) -> str:
        """다음 실행 정보 문자열 반환"""
        if not self.is_enabled:
            return "스케줄 비활성화"
        
        status = self.get_status()
        next_execution = status['next_execution']
        
        if next_execution:
            return f"다음 실행: {next_execution}"
        else:
            return "다음 실행 시간 계산 중..."