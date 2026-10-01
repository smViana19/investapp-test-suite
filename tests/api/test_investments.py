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


# ---------------------------------------------------------------------------
# Fixtures auxiliares
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def ativo_valido(base_url, auth_headers):
    """Busca a lista de ativos e devolve o primeiro disponível."""
    response = requests.get(f"{base_url}/api/assets", headers=auth_headers)
    assert response.status_code == 200, f"Falha ao listar ativos: {response.text}"

    ativos = response.json()
    assert len(ativos) > 0, "Nenhum ativo cadastrado na API"

    ativo = ativos[0]
    print(f"\n[INVEST] Ativo escolhido: {ativo['asset_name']} "
          f"({ativo['asset_type']}) - taxa {ativo['annual_rate']}")
    return ativo


def montar_payload(asset_name, amount=1000.00, price=1.00, days=30, planned=365):
    return {
        "asset_name": asset_name,
        "amount": amount,
        "purchase_price": price,
        "days_invested": days,
        "planned_days": planned,
    }


def pesquisar_investimento(base_url, auth_headers, investment_id):
    """Procura um investimento pelo id na listagem da carteira."""
    response = requests.get(f"{base_url}/api/investments", headers=auth_headers)
    assert response.status_code == 200, f"Falha ao listar investimentos: {response.text}"

    for inv in response.json():
        if inv["id"] == investment_id:
            return inv
    return None


def remover_investimento(base_url, auth_headers, investment_id):
    requests.delete(f"{base_url}/api/investments/{investment_id}", headers=auth_headers)


@pytest.fixture
def investimento_criado(base_url, auth_headers, ativo_valido):
    """Cria um investimento válido e o remove ao final do teste."""
    payload = montar_payload(ativo_valido["asset_name"])
    response = requests.post(f"{base_url}/api/investments", json=payload, headers=auth_headers)
    assert response.status_code == 201, f"Falha ao criar investimento: {response.text}"

    dados = response.json()
    print(f"[INVEST] Investimento criado com id {dados['id']}")

    yield payload, dados

    remover_investimento(base_url, auth_headers, dados["id"])
    print(f"[INVEST] Investimento {dados['id']} removido (limpeza)")


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

def test_criar_investimento_valido_retorna_201(investimento_criado):
    """A API deve aceitar um investimento válido e devolver os mesmos dados enviados."""
    payload, dados = investimento_criado

    assert isinstance(dados["id"], int)
    assert dados["asset_name"] == payload["asset_name"]
    assert dados["amount"] == payload["amount"]
    assert dados["purchase_price"] == payload["purchase_price"]
    assert dados["days_invested"] == payload["days_invested"]
    assert dados["planned_days"] == payload["planned_days"]


def test_criar_investimento_herda_dados_do_ativo(investimento_criado, ativo_valido):
    """O tipo e a taxa do investimento devem vir do ativo escolhido."""
    _, dados = investimento_criado

    assert dados["asset_type"] == ativo_valido["asset_type"]
    assert dados["annual_rate"] == ativo_valido["annual_rate"]


def test_criar_investimento_retorna_valores_calculados(investimento_criado):
    """A resposta deve trazer os campos de projeção calculados pelo backend."""
    _, dados = investimento_criado

    for campo in ("current_value", "future_value", "projected_profit"):
        assert campo in dados, f"Campo '{campo}' ausente na resposta"
        assert dados[campo] not in (None, ""), f"Campo '{campo}' veio vazio"


def test_pesquisar_investimento_criado_na_carteira(base_url, auth_headers, investimento_criado):
    """Depois de criado, o investimento deve aparecer em GET /api/investments."""
    payload, dados = investimento_criado

    encontrado = pesquisar_investimento(base_url, auth_headers, dados["id"])

    assert encontrado is not None, f"Investimento {dados['id']} não encontrado na carteira"
    assert encontrado["asset_name"] == payload["asset_name"]
    assert encontrado["amount"] == payload["amount"]


@pytest.mark.parametrize(
    "amount, price, days, planned",
    [
        (500.00, 1.00, 10, 90),
        (2500.50, 1.00, 60, 365),
        (10000.00, 1.00, 365, 730),
    ],
)
def test_criar_varios_investimentos_validos(
    base_url, auth_headers, ativo_valido, amount, price, days, planned
):
    """Cria investimentos com valores e prazos diferentes, todos válidos."""
    payload = montar_payload(ativo_valido["asset_name"], amount, price, days, planned)
    response = requests.post(f"{base_url}/api/investments", json=payload, headers=auth_headers)

    assert response.status_code == 201, response.text
    dados = response.json()
    try:
        assert dados["amount"] == amount
        assert dados["planned_days"] == planned
        assert pesquisar_investimento(base_url, auth_headers, dados["id"]) is not None
    finally:
        remover_investimento(base_url, auth_headers, dados["id"])