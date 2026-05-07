from __future__ import annotations

from stock_screener.models.company import Company
from stock_screener.models.financials import FinancialSeries, FinancialSnapshot


def load_sample_universe() -> list[tuple[Company, FinancialSeries]]:
    companies = [
        Company(code="8058", name="三菱商事", market="Prime", sector="卸売業", edinet_code="E02529", price=3150),
        Company(code="9432", name="日本電信電話", market="Prime", sector="情報・通信業", edinet_code="E04430", price=170),
        Company(code="7203", name="トヨタ自動車", market="Prime", sector="輸送用機器", edinet_code="E02144", price=3300),
        Company(code="6758", name="ソニーグループ", market="Prime", sector="電気機器", edinet_code="E01777", price=14000),
        Company(code="7974", name="任天堂", market="Prime", sector="その他製品", edinet_code="E02367", price=8200),
    ]

    data = {
        "8058": [
            FinancialSnapshot(fiscal_year=2021, revenue=12884500, operating_income=0, net_income=535300, roe=0.105, equity_ratio=0.34, operating_cf=700000, free_cf=420000, dividend_per_share=134, dividend_yield=0.042, payout_ratio=0.34, per=11, pbr=1.2),
            FinancialSnapshot(fiscal_year=2022, revenue=17264800, operating_income=0, net_income=937500, roe=0.168, equity_ratio=0.36, operating_cf=890000, free_cf=530000, dividend_per_share=150, dividend_yield=0.047, payout_ratio=0.28, per=8, pbr=1.1),
            FinancialSnapshot(fiscal_year=2023, revenue=21571900, operating_income=0, net_income=1180690, roe=0.182, equity_ratio=0.38, operating_cf=1050000, free_cf=650000, dividend_per_share=180, dividend_yield=0.057, payout_ratio=0.31, per=9, pbr=1.4),
        ],
        "9432": [
            FinancialSnapshot(fiscal_year=2021, revenue=11944000, operating_income=1671000, net_income=916200, roe=0.135, equity_ratio=0.34, operating_cf=2950000, free_cf=1050000, dividend_per_share=4.8, dividend_yield=0.028, payout_ratio=0.38, per=12, pbr=1.5),
            FinancialSnapshot(fiscal_year=2022, revenue=12156400, operating_income=1768500, net_income=1181000, roe=0.148, equity_ratio=0.35, operating_cf=3100000, free_cf=1160000, dividend_per_share=5.2, dividend_yield=0.031, payout_ratio=0.36, per=11, pbr=1.4),
            FinancialSnapshot(fiscal_year=2023, revenue=13136000, operating_income=1829000, net_income=1213100, roe=0.151, equity_ratio=0.36, operating_cf=3260000, free_cf=1210000, dividend_per_share=5.5, dividend_yield=0.032, payout_ratio=0.37, per=12, pbr=1.6),
        ],
        "7203": [
            FinancialSnapshot(fiscal_year=2021, revenue=27214500, operating_income=2197700, net_income=2245200, roe=0.102, equity_ratio=0.38, operating_cf=2727000, free_cf=800000, dividend_per_share=48, dividend_yield=0.015, payout_ratio=0.28, per=14, pbr=1.2),
            FinancialSnapshot(fiscal_year=2022, revenue=31379500, operating_income=2995700, net_income=2452800, roe=0.109, equity_ratio=0.39, operating_cf=3722000, free_cf=980000, dividend_per_share=52, dividend_yield=0.016, payout_ratio=0.30, per=13, pbr=1.1),
            FinancialSnapshot(fiscal_year=2023, revenue=37154200, operating_income=2725000, net_income=2451300, roe=0.105, equity_ratio=0.40, operating_cf=4100000, free_cf=1100000, dividend_per_share=60, dividend_yield=0.018, payout_ratio=0.32, per=12, pbr=1.3),
        ],
        "6758": [
            FinancialSnapshot(fiscal_year=2021, revenue=8999400, operating_income=955300, net_income=1029300, roe=0.247, equity_ratio=0.22, operating_cf=1150000, free_cf=620000, dividend_per_share=65, dividend_yield=0.005, payout_ratio=0.12, per=18, pbr=2.2),
            FinancialSnapshot(fiscal_year=2022, revenue=9921500, operating_income=1202300, net_income=882200, roe=0.145, equity_ratio=0.24, operating_cf=1260000, free_cf=690000, dividend_per_share=70, dividend_yield=0.005, payout_ratio=0.13, per=20, pbr=2.1),
            FinancialSnapshot(fiscal_year=2023, revenue=11539800, operating_income=1208200, net_income=937100, roe=0.139, equity_ratio=0.25, operating_cf=1330000, free_cf=710000, dividend_per_share=75, dividend_yield=0.005, payout_ratio=0.14, per=21, pbr=2.0),
        ],
        "7974": [
            FinancialSnapshot(fiscal_year=2021, revenue=1758900, operating_income=640600, net_income=480400, roe=0.242, equity_ratio=0.76, operating_cf=612000, free_cf=570000, dividend_per_share=203, dividend_yield=0.025, payout_ratio=0.50, per=22, pbr=3.4),
            FinancialSnapshot(fiscal_year=2022, revenue=1695300, operating_income=592700, net_income=477700, roe=0.214, equity_ratio=0.77, operating_cf=590000, free_cf=545000, dividend_per_share=203, dividend_yield=0.025, payout_ratio=0.52, per=21, pbr=3.1),
            FinancialSnapshot(fiscal_year=2023, revenue=1601600, operating_income=504300, net_income=432700, roe=0.181, equity_ratio=0.78, operating_cf=510000, free_cf=470000, dividend_per_share=186, dividend_yield=0.023, payout_ratio=0.50, per=24, pbr=3.2),
        ],
    }

    return [
        (company, FinancialSeries(company_code=company.code, snapshots=data[company.code]))
        for company in companies
    ]
