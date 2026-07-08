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


def test_ask_endpoint_refuses_irrelevant_short_query() -> None:
    response = client.post(
        "/api/ask",
        json={"question": "cc?", "top_k": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["confidence"] == "faible"
    assert payload["sources"] == []
    assert "Je ne trouve pas d'information fiable" in payload["answer_markdown"]


def test_ask_endpoint_handles_natural_line_continuous_question() -> None:
    response = client.post(
        "/api/ask",
        json={"question": "si je depasses une voiture dans une ligne continu?", "top_k": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["confidence"] == "élevé"
    assert "Franchissement de la ligne continue" in payload["answer_markdown"]
    assert "4 point" in payload["answer_markdown"]
    assert payload["sources"][0]["source_id"] == "narsa_tableau_points_pdf"


def test_ask_endpoint_refuses_mixed_noise_query() -> None:
    response = client.post(
        "/api/ask",
        json={"question": "pourquoi une voiture noire est interdite par police feu rouge?", "top_k": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["confidence"] == "faible"
    assert payload["sources"] == []
    assert "Je ne trouve pas d'information fiable" in payload["answer_markdown"]


def test_ask_endpoint_answers_authoroute_emergency_stop_question() -> None:
    response = client.post(
        "/api/ask",
        json={
            "question": "quelle sont les cas qui me permet de stopper dans une autoroute sans avoir des problemes avec police?",
            "top_k": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["confidence"] in {"moyen", "élevé"}
    assert "nécessité absolue" in payload["answer_markdown"]
    assert "bande d'arrêt d'urgence" in payload["answer_markdown"]
    assert payload["sources"][0]["source_id"] == "decret_2_10_420_regles_circulation"


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
