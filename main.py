#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
청약 분양정보 자동화 시스템 - 메인 실행 파일
파일명: main.py
작성자: 청약 자동화 시스템
설명: 프로그램의 진입점, GUI 애플리케이션 시작
"""

import os
import sys
import logging
from datetime import datetime

# 현재 디렉토리를 파이썬 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 필요한 디렉토리 생성
def create_directories():
    """필요한 디렉토리들을 생성"""
    directories = [
        'config',
        'output', 
        'logs',
        'gui',
        'api',
        'utils'
    ]
    
    for directory in directories:
        dir_path = os.path.join(current_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"디렉토리 생성: {dir_path}")

# __init__.py 파일 생성
def create_init_files():
    """필요한 __init__.py 파일들을 생성"""
    init_dirs = ['gui', 'api', 'utils']
    
    for init_dir in init_dirs:
        init_file = os.path.join(current_dir, init_dir, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(f'"""{init_dir} 모듈 패키지"""\n')

def check_dependencies():
    """필수 라이브러리 설치 확인"""
    required_modules = [
        'requests',
        'pandas', 
        'openpyxl',
        'cryptography',
        'schedule'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ 다음 라이브러리가 설치되지 않았습니다:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\n다음 명령어로 설치해주세요:")
        print(f"pip install {' '.join(missing_modules)}")
        
        # 자동 설치 여부 확인
        user_input = input("\n자동으로 설치하시겠습니까? (y/n): ").lower().strip()
        if user_input in ['y', 'yes', '예']:
            try:
                import subprocess
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_modules)
                print("✅ 라이브러리 설치 완료!")
            except Exception as e:
                print(f"❌ 자동 설치 실패: {e}")
                print("수동으로 설치해주세요.")
                return False
        else:
            return False
    
    return True

def setup_logging():
    """기본 로깅 설정"""
    log_dir = os.path.join(current_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"main_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """메인 함수"""
    print("=" * 60)
    print("🏠 청약 분양정보 자동화 시스템 v1.0")
    print("=" * 60)
    print("시스템을 초기화하고 있습니다...")
    
    # 로깅 설정
    logger = setup_logging()
    logger.info("청약 분양정보 자동화 시스템 시작")
    
    try:
        # 필요한 디렉토리 생성
        create_directories()
        create_init_files()
        
        print("✅ 디렉토리 구조 확인 완료")
        
        # 의존성 확인
        print("📦 필수 라이브러리 확인 중...")
        if not check_dependencies():
            print("❌ 필수 라이브러리가 설치되지 않았습니다.")
            input("아무 키나 누르면 종료합니다...")
            return
        
        print("✅ 필수 라이브러리 확인 완료")
        
        # tkinter 테스트
        print("🖥️ GUI 환경 확인 중...")
        try:
            import tkinter as tk
            # 간단한 tkinter 테스트
            root = tk.Tk()
            root.withdraw()  # 창 숨기기
            root.destroy()
            print("✅ GUI 환경 확인 완료")
        except Exception as e:
            print(f"❌ GUI 환경 오류: {e}")
            print("tkinter가 설치되지 않았거나 디스플레이 문제가 있습니다.")
            input("아무 키나 누르면 종료합니다...")
            return
        
        # GUI 애플리케이션 시작
        print("🚀 GUI 애플리케이션을 시작합니다...")
        logger.info("GUI 애플리케이션 시작")
        
        # GUI 모듈 import 및 실행
        try:
            from gui.main_window import SubscriptionGUI
            
            # GUI 애플리케이션 생성 및 실행
            app = SubscriptionGUI()
            app.run()
            
        except ImportError as e:
            print(f"❌ 모듈 import 오류: {e}")
            print("gui/main_window.py 파일이 존재하는지 확인해주세요.")
            logger.error(f"모듈 import 오류: {e}")
            
        except Exception as e:
            print(f"❌ GUI 실행 오류: {e}")
            logger.error(f"GUI 실행 오류: {e}")
            
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 프로그램이 중단되었습니다.")
        logger.info("사용자 인터럽트로 프로그램 종료")
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        logger.error(f"예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        logger.info("프로그램 종료")
        print("\n프로그램을 종료합니다.")

if __name__ == "__main__":
    main()