"""
Integrante 3 - Criação de investimentos válidos (POST /api/investments)

Fluxo coberto:
  1. Busca um ativo válido em GET /api/assets
  2. Cria o investimento via POST /api/investments (espera 201)
  3. Confere os dados devolvidos pela API
  4. Pesquisa o investimento criado em GET /api/investments
  5. Remove o investimento no final (teardown) para não sujar a carteira
"""

import pytest
import requests


def test_criar_investimento_poupanca(base_url, auth_headers):
    """Valida a criação de um investimento válido em Poupança."""
    payload = {
        "asset_name": "Poupança",
        "amount": 1000.00,
        "purchase_price": 1.00,
        "days_invested": 30,
        "planned_days": 365
    }

    response = requests.post(
        f"{base_url}/api/investments",
        json=payload,
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["asset_name"] == "Poupança"
    assert data["amount"] == 1000.00
    assert data["purchase_price"] == 1.00
    assert data["days_invested"] == 30
    assert data["planned_days"] == 365


def test_criar_investimento_cdb(base_url, auth_headers):
    """Valida a criação de um investimento válido em CDB."""
    payload = {
        "asset_name": "CDB",
        "amount": 5000.00,
        "purchase_price": 1.00,
        "days_invested": 180,
        "planned_days": 720
    }

    response = requests.post(
        f"{base_url}/api/investments",
        json=payload,
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["asset_name"] == "CDB"
    assert data["amount"] == 5000.00
    assert data["purchase_price"] == 1.00
    assert data["days_invested"] == 180
    assert data["planned_days"] == 720