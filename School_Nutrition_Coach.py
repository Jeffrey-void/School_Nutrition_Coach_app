from flask import Flask, render_template, request, jsonify
from ai_helper import get_regions, search_schools, get_meal_data
from nutrition_data import HEALTHY_FOODS
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    """메인 페이지"""
    regions = get_regions()
    return render_template('index.html', regions=regions)

@app.route('/api/regions')
def get_regions_api():
    """지역 목록 조회 API"""
    regions = get_regions()
    return jsonify(regions)

@app.route('/api/schools/<atpt_code>')
def search_schools_api(atpt_code):
    """학교 검색 API"""
    keyword = request.args.get('keyword', '')
    schools = search_schools(atpt_code, keyword)
    return jsonify(schools)

@app.route('/api/meals')
def get_meals():
    """급식 정보 조회 API"""
    atpt_code = request.args.get('atpt_code')
    school_code = request.args.get('school_code')

    if not atpt_code or not school_code:
        return jsonify([])

    # NEIS API에서 급식 정보 조회
    school_meals = get_meal_data(atpt_code, school_code)

    # 요일별로 정렬 (월-금만)
    weekday_map = {0: '월', 1: '화', 2: '수', 3: '목', 4: '금'}

    meals_with_weekday = []
    for meal in school_meals:
        try:
            meal_date = datetime.strptime(meal['date'], '%Y-%m-%d')
            weekday_num = meal_date.weekday()
            if weekday_num < 5:  # 월-금만
                meal['weekday'] = weekday_map[weekday_num]
                meals_with_weekday.append(meal)
        except Exception as e:
            print(f"날짜 파싱 오류: {e}")
            continue

    return jsonify(meals_with_weekday)

@app.route('/api/analyze', methods=['POST'])
def analyze_meals():
    """건강한 음식 분석 API"""
    data = request.json
    atpt_code = data.get('atpt_code')
    school_code = data.get('school_code')
    school_name = data.get('school_name', '')

    if not atpt_code or not school_code:
        return jsonify({
            'school_name': school_name,
            'healthy_foods': [],
            'total_count': 0
        })

    # NEIS API에서 급식 정보 조회
    school_meals = get_meal_data(atpt_code, school_code)
    healthy_items = []

    for meal in school_meals:
        for food in meal.get('foods', []):
            if any(food.lower() in healthy.lower() or healthy.lower() in food.lower()
                   for healthy in HEALTHY_FOODS):
                healthy_items.append({
                    'food': food,
                    'meal_type': meal.get('type'),
                    'date': meal.get('date')
                })

    return jsonify({
        'school_name': school_name,
        'healthy_foods': healthy_items,
        'total_count': len(healthy_items)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
