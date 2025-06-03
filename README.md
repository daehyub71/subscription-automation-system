# 🏠 청약 분양정보 자동화 시스템

공공데이터포털의 청약홈 분양정보 조회 서비스 API를 활용하여 분양정보를 자동으로 수집하고 이메일로 전송하는 Python 애플리케이션입니다.

## ✨ 주요 기능

- 🔄 **자동 데이터 수집**: 공공데이터포털 API를 통한 최신 분양정보 수집
- 📊 **엑셀 파일 생성**: 수집된 데이터를 보기 좋은 엑셀 파일로 자동 생성
- 📧 **이메일 자동 전송**: Gmail SMTP를 통한 엑셀 파일 첨부 및 HTML 이메일 전송
- 💬 **카카오톡 알림**: 분양정보 업데이트 시 카카오톡 메시지 전송 (선택사항)
- 🖥️ **직관적인 GUI**: tkinter 기반의 사용하기 쉬운 그래픽 인터페이스
- ⚙️ **설정 관리**: 암호화된 설정 저장 및 불러오기
- 📝 **상세한 로깅**: 모든 작업 과정의 상세한 로그 기록

## 🔧 시스템 요구사항

- **Python 3.8 이상**
- **Windows 10/11** (다른 OS에서도 동작하지만 Windows에서 최적화됨)
- **인터넷 연결** (API 호출 및 이메일 전송용)

## 📦 설치 방법

### 1. 저장소 클론 또는 다운로드

```bash
git clone https://github.com/your-username/subscription-automation.git
cd subscription-automation
```

또는 ZIP 파일로 다운로드하여 압축 해제

### 2. 필수 라이브러리 설치

```bash
pip install -r requirements.txt
```

필수 라이브러리 목록:
- `requests` - API 호출
- `pandas` - 데이터 처리  
- `openpyxl` - 엑셀 파일 생성
- `cryptography` - 설정 암호화
- `schedule` - 스케줄링
- `colorlog` - 로그 색상 표시

### 3. 프로그램 실행

```bash
python main.py
```

## 🚀 사용 방법

### 1단계: 공공데이터포털 API 키 발급

