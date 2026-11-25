# NEIS Open API로 학교 급식 조회하기 (Streamlit 프로젝트용)

> 출처: [나이스 교육정보 개방 포털](https://open.neis.go.kr)
> 2026-11-25에 대치중학교로 실제 호출해서 동작을 확인했습니다.

## 전체 흐름

1. **학교기본정보 API**로 학교를 검색해서 `교육청코드`와 `학교코드`를 얻습니다.
2. 이 두 코드로 **급식식단정보 API**를 호출합니다.

```
[지역 선택 + 학교 이름 입력] → schoolInfo → (ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE) → mealServiceDietInfo → [메뉴 표시]
```

---

## 0. 인증키 발급

- 포털에 회원가입한 뒤 상단 **"인증키 신청"** 메뉴에서 발급받습니다.
- **KEY 없이도 호출은 되지만 결과가 최대 5건만 옵니다.** (테스트용 샘플 모드)
  - 실제로 제주 학교를 조회했을 때 전체 205개 중 5개만 왔습니다.
  - 학교 목록을 제대로 보여주려면 인증키가 꼭 필요합니다.

---

## 1단계: 학교 검색 (학교기본정보)

```
GET https://open.neis.go.kr/hub/schoolInfo
```

### 요청 파라미터

| 파라미터 | 설명 | 예시 |
|---|---|---|
| `KEY` | 인증키 | |
| `Type` | 응답 형식. `json`으로 지정 (기본값은 xml) | `json` |
| `pIndex` | 페이지 번호 | `1` |
| `pSize` | 페이지당 개수 | `100` |
| `ATPT_OFCDC_SC_CODE` | 시도교육청코드 (지역 필터) | `B10` |
| `LCTN_SC_NM` | 시도명 (지역 필터의 다른 방법) | `서울특별시` |
| `SCHUL_NM` | 학교명 (일부만 입력해도 검색됨) | `대치중` |
| `SCHUL_KND_SC_NM` | 학교종류 | `초등학교`, `중학교`, `고등학교` |

### 예시 URL

```
https://open.neis.go.kr/hub/schoolInfo?KEY=인증키&Type=json&pIndex=1&pSize=100&ATPT_OFCDC_SC_CODE=B10&SCHUL_NM=대치중학교
```

### 응답에서 꼭 필요한 값

| 필드 | 의미 | 예시 |
|---|---|---|
| `ATPT_OFCDC_SC_CODE` | 시도교육청코드 | `B10` |
| `SD_SCHUL_CODE` | 학교코드 | `7091427` |
| `SCHUL_NM` | 학교명 | `대치중학교` |
| `ORG_RDNMA` | 도로명주소 (이름이 같은 학교를 구분할 때 유용) | `서울특별시 강남구 ...` |

### 시도교육청코드 표

| 지역 | 코드 | 지역 | 코드 | 지역 | 코드 |
|---|---|---|---|---|---|
| 서울 | B10 | 대전 | G10 | 충남 | N10 |
| 부산 | C10 | 울산 | H10 | 전북 | P10 |
| 대구 | D10 | 세종 | I10 | 전남 | Q10 |
| 인천 | E10 | 경기 | J10 | 경북 | R10 |
| 광주 | F10 | 강원 | K10 | 경남 | S10 |
| | | 충북 | M10 | 제주 | T10 |

---

## 2단계: 급식 조회 (급식식단정보)

```
GET https://open.neis.go.kr/hub/mealServiceDietInfo
```

### 요청 파라미터

| 파라미터 | 설명 | 예시 |
|---|---|---|
| `KEY`, `Type`, `pIndex`, `pSize` | 1단계와 동일 | |
| `ATPT_OFCDC_SC_CODE` | 시도교육청코드 (**필수**) | `B10` |
| `SD_SCHUL_CODE` | 학교코드 (**필수**) | `7091427` |
| `MLSV_YMD` | 급식일자, 하루 조회 (YYYYMMDD) | `20261125` |
| `MLSV_FROM_YMD` | 기간 조회 시작일 | `20261101` |
| `MLSV_TO_YMD` | 기간 조회 종료일 | `20261130` |
| `MMEAL_SC_CODE` | 식사코드: 1=조식, 2=중식, 3=석식 (생략하면 전부) | `2` |

### 예시 URL

```
https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=인증키&Type=json&ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7091427&MLSV_YMD=20261125
```

### 주요 응답 필드

| 필드 | 의미 | 예시 |
|---|---|---|
| `MLSV_YMD` | 급식일자 | `20261102` |
| `MMEAL_SC_NM` | 식사명 | `중식` |
| `DDISH_NM` | 메뉴 | `차수수밥 <br/>쇠고기미역국 (5.16)<br/>...` |
| `CAL_INFO` | 칼로리 | `747.7 Kcal` |
| `NTR_INFO` | 영양정보 | `탄수화물(g) : 97.6<br/>...` |
| `ORPLC_INFO` | 원산지 정보 | `쇠고기(종류) : 국내산(한우)<br/>...` |

---

## 응답 JSON 구조

### 정상 응답

```json
{
  "mealServiceDietInfo": [
    { "head": [ {"list_total_count": 16}, {"RESULT": {"CODE": "INFO-000", "MESSAGE": "정상 처리되었습니다."}} ] },
    { "row": [ { "MMEAL_SC_NM": "중식", "DDISH_NM": "...", "CAL_INFO": "747.7 Kcal" } ] }
  ]
}
```

- 실제 데이터 위치: `data["서비스이름"][1]["row"]`
- `[0]`은 head(전체 개수, 결과 코드)입니다.

### 데이터가 없을 때 (주말, 방학, 잘못된 날짜 등)

```json
{"RESULT": {"CODE": "INFO-200", "MESSAGE": "해당하는 데이터가 없습니다."}}
```

- 이때는 `"mealServiceDietInfo"` 키가 **아예 없습니다.** 확인하지 않고 바로 꺼내면 `KeyError`가 발생합니다.

---

## 자주 막히는 부분 체크리스트

- [ ] `Type=json`을 빠뜨리면 XML로 응답이 옵니다.
- [ ] KEY 없이 테스트하면 결과가 5건까지만 옵니다.
- [ ] 데이터가 없을 때 응답 구조가 달라지므로 예외 처리가 필요합니다.
- [ ] 메뉴(`DDISH_NM`)는 `<br/>`로 나누고, `(5.6.9)` 같은 알레르기 번호는 정규식으로 제거합니다.
- [ ] 날짜 형식은 `YYYYMMDD`입니다. 하이픈 없이 `20261125`처럼 씁니다.
- [ ] 인증키는 코드에 직접 쓰지 말고 `st.secrets`를 사용합니다. GitHub에 올라가면 키가 노출됩니다.
- [ ] 같은 요청을 반복하지 않도록 `@st.cache_data`를 사용합니다.

---

## 인증키 설정 (`st.secrets`)

프로젝트 폴더에 `.streamlit/secrets.toml` 파일을 만듭니다.

```toml
NEIS_KEY = "발급받은_인증키"
```

`.gitignore`에 아래 줄을 추가해서 키 파일이 GitHub에 올라가지 않게 합니다.

```
.streamlit/secrets.toml
```

> Streamlit Community Cloud에 배포할 때는 앱 설정의 **Secrets** 메뉴에 같은 내용을 붙여넣습니다.

---

## Streamlit 예제 코드 (`app.py`)

```python
import re
import datetime as dt
import requests
import streamlit as st

KEY = st.secrets.get("NEIS_KEY", "")
BASE = "https://open.neis.go.kr/hub"

REGIONS = {"서울":"B10","부산":"C10","대구":"D10","인천":"E10","광주":"F10","대전":"G10",
           "울산":"H10","세종":"I10","경기":"J10","강원":"K10","충북":"M10","충남":"N10",
           "전북":"P10","전남":"Q10","경북":"R10","경남":"S10","제주":"T10"}

def neis(service, **params):
    """NEIS API 공통 호출 함수. 데이터가 없으면 빈 리스트를 반환합니다."""
    params.update({"KEY": KEY, "Type": "json", "pIndex": 1, "pSize": 100})
    data = requests.get(f"{BASE}/{service}", params=params, timeout=10).json()
    if service not in data:          # INFO-200: 데이터 없음 등
        return []
    return data[service][1]["row"]

@st.cache_data
def search_school(region_code, name):
    return neis("schoolInfo", ATPT_OFCDC_SC_CODE=region_code, SCHUL_NM=name)

@st.cache_data
def get_meal(office, school, ymd):
    return neis("mealServiceDietInfo", ATPT_OFCDC_SC_CODE=office,
                SD_SCHUL_CODE=school, MLSV_YMD=ymd)

st.title("🍱 우리 학교 급식")
region = st.selectbox("지역", list(REGIONS))
name = st.text_input("학교 이름", "대치중")

if name:
    schools = search_school(REGIONS[region], name)
    if not schools:
        st.warning("학교를 찾을 수 없어요.")
    else:
        school = st.selectbox("학교 선택", schools,
                              format_func=lambda s: f"{s['SCHUL_NM']} ({s['ORG_RDNMA']})")
        date = st.date_input("날짜", dt.date.today())
        meals = get_meal(school["ATPT_OFCDC_SC_CODE"], school["SD_SCHUL_CODE"],
                         date.strftime("%Y%m%d"))
        if not meals:
            st.info("급식 정보가 없어요. (주말/방학일 수 있어요)")
        for m in meals:
            st.subheader(f"{m['MMEAL_SC_NM']} · {m['CAL_INFO']}")
            for dish in m["DDISH_NM"].split("<br/>"):
                st.write("- " + re.sub(r"\s*\([\d.]+\)", "", dish).strip())
```

### 실행 방법

```bash
pip install streamlit requests
streamlit run app.py
```

---

## 확장 아이디어

같은 방식(교육청코드 + 학교코드)으로 다른 API도 붙일 수 있습니다.

| 기능 | 서비스명 |
|---|---|
| 초등학교 시간표 | `elsTimetable` |
| 중학교 시간표 | `misTimetable` |
| 고등학교 시간표 | `hisTimetable` |
| 학사일정 | `SchoolSchedule` |

- 일주일 급식표: `MLSV_FROM_YMD`와 `MLSV_TO_YMD`로 기간을 조회하고 `st.columns`로 요일별로 표시해 보세요.
- 알레르기 필터: 메뉴 옆 번호(1=난류, 2=우유, 5=대두, 6=밀 ...)를 이용해 내 알레르기 메뉴를 강조해 보세요.
- 칼로리 차트: 기간 조회 결과의 `CAL_INFO`로 `st.line_chart`를 그려 보세요.

각 API의 정확한 명세는 포털 데이터셋 페이지의 **"Open API"** 탭에서 확인할 수 있습니다.
