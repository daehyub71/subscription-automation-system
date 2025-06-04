#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 API 사용 예제 모음
파일명: api/naver_api.py
"""

import requests
import json
import urllib.parse
import logging
from typing import Dict, List, Optional, Any

class NaverAPI:
    """네이버 API 클래스"""
    
    def __init__(self, client_id: str, client_secret: str):
        """
        초기화
        Args:
            client_id (str): 네이버 API Client ID
            client_secret (str): 네이버 API Client Secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        self.logger = logging.getLogger(__name__)
    
    def search_blog(self, query: str, display: int = 10, start: int = 1, 
                    sort: str = 'sim') -> Dict[str, Any]:
        """
        네이버 블로그 검색
        Args:
            query (str): 검색어
            display (int): 검색 결과 개수 (1~100)
            start (int): 검색 시작 위치 (1~1000)
            sort (str): 정렬 옵션 ('sim': 정확도순, 'date': 날짜순)
        Returns:
            Dict: 검색 결과
        """
        try:
            url = "https://openapi.naver.com/v1/search/blog"
            
            params = {
                'query': query,
                'display': display,
                'start': start,
                'sort': sort
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"블로그 검색 완료: {query}, 결과 {len(result.get('items', []))}건")
            
            return result
            
        except Exception as e:
            self.logger.error(f"블로그 검색 오류: {e}")
            return {'items': [], 'total': 0}
    
    def search_news(self, query: str, display: int = 10, start: int = 1, 
                    sort: str = 'sim') -> Dict[str, Any]:
        """
        네이버 뉴스 검색
        Args:
            query (str): 검색어
            display (int): 검색 결과 개수 (1~100)
            start (int): 검색 시작 위치 (1~1000)
            sort (str): 정렬 옵션 ('sim': 정확도순, 'date': 날짜순)
        Returns:
            Dict: 검색 결과
        """
        try:
            url = "https://openapi.naver.com/v1/search/news"
            
            params = {
                'query': query,
                'display': display,
                'start': start,
                'sort': sort
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"뉴스 검색 완료: {query}, 결과 {len(result.get('items', []))}건")
            
            return result
            
        except Exception as e:
            self.logger.error(f"뉴스 검색 오류: {e}")
            return {'items': [], 'total': 0}
    
    def search_shopping(self, query: str, display: int = 10, start: int = 1, 
                       sort: str = 'sim') -> Dict[str, Any]:
        """
        네이버 쇼핑 검색
        Args:
            query (str): 검색어
            display (int): 검색 결과 개수 (1~100)
            start (int): 검색 시작 위치 (1~1000)
            sort (str): 정렬 옵션 ('sim': 정확도순, 'date': 날짜순, 'asc': 가격 오름차순, 'dsc': 가격 내림차순)
        Returns:
            Dict: 검색 결과
        """
        try:
            url = "https://openapi.naver.com/v1/search/shop"
            
            params = {
                'query': query,
                'display': display,
                'start': start,
                'sort': sort
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"쇼핑 검색 완료: {query}, 결과 {len(result.get('items', []))}건")
            
            return result
            
        except Exception as e:
            self.logger.error(f"쇼핑 검색 오류: {e}")
            return {'items': [], 'total': 0}
    
    def translate_text(self, text: str, source: str = 'ko', target: str = 'en') -> str:
        """
        네이버 파파고 번역 API
        Args:
            text (str): 번역할 텍스트
            source (str): 원본 언어 ('ko', 'en', 'ja', 'zh-cn', 'zh-tw', 'vi', 'id', 'th', 'de', 'ru', 'es', 'it', 'fr')
            target (str): 대상 언어
        Returns:
            str: 번역된 텍스트
        """
        try:
            url = "https://openapi.naver.com/v1/papago/n2mt"
            
            data = {
                'source': source,
                'target': target,
                'text': text
            }
            
            response = requests.post(url, headers=self.headers, data=data)
            response.raise_for_status()
            
            result = response.json()
            translated_text = result['message']['result']['translatedText']
            
            self.logger.info(f"번역 완료: {source} -> {target}")
            return translated_text
            
        except Exception as e:
            self.logger.error(f"번역 오류: {e}")
            return text
    
    def detect_language(self, text: str) -> str:
        """
        언어 감지 API
        Args:
            text (str): 언어를 감지할 텍스트
        Returns:
            str: 감지된 언어 코드
        """
        try:
            url = "https://openapi.naver.com/v1/papago/detectLangs"
            
            data = {'query': text}
            
            response = requests.post(url, headers=self.headers, data=data)
            response.raise_for_status()
            
            result = response.json()
            detected_lang = result['langCode']
            
            self.logger.info(f"언어 감지 완료: {detected_lang}")
            return detected_lang
            
        except Exception as e:
            self.logger.error(f"언어 감지 오류: {e}")
            return 'unknown'
    
    def shorten_url(self, long_url: str) -> str:
        """
        URL 단축 API
        Args:
            long_url (str): 단축할 URL
        Returns:
            str: 단축된 URL
        """
        try:
            url = "https://openapi.naver.com/v1/util/shorturl"
            
            data = {'url': long_url}
            
            response = requests.post(url, headers=self.headers, data=data)
            response.raise_for_status()
            
            result = response.json()
            short_url = result['result']['url']
            
            self.logger.info(f"URL 단축 완료: {long_url} -> {short_url}")
            return short_url
            
        except Exception as e:
            self.logger.error(f"URL 단축 오류: {e}")
            return long_url
    
    def search_comprehensive(self, query: str, categories: List[str] = None) -> Dict[str, Any]:
        """
        종합 검색 (여러 카테고리 동시 검색)
        Args:
            query (str): 검색어
            categories (List[str]): 검색할 카테고리 목록 ['blog', 'news', 'shopping']
        Returns:
            Dict: 카테고리별 검색 결과
        """
        if categories is None:
            categories = ['blog', 'news', 'shopping']
        
        results = {}
        
        for category in categories:
            try:
                if category == 'blog':
                    results['blog'] = self.search_blog(query, display=5)
                elif category == 'news':
                    results['news'] = self.search_news(query, display=5)
                elif category == 'shopping':
                    results['shopping'] = self.search_shopping(query, display=5)
                    
            except Exception as e:
                self.logger.error(f"{category} 검색 실패: {e}")
                results[category] = {'items': [], 'total': 0}
        
        return results

