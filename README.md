# 🥗 급식영양 코치

> 전국 학교의 실시간 급식 정보를 조회하고 건강한 음식을 추천하는 웹 애플리케이션

## 📋 프로젝트 개요

- **목표**: 학교 급식에서 건강한 메뉴를 찾아 학생들이 올바른 식단을 선택하도록 돕기
- **데이터**: NEIS(나이스) Open API - 교육부 공식 급식 정보
- **플랫폼**: Flask 기반 웹 애플리케이션

## ✨ 주요 기능

### 1️⃣ 지역 선택
- 전국 16개 광역시/도 선택 가능
- 올바른 시도교육청 코드 기반

### 2️⃣ 학교 검색 & 선택
- 선택한 지역의 모든 학교 조회 (초등학교, 중학교, 고등학교)
- 학교명 실시간 필터링 검색
- 도로명주소로 같은 이름 학교 구분

### 3️⃣ 급식 정보 조회
- 주간 급식표를 달력 형태로 표시 (월-금)
- 아침, 점심, 저녁 메뉴 모두 지원
- 칼로리 및 영양 정보 표시

### 4️⃣ 건강한 음식 분석
- 급식 메뉴 중 건강한 음식 자동 감지
- 건강도 점수 표시
- 각 음식의 식사 시간 및 날짜 표시

## 🚀 설치 & 실행

### 사전 요구사항
- Python 3.8+
- pip

### 1. 프로젝트 클론
```bash
git clone https://github.com/yourusername/School-Nutrition-Coach-app.git
cd School-Nutrition-Coach-app
```

### 2. NEIS API 인증키 발급
- [NEIS 교육정보 개방 포털](https://open.neis.go.kr)에 접속
- 회원가입 후 "인증키 신청" 메뉴에서 발급

### 3. 환경 변수 설정
`.env` 파일을 생성하고 아래 내용을 추가합니다:

```
NEIS_DATA_OPEN_API_KEY=your_api_key_here
```

### 4. 의존성 설치
```bash
pip install -r requirements.txt
```

### 5. 애플리케이션 실행
```bash
python School_Nutrition_Coach.py
```

웹 브라우저에서 `http://localhost:5000` 접속

## 📁 프로젝트 구조

```
project5_School_Nutrition_Coach_app/
├── School_Nutrition_Coach.py    # Flask 메인 애플리케이션
├── ai_helper.py                 # NEIS API 통신 로직
├── nutrition_data.py            # 건강한 음식 데이터
├── requirements.txt             # 의존성 라이브러리
├── .env                         # 환경 변수 (Git 무시)
├── .gitignore                   # Git 무시 파일 목록
├── templates/
│   └── index.html               # 웹 UI
├── PLAN.md                      # 프로젝트 계획
└── README.md                    # 이 파일
```

## 🔧 주요 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | 메인 페이지 |
| `/api/regions` | GET | 지역 목록 조회 |
| `/api/schools/<atpt_code>` | GET | 학교 검색 |
| `/api/meals` | GET | 급식 정보 조회 |
| `/api/analyze` | POST | 건강한 음식 분석 |

## 📊 사용한 기술

- **백엔드**: Flask (Python 웹 프레임워크)
- **API**: NEIS Open API (JSON 형식)
- **프론트엔드**: HTML, CSS, JavaScript (Vanilla)
- **데이터 처리**: JSON 파싱, 정규식 기반 메뉴 파싱

## 🎯 개발 계획

- [ ] 모바일 반응형 UI 개선
- [ ] 알레르기 정보 필터링
- [ ] 주간 칼로리 차트
- [ ] 사용자 맞춤 건강 점수
- [ ] 학교 비교 기능
- [ ] 다국어 지원

## ⚠️ 주의사항

### 성능
- KEY 없이도 호출 가능하지만 **최대 5건만 반환됩니다**
- 정상 작동을 위해 NEIS API 인증키 발급이 필수입니다

### 데이터
- 주말/방학/휴무일에는 급식 정보가 없을 수 있습니다
- 학교가 급식 정보를 입력하지 않으면 데이터가 없습니다

## 📚 참고 자료

- [NEIS Open API 가이드](https://open.neis.go.kr/hub/guide)
- [시도교육청 코드 표](https://open.neis.go.kr)

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 👨‍💻 기여

버그 리포트, 기능 제안, Pull Request를 환영합니다!

## 📧 문의

문제가 있으면 GitHub Issues에 등록해주세요.

---

**마지막 업데이트**: 2026-11-25
