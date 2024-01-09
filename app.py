from src.domain.entities.fii import FII
from typing import List


def possui_patrimonio_e_dividend_yield(fii: FII) -> bool:
    return fii.dividend_yield is not None and fii.patrimonio_liquido is not None

def main():
    from src.application.services.fii_service import FIIService
    fii_service = FIIService()
    df = fii_service.start()

if __name__ == '__main__':
    main()