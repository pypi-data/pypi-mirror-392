"""
V-World API 비동기 버전 테스트
"""

import asyncio
import os

from dotenv import load_dotenv

from pycobaltix.public.vworld.endpoints import AsyncVWorldAPI
from pycobaltix.schemas.responses import PaginatedAPIResponse


async def test_async_get_indvd_land_price_attr():
    """비동기 개별공시지가 조회 테스트"""
    load_dotenv()
    api_key = os.getenv("VWORLD_API_KEY")
    domain = os.getenv("VWORLD_DOMAIN")

    if not api_key or not domain:
        print("❌ 환경변수를 설정해주세요:")
        print("export VWORLD_API_KEY='your_key'")
        print("export VWORLD_DOMAIN='your_domain'")
        return

    # 비동기 API 클라이언트 생성
    api = AsyncVWorldAPI(api_key=api_key, domain=domain)

    print("\n🚀 비동기 V-World API 테스트 시작\n")

    # 테스트용 PNU (서울특별시 종로구 청운동)
    test_pnu = "1111010100100260000"

    # 1. 개별공시지가 조회 (전체 연도)
    print("💰 개별공시지가 조회 (전체 연도)")
    price_result = await api.getIndvdLandPriceAttr(pnu=test_pnu)

    print(f"✅ 결과: {price_result.success}")
    print(f"📊 총 {price_result.pagination.totalCount}개 연도 데이터")

    if price_result.data:
        first_price = price_result.data[0]
        print(f"\n📍 위치: {first_price.ldCodeNm}")
        print(f"📏 면적: {first_price.lndpclAr}㎡")
        print(f"🏷️  지목: {first_price.lndcgrCodeNm}")

        # 최근 5개 연도 공시지가 표시
        print("\n📈 최근 공시지가 추이:")
        for price_data in price_result.data[:5]:
            print(f"  - {price_data.stdrYear}년: {price_data.pblntfPclnd:>12}원/㎡")

    # 2. 특정 연도 조회
    print("\n\n💰 개별공시지가 조회 (2024년)")
    price_2024 = await api.getIndvdLandPriceAttr(pnu=test_pnu, stdrYear="2024")

    if price_2024.data:
        for price in price_2024.data:
            if price.stdrYear == "2024":
                print(f"✅ 2024년 공시지가: {price.pblntfPclnd}원/㎡")
                break

    # 3. 토지 정보 조회
    print("\n\n🏞️  토지 정보 조회")
    land_result = await api.ladfrlList(pnu=test_pnu)

    if land_result.data:
        land = land_result.data[0]
        print(f"✅ 토지명: {land.ldCodeNm}")
        print(f"📏 토지면적: {land.lndpclAr}㎡")
        print(f"🏷️  지목: {land.lndcgrCodeNm}")

    # 4. 건물 정보 조회
    print("\n\n🏢 건물 정보 조회")
    building_result = await api.buldSnList(pnu=test_pnu)

    if building_result.data:
        print(f"✅ 총 {len(building_result.data)}개 건물")
        for idx, building in enumerate(building_result.data[:3], 1):
            print(f"  {idx}. {building.buldNm or '(건물명 없음)'}")

    print("\n\n✅ 모든 비동기 테스트 완료!")


async def test_async_concurrent_requests():
    """여러 PNU를 동시에 조회하는 비동기 테스트"""
    api_key = os.getenv("VWORLD_API_KEY")
    domain = os.getenv("VWORLD_DOMAIN")

    if not api_key or not domain:
        print("❌ 환경변수를 설정해주세요:")
        return

    api = AsyncVWorldAPI(api_key=api_key, domain=domain)

    print("\n🚀 동시 다발 조회 테스트 시작\n")

    # 여러 PNU를 동시에 조회
    test_pnus = [
        "1111010100100260000",  # 서울특별시 종로구
        "1168010100100260000",  # 서울특별시 강남구
        "2611010100100010000",  # 부산광역시
    ]

    # 동시에 여러 요청 실행
    tasks = [api.getIndvdLandPriceAttr(pnu=pnu) for pnu in test_pnus]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 결과 출력
    for pnu, result in zip(test_pnus, results):
        # Exception 발생한 경우
        if isinstance(result, Exception):
            print(f"❌ {pnu}: 오류 발생 - {result}")
            continue

        # PaginatedAPIResponse 타입인 경우만 처리
        if not isinstance(result, PaginatedAPIResponse):
            continue

        if result.data:
            latest = result.data[0]
            print(
                f"✅ {pnu}: {latest.ldCodeNm} - {latest.stdrYear}년 {latest.pblntfPclnd}원/㎡"
            )
        else:
            print(f"⚠️  {pnu}: 데이터 없음")

    print("\n✅ 동시 다발 조회 테스트 완료!")


if __name__ == "__main__":
    print("=" * 60)
    print("V-World API 비동기 테스트".center(60))
    print("=" * 60)

    # 테스트 1: 기본 비동기 테스트
    asyncio.run(test_async_get_indvd_land_price_attr())

    print("\n" + "=" * 60 + "\n")

    # 테스트 2: 동시 다발 조회 테스트
    asyncio.run(test_async_concurrent_requests())

    print("\n" + "=" * 60)