1. [공공데이터포털](https://www.data.go.kr) 접속
2. 회원가입 및 로그인
3. "한국부동산원_청약홈 분양정보 조회 서비스" 검색
4. 활용신청 후 승인 대기 (보통 1-2시간)
5. 승인 후 인증키 확인

### 2단계: Gmail 앱 비밀번호 설정

1. [Google 계정 관리](https://myaccount.google.com) 접속
2. **보안** → **2단계 인증** 활성화
3. **보안** → **앱 비밀번호** 생성
4. "메일" 선택 후 16자리 앱 비밀번호 복사

### 3단계: 프로그램 설정

1. 프로그램 실행 후 다음 정보 입력:
   - **공공데이터포털 인증키**
   - **발신자 Gmail 주소**
   - **Gmail 앱 비밀번호** 
   - **수신자 이메일 주소** (복수 가능)

2. **테스트 버튼**으로 설정 확인

3. **설정저장**으로 정보 저장

### 4단계: 시스템 실행

1. **실행** 버튼 클릭
2. 진행상태 및 로그 확인
3. 이메일로 분양정보 엑셀 파일 수신

## 📁 프로젝트 구조

```
subscription_automation/
├── main.py                  # 메인 실행 파일
├── requirements.txt         # 필수 라이브러리 목록
├── README.md               # 사용자 가이드
├── config/
│   └── settings.ini        # 기본 설정 파일
├── gui/
│   ├── __init__.py
│   └── main_window.py      # GUI 메인 창
├── api/
│   ├── __init__.py
│   ├── public_data.py      # 공공데이터 API 연동
│   └── kakao_api.py        # 카카오톡 API 연동
├── utils/
│   ├── __init__.py
│   ├── config_manager.py   # 설정 관리
│   ├── excel_handler.py    # 엑셀 파일 생성
│   └── email_sender.py     # 이메일 전송
├── output/                 # 생성된 엑셀 파일 저장
└── logs/                   # 로그 파일 저장
```

## 🎯 주요 기능 상세

### 📊 엑셀 파일 생성

- **파일명**: `청약분양정보_YYYYMMDD_HHMMSS.xlsx`
- **포함 정보**:
  - 순번, 주택명, 공급지역, 공급규모
  - 모집공고일, 청약접수일, 당첨발표일
  - 계약일, 입주예정일, 분양가격
  - 건설업체, 분양업체, 연락처, 홈페이지
- **스타일링**: 헤더 색상, 테두리, 자동 컬럼 크기 조정
- **다중 시트**: 일반분양, APT분양, 오피스텔분양, 전체요약

### 📧 이메일 전송

- **HTML 형식**: 보기 좋은 템플릿 적용
- **파일 첨부**: 엑셀 파일 자동 첨부
- **요약 정보**: 분양 건수 및 주요 정보 요약
- **복수 수신자**: 여러 이메일 주소로 동시 전송

### 💬 카카오톡 알림 (선택사항)

- **간단한 알림**: 분양정보 업데이트 알림
- **요약 정보**: 총 분양 건수 및 카테고리별 현황

## ⚠️ 문제 해결

### 자주 발생하는 오류

#### 1. tkinter 관련 오류
```
ERROR: Could not find a version that satisfies the requirement tkinter
```
**해결방법**: tkinter는 Python 표준 라이브러리이므로 별도 설치 불필요

#### 2. API 연결 실패
```
API 오류: SERVICE_KEY_IS_NOT_REGISTERED_ERROR
```
**해결방법**: 
- 공공데이터포털에서 API 활용신청 승인 확인
- 인증키 정확성 확인

#### 3. 이메일 전송 실패
```
Authentication failed
```
**해결방법**:
- Gmail 2단계 인증 활성화 확인
- 앱 비밀번호 정확성 확인 (16자리, 공백 포함)

#### 4. 엑셀 파일 생성 실패
```
Permission denied
```
**해결방법**:
- 같은 이름의 엑셀 파일이 열려있지 않은지 확인
- output 폴더 권한 확인

### 로그 파일 확인

상세한 오류 정보는 `logs/` 폴더의 로그 파일에서 확인 가능합니다.

```
logs/
├── main_20241219.log           # 메인 로그
├── subscription_system_20241219.log  # 시스템 로그
```

## 🔒 보안 고려사항

- **설정 암호화**: 이메일 비밀번호, API 키 등 민감정보 암호화 저장
- **앱 비밀번호**: Gmail 일반 비밀번호 대신 앱 비밀번호 사용 권장
- **HTTPS/TLS**: 모든 API 호출 및 이메일 전송 시 보안 연결 사용

## 📝 사용 팁

### 1. 정기적 실행
- 스케줄 기능을 사용하여 매일 자동 실행 설정
- Windows 작업 스케줄러와 연동하여 부팅 시 자동 실행

### 2. 수신자 관리
- 여러 수신자 등록으로 팀원들과 정보 공유
- 더블클릭으로 수신자 제거 가능

### 3. 설정 백업
- 설정저장 후 `config/settings.ini` 파일 백업 권장
- 다른 컴퓨터에서도 같은 설정 사용 가능

## 🤝 기여하기

버그 리포트, 기능 제안, 코드 기여를 환영합니다!

1. 이슈 등록: [GitHub Issues](https://github.com/your-username/subscription-automation/issues)
2. 풀 리퀘스트: [GitHub Pull Requests](https://github.com/your-username/subscription-automation/pulls)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- **이메일**: your-email@example.com
- **GitHub**: [프로젝트 페이지](https://github.com/your-username/subscription-automation)

## 🔄 업데이트 로그

### v1.0.0 (2024-12-19)
- 초기 릴리스
- 공공데이터 API 연동
- GUI 기반 설정 관리
- 이메일 자동 전송
- 엑셀 파일 생성
- 카카오톡 알림 (베타)

---

**⚡ 빠른 시작**: `python main.py` 실행 → API 키 입력 → 이메일 설정 → 실행!