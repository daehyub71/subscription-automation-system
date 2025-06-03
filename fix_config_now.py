#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
즉시 실행 설정 파일 복구 스크립트
파일명: fix_config_now.py

실행 방법: python fix_config_now.py
"""

import json
import os
import urllib.parse
import shutil
from datetime import datetime

def main():
    print("🔧 청약 시스템 설정 파일 복구 도구")
    print("=" * 50)
    
    # 설정 파일 경로 찾기
    config_paths = [
        "config/settings.json",
        "settings.json", 
        "../config/settings.json",
        "./config/settings.json"
    ]
    
    config_file = None
    for path in config_paths:
        if os.path.exists(path):
            config_file = path
            break
    
    if not config_file:
        print("❌ 설정 파일을 찾을 수 없습니다.")
        print("다음 경로들을 확인했습니다:")
        for path in config_paths:
            print(f"   - {path}")
        
        create_new = input("\n새로운 설정 파일을 생성하시겠습니까? (y/n): ").lower()
        if create_new == 'y':
            create_default_config()
        return
    
    print(f"📁 설정 파일 발견: {config_file}")
    
    try:
        # 1. 백업 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{config_file}.backup_{timestamp}"
        shutil.copy2(config_file, backup_file)
        print(f"💾 백업 생성: {backup_file}")
        
        # 2. 설정 파일 읽기
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📖 설정 파일 읽기 완료")
        
        # 3. JSON 파싱
        config = json.loads(content)
        
        # 4. 문제 서비스키 확인 및 수정
        fixed = False
        
        # API 섹션 확인
        if 'api' in config and 'service_key' in config['api']:
            service_key = config['api']['service_key']
            if isinstance(service_key, str) and '%' in service_key:
                print(f"🔍 URL 인코딩된 서비스키 발견:")
                print(f"   원본: {service_key[:30]}...")
                
                decoded_key = urllib.parse.unquote(service_key)
                config['api']['service_key'] = decoded_key
                
                print(f"   수정: {decoded_key[:30]}...")
                fixed = True
        
        # 기타 필드도 확인 (혹시 다른 곳에 URL 인코딩이 있을 수 있음)
        if 'service_key' in config:  # 루트 레벨
            service_key = config['service_key']
            if isinstance(service_key, str) and '%' in service_key:
                decoded_key = urllib.parse.unquote(service_key)
                config['service_key'] = decoded_key
                fixed = True
        
        if fixed:
            # 5. 수정된 설정 저장
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print("✅ 설정 파일 수정 완료!")
            
            # 6. 검증
            print("\n🔍 수정 결과 검증 중...")
            with open(config_file, 'r', encoding='utf-8') as f:
                test_config = json.load(f)
            
            service_key = test_config.get('api', {}).get('service_key', '')
            if '%' in service_key:
                print("⚠️  여전히 URL 인코딩된 문자가 있습니다.")
            else:
                print("✅ 검증 완료! URL 인코딩 문제가 해결되었습니다.")
        else:
            print("ℹ️  URL 인코딩 문제가 발견되지 않았습니다.")
        
        print(f"\n📊 설정 파일 상태:")
        print(f"   API 키 길이: {len(config.get('api', {}).get('service_key', ''))}")
        print(f"   이메일 설정: {'✅' if config.get('email', {}).get('sender_email') else '❌'}")
        print(f"   수신자 수: {len(config.get('email', {}).get('recipients', []))}")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        print("설정 파일 형식에 문제가 있습니다.")
        
        fix_json = input("JSON 형식 오류를 수정하시겠습니까? (y/n): ").lower()
        if fix_json == 'y':
            try_fix_json(config_file, backup_file)
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print(f"백업 파일에서 복원하려면: cp {backup_file} {config_file}")

def try_fix_json(config_file, backup_file):
    """JSON 형식 오류 수정 시도"""
    try:
        print("🔧 JSON 형식 오류 수정 시도 중...")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 일반적인 JSON 오류 수정
        # 1. 후행 쉼표 제거
        import re
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        # 2. 다시 JSON 파싱 시도
        config = json.loads(content)
        
        # 3. 수정된 내용 저장
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("✅ JSON 형식 오류 수정 완료!")
        
    except Exception as e:
        print(f"❌ JSON 수정 실패: {e}")
        print("수동으로 설정 파일을 확인해야 합니다.")

def create_default_config():
    """기본 설정 파일 생성"""
    config_dir = "config"
    config_file = os.path.join(config_dir, "settings.json")
    
    # 디렉토리 생성
    os.makedirs(config_dir, exist_ok=True)
    
    default_config = {
        "api": {
            "service_key": "",
            "max_rows": 50
        },
        "email": {
            "sender_email": "",
            "app_password": "",
            "recipients": []
        },
        "kakao": {
            "enabled": False,
            "api_key": ""
        },
        "schedule": {
            "enabled": False,
            "time": "09:00"
        }
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 기본 설정 파일 생성: {config_file}")
    print("🔑 이제 공공데이터포털 서비스키를 설정하세요.")

def manual_service_key_input():
    """수동 서비스키 입력 및 처리"""
    print("\n🔑 서비스키 수동 입력")
    print("-" * 30)
    
    service_key = input("공공데이터포털 서비스키를 입력하세요: ").strip()
    
    if not service_key:
        print("❌ 서비스키가 입력되지 않았습니다.")
        return
    
    # URL 디코딩 처리
    if '%' in service_key:
        print("🔄 URL 인코딩된 키를 디코딩합니다...")
        decoded_key = urllib.parse.unquote(service_key)
        print(f"원본: {service_key[:30]}...")
        print(f"디코딩: {decoded_key[:30]}...")
        service_key = decoded_key
    
    # 설정 파일 업데이트
    config_file = "config/settings.json"
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {"api": {}}
        
        config['api']['service_key'] = service_key
        
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("✅ 서비스키가 설정되었습니다!")
        
    except Exception as e:
        print(f"❌ 서비스키 설정 실패: {e}")

if __name__ == "__main__":
    try:
        main()
        
        print("\n" + "=" * 50)
        print("🎯 추가 옵션:")
        print("1. 서비스키 수동 입력 (s)")
        print("2. 종료 (Enter)")
        
        choice = input("선택: ").lower().strip()
        
        if choice == 's':
            manual_service_key_input()
        
        print("\n✅ 모든 작업이 완료되었습니다!")
        print("이제 청약 시스템을 다시 실행해보세요.")
        
    except KeyboardInterrupt:
        print("\n\n❌ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
    
    input("\nEnter 키를 눌러 종료...")