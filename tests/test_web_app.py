from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_page_loads() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Tariqi Legal AI" in response.text
    assert "streamlit" not in response.text.lower()


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_endpoint_returns_specific_red_light_answer() -> None:
    response = client.post(
        "/api/ask",
        json={"question": "Combien de points sont retirés pour un feu rouge ?", "top_k": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "4 point" in payload["answer_markdown"]
    assert payload["sources"][0]["source_id"] == "narsa_tableau_points_pdf"


def test_calculate_endpoint() -> None:
    response = client.post(
        "/api/calculate",
        json={"infraction": "feu rouge", "delay": "24h"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["matched"] is True
    assert payload["amount"] == "400"
    assert payload["points"] == "4"


def test_procedure_endpoint() -> None:
    response = client.get("/api/procedure", params={"q": "Je veux déposer une réclamation"})

    assert response.status_code == 200
    assert response.json()["procedure"]["id"] == "reclamer_contravention"
