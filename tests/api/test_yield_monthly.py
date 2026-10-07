import requests


def test_simulacao_rendimento_mensal(base_url, auth_headers):
    """Testa a simulação de rendimento mensal."""

    payload = {
        "amount": 1000.00,
        "monthly_rate": 1.0,
        "months": 12
    }

    response = requests.post(
        f"{base_url}/api/simulate/yield-monthly",
        json=payload,
        headers=auth_headers
    )

    print("\n[TEST_SIMULATION] Status:", response.status_code)
    print("[TEST_SIMULATION] Resposta:", response.text)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    assert "monthly_breakdown" in data
    assert "type_summary" in data
    assert "total_portfolio_invested" in data
    assert "total_portfolio_future" in data
    assert "total_portfolio_profit" in data
    assert "total_portfolio_growth_pct" in data

    assert isinstance(data["monthly_breakdown"], list)
    assert len(data["monthly_breakdown"]) > 0

    mes = data["monthly_breakdown"][0]

    assert "month" in mes
    assert "assets" in mes
    assert "total_month_value" in mes

    assert isinstance(mes["assets"], list)
    assert len(mes["assets"]) > 0

    for asset in mes["assets"]:
        assert "asset_name" in asset
        assert "asset_type" in asset
        assert "projected_value" in asset
        assert "monthly_growth_pct" in asset

        assert asset["projected_value"] >= 0
        assert asset["monthly_growth_pct"] >= 0

    assert isinstance(data["type_summary"], list)
    assert len(data["type_summary"]) > 0

    for item in data["type_summary"]:
        assert "asset_type" in item
        assert "total_invested" in item
        assert "total_final_value" in item
        assert "total_profit" in item
        assert "growth_pct" in item
        assert "share_pct" in item

    total_investido = data["total_portfolio_invested"]
    total_futuro = data["total_portfolio_future"]
    total_lucro = data["total_portfolio_profit"]

    assert total_investido >= 0
    assert total_futuro >= 0
    assert total_lucro >= 0

    assert round(total_investido + total_lucro, 2) == round(
        total_futuro, 2
    )

    print("\nTESTE DO ALUNO 5 APROVADO!")
    print("Total investido:", total_investido)
    print("Valor futuro:", total_futuro)
    print("Lucro:", total_lucro)
    print(
        "Crescimento:",
        data["total_portfolio_growth_pct"],
        "%"
    )