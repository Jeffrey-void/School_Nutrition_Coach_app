import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import re
from functools import lru_cache

load_dotenv()

API_KEY = os.getenv('NEIS_DATA_OPEN_API_KEY')
BASE_URL = 'https://open.neis.go.kr/hub'

# 올바른 시도교육청 코드 (가이드 참고)
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

def neis_api(service, **params):
    """NEIS API 공통 호출 함수 (JSON 응답)"""
    params.update({
        'KEY': API_KEY,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 100
    })

    try:
        response = requests.get(f'{BASE_URL}/{service}', params=params, timeout=10)
        data = response.json()

        # 데이터가 없거나 오류일 때 (INFO-200 등)
        if service not in data:
            return []

        # 정상 응답: data[service][1]["row"]
        return data[service][1]['row']

    except Exception as e:
        print(f"NEIS API 오류 ({service}): {e}")
        return []

def get_regions():
    """지역 목록 조회"""
    regions = []
    for code, name in sorted(REGION_CODES.items(), key=lambda x: x[1]):
        regions.append({
            'code': code,
            'name': name
        })
    return regions

@lru_cache(maxsize=32)
def search_schools_cached(atpt_code, keyword=''):
    """학교 검색 (캐싱 적용)"""
    return _search_schools(atpt_code, keyword)

def _search_schools(atpt_code, keyword=''):
    """학교 검색 내부 함수"""
    params = {
        'ATPT_OFCDC_SC_CODE': atpt_code
    }

    if keyword:
        params['SCHUL_NM'] = keyword

    schools = neis_api('schoolInfo', **params)

    # 응답 형식: [{"SCHUL_NM": "...", "SD_SCHUL_CODE": "...", "ATPT_OFCDC_SC_CODE": "...", ...}, ...]
    result = []
    for school in schools:
        result.append({
            'code': school.get('SD_SCHUL_CODE', ''),
            'name': school.get('SCHUL_NM', ''),
            'atpt_code': school.get('ATPT_OFCDC_SC_CODE', ''),
            'address': school.get('ORG_RDNMA', '')
        })

    return result

def search_schools(atpt_code, keyword=''):
    """학교 검색 (공개 함수)"""
    # 튜플로 변환해서 캐싱 가능하게 함
    results = search_schools_cached(atpt_code, keyword)
    return results

def get_meal_data(atpt_code, school_code, year=None, month=None):
    """NEIS API에서 급식 정보 조회"""
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month

    # 한 달 전체 조회
    from_ymd = f'{year}{month:02d}01'

    # 월의 마지막 날짜 계산
    if month == 12:
        to_ymd = f'{year + 1}0131'
    else:
        from datetime import date
        last_day = (date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)) - \
                   __import__('datetime').timedelta(days=1)
        to_ymd = f'{year}{month + 1:02d}{last_day.day:02d}' if month < 12 else f'{year}{month + 1:02d}{last_day.day:02d}'

    # 간단하게: 항상 1-28 조회
    to_ymd = f'{year}{month:02d}28'

    params = {
        'ATPT_OFCDC_SC_CODE': atpt_code,
        'SD_SCHUL_CODE': school_code,
        'MLSV_FROM_YMD': from_ymd,
        'MLSV_TO_YMD': to_ymd
    }

    meals_data = neis_api('mealServiceDietInfo', **params)

    # 응답 처리
    meals = []
    for meal in meals_data:
        meal_date = meal.get('MLSV_YMD', '')
        meal_type = meal.get('MMEAL_SC_NM', '점심')
        menu_text = meal.get('DDISH_NM', '')

        # 메뉴 파싱
        foods = parse_menu_text(menu_text)

        if foods:
            meals.append({
                'type': meal_type,
                'date': format_date(meal_date),
                'foods': foods,
                'calorie': meal.get('CAL_INFO', ''),
                'nutrition': meal.get('NTR_INFO', '')
            })

    return meals

def parse_menu_text(menu_text):
    """메뉴 텍스트를 음식 목록으로 파싱"""
    if not menu_text:
        return []

    # HTML 태그 제거 (<br/>, <br>, 등)
    menu_text = re.sub(r'<[^>]+>', '\n', menu_text)

    # 별표(*) 제거
    menu_text = menu_text.replace('*', '')

    # (1.2.5.6) 같은 알레르기 정보 제거
    menu_text = re.sub(r'\s*\([0-9.,]*\)', '', menu_text)

    # 쉼표나 개행으로 구분된 음식들을 추출
    items = [item.strip() for item in menu_text.replace('\n', ',').split(',')]

    # 빈 문자열과 너무 짧은 항목 제거
    foods = [item for item in items if item and len(item) > 1]

    return foods

def format_date(date_str):
    """YYYYMMDD 형식을 YYYY-MM-DD로 변환"""
    if len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    return date_str
