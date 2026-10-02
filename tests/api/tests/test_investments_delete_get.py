"""
Integrante 4 - Listagem e exclusão de investimentos.

Endpoints cobertos:
  - GET    /api/investments
  - DELETE /api/investments/{id}

Estes testes devem ser colados em tests/api/test_investments.py
(junto com os testes dos Integrantes 3 e 7). Os imports e helpers
abaixo usam sufixo/prefixo "aluno4" para não colidir com o código dos colegas.
"""
import pytest
import requests

ID_INEXISTENTE = 999999999

PAYLOAD_INVESTIMENTO_ALUNO4 = {
    "asset_name": "CDB",
    "amount": 1500.00,
    "purchase_price": 1.00,
    "days_invested": 90,
    "planned_days": 360,
}


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------
def _criar_investimento_aluno4(base_url, auth_headers):
    """Cria um investimento válido e retorna o JSON de resposta."""
    response = requests.post(
        f"{base_url}/api/investments",
        json=PAYLOAD_INVESTIMENTO_ALUNO4,
        headers=auth_headers,
    )
    assert response.status_code in (200, 201), (
        f"Falha ao criar investimento de apoio. Resposta: {response.text}"
    )
    return response.json()


def _listar_ids_aluno4(base_url, auth_headers):
    """Retorna o conjunto de IDs dos investimentos listados na API."""
    response = requests.get(f"{base_url}/api/investments", headers=auth_headers)
    assert response.status_code == 200
    return {item["id"] for item in response.json()}


@pytest.fixture
def investimento_aluno4(base_url, auth_headers):
    """Cria um investimento antes do teste e o remove ao final (limpeza)."""
    investimento = _criar_investimento_aluno4(base_url, auth_headers)
    yield investimento
    # Limpeza: ignora o resultado, pois o teste pode já ter excluído o registro
    requests.delete(
        f"{base_url}/api/investments/{investimento['id']}",
        headers=auth_headers,
    )


# ---------------------------------------------------------------------------
# GET /api/investments
# ---------------------------------------------------------------------------
def test_listar_investimentos_sucesso(base_url, auth_headers):
    """Valida que a listagem autenticada retorna HTTP 200 e uma lista."""
    response = requests.get(f"{base_url}/api/investments", headers=auth_headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_listar_investimentos_contem_registro_criado(
    base_url, auth_headers, investimento_aluno4
):
    """Valida que um investimento recém-criado aparece na listagem."""
    ids = _listar_ids_aluno4(base_url, auth_headers)

    assert investimento_aluno4["id"] in ids


def test_listar_investimentos_estrutura_dos_campos(
    base_url, auth_headers, investimento_aluno4
):
    """Valida que cada item da listagem possui os campos esperados."""
    response = requests.get(f"{base_url}/api/investments", headers=auth_headers)
    assert response.status_code == 200

    itens = response.json()
    assert len(itens) > 0

    item = next(i for i in itens if i["id"] == investimento_aluno4["id"])
    for campo in ("id", "asset_name", "amount", "purchase_price"):
        assert campo in item, f"Campo '{campo}' ausente na resposta"

    assert item["asset_name"] == PAYLOAD_INVESTIMENTO_ALUNO4["asset_name"]
    assert item["amount"] == pytest.approx(PAYLOAD_INVESTIMENTO_ALUNO4["amount"])


def test_listar_investimentos_sem_token(base_url):
    """Valida que a listagem sem autenticação é recusada."""
    response = requests.get(f"{base_url}/api/investments")

    assert response.status_code in (401, 403)


def test_listar_investimentos_token_invalido(base_url):
    """Valida que a listagem com token JWT inválido é recusada."""
    headers = {"Authorization": "Bearer token.invalido.xyz"}
    response = requests.get(f"{base_url}/api/investments", headers=headers)

    assert response.status_code in (401, 403)


# ---------------------------------------------------------------------------
# DELETE /api/investments/{id}
# ---------------------------------------------------------------------------
def test_excluir_investimento_sucesso(base_url, auth_headers, investimento_aluno4):
    """Valida a exclusão de um investimento existente."""
    investimento_id = investimento_aluno4["id"]

    response = requests.delete(
        f"{base_url}/api/investments/{investimento_id}", headers=auth_headers
    )

    assert response.status_code in (200, 204)


def test_excluir_investimento_remove_da_listagem(
    base_url, auth_headers, investimento_aluno4
):
    """Valida que, após a exclusão, o investimento não aparece mais na listagem."""
    investimento_id = investimento_aluno4["id"]
    assert investimento_id in _listar_ids_aluno4(base_url, auth_headers)

    response = requests.delete(
        f"{base_url}/api/investments/{investimento_id}", headers=auth_headers
    )
    assert response.status_code in (200, 204)

    assert investimento_id not in _listar_ids_aluno4(base_url, auth_headers)


def test_excluir_investimento_inexistente(base_url, auth_headers):
    """Valida que excluir um ID inexistente retorna HTTP 404."""
    response = requests.delete(
        f"{base_url}/api/investments/{ID_INEXISTENTE}", headers=auth_headers
    )

    assert response.status_code == 404


def test_excluir_investimento_duas_vezes(base_url, auth_headers, investimento_aluno4):
    """Valida que a segunda exclusão do mesmo investimento retorna HTTP 404."""
    url = f"{base_url}/api/investments/{investimento_aluno4['id']}"

    primeira = requests.delete(url, headers=auth_headers)
    assert primeira.status_code in (200, 204)

    segunda = requests.delete(url, headers=auth_headers)
    assert segunda.status_code == 404


def test_excluir_investimento_sem_token(base_url, investimento_aluno4):
    """Valida que a exclusão sem autenticação é recusada e o registro permanece."""
    response = requests.delete(
        f"{base_url}/api/investments/{investimento_aluno4['id']}"
    )

    assert response.status_code in (401, 403)


def test_excluir_investimento_id_invalido(base_url, auth_headers):
    """Valida que um ID não numérico é rejeitado (HTTP 422 de validação do FastAPI)."""
    response = requests.delete(
        f"{base_url}/api/investments/abc", headers=auth_headers
    )

    assert response.status_code in (404, 422)