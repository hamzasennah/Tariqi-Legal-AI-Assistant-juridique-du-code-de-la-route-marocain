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
    assert payload["sources"][0]["source_id"] == "khadamat_paiement_infractions"


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


def test_ask_endpoint_answers_phone_while_driving_question() -> None:
    response = client.post(
        "/api/ask",
        json={"question": "Que risque un conducteur qui utilise son téléphone en conduisant ?", "top_k": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "Utilisation du téléphone tenu en main en conduisant" in payload["answer_markdown"]
    assert "1 point" in payload["answer_markdown"]
    assert payload["sources"][0]["source_id"] == "narsa_tableau_points_pdf"


def test_ask_endpoint_answers_driving_without_license_question() -> None:
    response = client.post(
        "/api/ask",
        json={"question": "Que risque-t-on si on conduit sans permis ?", "top_k": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "permis de conduire valide" in payload["answer_markdown"]
    assert payload["sources"][0]["source_id"] == "loi_52_05_code_route"


def test_ask_endpoint_uses_reclamation_for_contestation_deadline() -> None:
    response = client.post(
        "/api/ask",
        json={"question": "Quel est le délai pour contester une contravention ?", "top_k": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "réclamation" in payload["answer_markdown"].lower()
    assert "30 jours" in payload["answer_markdown"]
    assert payload["sources"][0]["source_id"] == "khadamat_reclamation"


def test_ask_endpoint_includes_source_for_other_driver_procedure() -> None:
    response = client.post(
        "/api/ask",
        json={
            "question": "Que faire si je reçois une contravention alors que je n’étais pas le conducteur ?",
            "top_k": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "déclaration" in payload["answer_markdown"].lower()
    assert payload["sources"][0]["source_id"] == "khadamat_declaration"


def test_ask_endpoint_answers_generic_speeding_consequences() -> None:
    response = client.post(
        "/api/ask",
        json={"question": "Quelles sont les conséquences d’un excès de vitesse ?", "top_k": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "excès de vitesse" in payload["answer_markdown"].lower()
    assert "4 points" in payload["answer_markdown"] or "6 points" in payload["answer_markdown"]
    assert payload["sources"][0]["source_id"] == "narsa_tableau_points_pdf"


def test_ask_endpoint_includes_source_for_point_recovery() -> None:
    response = client.post(
        "/api/ask",
        json={"question": "Comment récupérer les points perdus du permis de conduire ?", "top_k": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "récup" in payload["answer_markdown"].lower()
    assert payload["sources"][0]["source_id"] in {"khadamat_permis_points", "khadamat_retrait_points"}


def test_ask_endpoint_answers_payment_effect_on_points() -> None:
    response = client.post(
        "/api/ask",
        json={"question": "J’ai payé mon amende, est-ce que les points sont retirés automatiquement ?", "top_k": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "paiement" in payload["answer_markdown"].lower()
    assert "retrait de points" in payload["answer_markdown"].lower() or "réduction du capital" in payload["answer_markdown"].lower()
    assert payload["sources"][0]["source_id"] == "khadamat_retrait_points"


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
