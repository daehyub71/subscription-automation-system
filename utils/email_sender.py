#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이메일 전송 모듈 (네이버 API 결과 포함)
파일명: utils/email_sender.py
작성자: 청약 자동화 시스템
설명: Gmail SMTP를 통한 이메일 전송 및 파일 첨부, 네이버 API 결과 포함
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import logging
from typing import List, Optional, Dict, Tuple

class EmailSender:
    """Gmail SMTP 이메일 전송 클래스"""
    
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        """
        초기화
        Args:
            smtp_server (str): SMTP 서버 주소
            smtp_port (int): SMTP 포트 번호
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.logger = logging.getLogger(__name__)
    
    def test_connection(self, sender_email: str, app_password: str) -> Tuple[bool, str]:
        """
        SMTP 연결 테스트
        Args:
            sender_email (str): 발신자 이메일
            app_password (str): Gmail 앱 비밀번호
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            self.logger.info("SMTP 연결 테스트 시작")
            
            # SMTP 서버 연결
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # TLS 보안 연결
            
            # 로그인 테스트
            server.login(sender_email, app_password)
            server.quit()
            
            self.logger.info("SMTP 연결 테스트 성공")
            return True, "SMTP 연결 성공"
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"인증 실패: Gmail 주소 또는 앱 비밀번호를 확인하세요. ({e})"
            self.logger.error(error_msg)
            return False, error_msg
            
        except smtplib.SMTPConnectError as e:
            error_msg = f"SMTP 서버 연결 실패: 네트워크 연결을 확인하세요. ({e})"
            self.logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"예상치 못한 오류: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def send_subscription_email(self, 
                               sender_email: str, 
                               app_password: str,
                               recipients: List[str], 
                               excel_file_path: str,
                               data_summary: Dict,
                               naver_results: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        청약 분양정보 이메일 전송 (네이버 API 결과 포함)
        Args:
            sender_email (str): 발신자 이메일
            app_password (str): Gmail 앱 비밀번호  
            recipients (List[str]): 수신자 이메일 목록
            excel_file_path (str): 첨부할 엑셀 파일 경로
            data_summary (Dict): 데이터 요약 정보
            naver_results (Optional[Dict]): 네이버 API 결과
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            self.logger.info(f"이메일 전송 시작: {len(recipients)}명의 수신자")
            
            # 이메일 메시지 생성
            msg = self._create_email_message(
                sender_email, 
                recipients, 
                excel_file_path, 
                data_summary,
                naver_results
            )
            
            # SMTP 서버 연결 및 전송
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(sender_email, app_password)
            
            # 이메일 전송
            text = msg.as_string()
            server.sendmail(sender_email, recipients, text)
            server.quit()
            
            success_msg = f"이메일 전송 성공: {len(recipients)}명"
            self.logger.info(success_msg)
            return True, success_msg
            
        except Exception as e:
            error_msg = f"이메일 전송 실패: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _create_email_message(self, 
                             sender_email: str, 
                             recipients: List[str], 
                             excel_file_path: str,
                             data_summary: Dict,
                             naver_results: Optional[Dict] = None) -> MIMEMultipart:
        """
        이메일 메시지 생성
        Args:
            sender_email (str): 발신자 이메일
            recipients (List[str]): 수신자 목록
            excel_file_path (str): 엑셀 파일 경로
            data_summary (Dict): 데이터 요약 정보
            naver_results (Optional[Dict]): 네이버 API 결과
        Returns:
            MIMEMultipart: 이메일 메시지 객체
        """
        # 메시지 객체 생성
        msg = MIMEMultipart('alternative')
        
        # 이메일 헤더 설정
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipients)
        
        # 네이버 API 결과 포함 여부에 따른 제목 설정
        if naver_results:
            msg['Subject'] = f"🏠 청약 분양정보 + 시장분석 업데이트 - {datetime.now().strftime('%Y년 %m월 %d일')}"
        else:
            msg['Subject'] = f"🏠 청약 분양정보 업데이트 - {datetime.now().strftime('%Y년 %m월 %d일')}"
        
        # 이메일 본문 생성
        html_body = self._create_html_body(data_summary, excel_file_path, naver_results)
        text_body = self._create_text_body(data_summary, naver_results)
        
        # 본문 첨부
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # 엑셀 파일 첨부
        if excel_file_path and os.path.exists(excel_file_path):
            self._attach_file(msg, excel_file_path)
            self.logger.info(f"첨부파일 추가: {os.path.basename(excel_file_path)}")
        
        return msg
    
    def _create_html_body(self, data_summary: Dict, excel_file_path: str, naver_results: Optional[Dict] = None) -> str:
        """
        HTML 이메일 본문 생성 (네이버 API 결과 포함)
        Args:
            data_summary (Dict): 데이터 요약 정보
            excel_file_path (str): 엑셀 파일 경로
            naver_results (Optional[Dict]): 네이버 API 결과
        Returns:
            str: HTML 본문
        """
        # 기본 통계 계산
        total_count = sum(len(data_list) for data_list in data_summary.values() if isinstance(data_list, list))
        general_count = len(data_summary.get('general', []))
        apt_count = len(data_summary.get('apt', []))
        officetel_count = len(data_summary.get('officetel', []))
        
        # 파일명 추출
        filename = os.path.basename(excel_file_path) if excel_file_path else "분양정보.xlsx"
        
        # 최신 분양정보 HTML 생성
        recent_items_html = self._generate_recent_items_html(data_summary)
        
        # 네이버 API 결과 HTML 생성
        naver_section_html = self._generate_naver_analysis_html(naver_results) if naver_results else ""
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ 
                    font-family: '맑은 고딕', Arial, sans-serif; 
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #4F81BD 0%, #6BA3E0 100%);
                    color: white; 
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 26px;
                    font-weight: bold;
                }}
                .content {{ 
                    padding: 30px;
                }}
                .summary {{ 
                    background-color: #f8f9fa; 
                    padding: 20px; 
                    margin: 20px 0;
                    border-radius: 8px;
                    border-left: 4px solid #4F81BD;
                }}
                .summary h3 {{
                    margin-top: 0;
                    color: #4F81BD;
                    font-size: 18px;
                }}
                .stats {{
                    display: flex;
                    justify-content: space-around;
                    margin: 20px 0;
                    flex-wrap: wrap;
                }}
                .stat-item {{
                    text-align: center;
                    padding: 15px;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin: 5px;
                    min-width: 120px;
                }}
                .stat-number {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #4F81BD;
                }}
                .stat-label {{
                    font-size: 12px;
                    color: #666;
                    margin-top: 5px;
                }}
                .recent-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background-color: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .recent-table th {{
                    background-color: #4F81BD;
                    color: white;
                    padding: 12px 8px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 14px;
                }}
                .recent-table td {{
                    padding: 8px;
                    border: 1px solid #ddd;
                    font-size: 13px;
                }}
                .naver-section {{
                    background-color: #f0f8ff;
                    border: 1px solid #4F81BD;
                    border-radius: 10px;
                    margin: 30px 0;
                    padding: 0;
                    overflow: hidden;
                }}
                .naver-header {{
                    background: linear-gradient(135deg, #2DB400 0%, #4FD400 100%);
                    color: white;
                    padding: 15px 20px;
                    font-size: 18px;
                    font-weight: bold;
                }}
                .naver-content {{
                    padding: 20px;
                }}
                .analysis-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .analysis-card {{
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }}
                .analysis-card h4 {{
                    margin-top: 0;
                    color: #2DB400;
                    font-size: 16px;
                    border-bottom: 2px solid #2DB400;
                    padding-bottom: 5px;
                }}
                .news-item {{
                    background-color: #f9f9f9;
                    border-left: 3px solid #2DB400;
                    padding: 10px 15px;
                    margin: 10px 0;
                    border-radius: 0 5px 5px 0;
                }}
                .news-title {{
                    font-weight: bold;
                    color: #333;
                    margin-bottom: 5px;
                    font-size: 14px;
                }}
                .news-date {{
                    color: #666;
                    font-size: 12px;
                    margin-bottom: 5px;
                }}
                .news-desc {{
                    color: #555;
                    font-size: 13px;
                    line-height: 1.4;
                }}
                .keywords {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 5px;
                    margin: 10px 0;
                }}
                .keyword-tag {{
                    background-color: #2DB400;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    border-top: 1px solid #eee;
                }}
                .attachment {{
                    background-color: #e8f4f8;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border: 1px solid #4F81BD;
                }}
                .attachment-icon {{
                    color: #4F81BD;
                    font-size: 18px;
                    margin-right: 10px;
                }}
                .highlight-box {{
                    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
                    border: 1px solid #ffc107;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 15px 0;
                }}
                .trend-stat {{
                    display: inline-block;
                    background-color: #4F81BD;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 5px;
                    margin: 5px;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏠 청약 분양정보{'+ 시장분석' if naver_results else ''} 업데이트</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">
                        {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')} 기준
                    </p>
                </div>
                
                <div class="content">
                    <p>안녕하세요! 최신 청약 분양정보{'와 시장 분석 결과' if naver_results else ''}를 전달드립니다.</p>
                    
                    <div class="summary">
                        <h3>📊 분양정보 요약</h3>
                        <div class="stats">
                            <div class="stat-item">
                                <div class="stat-number">{total_count}</div>
                                <div class="stat-label">총 분양건수</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">{general_count}</div>
                                <div class="stat-label">일반분양</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">{apt_count}</div>
                                <div class="stat-label">APT분양</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">{officetel_count}</div>
                                <div class="stat-label">오피스텔분양</div>
                            </div>
                        </div>
                    </div>
                    
                    {recent_items_html}
                    
                    {naver_section_html}
                    
                    <div class="attachment">
                        <span class="attachment-icon">📎</span>
                        <strong>첨부파일:</strong> {filename}
                        <br>
                        <small style="color: #666;">자세한 분양정보는 첨부된 엑셀 파일을 확인해주세요.</small>
                    </div>
                    
                    <p style="margin-top: 30px;">
                        궁금한 사항이 있으시면 언제든지 연락주세요.<br>
                        감사합니다.
                    </p>
                </div>
                
                <div class="footer">
                    <p>
                        <strong>청약 분양정보 자동화 시스템</strong><br>
                        이 이메일은 자동으로 생성되었습니다.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _generate_recent_items_html(self, data_summary: Dict) -> str:
        """분양정보 HTML 생성 (아파트 20개 이하면 모든 아파트 표시)"""
        # 아파트 분양정보 개수 확인
        apt_items = data_summary.get('apt', [])
        apt_count = len(apt_items)
        
        # 아파트 분양이 20개 이하인 경우: 모든 아파트 분양정보 표시
        if apt_count <= 20 and apt_count > 0:
            display_items = []
            for item in apt_items:
                item_with_category = item.copy()
                item_with_category['분양유형'] = 'APT분양'
                display_items.append(item_with_category)
            
            # 최신순 정렬
            try:
                display_items.sort(key=lambda x: x.get('모집공고일', ''), reverse=True)
            except:
                pass
            
            title = f"🏠 APT 분양정보 (전체 {apt_count}개)"
            
        else:
            # 아파트 분양이 20개 초과이거나 0개인 경우: 기존 로직 (최신 5개)
            all_items = []
            
            for category, items in data_summary.items():
                if isinstance(items, list):
                    for item in items:
                        item_with_category = item.copy()
                        item_with_category['분양유형'] = {
                            'general': '일반분양',
                            'apt': 'APT분양',
                            'officetel': '오피스텔분양'
                        }.get(category, category)
                        all_items.append(item_with_category)
            
            # 최신순 정렬
            try:
                all_items.sort(key=lambda x: x.get('모집공고일', ''), reverse=True)
                display_items = all_items[:5]
            except:
                display_items = all_items[:5]
            
            title = "🏠 최신 분양정보 (상위 5개)"
        
        if not display_items:
            return '<p style="color: #666; text-align: center; padding: 20px;">표시할 분양정보가 없습니다.</p>'
        
        # 분양정보 HTML 생성
        items_html = ""
        for i, item in enumerate(display_items, 1):
            # 청약접수 상태 확인
            today = datetime.now().strftime('%Y%m%d')
            rcept_start = item.get('청약접수시작일', '').replace('-', '')
            rcept_end = item.get('청약접수종료일', '').replace('-', '')
            
            status = ""
            if rcept_start and rcept_end:
                if rcept_start <= today <= rcept_end:
                    status = '<span style="color: #e74c3c; font-weight: bold;">🔥 접수중</span>'
                elif today < rcept_start:
                    status = '<span style="color: #3498db; font-weight: bold;">⏰ 예정</span>'
                elif today > rcept_end:
                    status = '<span style="color: #95a5a6;">✅ 완료</span>'
            
            items_html += f"""
            <tr style="background-color: {'#f9f9f9' if i % 2 == 0 else '#ffffff'};">
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{i}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{item.get('분양유형', '')}</td>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">
                    {item.get('주택명', '')}<br>
                    <small style="color: #666;">{item.get('공급위치', '')}</small>
                </td>
                <td style="padding: 8px; border: 1px solid #ddd;">{item.get('공급지역', '')}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                    {item.get('모집공고일', '')}<br>
                    {status}
                </td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                    <small>{item.get('청약접수시작일', '')}</small><br>
                    <small>~{item.get('청약접수종료일', '')}</small>
                </td>
            </tr>
            """
        
        return f'''
        <h3 style="color: #4F81BD; margin-top: 30px;">{title}</h3>
        <table class="recent-table">
            <thead>
                <tr>
                    <th style="width: 50px;">순번</th>
                    <th style="width: 80px;">분양유형</th>
                    <th style="width: 250px;">주택명/위치</th>
                    <th style="width: 100px;">공급지역</th>
                    <th style="width: 120px;">모집공고일/상태</th>
                    <th style="width: 130px;">청약접수기간</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>
        '''
    
    def _generate_naver_analysis_html(self, naver_results: Dict) -> str:
        """네이버 API 분석 결과 HTML 생성"""
        if not naver_results:
            return ""
        
        analysis_cards = []
        
        # 뉴스 검색 결과
        if 'news_search' in naver_results and naver_results['news_search']:
            news_html = ""
            for news in naver_results['news_search'][:3]:  # 상위 3개만
                title = news.get('title', '').replace('<b>', '').replace('</b>', '')
                news_html += f"""
                <div class="news-item">
                    <div class="news-title">{title}</div>
                    <div class="news-date">📅 {news.get('pubDate', 'N/A')}</div>
                    <div class="news-desc">{news.get('description', '')[:100]}...</div>
                </div>
                """
            
            analysis_cards.append(f"""
            <div class="analysis-card">
                <h4>📰 관련 뉴스</h4>
                <p><strong>총 {len(naver_results['news_search'])}건</strong>의 뉴스가 검색되었습니다.</p>
                {news_html}
            </div>
            """)
        
        # 시장 동향 분석
        if 'market_trends' in naver_results and naver_results['market_trends']:
            trends = naver_results['market_trends']
            keywords_html = ""
            
            keywords = trends.get('market_keywords', [])
            if keywords:
                for keyword in keywords[:8]:  # 상위 8개
                    keywords_html += f'<span class="keyword-tag">{keyword}</span>'
            
            latest_news_html = ""
            latest_news = trends.get('latest_news', [])
            if latest_news:
                for news in latest_news[:2]:  # 상위 2개
                    title = news.get('title', '').replace('<b>', '').replace('</b>', '')
                    latest_news_html += f"""
                    <div class="news-item">
                        <div class="news-title">{title}</div>
                        <div class="news-date">📅 {news.get('pubDate', 'N/A')}</div>
                    </div>
                    """
            
            analysis_cards.append(f"""
            <div class="analysis-card">
                <h4>📈 시장 동향 분석</h4>
                <div class="highlight-box">
                    <span class="trend-stat">뉴스 {trends.get('news_count', 0)}건</span>
                    <span class="trend-stat">블로그 {trends.get('blog_count', 0)}건</span>
                </div>
                
                {f'<p><strong>🔑 주요 키워드:</strong></p><div class="keywords">{keywords_html}</div>' if keywords else ''}
                
                {f'<p><strong>📰 최신 관련 뉴스:</strong></p>{latest_news_html}' if latest_news else ''}
            </div>
            """)
        
        # 종합 분석 보고서
        if 'comprehensive_report' in naver_results and naver_results['comprehensive_report']:
            report = naver_results['comprehensive_report']
            summary = report.get('summary', {})
            
            regional_html = ""
            regional_analysis = report.get('regional_analysis', {})
            if regional_analysis:
                for region, data in list(regional_analysis.items())[:3]:  # 상위 3개 지역
                    regional_html += f"""
                    <div style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
                        <strong>📍 {region}</strong><br>
                        <small>뉴스 {data.get('news_count', 0)}건, 블로그 {data.get('blog_count', 0)}건</small>
                    </div>
                    """
            
            hot_keywords_html = ""
            hot_keywords = summary.get('hot_keywords', [])
            if hot_keywords:
                for keyword in hot_keywords[:6]:
                    hot_keywords_html += f'<span class="keyword-tag">{keyword}</span>'
            
            analysis_cards.append(f"""
            <div class="analysis-card">
                <h4>🔍 종합 분석 보고서</h4>
                <div class="highlight-box">
                    <p><strong>📋 요약:</strong></p>
                    <p>• 총 분양 건수: <strong>{summary.get('total_subscriptions', 0)}건</strong></p>
                    <p>• 분석 지역: <strong>{len(summary.get('analyzed_regions', []))}개 지역</strong></p>
                </div>
                
                {f'<p><strong>🔥 핫 키워드:</strong></p><div class="keywords">{hot_keywords_html}</div>' if hot_keywords else ''}
                
                {f'<p><strong>🌍 지역별 분석:</strong></p>{regional_html}' if regional_html else ''}
            </div>
            """)
        
        if not analysis_cards:
            return ""
        
        return f"""
        <div class="naver-section">
            <div class="naver-header">
                🔍 네이버 API 시장 분석 결과
            </div>
            <div class="naver-content">
                <p>네이버 검색 API를 통해 수집한 시장 동향과 관련 뉴스를 분석한 결과입니다.</p>
                <div class="analysis-grid">
                    {''.join(analysis_cards)}
                </div>
            </div>
        </div>
        """
    
    def _create_text_body(self, data_summary: Dict, naver_results: Optional[Dict] = None) -> str:
        """
        텍스트 이메일 본문 생성 (네이버 API 결과 포함)
        Args:
            data_summary (Dict): 데이터 요약 정보
            naver_results (Optional[Dict]): 네이버 API 결과
        Returns:
            str: 텍스트 본문
        """
        total_count = sum(len(data_list) for data_list in data_summary.values() if isinstance(data_list, list))
        general_count = len(data_summary.get('general', []))
        apt_count = len(data_summary.get('apt', []))
        officetel_count = len(data_summary.get('officetel', []))
        
        # 네이버 API 결과 텍스트 생성
        naver_text = ""
        if naver_results:
            naver_text = "\n\n🔍 네이버 API 시장 분석 결과\n" + "="*40 + "\n"
            
            # 뉴스 검색 결과
            if 'news_search' in naver_results and naver_results['news_search']:
                naver_text += f"\n📰 관련 뉴스: {len(naver_results['news_search'])}건\n"
                for i, news in enumerate(naver_results['news_search'][:3], 1):
                    title = news.get('title', '').replace('<b>', '').replace('</b>', '')
                    naver_text += f"{i}. {title}\n   📅 {news.get('pubDate', 'N/A')}\n"
            
            # 시장 동향
            if 'market_trends' in naver_results and naver_results['market_trends']:
                trends = naver_results['market_trends']
                naver_text += f"\n📈 시장 동향 분석\n"
                naver_text += f"뉴스: {trends.get('news_count', 0)}건, 블로그: {trends.get('blog_count', 0)}건\n"
                
                keywords = trends.get('market_keywords', [])
                if keywords:
                    naver_text += f"주요 키워드: {', '.join(keywords[:5])}\n"
            
            # 종합 분석
            if 'comprehensive_report' in naver_results and naver_results['comprehensive_report']:
                report = naver_results['comprehensive_report']
                summary = report.get('summary', {})
                naver_text += f"\n🔍 종합 분석\n"
                naver_text += f"분석 지역: {len(summary.get('analyzed_regions', []))}개\n"
                
                hot_keywords = summary.get('hot_keywords', [])
                if hot_keywords:
                    naver_text += f"핫 키워드: {', '.join(hot_keywords[:5])}\n"
        
        text_body = f"""
청약 분양정보{'+ 시장분석' if naver_results else ''} 업데이트
{datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')} 기준

안녕하세요! 최신 청약 분양정보{'와 시장 분석 결과' if naver_results else ''}를 전달드립니다.

📊 분양정보 요약
- 총 분양건수: {total_count}건
- 일반분양: {general_count}건  
- APT분양: {apt_count}건
- 오피스텔분양: {officetel_count}건
{naver_text}

자세한 정보는 첨부된 엑셀 파일을 확인해주세요.

감사합니다.

---
청약 분양정보 자동화 시스템
이 이메일은 자동으로 생성되었습니다.
        """
        
        return text_body.strip()
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """
        파일 첨부 (한글 파일명 완벽 지원)
        """
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"첨부파일이 존재하지 않음: {file_path}")
                return
            
            # 파일명 추출
            filename = os.path.basename(file_path)
            
            # 파일 읽기
            with open(file_path, "rb") as attachment:
                # XLSX 파일용 MIME 타입
                part = MIMEBase('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                part.set_payload(attachment.read())
            
            # Base64 인코딩
            encoders.encode_base64(part)
            
            # 한글 파일명 처리
            import urllib.parse
            
            # URL 인코딩으로 한글 파일명 안전하게 처리
            encoded_filename = urllib.parse.quote(filename)
            
            # Content-Disposition 헤더 설정 (RFC 2231 방식)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename*=UTF-8\'\'{encoded_filename}; filename="{filename}"'
            )
            
            # 추가 헤더 설정
            part.add_header('Content-Type', f'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet; name="{filename}"')
            
            # 메시지에 첨부
            msg.attach(part)
            
            self.logger.info(f"첨부파일 추가 완료: {filename}")
            
        except Exception as e:
            self.logger.error(f"파일 첨부 오류: {e}")
    
    def send_test_email(self, sender_email: str, app_password: str, test_recipient: str) -> Tuple[bool, str]:
        """
        테스트 이메일 전송
        Args:
            sender_email (str): 발신자 이메일
            app_password (str): Gmail 앱 비밀번호
            test_recipient (str): 테스트 수신자
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = test_recipient
            msg['Subject'] = "🧪 청약 시스템 이메일 테스트"
            
            body = f"""
이메일 설정 테스트

발신자: {sender_email}
수신자: {test_recipient}
테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

이 이메일을 받으셨다면 이메일 설정이 정상적으로 완료된 것입니다! 🎉

청약 분양정보 자동화 시스템
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # SMTP 전송
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, test_recipient, msg.as_string())
            server.quit()
            
            success_msg = f"테스트 이메일 전송 성공: {test_recipient}"
            self.logger.info(success_msg)
            return True, success_msg
            
        except Exception as e:
            error_msg = f"테스트 이메일 전송 실패: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg