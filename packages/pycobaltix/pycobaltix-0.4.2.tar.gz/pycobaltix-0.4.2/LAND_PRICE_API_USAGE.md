# 개별공시지가 조회 API 사용 가이드

## 개요

V-World API를 통해 개별공시지가(Individual Land Price) 정보를 조회할 수 있는 기능이 추가되었습니다.

## 설치

```bash
# uv를 사용하여 패키지 설치
uv add pycobaltix
```

## 환경 변수 설정

API를 사용하기 위해서는 V-World API 키와 도메인이 필요합니다.

```bash
export VWORLD_API_KEY='your_vworld_api_key'
export VWORLD_DOMAIN='your_domain'
```

## 기본 사용법

### 1. 동기 방식 (VWorldAPI)

```python
from pycobaltix.public.vworld.endpoints import VWorldAPI

# API 클라이언트 생성
api = VWorldAPI()

# PNU(필지고유번호)로 개별공시지가 조회
pnu = "1111010100100260000"  # 서울특별시 종로구 청운동
result = api.getIndvdLandPriceAttr(pnu=pnu)

# 결과 확인
if result.success and result.data:
    for price_info in result.data[:3]:  # 최근 3개 연도
        print(f"{price_info.stdrYear}년: {price_info.pblntfPclnd}원/㎡")
        print(f"위치: {price_info.ldCodeNm}")
        print(f"면적: {price_info.lndpclAr}㎡")
```

### 2. 특정 연도 조회

```python
# 2024년 공시지가만 조회
result = api.getIndvdLandPriceAttr(
    pnu="1111010100100260000",
    stdrYear="2024"
)

if result.data:
    price = result.data[0]
    print(f"2024년 공시지가: {price.pblntfPclnd}원/㎡")
```

### 3. 비동기 방식 (AsyncVWorldAPI)

```python
import asyncio
from pycobaltix.public.vworld.endpoints import AsyncVWorldAPI

async def get_land_price():
    # 비동기 API 클라이언트 생성
    api = AsyncVWorldAPI()

    # 개별공시지가 조회
    result = await api.getIndvdLandPriceAttr(pnu="1111010100100260000")

    if result.data:
        latest = result.data[0]
        print(f"최신 공시지가 ({latest.year}년): {latest.price:,}원/㎡")

    return result

# 실행
asyncio.run(get_land_price())
```

### 4. 여러 지역 동시 조회 (비동기)

```python
import asyncio
from pycobaltix.public.vworld.endpoints import AsyncVWorldAPI

async def get_multiple_land_prices():
    api = AsyncVWorldAPI()

    # 여러 PNU 리스트
    pnus = [
        "1111010100100260000",  # 서울 종로구
        "1168010100100260000",  # 서울 강남구
        "2611010100100010000",  # 부산
    ]

    # 동시에 조회
    tasks = [api.getIndvdLandPriceAttr(pnu=pnu) for pnu in pnus]
    results = await asyncio.gather(*tasks)

    # 결과 출력
    for pnu, result in zip(pnus, results):
        if result.data:
            latest = result.data[0]
            print(f"{latest.ldCodeNm}: {latest.pblntfPclnd}원/㎡")

asyncio.run(get_multiple_land_prices())
```

## 응답 데이터 구조

### PublicPrice 모델

```python
@dataclass
class PublicPrice:
    stdrYear: str           # 기준연도 (예: "2024")
    pblntfPclnd: str        # 공시지가 (원/㎡)
    pnu: str                # 필지고유번호
    ldCodeNm: str           # 토지코드명 (주소)
    ldCode: str             # 토지코드
    mnnmSlno: str           # 본번슬번호
    lndcgrCode: str         # 토지분류코드
    lndcgrCodeNm: str       # 토지분류코드명
    lndpclAr: str           # 토지면적 (㎡)
    pblntfPc: str           # 공시가격 (원)
    ladRegstrSeCode: str    # 토지등록구분코드
    ladRegstrSeCodeNm: str  # 토지등록구분코드명
    lastUpdtDt: str         # 최종수정일

    # 편의 속성
    @property
    def year(self) -> int:
        """기준연도를 정수로 반환"""

    @property
    def price(self) -> int:
        """공시지가를 정수로 반환 (원/㎡)"""
```

### PaginatedAPIResponse

```python
result = api.getIndvdLandPriceAttr(pnu="1111010100100260000")

# 성공 여부
print(result.success)  # True/False

# 상태 코드
print(result.status)   # 200

# 데이터 리스트 (최신 연도순으로 정렬됨)
for price_info in result.data:
    print(f"{price_info.year}년: {price_info.price:,}원/㎡")

# 페이지네이션 정보
print(f"총 {result.pagination.totalCount}개 연도 데이터")
print(f"현재 페이지: {result.pagination.currentPage}")
```

## 주요 파라미터

### getIndvdLandPriceAttr()

| 파라미터  | 타입        | 필수 | 기본값 | 설명                                        |
| --------- | ----------- | ---- | ------ | ------------------------------------------- |
| pnu       | str         | ✅   | -      | 필지고유번호 (19자리)                       |
| stdrYear  | str \| None | ❌   | None   | 기준연도 (YYYY 형식), None인 경우 전체 연도 |
| numOfRows | int         | ❌   | 1000   | 페이지당 결과 수                            |
| pageNo    | int         | ❌   | 1      | 페이지 번호                                 |

## 테스트

### 동기 테스트

```bash
# 환경변수 설정 후
uv run python tests/vworld/api_test.py
```

### 비동기 테스트

```bash
# 환경변수 설정 후
uv run python tests/vworld/async_test.py
```

### pytest 실행

```bash
# 통합 테스트 실행
uv run pytest tests/vworld/api_test.py -v -m integration

# 특정 테스트만 실행
uv run pytest tests/vworld/api_test.py::TestVWorldAPIIntegration::test_get_indvd_land_price_attr_success -v
```

## 에러 처리

API는 자동으로 재시도 로직을 포함하고 있습니다:

-   최대 5회 재시도
-   Exponential backoff 없이 1초 간격으로 재시도
-   타임아웃: 5초

```python
try:
    result = api.getIndvdLandPriceAttr(pnu="invalid_pnu")
    if not result.success:
        print("API 호출 실패")
    elif len(result.data) == 0:
        print("해당 PNU에 대한 데이터가 없습니다")
except Exception as e:
    print(f"오류 발생: {e}")
```

## 활용 예시

### 1. 공시지가 추이 분석

```python
result = api.getIndvdLandPriceAttr(pnu="1111010100100260000")

if result.data:
    print("📈 공시지가 추이 분석")
    print("-" * 50)

    prices = [(p.year, p.price) for p in result.data]
    prices.sort(key=lambda x: x[0])  # 연도순 정렬

    for i, (year, price) in enumerate(prices):
        if i > 0:
            prev_year, prev_price = prices[i-1]
            change = price - prev_price
            change_rate = (change / prev_price) * 100

            print(f"{year}년: {price:>12,}원/㎡ "
                  f"(전년대비 {change_rate:+.2f}%)")
        else:
            print(f"{year}년: {price:>12,}원/㎡")
```

### 2. 여러 지역 가격 비교

```python
import asyncio
from pycobaltix.public.vworld.endpoints import AsyncVWorldAPI

async def compare_regions():
    api = AsyncVWorldAPI()

    regions = {
        "서울 강남": "1168010100100260000",
        "서울 종로": "1111010100100260000",
        "부산": "2611010100100010000",
    }

    tasks = [
        api.getIndvdLandPriceAttr(pnu=pnu)
        for pnu in regions.values()
    ]
    results = await asyncio.gather(*tasks)

    print("📊 지역별 최신 공시지가 비교")
    print("-" * 60)

    for region_name, result in zip(regions.keys(), results):
        if result.data:
            latest = result.data[0]
            print(f"{region_name:15}: {latest.price:>12,}원/㎡ ({latest.year}년)")

asyncio.run(compare_regions())
```

## 참고사항

-   데이터는 최신 연도순으로 자동 정렬됩니다
-   PNU는 19자리 필지고유번호입니다
-   공시지가는 원/㎡ 단위입니다
-   API 키와 도메인은 V-World에서 발급받아야 합니다
-   재시도 로직이 내장되어 있어 일시적인 네트워크 오류를 자동으로 처리합니다

## 추가 리소스

-   [V-World API 공식 문서](https://www.vworld.kr/dev/v4dv_openapiguide2_s001.do)
-   [PNU(필지고유번호) 조회 방법](https://www.vworld.kr)
