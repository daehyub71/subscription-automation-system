#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 API Rate Limiting 해결 코드
파일명: api/subscription_with_naver.py (수정 버전)
"""

import requests
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
import random

class SubscriptionNaverIntegration:
    """청약 분양정보와 네이버 API 통합 클래스 (Rate Limiting 해결)"""
    
    def __init__(self, client_id: str, client_secret: str):
        """
        초기화
        Args:
            client_id (str): 네이버 API 클라이언트 ID
            client_secret (str): 네이버 API 클라이언트 시크릿
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.logger = logging.getLogger(__name__)
        
        # Rate Limiting 설정
        self.min_delay = 0.5  # 최소 딜레이 (초)
        self.max_delay = 2.0  # 최대 딜레이 (초)
        self.max_retries = 3  # 최대 재시도 횟수
        self.backoff_factor = 2  # 백오프 배수
        
        # API 호출 간격 제어
        self.last_call_time = 0
        
        # 네이버 API 헤더
        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def _wait_for_rate_limit(self):
        """API 호출 간격 제어"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_delay:
            sleep_time = self.min_delay - time_since_last_call
            # 랜덤 지터 추가 (0.1~0.3초)
            jitter = random.uniform(0.1, 0.3)
            total_sleep = sleep_time + jitter
            
            self.logger.debug(f"Rate limiting: {total_sleep:.2f}초 대기")
            time.sleep(total_sleep)
        
        self.last_call_time = time.time()
    
    def _make_api_request(self, url: str, params: Dict) -> Optional[Dict]:
        """
        안전한 API 요청 (재시도 로직 포함)
        Args:
            url (str): API URL
            params (Dict): 요청 파라미터
        Returns:
            Optional[Dict]: API 응답 또는 None
        """
        for attempt in range(self.max_retries):
            try:
                # Rate Limiting 적용
                self._wait_for_rate_limit()
                
                self.logger.debug(f"API 요청 시도 {attempt + 1}/{self.max_retries}: {url}")
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                # 성공적인 응답
                if response.status_code == 200:
                    self.logger.debug(f"API 요청 성공: {url}")
                    return response.json()
                
                # Rate Limiting 에러 처리
                elif response.status_code == 429:
                    retry_delay = self.min_delay * (self.backoff_factor ** attempt)
                    # 최대 30초까지만 대기
                    retry_delay = min(retry_delay, 30.0)
                    
                    self.logger.warning(f"Rate limit 도달. {retry_delay:.1f}초 후 재시도... (시도 {attempt + 1}/{self.max_retries})")
                    time.sleep(retry_delay)
                    continue
                
                # 기타 HTTP 에러
                else:
                    self.logger.error(f"HTTP 오류 {response.status_code}: {url}")
                    if attempt == self.max_retries - 1:
                        return None
                    
                    # 짧은 딜레이 후 재시도
                    time.sleep(1.0)
                    continue
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"API 요청 타임아웃: {url} (시도 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(2.0)
                    continue
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"API 요청 오류: {e} (시도 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(1.0)
                    continue
        
        self.logger.error(f"API 요청 최종 실패: {url}")
        return None
    
    def search_naver_news(self, query: str, display: int = 5) -> List[Dict]:
        """
        네이버 뉴스 검색 (안전한 버전)
        Args:
            query (str): 검색 쿼리
            display (int): 결과 개수
        Returns:
            List[Dict]: 뉴스 검색 결과
        """
        try:
            url = "https://openapi.naver.com/v1/search/news"
            params = {
                "query": query,
                "display": display,
                "start": 1,
                "sort": "date"
            }
            
            result = self._make_api_request(url, params)
            
            if result and 'items' in result:
                self.logger.info(f"뉴스 검색 성공: '{query}' - {len(result['items'])}건")
                return result['items']
            else:
                self.logger.warning(f"뉴스 검색 결과 없음: '{query}'")
                return []
                
        except Exception as e:
            self.logger.error(f"뉴스 검색 예외 오류: {e}")
            return []
    
    def search_naver_blog(self, query: str, display: int = 5) -> List[Dict]:
        """
        네이버 블로그 검색 (안전한 버전)
        Args:
            query (str): 검색 쿼리
            display (int): 결과 개수
        Returns:
            List[Dict]: 블로그 검색 결과
        """
        try:
            url = "https://openapi.naver.com/v1/search/blog"
            params = {
                "query": query,
                "display": display,
                "start": 1,
                "sort": "date"
            }
            
            result = self._make_api_request(url, params)
            
            if result and 'items' in result:
                self.logger.info(f"블로그 검색 성공: '{query}' - {len(result['items'])}건")
                return result['items']
            else:
                self.logger.warning(f"블로그 검색 결과 없음: '{query}'")
                return []
                
        except Exception as e:
            self.logger.error(f"블로그 검색 예외 오류: {e}")
            return []
    
    def search_related_news(self, keyword: str = "", region: str = "") -> List[Dict]:
        """
        관련 뉴스 검색 (고정 키워드 사용)
        Args:
            keyword (str): 검색 키워드 (사용하지 않음, 호환성 유지용)
            region (str): 지역명 (사용하지 않음, 호환성 유지용)
        Returns:
            List[Dict]: 뉴스 검색 결과
        """
        try:
            # 고정 검색 키워드
            search_keywords = ['부동산', '분양', '청약']
            
            self.logger.info("관련 뉴스 검색 시작: 부동산, 분양, 청약")
            
            all_news = []
            
            for search_keyword in search_keywords:
                self.logger.info(f"뉴스 검색 진행: '{search_keyword}'")
                
                # 각 키워드별 뉴스 검색
                news_results = self.search_naver_news(search_keyword, display=5)
                all_news.extend(news_results)
                
                # API 호출 간격 추가 대기
                time.sleep(random.uniform(1.0, 1.5))
            
            # 중복 제거 (링크 기준)
            unique_news = []
            seen_links = set()
            
            for news in all_news:
                link = news.get('link', '')
                if link and link not in seen_links:
                    seen_links.add(link)
                    unique_news.append(news)
            
            self.logger.info(f"관련 뉴스 검색 완료: 총 {len(unique_news)}건 (중복 제거 후)")
            return unique_news[:15]  # 최대 15개까지만 반환
            
        except Exception as e:
            self.logger.error(f"관련 뉴스 검색 오류: {e}")
            return []
    
    def search_market_trends(self, region: str = "") -> Dict:
        """
        시장 동향 분석 (고정 키워드 사용)
        Args:
            region (str): 지역명 (사용하지 않음, 호환성 유지용)
        Returns:
            Dict: 시장 동향 분석 결과
        """
        try:
            self.logger.info("시장 동향 분석 시작: 부동산, 분양, 청약")
            
            trends_data = {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'search_keywords': ['부동산', '분양', '청약'],
                'news_count': 0,
                'blog_count': 0,
                'market_keywords': [],
                'latest_news': []
            }
            
            # 고정 검색 키워드
            search_keywords = ['부동산', '분양', '청약']
            
            all_news = []
            all_blogs = []
            
            for keyword in search_keywords:
                self.logger.info(f"시장 동향 검색: '{keyword}'")
                
                # 뉴스 검색
                news_results = self.search_naver_news(keyword, display=3)
                all_news.extend(news_results)
                
                # API 호출 간격 대기
                time.sleep(random.uniform(1.0, 1.5))
                
                # 블로그 검색
                blog_results = self.search_naver_blog(keyword, display=3)
                all_blogs.extend(blog_results)
                
                # API 호출 간격 대기
                time.sleep(random.uniform(1.0, 1.5))
            
            # 중복 제거
            unique_news = []
            seen_links = set()
            
            for news in all_news:
                link = news.get('link', '')
                if link and link not in seen_links:
                    seen_links.add(link)
                    unique_news.append(news)
            
            unique_blogs = []
            seen_blog_links = set()
            
            for blog in all_blogs:
                link = blog.get('link', '')
                if link and link not in seen_blog_links:
                    seen_blog_links.add(link)
                    unique_blogs.append(blog)
            
            # 결과 취합
            trends_data['news_count'] = len(unique_news)
            trends_data['blog_count'] = len(unique_blogs)
            trends_data['latest_news'] = unique_news[:5]  # 최신 5개만
            
            # 키워드 분석
            keywords = set()
            all_content = unique_news + unique_blogs
            
            for item in all_content:
                title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                description = item.get('description', '').replace('<b>', '').replace('</b>', '')
                
                # 부동산 관련 키워드 추출
                content = f"{title} {description}".lower()
                
                keyword_candidates = [
                    '분양', '청약', '부동산', '아파트', '시세', '가격',
                    '투자', '전세', '매매', '경쟁률', '당첨', '공급',
                    '입주', '계약', '분양권', '신축', '재건축', '재개발'
                ]
                
                for candidate in keyword_candidates:
                    if candidate in content:
                        keywords.add(candidate)
            
            trends_data['market_keywords'] = list(keywords)[:10]  # 최대 10개
            
            self.logger.info(f"시장 동향 분석 완료: 뉴스 {trends_data['news_count']}건, 블로그 {trends_data['blog_count']}건")
            return trends_data
            
        except Exception as e:
            self.logger.error(f"시장 동향 분석 오류: {e}")
            return {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'search_keywords': ['부동산', '분양', '청약'],
                'news_count': 0,
                'blog_count': 0,
                'market_keywords': [],
                'latest_news': [],
                'error': str(e)
            }
    
    def get_comprehensive_market_report(self, subscription_data: Dict) -> Dict:
        """
        종합 시장 분석 보고서 (고정 키워드 사용)
        Args:
            subscription_data (Dict): 분양정보 데이터
        Returns:
            Dict: 종합 분석 보고서
        """
        try:
            self.logger.info("종합 시장 분석 보고서 생성 시작")
            
            # 고정 검색 키워드
            search_keywords = ['부동산', '분양', '청약']
            
            report = {
                'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'search_keywords': search_keywords,
                'summary': {
                    'total_subscriptions': sum(len(items) for items in subscription_data.values() if isinstance(items, list)),
                    'analyzed_keywords': search_keywords,
                    'hot_keywords': []
                },
                'keyword_analysis': {}
            }
            
            # 키워드별 분석
            all_keywords = set()
            
            for keyword in search_keywords:
                self.logger.info(f"키워드 분석 진행: {keyword}")
                
                # 뉴스 검색
                news_results = self.search_naver_news(keyword, display=3)
                
                # API 호출 간격 대기
                time.sleep(random.uniform(1.5, 2.0))
                
                # 블로그 검색
                blog_results = self.search_naver_blog(keyword, display=2)
                
                # API 호출 간격 대기  
                time.sleep(random.uniform(1.5, 2.0))
                
                # 키워드별 결과 저장
                report['keyword_analysis'][keyword] = {
                    'news_count': len(news_results),
                    'blog_count': len(blog_results),
                    'latest_news': news_results[:2],
                    'latest_blogs': blog_results[:1]
                }
                
                # 키워드 수집
                for item in news_results + blog_results:
                    title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                    description = item.get('description', '').replace('<b>', '').replace('</b>', '')
                    
                    content = f"{title} {description}".lower()
                    
                    # 부동산 관련 키워드 추출
                    keyword_candidates = [
                        '분양', '청약', '부동산', '아파트', '시세', '가격',
                        '투자', '전세', '매매', '경쟁률', '당첨', '공급',
                        '입주', '계약', '분양권', '신축', '재건축', '재개발',
                        '대출', '금리', '정책', '규제', '완화'
                    ]
                    
                    for candidate in keyword_candidates:
                        if candidate in content:
                            all_keywords.add(candidate)
            
            # 핫 키워드 설정
            report['summary']['hot_keywords'] = list(all_keywords)[:8]  # 상위 8개
            
            # 전체 통계
            total_news = sum(data['news_count'] for data in report['keyword_analysis'].values())
            total_blogs = sum(data['blog_count'] for data in report['keyword_analysis'].values())
            
            report['summary']['total_news'] = total_news
            report['summary']['total_blogs'] = total_blogs
            
            self.logger.info(f"종합 시장 분석 보고서 생성 완료: 뉴스 {total_news}건, 블로그 {total_blogs}건")
            return report
            
        except Exception as e:
            self.logger.error(f"종합 분석 보고서 생성 오류: {e}")
            return {
                'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'search_keywords': ['부동산', '분양', '청약'],
                'summary': {
                    'total_subscriptions': 0,
                    'analyzed_keywords': [],
                    'hot_keywords': [],
                    'total_news': 0,
                    'total_blogs': 0
                },
                'keyword_analysis': {},
                'error': str(e)
            }