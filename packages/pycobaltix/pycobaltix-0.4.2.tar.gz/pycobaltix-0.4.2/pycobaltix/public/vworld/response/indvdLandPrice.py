from dataclasses import dataclass


@dataclass
class PublicPrice:
    """개별공시지가 데이터 클래스"""

    # 기준 연도
    stdrYear: str  # 기준연도

    # 공시지가 정보
    pblntfPclnd: str  # 공시지가 (원/㎡)

    # 토지 정보
    pnu: str  # 필지고유번호
    ldCodeNm: str  # 토지코드명 (주소)
    ldCode: str  # 토지코드
    mnnmSlno: str  # 본번슬번호

    # 토지 특성
    lndcgrCode: str  # 토지분류코드
    lndcgrCodeNm: str  # 토지분류코드명
    lndpclAr: str  # 토지면적 (㎡)

    # 공시지가 상세
    pblntfPc: str  # 공시가격 (원)

    # 지목 정보
    ladRegstrSeCode: str  # 토지등록구분코드
    ladRegstrSeCodeNm: str  # 토지등록구분코드명

    # 업데이트 정보
    lastUpdtDt: str  # 최종수정일 (YYYY-MM-DD)

    @classmethod
    def from_dict(cls, data: dict) -> "PublicPrice":
        """딕셔너리에서 PublicPrice 인스턴스 생성"""
        return cls(
            stdrYear=data.get("stdrYear", ""),
            pblntfPclnd=data.get("pblntfPclnd", ""),
            pnu=data.get("pnu", ""),
            ldCodeNm=data.get("ldCodeNm", ""),
            ldCode=data.get("ldCode", ""),
            mnnmSlno=data.get("mnnmSlno", ""),
            lndcgrCode=data.get("lndcgrCode", ""),
            lndcgrCodeNm=data.get("lndcgrCodeNm", ""),
            lndpclAr=data.get("lndpclAr", ""),
            pblntfPc=data.get("pblntfPc", ""),
            ladRegstrSeCode=data.get("ladRegstrSeCode", ""),
            ladRegstrSeCodeNm=data.get("ladRegstrSeCodeNm", ""),
            lastUpdtDt=data.get("lastUpdtDt", ""),
        )

    def to_dict(self) -> dict:
        """인스턴스를 딕셔너리로 변환"""
        return {
            "stdrYear": self.stdrYear,
            "pblntfPclnd": self.pblntfPclnd,
            "pnu": self.pnu,
            "ldCodeNm": self.ldCodeNm,
            "ldCode": self.ldCode,
            "mnnmSlno": self.mnnmSlno,
            "lndcgrCode": self.lndcgrCode,
            "lndcgrCodeNm": self.lndcgrCodeNm,
            "lndpclAr": self.lndpclAr,
            "pblntfPc": self.pblntfPc,
            "ladRegstrSeCode": self.ladRegstrSeCode,
            "ladRegstrSeCodeNm": self.ladRegstrSeCodeNm,
            "lastUpdtDt": self.lastUpdtDt,
        }

    @property
    def year(self) -> int:
        """기준연도를 정수로 반환"""
        try:
            return int(self.stdrYear) if self.stdrYear else 0
        except (ValueError, TypeError):
            return 0

    @property
    def price(self) -> int:
        """공시지가를 정수로 반환 (원/㎡)"""
        try:
            return int(self.pblntfPclnd) if self.pblntfPclnd else 0
        except (ValueError, TypeError):
            return 0
