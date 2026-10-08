import requests


def test_simulacao_resgate_otimizacao_fiscal(base_url, auth_headers):
    """Testa a simulação de resgate com otimização fiscal."""

    payload = {
        "target_amount": 10
    }

    response = requests.post(
        f"{base_url}/api/simulate/tax-withdrawal",
        json=payload,
        headers=auth_headers
    )

    print("\n[TEST_TAX_WITHDRAWAL] Status:", response.status_code)
    print("[TEST_TAX_WITHDRAWAL] Resposta:", response.text)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    for asset in data:
        assert "asset_name" in asset
        assert "asset_type" in asset
        assert "current_val" in asset
        assert "tax_due" in asset
        assert "effective_tax_rate" in asset
        assert "net_amount" in asset
        assert "is_exempt" in asset

        assert isinstance(asset["asset_name"], str)
        assert isinstance(asset["asset_type"], str)
        assert isinstance(asset["current_val"], (int, float))
        assert isinstance(asset["tax_due"], (int, float))
        assert isinstance(asset["effective_tax_rate"], (int, float))
        assert isinstance(asset["net_amount"], (int, float))
        assert isinstance(asset["is_exempt"], bool)

        assert asset["current_val"] >= 0
        assert asset["tax_due"] >= 0
        assert asset["effective_tax_rate"] >= 0
        assert asset["net_amount"] >= 0

    ativos_isentos = [
        asset for asset in data
        if asset["is_exempt"] is True
    ]

    assert len(ativos_isentos) > 0

    for asset in ativos_isentos:
        assert asset["tax_due"] == 0
        assert asset["effective_tax_rate"] == 0

    ativos_tributaveis = [
        asset for asset in data
        if asset["is_exempt"] is False
    ]

    assert len(ativos_tributaveis) > 0

    for asset in ativos_tributaveis:
        assert asset["tax_due"] >= 0
        assert asset["effective_tax_rate"] >= 0

    print("\nTESTE DO ALUNO 6 APROVADO!")
    print("Quantidade de ativos:", len(data))
    print("Ativos isentos:", len(ativos_isentos))
    print("Ativos tributáveis:", len(ativos_tributaveis))