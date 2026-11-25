import streamlit as st
import requests
import re
import datetime as dt
from functools import lru_cache
import os
from dotenv import load_dotenv

# 페이지 설정
st.set_page_config(
    page_title="🥗 급식영양 코치",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# API 설정
API_KEY = os.getenv('NEIS_DATA_OPEN_API_KEY', '')
BASE_URL = 'https://open.neis.go.kr/hub'

# 올바른 시도교육청 코드
REGION_CODES = {
    'B10': '서울',
    'C10': '부산',
    'D10': '대구',
    'E10': '인천',
    'F10': '광주',
    'G10': '대전',
    'H10': '울산',
    'I10': '세종',
    'J10': '경기',
    'K10': '강원',
    'M10': '충북',
    'N10': '충남',
    'P10': '전북',
    'Q10': '전남',
    'R10': '경북',
    'S10': '경남',
    'T10': '제주'
}

# 건강한 음식 목록
HEALTHY_FOODS = [
    '현미밥', '보리밥', '강황쌀밥', '클로렐라밥', '된장국', '콩나물국',
    '건새우아욱된장국', '짬뽕',
    '계란', '계란프라이', '우유', '요구르트', '치즈',
    '생선', '코다리살강정', '생선까스', '치킨까스', '돈까스',
    '불고기', '수육', '닭고기김치찜', '떡갈비스테이크', '등심탕수육',
    '시금치', '브로콜리', '나물', '콩나물무침', '야채',
    '샐러드', '과일샐러드', '오이지', '오이지매실무침',
    '배추김치', '백김치', '깍두기', '석박지',
    '견과류멸치볶음', '김', '김자반',
    '통곡물빵', '밥', '쌀밥', '흰쌀밥',
    '바나나', '딸기', '복숭아', '오렌지', '사과',
    '과일', '워터젤리', '하트파이', '초콜릿',
    '수제비', '들깨수제비', '카레라이스', '쫄면'
]

def neis_api(service, **params):
    """NEIS API 공통 호출 함수"""
    params.update({
        'KEY': API_KEY,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 100
    })

    try:
        response = requests.get(f'{BASE_URL}/{service}', params=params, timeout=10)
        data = response.json()

        if service not in data:
            return []

        return data[service][1]['row']
    except Exception as e:
        st.error(f"API 오류: {e}")
        return []

@st.cache_data
def search_schools(atpt_code, keyword=''):
    """학교 검색"""
    params = {'ATPT_OFCDC_SC_CODE': atpt_code}
    if keyword:
        params['SCHUL_NM'] = keyword

    schools = neis_api('schoolInfo', **params)

    result = []
    for school in schools:
        result.append({
            'code': school.get('SD_SCHUL_CODE', ''),
            'name': school.get('SCHUL_NM', ''),
            'address': school.get('ORG_RDNMA', '')
        })

    return result

@st.cache_data
def get_meal_data(atpt_code, school_code, year=None, month=None):
    """급식 정보 조회"""
    if year is None or month is None:
        now = dt.datetime.now()
        year = now.year
        month = now.month

    from_ymd = f'{year}{month:02d}01'
    to_ymd = f'{year}{month:02d}28'

    params = {
        'ATPT_OFCDC_SC_CODE': atpt_code,
        'SD_SCHUL_CODE': school_code,
        'MLSV_FROM_YMD': from_ymd,
        'MLSV_TO_YMD': to_ymd
    }

    meals_data = neis_api('mealServiceDietInfo', **params)

    meals = []
    for meal in meals_data:
        meal_date = meal.get('MLSV_YMD', '')
        meal_type = meal.get('MMEAL_SC_NM', '점심')
        menu_text = meal.get('DDISH_NM', '')

        foods = parse_menu(menu_text)

        if foods:
            meals.append({
                'type': meal_type,
                'date': format_date(meal_date),
                'foods': foods,
                'calorie': meal.get('CAL_INFO', '')
            })

    return meals

def parse_menu(menu_text):
    """메뉴 텍스트 파싱"""
    if not menu_text:
        return []

    menu_text = re.sub(r'<[^>]+>', '\n', menu_text)
    menu_text = menu_text.replace('*', '')
    menu_text = re.sub(r'\s*\([0-9.,]*\)', '', menu_text)

    items = [item.strip() for item in menu_text.replace('\n', ',').split(',')]
    foods = [item for item in items if item and len(item) > 1]

    return foods

def format_date(date_str):
    """날짜 형식 변환"""
    if len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    return date_str

def is_healthy(food):
    """건강한 음식 판별"""
    return any(food.lower() in healthy.lower() or healthy.lower() in food.lower()
               for healthy in HEALTHY_FOODS)

# 메인 UI
st.title("🥗 급식영양 코치")
st.subheader("전국 학교의 실시간 급식 정보를 조회하고 건강한 음식을 추천합니다")

# API KEY 체크
if not API_KEY:
    st.warning("⚠️ NEIS API 인증키가 필요합니다. .env 파일에 NEIS_DATA_OPEN_API_KEY를 설정하세요.")
    st.info("📌 [NEIS 교육정보 개방 포털](https://open.neis.go.kr)에서 인증키를 발급받을 수 있습니다.")

# 사이드바
st.sidebar.header("🔍 학교 검색")

col1, col2 = st.columns(2)

with col1:
    region_name = st.selectbox("지역 선택", list(REGION_CODES.values()))
    region_code = [k for k, v in REGION_CODES.items() if v == region_name][0]

with col2:
    keyword = st.text_input("학교명 검색")

# 학교 검색
if keyword and len(keyword) >= 1:
    with st.spinner("🔍 학교를 검색 중입니다..."):
        schools = search_schools(region_code, keyword)

    if schools:
        school_names = [f"{s['name']} ({s['address']})" for s in schools]
        selected_school_idx = st.selectbox("학교 선택", range(len(schools)),
                                          format_func=lambda i: school_names[i])

        selected_school = schools[selected_school_idx]
        school_code = selected_school['code']
        school_name = selected_school['name']

        # 탭 생성
        tab1, tab2 = st.tabs(["📅 급식표", "🥗 건강 분석"])

        with tab1:
            st.subheader(f"{school_name} - 주간 급식표")

            with st.spinner("⏳ 급식 정보를 불러오는 중..."):
                meals = get_meal_data(region_code, school_code)

            if meals:
                # 요일별로 그룹화
                weekday_map = {0: '월', 1: '화', 2: '수', 3: '목', 4: '금'}
                meals_by_weekday = {}

                for meal in meals:
                    try:
                        meal_date = dt.datetime.strptime(meal['date'], '%Y-%m-%d')
                        weekday_num = meal_date.weekday()
                        if weekday_num < 5:
                            weekday = weekday_map[weekday_num]
                            if weekday not in meals_by_weekday:
                                meals_by_weekday[weekday] = []
                            meals_by_weekday[weekday].append(meal)
                    except:
                        continue

                # 달력 형태로 표시
                cols = st.columns(5)
                weekdays = ['월', '화', '수', '목', '금']
                emojis = {'월': '🌙', '화': '🔥', '수': '💧', '목': '🌳', '금': '⭐'}

                for idx, (col, day) in enumerate(zip(cols, weekdays)):
                    with col:
                        st.markdown(f"### {emojis[day]} {day}요일")

                        if day in meals_by_weekday:
                            for meal in meals_by_weekday[day]:
                                with st.expander(f"🍽️ {meal['type']} ({meal['date']})"):
                                    st.write(f"**칼로리**: {meal['calorie']}")
                                    st.write("**메뉴**:")
                                    for food in meal['foods']:
                                        st.write(f"- {food}")
                        else:
                            st.info("급식 정보 없음")
            else:
                st.info("🤔 급식 정보를 찾을 수 없습니다. (주말/방학일 가능)")

        with tab2:
            st.subheader(f"🥗 {school_name} - 건강한 음식 분석")

            if meals:
                healthy_foods = []

                for meal in meals:
                    for food in meal['foods']:
                        if is_healthy(food):
                            healthy_foods.append({
                                'food': food,
                                'date': meal['date'],
                                'type': meal['type']
                            })

                if healthy_foods:
                    st.success(f"✅ 발견된 건강한 음식: **{len(healthy_foods)}개**")

                    for item in healthy_foods:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"🥗 **{item['food']**")
                        with col2:
                            st.write(f"📅 {item['date']}")
                        with col3:
                            st.write(f"🕐 {item['type']}")
                else:
                    st.info("이 급식 중에 건강한 음식이 없습니다.")
            else:
                st.info("급식 정보를 불러올 수 없습니다.")
    else:
        st.warning("❌ 검색된 학교가 없습니다. 다른 검색어를 시도해보세요.")

else:
    st.info("👈 왼쪽 사이드바에서 지역을 선택하고 학교명을 입력하세요.")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">

**🥗 급식영양 코치** | NEIS Open API 기반
📧 문제가 있으면 GitHub Issues를 등록해주세요.

</div>
""", unsafe_allow_html=True)
