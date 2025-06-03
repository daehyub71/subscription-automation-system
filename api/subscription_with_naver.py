#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
청약 시스템 + 네이버 API 통합 모듈
파일명: api/subscription_with_naver.py
"""

import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class SubscriptionNaverIntegration:
    """청약 시스템과 네이버 API 통합 클래스"""
    
    def __init__(self, naver_client_id: str, naver_client_secret: str):
        """
        초기화
        Args:
            naver_client_id (str): 네이버 API Client ID
            naver_client_secret (str): 네이버 API Client Secret
        """
        self.client_id = naver_client_id
        self.client_secret = naver_client_secret
        self.headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        self.logger = logging.getLogger(__name__)
    
    def search_related_news(self, apartment_name: str, location: str = "") -> List[Dict[str, Any]]:
        """
        분양정보 관련 뉴스 검색
        Args:
            apartment_name (str): 아파트명
            location (str): 지역명
        Returns:
            List[Dict]: 관련 뉴스 목록
        """
        try:
            # 검색 키워드 조합
            search_queries = []
            
            if apartment_name:
                search_queries.append(f'"{apartment_name}" 분양')
                search_queries.append(f'"{apartment_name}" 청약')
            
            if location:
                search_queries.append(f'"{location}" 분양')
                search_queries.append(f'"{location}" 청약')
                search_queries.append(f'"{location}" 아파트')
            
            all_news = []
            
            for query in search_queries:
                news_results = self._search_naver_news(query, display=10)
                
                for item in news_results.get('items', []):
                    # 중복 제거를 위한 URL 체크
                    if not any(existing['link'] == item['link'] for existing in all_news):
                        processed_item = self._process_news_item(item)
                        if processed_item:
                            all_news.append(processed_item)
            
            # 최신순 정렬
            all_news.sort(key=lambda x: x.get('pubDate', ''), reverse=True)
            
            self.logger.info(f"관련 뉴스 검색 완료: {apartment_name} {location}, {len(all_news)}건")
            return all_news[:20]  # 상위 20개만 반환
            
        except Exception as e:
            self.logger.error(f"관련 뉴스 검색 오류: {e}")
            return []
    
    def search_market_trends(self, location: str) -> Dict[str, Any]:
        """
        지역별 부동산 시장 트렌드 검색
        Args:
            location (str): 지역명
        Returns:
            Dict: 시장 트렌드 정보
        """
        try:
            trend_keywords = [
                f'"{location}" 아파트 시세',
                f'"{location}" 부동산 동향',
                f'"{location}" 아파트 가격',
                f'"{location}" 청약 경쟁률',
                f'"{location}" 분양권 시세'
            ]
            
            trend_data = {
                'location': location,
                'news_count': 0,
                'blog_count': 0,
                'latest_news': [],
                'market_keywords': [],
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            for keyword in trend_keywords:
                # 뉴스 검색
                news_results = self._search_naver_news(keyword, display=5)
                trend_data['news_count'] += len(news_results.get('items', []))
                
                # 최신 뉴스 추가
                for item in news_results.get('items', [])[:2]:
                    processed_item = self._process_news_item(item)
                    if processed_item and processed_item not in trend_data['latest_news']:
                        trend_data['latest_news'].append(processed_item)
                
                # 블로그 검색
                blog_results = self._search_naver_blog(keyword, display=5)
                trend_data['blog_count'] += len(blog_results.get('items', []))
            
            # 키워드 추출
            trend_data['market_keywords'] = self._extract_market_keywords(trend_data['latest_news'])
            
            return trend_data
            
        except Exception as e:
            self.logger.error(f"시장 트렌드 검색 오류: {e}")
            return {'location': location, 'error': str(e)}
    
    def analyze_competition_rate(self, apartment_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        청약 경쟁률 관련 정보 분석
        Args:
            apartment_list (List[Dict]): 아파트 목록
        Returns:
            Dict: 경쟁률 분석 결과
        """
        try:
            competition_analysis = {
                'total_analyzed': len(apartment_list),
                'high_competition': [],
                'market_insights': [],
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            for apt in apartment_list[:10]:  # 상위 10개만 분석
                apt_name = apt.get('주택명', '')
                location = apt.get('공급지역', '')
                
                if apt_name:
                    # 경쟁률 관련 뉴스 검색
                    competition_query = f'"{apt_name}" 경쟁률'
                    news_results = self._search_naver_news(competition_query, display=5)
                    
                    competition_info = {
                        'apartment_name': apt_name,
                        'location': location,
                        'news_count': len(news_results.get('items', [])),
                        'related_news': []
                    }
                    
                    for item in news_results.get('items', [])[:3]:
                        processed_item = self._process_news_item(item)
                        if processed_item:
                            competition_info['related_news'].append(processed_item)
                    
                    if competition_info['news_count'] > 0:
                        competition_analysis['high_competition'].append(competition_info)
            
            return competition_analysis
            
        except Exception as e:
            self.logger.error(f"경쟁률 분석 오류: {e}")
            return {'error': str(e)}
    
    def get_comprehensive_market_report(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        종합 시장 분석 보고서 생성
        Args:
            subscription_data (Dict): 청약 분양정보 데이터
        Returns:
            Dict: 종합 분석 보고서
        """
        try:
            report = {
                'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'summary': {
                    'total_subscriptions': 0,
                    'analyzed_regions': set(),
                    'hot_keywords': []
                },
                'regional_analysis': {},
                'market_trends': [],
                'investment_insights': []
            }
            
            # 전체 분양정보 통계
            for category, items in subscription_data.items():
                report['summary']['total_subscriptions'] += len(items)
                
                for item in items:
                    location = item.get('공급지역', '')
                    if location:
                        report['summary']['analyzed_regions'].add(location)
            
            # 지역별 분석
            for region in list(report['summary']['analyzed_regions'])[:5]:  # 상위 5개 지역
                regional_data = self.search_market_trends(region)
                report['regional_analysis'][region] = regional_data
            
            # 핫 키워드 추출
            all_keywords = []
            for region_data in report['regional_analysis'].values():
                all_keywords.extend(region_data.get('market_keywords', []))
            
            # 키워드 빈도 계산
            keyword_count = {}
            for keyword in all_keywords:
                keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
            
            # 상위 키워드 정렬
            sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
            report['summary']['hot_keywords'] = [k[0] for k in sorted_keywords[:10]]
            
            return report
            
        except Exception as e:
            self.logger.error(f"종합 보고서 생성 오류: {e}")
            return {'error': str(e)}
    
    def _search_naver_news(self, query: str, display: int = 10) -> Dict[str, Any]:
        """네이버 뉴스 검색 (내부 메서드)"""
        try:
            url = "https://openapi.naver.com/v1/search/news"
            params = {
                'query': query,
                'display': display,
                'start': 1,
                'sort': 'date'  # 최신순
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"네이버 뉴스 검색 오류: {e}")
            return {'items': [], 'total': 0}
    
    def _search_naver_blog(self, query: str, display: int = 10) -> Dict[str, Any]:
        """네이버 블로그 검색 (내부 메서드)"""
        try:
            url = "https://openapi.naver.com/v1/search/blog"
            params = {
                'query': query,
                'display': display,
                'start': 1,
                'sort': 'date'  # 최신순
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"네이버 블로그 검색 오류: {e}")
            return {'items': [], 'total': 0}
    
    def _process_news_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """뉴스 항목 처리 (HTML 태그 제거 등)"""
        try:
            # HTML 태그 제거
            title = re.sub('<[^<]+?>', '', item.get('title', ''))
            description = re.sub('<[^<]+?>', '', item.get('description', ''))
            
            # 특수문자 정리
            title = re.sub('&quot;', '"', title)
            title = re.sub('&amp;', '&', title)
            description = re.sub('&quot;', '"', description)
            description = re.sub('&amp;', '&', description)
            
            return {
                'title': title.strip(),
                'description': description.strip(),
                'link': item.get('link', ''),
                'pubDate': item.get('pubDate', ''),
                'source': '네이버뉴스'
            }
            
        except Exception as e:
            self.logger.error(f"뉴스 항목 처리 오류: {e}")
            return None
    
    def _extract_market_keywords(self, news_list: List[Dict[str, Any]]) -> List[str]:
        """뉴스에서 시장 관련 키워드 추출"""
        try:
            keywords = []
            market_terms = ['상승', '하락', '급등', '급락', '투자', '수익', '전망', '예측', '시세', '가격']
            
            for news in news_list:
                title = news.get('title', '')
                description = news.get('description', '')
                
                for term in market_terms:
                    if term in title or term in description:
                        keywords.append(term)
            
            # 중복 제거 및 빈도순 정렬
            unique_keywords = list(set(keywords))
            return unique_keywords[:10]
            
        except Exception as e:
            self.logger.error(f"키워드 추출 오류: {e}")
            return []

# 사용 예제
def example_integration():
    """청약 시스템과 네이버 API 통합 예제"""
    
    # 네이버 API 키 설정
    NAVER_CLIENT_ID = ""
    NAVER_CLIENT_SECRET = ""
    
    # 통합 클래스 초기화
    integration = SubscriptionNaverIntegration(NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)
    
    # 예시 청약 데이터
    sample_apartment = {
        '주택명': '래미안 강남포레스트',
        '공급지역': '서울 강남구',
        '모집공고일': '2025-06-01'
    }
    
    print("=== 청약 시스템 + 네이버 API 통합 테스트 ===")
    
    # 1. 관련 뉴스 검색
    print("\n1. 관련 뉴스 검색:")
    related_news = integration.search_related_news(
        sample_apartment['주택명'], 
        sample_apartment['공급지역']
    )
    
    for news in related_news[:3]:
        print(f"- {news.get('title', 'N/A')}")
    
    # 2. 시장 트렌드 분석
    print("\n2. 시장 트렌드 분석:")
    market_trends = integration.search_market_trends("강남구")
    print(f"뉴스 건수: {market_trends.get('news_count', 0)}")
    print(f"블로그 건수: {market_trends.get('blog_count', 0)}")
    print(f"주요 키워드: {', '.join(market_trends.get('market_keywords', [])[:5])}")

if __name__ == "__main__":
    example_integration()