class NaverSearchAnalyzer:
    """네이버 검색 결과 분석 클래스"""
    
    def __init__(self, naver_api: NaverAPI):
        self.naver_api = naver_api
        self.logger = logging.getLogger(__name__)
    
    def analyze_trend(self, keywords: List[str], days: int = 7) -> Dict[str, Any]:
        """
        키워드 트렌드 분석
        Args:
            keywords (List[str]): 분석할 키워드 목록
            days (int): 분석 기간 (일)
        Returns:
            Dict: 트렌드 분석 결과
        """
        trend_data = {}
        
        for keyword in keywords:
            try:
                # 블로그와 뉴스에서 키워드 검색
                blog_results = self.naver_api.search_blog(keyword, display=50)
                news_results = self.naver_api.search_news(keyword, display=50)
                
                trend_data[keyword] = {
                    'blog_count': len(blog_results.get('items', [])),
                    'news_count': len(news_results.get('items', [])),
                    'total_mentions': len(blog_results.get('items', [])) + len(news_results.get('items', [])),
                    'blog_total': blog_results.get('total', 0),
                    'news_total': news_results.get('total', 0)
                }
                
            except Exception as e:
                self.logger.error(f"키워드 '{keyword}' 트렌드 분석 실패: {e}")
                trend_data[keyword] = {
                    'blog_count': 0,
                    'news_count': 0,
                    'total_mentions': 0,
                    'blog_total': 0,
                    'news_total': 0
                }
        
        return trend_data
    
    def extract_keywords_from_results(self, search_results: Dict[str, Any]) -> List[str]:
        """
        검색 결과에서 키워드 추출
        Args:
            search_results (Dict): 검색 결과
        Returns:
            List[str]: 추출된 키워드 목록
        """
        keywords = []
        
        try:
            items = search_results.get('items', [])
            
            for item in items:
                title = item.get('title', '')
                description = item.get('description', '')
                
                # HTML 태그 제거
                import re
                title = re.sub('<[^<]+?>', '', title)
                description = re.sub('<[^<]+?>', '', description)
                
                # 간단한 키워드 추출 (공백으로 분리)
                title_words = title.split()
                desc_words = description.split()
                
                keywords.extend(title_words[:3])  # 제목에서 상위 3개
                keywords.extend(desc_words[:2])   # 설명에서 상위 2개
                
        except Exception as e:
            self.logger.error(f"키워드 추출 오류: {e}")
        
        # 중복 제거 및 길이 필터링
        unique_keywords = list(set([k for k in keywords if len(k) > 1]))
        return unique_keywords[:10]  # 상위 10개만

# 사용 예제 및 테스트 함수
def example_usage():
    """네이버 API 사용 예제"""
    
    # API 키 설정 (실제 사용시 환경변수나 설정파일에서 읽어오세요)
    CLIENT_ID = "your_client_id_here"
    CLIENT_SECRET = "your_client_secret_here"
    
    # 네이버 API 초기화
    naver_api = NaverAPI(CLIENT_ID, CLIENT_SECRET)
    
    print("=== 네이버 API 테스트 ===")
    
    # 1. 블로그 검색
    print("\n1. 블로그 검색:")
    blog_results = naver_api.search_blog("청약", display=5)
    for item in blog_results.get('items', [])[:3]:
        print(f"- {item.get('title', '')}")
    
    # 2. 뉴스 검색
    print("\n2. 뉴스 검색:")
    news_results = naver_api.search_news("부동산", display=5)
    for item in news_results.get('items', [])[:3]:
        print(f"- {item.get('title', '')}")
    
    # 3. 번역
    print("\n3. 번역:")
    translated = naver_api.translate_text("안녕하세요", source='ko', target='en')
    print(f"한국어 -> 영어: {translated}")
    
    # 4. URL 단축
    print("\n4. URL 단축:")
    short_url = naver_api.shorten_url("https://www.naver.com")
    print(f"단축 URL: {short_url}")
    
    # 5. 종합 검색
    print("\n5. 종합 검색:")
    comprehensive_results = naver_api.search_comprehensive("분양", ['blog', 'news'])
    print(f"블로그 결과: {len(comprehensive_results.get('blog', {}).get('items', []))}건")
    print(f"뉴스 결과: {len(comprehensive_results.get('news', {}).get('items', []))}건")

if __name__ == "__main__":
    example_usage()