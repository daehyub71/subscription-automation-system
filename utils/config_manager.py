#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
설정 관리 모듈 (GUI 맞춤 버전)
파일명: utils/config_manager.py
작성자: 청약 자동화 시스템
설명: 애플리케이션 설정 저장/불러오기, 암호화 관리, URL 인코딩 문제 해결
"""

import os
import json
import base64
import urllib.parse
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️ cryptography 패키지가 설치되지 않았습니다. 암호화 기능이 비활성화됩니다.")

class ConfigManager:
    """설정 파일 관리 클래스 (JSON 형식, 암호화 지원, URL 인코딩 문제 해결)"""
    
    def __init__(self, config_dir: str = "config"):
        """
        초기화
        Args:
            config_dir (str): 설정 파일 디렉토리
        """
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "settings.json")
        self.key_file = os.path.join(config_dir, "secret.key")
        self.backup_dir = os.path.join(config_dir, "backups")
        
        # 로거 설정
        self.logger = logging.getLogger(__name__)
        
        # 설정 디렉토리 생성
        for directory in [config_dir, self.backup_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # 암호화 키 설정
        if CRYPTO_AVAILABLE:
            self._setup_encryption()
        else:
            self.encryption_enabled = False
        
        # 기본 설정
        self.default_config = self._get_default_config()
    
    def _setup_encryption(self):
        """암호화 설정"""
        try:
            if os.path.exists(self.key_file):
                # 기존 키 로드
                with open(self.key_file, 'rb') as f:
                    key_data = f.read()
                
                if len(key_data) >= 48:  # salt(16) + key(32) 최소 크기
                    salt = key_data[:16]
                    self.encryption_key = key_data[16:48]
                    self.encryption_enabled = True
                else:
                    self.logger.warning("키 파일이 손상되었습니다. 새 키를 생성합니다.")
                    self._generate_new_key()
            else:
                # 새 키 생성
                self._generate_new_key()
                
        except Exception as e:
            self.logger.error(f"암호화 설정 오류: {e}")
            self.encryption_enabled = False
    
    def _generate_new_key(self):
        """새로운 암호화 키 생성"""
        try:
            password = b"subscription_automation_2024"
            salt = os.urandom(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = kdf.derive(password)
            
            # 키 파일에 저장 (salt + key)
            with open(self.key_file, 'wb') as f:
                f.write(salt + key)
            
            self.encryption_key = key
            self.encryption_enabled = True
            self.logger.info("새로운 암호화 키가 생성되었습니다.")
            
        except Exception as e:
            self.logger.error(f"암호화 키 생성 오류: {e}")
            self.encryption_enabled = False
    
    def _encrypt_value(self, value: str) -> str:
        """값 암호화"""
        if not value or not self.encryption_enabled:
            return value
        
        try:
            f = Fernet(base64.urlsafe_b64encode(self.encryption_key))
            encrypted = f.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            self.logger.warning(f"암호화 오류: {e}")
            return value
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """값 복호화"""
        if not encrypted_value or not self.encryption_enabled:
            return encrypted_value
        
        try:
            f = Fernet(base64.urlsafe_b64encode(self.encryption_key))
            decoded = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = f.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            self.logger.warning(f"복호화 오류 (원본 값 반환): {e}")
            return encrypted_value
    
    def _process_service_key(self, service_key: str) -> str:
        """서비스키 URL 디코딩 처리"""
        if not service_key:
            return service_key
        
        # URL 인코딩된 키인지 확인하고 디코딩
        if '%' in service_key:
            try:
                decoded_key = urllib.parse.unquote(service_key)
                if decoded_key != service_key:
                    self.logger.info("서비스키 URL 디코딩 완료")
                    return decoded_key
            except Exception as e:
                self.logger.warning(f"서비스키 디코딩 중 오류: {e}")
        
        return service_key
    
    def _create_backup(self) -> str:
        """설정 파일 백업 생성"""
        if not os.path.exists(self.config_file):
            return ""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"settings_backup_{timestamp}.json")
            
            with open(self.config_file, 'r', encoding='utf-8') as src, \
                 open(backup_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            
            self.logger.info(f"설정 파일 백업 생성: {backup_file}")
            return backup_file
            
        except Exception as e:
            self.logger.error(f"백업 생성 오류: {e}")
            return ""
    
    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정 반환"""
        return {
            'api': {
                'service_key': '',
                'max_rows': 50,
                'timeout': 30
            },
            'email': {
                'sender_email': '',
                'app_password': '',  # 암호화됨
                'recipients': [],
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587
            },
            'kakao': {
                'enabled': False,
                'api_key': '',  # 암호화됨
                'template_id': ''
            },
            'schedule': {
                'enabled': False,
                'time': '09:00',
                'frequency': 'daily'
            },
            'files': {
                'output_dir': 'output',
                'filename_format': '청약분양정보_{timestamp}.xlsx'
            },
            'logging': {
                'level': 'INFO',
                'file_enabled': True,
                'console_enabled': True
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        설정 불러오기 (URL 인코딩 문제 자동 해결)
        Returns:
            Dict[str, Any]: 설정 데이터
        """
        try:
            if not os.path.exists(self.config_file):
                self.logger.info("설정 파일이 없습니다. 기본 설정을 생성합니다.")
                return self.default_config.copy()
            
            # 설정 파일 읽기
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # JSON 파싱
            config = json.loads(content)
            
            # 서비스키 URL 디코딩 처리
            api_config = config.get('api', {})
            if 'service_key' in api_config:
                original_key = api_config['service_key']
                processed_key = self._process_service_key(original_key)
                
                if original_key != processed_key:
                    api_config['service_key'] = processed_key
                    self.logger.info("설정 파일의 서비스키가 자동으로 디코딩되었습니다.")
                    
                    # 수정된 설정을 자동 저장
                    self._save_config_internal(config)
            
            # 민감정보 복호화
            if self.encryption_enabled:
                email_config = config.get('email', {})
                if 'app_password' in email_config:
                    email_config['app_password'] = self._decrypt_value(email_config['app_password'])
                
                kakao_config = config.get('kakao', {})
                if 'api_key' in kakao_config:
                    kakao_config['api_key'] = self._decrypt_value(kakao_config['api_key'])
            
            # 기본값과 병합
            merged_config = self._merge_with_defaults(config)
            
            self.logger.info("설정 파일 로드 완료")
            return merged_config
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류: {e}")
            return self._handle_corrupted_config()
            
        except Exception as e:
            self.logger.error(f"설정 불러오기 오류: {e}")
            return self.default_config.copy()
    
    def _handle_corrupted_config(self) -> Dict[str, Any]:
        """손상된 설정 파일 처리"""
        self.logger.warning("설정 파일이 손상되었습니다.")
        
        # 백업 파일에서 복구 시도
        if os.path.exists(self.backup_dir):
            backup_files = [f for f in os.listdir(self.backup_dir) if f.startswith('settings_backup_')]
            if backup_files:
                latest_backup = os.path.join(self.backup_dir, sorted(backup_files)[-1])
                try:
                    with open(latest_backup, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    self.logger.info(f"백업 파일에서 복구: {latest_backup}")
                    return config
                except Exception as e:
                    self.logger.error(f"백업 파일 복구 실패: {e}")
        
        # 손상된 파일 백업하고 기본 설정 반환
        if os.path.exists(self.config_file):
            corrupted_file = f"{self.config_file}.corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(self.config_file, corrupted_file)
            self.logger.info(f"손상된 설정 파일을 이동: {corrupted_file}")
        
        return self.default_config.copy()
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """기본값과 병합"""
        merged = self.default_config.copy()
        
        for section, values in config.items():
            if section in merged and isinstance(values, dict):
                merged[section].update(values)
            else:
                merged[section] = values
        
        return merged
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """
        설정 저장 (공개 메서드)
        Args:
            config_data (Dict[str, Any]): 저장할 설정 데이터
        Returns:
            bool: 성공 여부
        """
        try:
            # 백업 생성
            self._create_backup()
            
            # 설정 유효성 검증
            is_valid, errors = self.validate_config(config_data)
            if not is_valid:
                self.logger.error(f"설정 유효성 검사 실패: {errors}")
                return False
            
            # 설정 저장
            return self._save_config_internal(config_data)
            
        except Exception as e:
            self.logger.error(f"설정 저장 오류: {e}")
            return False
    
    def _save_config_internal(self, config_data: Dict[str, Any]) -> bool:
        """
        설정 저장 (내부 메서드)
        Args:
            config_data (Dict[str, Any]): 저장할 설정 데이터
        Returns:
            bool: 성공 여부
        """
        try:
            # 저장용 설정 데이터 복사
            save_config = config_data.copy()
            
            # 민감정보 암호화
            if self.encryption_enabled:
                # 이메일 앱 비밀번호 암호화
                if 'email' in save_config and 'app_password' in save_config['email']:
                    app_password = save_config['email']['app_password']
                    if app_password:
                        save_config['email']['app_password'] = self._encrypt_value(app_password)
                
                # 카카오톡 API 키 암호화
                if 'kakao' in save_config and 'api_key' in save_config['kakao']:
                    api_key = save_config['kakao']['api_key']
                    if api_key:
                        save_config['kakao']['api_key'] = self._encrypt_value(api_key)
            
            # JSON 파일로 저장
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(save_config, f, ensure_ascii=False, indent=2)
            
            self.logger.info("설정 파일 저장 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 저장 내부 오류: {e}")
            return False
    
    def validate_config(self, config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        설정 유효성 검증
        Args:
            config_data (Dict[str, Any]): 검증할 설정 데이터
        Returns:
            Tuple[bool, List[str]]: (유효성, 오류 메시지 목록)
        """
        errors = []
        
        try:
            # API 키 검증
            api_config = config_data.get('api', {})
            if not api_config.get('service_key'):
                errors.append("공공데이터포털 인증키가 필요합니다.")
            else:
                service_key = api_config['service_key']
                if len(service_key) < 20:
                    errors.append("인증키가 너무 짧습니다.")
            
            # 이메일 설정 검증
            email_config = config_data.get('email', {})
            if not email_config.get('sender_email'):
                errors.append("발신자 이메일 주소가 필요합니다.")
            
            if not email_config.get('app_password'):
                errors.append("Gmail 앱 비밀번호가 필요합니다.")
            
            if not email_config.get('recipients'):
                errors.append("수신자 이메일 주소가 필요합니다.")
            
            # 이메일 형식 검증
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            sender_email = email_config.get('sender_email', '')
            if sender_email and not re.match(email_pattern, sender_email):
                errors.append("발신자 이메일 형식이 올바르지 않습니다.")
            
            recipients = email_config.get('recipients', [])
            if isinstance(recipients, list):
                for recipient in recipients:
                    if recipient and not re.match(email_pattern, recipient):
                        errors.append(f"수신자 이메일 형식이 올바르지 않습니다: {recipient}")
            
            # 스케줄 시간 형식 검증
            schedule_config = config_data.get('schedule', {})
            if schedule_config.get('enabled'):
                time_str = schedule_config.get('time', '')
                if time_str:
                    time_pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
                    if not re.match(time_pattern, time_str):
                        errors.append("스케줄 시간 형식이 올바르지 않습니다 (HH:MM).")
            
        except Exception as e:
            errors.append(f"설정 검증 중 오류: {str(e)}")
        
        return len(errors) == 0, errors
    
    def reset_config(self) -> bool:
        """설정 초기화"""
        try:
            # 백업 생성
            self._create_backup()
            
            # 기본 설정으로 저장
            success = self._save_config_internal(self.default_config)
            if success:
                self.logger.info("설정이 초기화되었습니다.")
            return success
            
        except Exception as e:
            self.logger.error(f"설정 초기화 오류: {e}")
            return False
    
    def fix_url_encoding_issues(self) -> bool:
        """URL 인코딩 문제 수동 수정"""
        try:
            config = self.load_config()
            
            # 서비스키 처리
            api_config = config.get('api', {})
            if 'service_key' in api_config:
                service_key = api_config['service_key']
                processed_key = self._process_service_key(service_key)
                
                if service_key != processed_key:
                    api_config['service_key'] = processed_key
                    success = self.save_config(config)
                    if success:
                        self.logger.info("URL 인코딩 문제가 수정되었습니다.")
                    return success
                else:
                    self.logger.info("URL 인코딩 문제가 발견되지 않았습니다.")
                    return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"URL 인코딩 문제 수정 오류: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """설정 파일 정보 반환"""
        info = {
            'config_file': self.config_file,
            'config_exists': os.path.exists(self.config_file),
            'encryption_enabled': self.encryption_enabled,
            'backup_dir': self.backup_dir,
            'last_modified': None
        }
        
        if info['config_exists']:
            try:
                stat = os.stat(self.config_file)
                info['last_modified'] = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                info['file_size'] = stat.st_size
            except:
                pass
        
        return info
    
    def export_config(self, export_path: str, include_sensitive: bool = False) -> bool:
        """설정 내보내기"""
        try:
            config = self.load_config()
            
            if not include_sensitive:
                # 민감정보 제거
                if 'email' in config:
                    config['email']['app_password'] = ''
                if 'kakao' in config:
                    config['kakao']['api_key'] = ''
                config['api']['service_key'] = ''
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"설정을 내보냈습니다: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 내보내기 오류: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """설정 가져오기"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 유효성 검증 (경고만)
            is_valid, errors = self.validate_config(imported_config)
            if not is_valid:
                self.logger.warning(f"가져온 설정에 문제가 있습니다: {errors}")
            
            # 설정 저장
            success = self.save_config(imported_config)
            if success:
                self.logger.info(f"설정을 가져왔습니다: {import_path}")
            return success
            
        except Exception as e:
            self.logger.error(f"설정 가져오기 오류: {e}")
            return False

# 하위 호환성을 위한 함수들
def load_config_safe(config_dir: str = "config") -> Dict[str, Any]:
    """안전한 설정 로드 (하위 호환성)"""
    manager = ConfigManager(config_dir)
    return manager.load_config()

def save_config_safe(config_data: Dict[str, Any], config_dir: str = "config") -> bool:
    """안전한 설정 저장 (하위 호환성)"""
    manager = ConfigManager(config_dir)
    return manager.save_config(config_data)

if __name__ == "__main__":
    # 테스트 실행
    manager = ConfigManager()
    
    print("🔧 ConfigManager 테스트")
    print("=" * 40)
    
    # 설정 정보 출력
    info = manager.get_config_info()
    print(f"설정 파일: {info['config_file']}")
    print(f"암호화 사용: {info['encryption_enabled']}")
    print(f"파일 존재: {info['config_exists']}")
    
    # 설정 로드 테스트
    config = manager.load_config()
    print(f"로드된 설정 섹션: {list(config.keys())}")
    
    # URL 인코딩 문제 수정 테스트
    if manager.fix_url_encoding_issues():
        print("✅ URL 인코딩 문제 확인/수정 완료")
    else:
        print("❌ URL 인코딩 문제 수정 실패")