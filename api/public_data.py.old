#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공공데이터포털 API 연동 모듈
파일명: api/public_data.py
작성자: 청약 자동화 시스템
설명: 청약홈 분양정보 조회 서비스 API 연동 (수정버전)
"""

import requests
import json
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urlencode

class PublicDataAPI:
    """공공데이터포털 청약홈 분양정보 API 클래스"""
    
    def __init__(self, service_key: str, timeout: int = 30):
        """
        초기화
        Args:
            service_key (str): 공공데이터포털 인증키
            timeout (int): API 호출 타임아웃 (초)
        """
        self.service_key = service_key
        self.timeout = timeout
        self.base_url = "https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1"
        self.logger = logging.getLogger(__name__)
        
        # API 엔드포인트들 (기술문서 기준)
        self.endpoints = {
            'apt_detail': f"{self.base_url}/getAPTLttotPblancDetail",  # APT 분양정보 상세조회
            'apt_model': f"{self.base_url}/getAPTLttotPblancMdl",  # APT 분양정보 주택형별 상세조회
            'officetel_detail': f"{self.base_url}/getUrbtyOfctlLttotPblancDetail",  # 오피스텔/도시형/민간임대 분양정보 상세조회
            'officetel_model': f"{self.base_url}/getUrbtyOfctlLttotPblancMdl",  # 오피스텔/도시형/민간임대 분양정보 주택형별 상세조회
            'remndr_detail': f"{self.base_url}/getRemndrLttotPblancDetail",  # APT 잔여세대 분양정보 상세조회
            'remndr_model': f"{self.base_url}/getRemndrLttotPblancMdl",  # APT 잔여세대 주택형별 상세조회
            'public_rent_detail': f"{self.base_url}/getPblPvtRentLttotPblancDetail",  # 공공지원 민간임대 분양정보 상세조회
            'public_rent_model': f"{self.base_url}/getPblPvtRentLttotPblancMdl",  # 공공지원 민간임대 분양정보 주택형별 상세조회
            'opt_detail': f"{self.base_url}/getOPTLttotPblancDetail",  # 임의공급 분양정보 상세조회
            'opt_model': f"{self.base_url}/getOPTLttotPblancMdl"  # 임의공급 분양정보 주택형별 상세조회
        }
    
    def test_connection(self) -> tuple[bool, str]:
        """
        API 연결 테스트
        Returns:
            tuple: (성공여부, 메시지)
        """
        try:
            self.logger.info("API 연결 테스트 시작")
            
            # APT 분양정보 상세조회로 테스트 (최소한의 파라미터)
            params = {
                'serviceKey': self.service_key,
                'page': 1,
                'perPage': 1
            }
            
            response = requests.get(
                self.endpoints['apt_detail'],
                params=params,
                timeout=self.timeout
            )
            
            self.logger.info(f"API 응답 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'currentCount' in data:
                        self.logger.info("API 연결 테스트 성공")
                        return True, "API 연결 성공"
                    else:
                        error_msg = "API 응답 형식 오류"
                        self.logger.error(error_msg)
                        return False, error_msg
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON 파싱 오류: {e}")
                    return False, f"JSON 파싱 오류: {e}"
            else:
                error_msg = f"HTTP 오류: {response.status_code}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "API 호출 타임아웃"
            self.logger.error(error_msg)
            return False, error_msg
            
        except requests.exceptions.ConnectionError:
            error_msg = "네트워크 연결 오류"
            self.logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"예상치 못한 오류: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_apt_subscription_list(self, max_rows: int = 150, filters: Dict = None) -> List[Dict]:
        """
        APT 분양정보 목록 조회
        Args:
            max_rows (int): 최대 조회 건수
            filters (Dict): 필터 조건
        Returns:
            List[Dict]: APT 분양정보 목록
        """
        subscription_list = []
        
        try:
            max_rows = 150
            self.logger.info(f"APT 분양정보 목록 조회 시작 (최대 {max_rows}건)")
            
            # 기본 파라미터
            params = {
                'serviceKey': self.service_key,
                'page': 1,
                'perPage': max_rows
            }
            
            # 필터 조건 추가
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        # 조건부 파라미터 형식으로 변환
                        cond_key = f"cond[{key.upper()}::EQ]"
                        params[cond_key] = value
            
            # 재시도 로직 (최대 3회)
            for attempt in range(3):
                try:
                    response = requests.get(
                        self.endpoints['apt_detail'],
                        params=params,
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        break
                    else:
                        self.logger.warning(f"API 호출 실패 (시도 {attempt + 1}/3): HTTP {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"API 호출 실패 (시도 {attempt + 1}/3): {e}")
                    
                if attempt < 2:  # 마지막 시도가 아니면 대기
                    time.sleep(1)
            else:
                raise Exception("API 호출 재시도 횟수 초과")
            
            # JSON 응답 파싱
            data = response.json()
            
            # 결과 확인
            if 'data' not in data:
                raise Exception("API 응답에 data 필드가 없습니다")
            
            # 데이터 추출
            items = data['data']
            self.logger.info(f"조회된 APT 분양정보: {len(items)}건")
            
            for item in items:
                subscription_info = self._parse_apt_subscription_item(item)
                if subscription_info:
                    subscription_list.append(subscription_info)
            
            self.logger.info(f"APT 분양정보 목록 조회 완료: {len(subscription_list)}건")
            
        except Exception as e:
            self.logger.error(f"APT 분양정보 목록 조회 오류: {e}")
            raise
        
        return subscription_list
    
    def get_officetel_subscription_list(self, max_rows: int = 150, filters: Dict = None) -> List[Dict]:
        """
        오피스텔/도시형/민간임대 분양정보 목록 조회
        Args:
            max_rows (int): 최대 조회 건수
            filters (Dict): 필터 조건
        Returns:
            List[Dict]: 오피스텔 분양정보 목록
        """
        try:
            self.logger.info(f"오피스텔 분양정보 목록 조회 시작 (최대 {max_rows}건)")
            
            params = {
                'serviceKey': self.service_key,
                'page': 1,
                'perPage': max_rows
            }
            
            # 필터 조건 추가
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        cond_key = f"cond[{key.upper()}::EQ]"
                        params[cond_key] = value
            
            response = requests.get(
                self.endpoints['officetel_detail'],
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP 오류: {response.status_code}")
            
            # JSON 파싱
            data = response.json()
            
            if 'data' not in data:
                raise Exception("API 응답에 data 필드가 없습니다")
            
            # 데이터 추출
            items = data['data']
            officetel_list = []
            
            for item in items:
                officetel_info = self._parse_officetel_subscription_item(item)
                if officetel_info:
                    officetel_list.append(officetel_info)
            
            self.logger.info(f"오피스텔 분양정보 조회 완료: {len(officetel_list)}건")
            return officetel_list
            
        except Exception as e:
            self.logger.error(f"오피스텔 분양정보 조회 오류: {e}")
            raise
    
    def get_comprehensive_data(self, max_rows: int = 150, filters: Dict = None) -> Dict[str, List[Dict]]:
        """
        종합 분양정보 조회 (APT + 오피스텔 + 기타)
        Args:
            max_rows (int): 각 카테고리별 최대 조회 건수
            filters (Dict): 필터 조건
        Returns:
            Dict[str, List[Dict]]: 카테고리별 분양정보
        """
        comprehensive_data = {
            'apt': [],           # APT 분양정보
            'officetel': [],     # 오피스텔 분양정보
            'remndr': [],        # 잔여세대 분양정보
            'public_rent': [],   # 공공지원 민간임대
            'opt': []            # 임의공급
        }
        
        try:
            self.logger.info("종합 분양정보 조회 시작")
            
            # APT 분양정보 조회
            try:
                comprehensive_data['apt'] = self.get_apt_subscription_list(max_rows, filters)
            except Exception as e:
                self.logger.error(f"APT 분양정보 조회 실패: {e}")
            
            # 오피스텔 분양정보 조회
            try:
                comprehensive_data['officetel'] = self.get_officetel_subscription_list(max_rows, filters)
            except Exception as e:
                self.logger.error(f"오피스텔 분양정보 조회 실패: {e}")
            
            # 통계 로그
            total_count = sum(len(data) for data in comprehensive_data.values())
            self.logger.info(f"종합 분양정보 조회 완료: 총 {total_count}건")
            self.logger.info(f"  - APT: {len(comprehensive_data['apt'])}건")
            self.logger.info(f"  - 오피스텔: {len(comprehensive_data['officetel'])}건")
            self.logger.info(f"  - 잔여세대: {len(comprehensive_data['remndr'])}건")
            self.logger.info(f"  - 공공지원임대: {len(comprehensive_data['public_rent'])}건")
            self.logger.info(f"  - 임의공급: {len(comprehensive_data['opt'])}건")
            
        except Exception as e:
            self.logger.error(f"종합 분양정보 조회 오류: {e}")
            raise
        
        return comprehensive_data
    
    def _parse_apt_subscription_item(self, item: Dict) -> Optional[Dict]:
        """
        APT 분양정보 항목 파싱
        Args:
            item (Dict): JSON 데이터 아이템
        Returns:
            Optional[Dict]: 파싱된 분양정보
        """
        try:
            def get_value(key: str, default: str = "") -> str:
                return str(item.get(key, default)).strip() if item.get(key) is not None else default
            
            subscription_info = {
                '주택관리번호': get_value('HOUSE_MANAGE_NO'),
                '공고번호': get_value('PBLANC_NO'),
                '주택명': get_value('HOUSE_NM'),
                '주택구분': get_value('HOUSE_SECD_NM'),
                '주택상세구분': get_value('HOUSE_DTL_SECD_NM'),
                '분양구분': get_value('RENT_SECD_NM'),
                '공급지역': get_value('SUBSCRPT_AREA_CODE_NM'),
                '공급위치': get_value('HSSPLY_ADRES'),
                '공급규모': get_value('TOT_SUPLY_HSHLDCO'),
                '모집공고일': get_value('RCRIT_PBLANC_DE'),
                '청약접수시작일': get_value('RCEPT_BGNDE'),
                '청약접수종료일': get_value('RCEPT_ENDDE'),
                '당첨발표일': get_value('PRZWNER_PRESNATN_DE'),
                '계약시작일': get_value('CNTRCT_CNCLS_BGNDE'),
                '계약종료일': get_value('CNTRCT_CNCLS_ENDDE'),
                '입주예정월': get_value('MVN_PREARNGE_YM'),
                '홈페이지': get_value('HMPG_ADRES'),
                '건설업체': get_value('CNSTRCT_ENTRPS_NM'),
                '사업주체': get_value('BSNS_MBY_NM'),
                '연락처': get_value('MDHS_TELNO'),
                '분양정보URL': get_value('PBLANC_URL')
            }
            
            # 필수 정보 검증
            if not subscription_info['주택명']:
                self.logger.warning("주택명이 없는 항목 건너뜀")
                return None
            
            return subscription_info
            
        except Exception as e:
            self.logger.error(f"APT 분양정보 파싱 오류: {e}")
            return None
    
    def _parse_officetel_subscription_item(self, item: Dict) -> Optional[Dict]:
        """
        오피스텔 분양정보 항목 파싱
        Args:
            item (Dict): JSON 데이터 아이템
        Returns:
            Optional[Dict]: 파싱된 분양정보
        """
        try:
            def get_value(key: str, default: str = "") -> str:
                return str(item.get(key, default)).strip() if item.get(key) is not None else default
            
            subscription_info = {
                '주택관리번호': get_value('HOUSE_MANAGE_NO'),
                '공고번호': get_value('PBLANC_NO'),
                '주택명': get_value('HOUSE_NM'),
                '주택구분': get_value('HOUSE_SECD_NM'),
                '주택상세구분': get_value('HOUSE_DTL_SECD_NM'),
                '공급지역': get_value('SUBSCRPT_AREA_CODE_NM'),
                '공급위치': get_value('HSSPLY_ADRES'),
                '공급규모': get_value('TOT_SUPLY_HSHLDCO'),
                '모집공고일': get_value('RCRIT_PBLANC_DE'),
                '청약접수시작일': get_value('SUBSCRPT_RCEPT_BGNDE'),
                '청약접수종료일': get_value('SUBSCRPT_RCEPT_ENDDE'),
                '당첨발표일': get_value('PRZWNER_PRESNATN_DE'),
                '계약시작일': get_value('CNTRCT_CNCLS_BGNDE'),
                '계약종료일': get_value('CNTRCT_CNCLS_ENDDE'),
                '입주예정월': get_value('MVN_PREARNGE_YM'),
                '홈페이지': get_value('HMPG_ADRES'),
                '사업주체': get_value('BSNS_MBY_NM'),
                '연락처': get_value('MDHS_TELNO'),
                '분양정보URL': get_value('PBLANC_URL')
            }
            
            # 필수 정보 검증
            if not subscription_info['주택명']:
                self.logger.warning("주택명이 없는 항목 건너뜀")
                return None
            
            return subscription_info
            
        except Exception as e:
            self.logger.error(f"오피스텔 분양정보 파싱 오류: {e}")
            return None
    
    def get_apt_model_detail(self, house_manage_no: str, pblanc_no: str) -> List[Dict]:
        """
        APT 분양정보 주택형별 상세조회
        Args:
            house_manage_no (str): 주택관리번호
            pblanc_no (str): 공고번호
        Returns:
            List[Dict]: 주택형별 상세정보
        """
        try:
            params = {
                'serviceKey': self.service_key,
                'page': 1,
                'perPage': 100,
                'cond[HOUSE_MANAGE_NO::EQ]': house_manage_no,
                'cond[PBLANC_NO::EQ]': pblanc_no
            }
            
            response = requests.get(
                self.endpoints['apt_model'],
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                raise Exception(f"HTTP 오류: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"APT 주택형별 상세조회 오류: {e}")
            raise
    
    def create_date_filter(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        날짜 필터 생성 도우미
        Args:
            start_date (str): 시작일 (YYYY-MM-DD)
            end_date (str): 종료일 (YYYY-MM-DD)
        Returns:
            Dict: 필터 조건
        """
        filters = {}
        if start_date:
            filters['RCRIT_PBLANC_DE::GTE'] = start_date
        if end_date:
            filters['RCRIT_PBLANC_DE::LTE'] = end_date
        return filters