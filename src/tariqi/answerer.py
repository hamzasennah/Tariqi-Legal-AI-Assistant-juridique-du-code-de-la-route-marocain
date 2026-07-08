from __future__ import annotations

from .config import AppConfig
from .calculator import FineCalculator
from .cleaning import meaningful_tokens
from .procedures import ProcedureGuide
from .retriever import Retriever
from .schemas import RAGAnswer, ScoredChunk


LEGAL_WARNING = (
    "Cette réponse est informative. Elle ne remplace pas une décision officielle, "
    "une consultation juridique ou la vérification auprès de l'autorité compétente."
)


class TariqiAssistant:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig.from_env()
        self.retriever = Retriever(self.config)

    def ask(self, question: str, top_k: int = 5) -> RAGAnswer:
        chunks = self.retriever.retrieve(question, top_k=top_k)
        confidence = self._confidence(chunks)
        fine_result = FineCalculator(self.config.infractions_csv).calculate(question)
        procedure = ProcedureGuide(self.config.procedures_path).match(question)

        if fine_result.matched and fine_result.infraction:
            structured_confidence = self._structured_confidence(fine_result.infraction, confidence)
            answer_text = self._infraction_answer(
                fine_result,
                chunks,
                structured_confidence,
            )
            return RAGAnswer(question, answer_text, chunks, structured_confidence, used_llm=False)

        if procedure:
            answer_text = self._procedure_answer(
                procedure,
                chunks,
                confidence if chunks else "élevé",
            )
            return RAGAnswer(question, answer_text, chunks, confidence if chunks else "élevé", used_llm=False)

        if not chunks:
            answer_text = self._no_relevant_source_answer(question)
            return RAGAnswer(question, answer_text, [], "faible", used_llm=False)

        if self.config.use_openai_answer and self.config.openai_api_key and confidence != "faible":
            answer_text = self._answer_with_openai(question, chunks)
            return RAGAnswer(question, answer_text, chunks, confidence, used_llm=True)

        answer_text = self._answer_without_llm(question, chunks, confidence)
        return RAGAnswer(question, answer_text, chunks, confidence, used_llm=False)

    def _answer_with_openai(self, question: str, chunks: list[ScoredChunk]) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.config.openai_api_key)
        context = self._build_context(chunks)

        system_message = (
            "Tu es Tariqi Legal AI, assistant juridique informatif sur le code de la route "
            "marocain. Réponds uniquement à partir du contexte fourni. Si l'information "
            "n'existe pas dans le contexte, dis-le clairement. Réponds en français avec "
            "les sections : Réponse courte, Détails, Conséquences possibles, Procédure, "
            "Sources, Prudence juridique."
        )
        user_message = f"CONTEXTE:\n{context}\n\nQUESTION:\n{question}"

        response = client.responses.create(
            model=self.config.openai_generation_model,
            input=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
        )
        return response.output_text

    def _answer_without_llm(
        self,
        question: str,
        chunks: list[ScoredChunk],
        confidence: str,
    ) -> str:
        if not chunks or chunks[0].score < 0.05:
            return self._no_relevant_source_answer(question)

        best = chunks[0]
        details = self._evidence_bullets(chunks)
        sources = self._source_bullets(chunks)

        return (
            "### Réponse courte\n"
            f"{best.chunk.text}\n\n"
            "### Détails\n"
            f"{details}\n\n"
            "### Conséquences possibles\n"
            f"{self._generic_consequences(chunks)}\n\n"
            "### Procédure\n"
            f"{self._generic_procedure(chunks)}\n\n"
            "### Sources\n"
            f"{sources}\n\n"
            "### Prudence juridique\n"
            f"{LEGAL_WARNING}\n\n"
            "### Confiance\n"
            f"{confidence}"
        )

    def _infraction_answer(self, result, chunks: list[ScoredChunk], confidence: str) -> str:
        row = result.infraction
        amount = (
            f"{result.amount} DH si le délai sélectionné est {result.delay}"
            if result.amount
            else "montant non calculé dans la base structurée"
        )
        notes = row.get("notes") or "Vérifier le cas exact dans la source officielle."

        return (
            "### Réponse courte\n"
            f"{row['nom_infraction']} entraîne {row['points_retires']} point(s) à retirer. "
            f"Montant indicatif : {amount}.\n\n"
            "### Détails\n"
            f"- Type : {row['type_infraction']}.\n"
            f"- Classe : {row['classe']}.\n"
            f"- Sanction possible : {row['sanction_possible']}.\n"
            f"- Précision : {notes}\n\n"
            "### Conséquences possibles\n"
            "Le conducteur peut être concerné par une amende, un retrait de points et, "
            "selon le cas, une procédure administrative ou judiciaire.\n\n"
            "### Procédure\n"
            "Vérifier l'avis de contravention, respecter le délai applicable, utiliser un "
            "canal officiel de paiement ou de contestation, puis conserver la preuve de la démarche.\n\n"
            "### Sources\n"
            f"- {row['source']} - {row['document']} - {row['article_ou_page']}.\n"
            f"{self._source_bullets(chunks)}\n\n"
            "### Prudence juridique\n"
            f"{LEGAL_WARNING}\n\n"
            "### Confiance\n"
            f"{confidence}"
        )

    def _no_relevant_source_answer(self, question: str) -> str:
        tokens = meaningful_tokens(question)
        detail = (
            "La question est trop courte ou trop vague pour être reliée de manière fiable aux sources."
            if not tokens
            else "Aucun passage officiel suffisamment pertinent n'a été récupéré pour cette question."
        )
        return (
            "### Réponse courte\n"
            "Je ne trouve pas d'information fiable dans les sources disponibles pour répondre à cette question.\n\n"
            "### Détails\n"
            f"{detail} Dans un système RAG, l'assistant doit refuser de répondre quand la recherche documentaire ne trouve pas de contexte solide.\n\n"
            "### Conséquences possibles\n"
            "Répondre malgré une recherche faible pourrait produire une réponse inventée ou hors sujet.\n\n"
            "### Procédure\n"
            "Reformulez avec une vraie question liée au code de la route marocain, par exemple : "
            "\"Combien de points pour un feu rouge ?\" ou \"Que faire pour contester une contravention ?\".\n\n"
            "### Sources\n"
            "- Aucune source suffisamment pertinente.\n\n"
            "### Prudence juridique\n"
            f"{LEGAL_WARNING}\n\n"
            "### Confiance\n"
            "faible"
        )

    def _procedure_answer(self, procedure: dict, chunks: list[ScoredChunk], confidence: str) -> str:
        steps = "\n".join(f"- {step}" for step in procedure.get("steps", []))
        return (
            "### Réponse courte\n"
            f"{procedure['summary']}\n\n"
            "### Détails\n"
            f"{steps}\n\n"
            "### Conséquences possibles\n"
            "Le non-respect d'un délai ou l'absence de justificatif peut rendre la démarche "
            "plus difficile. Il faut donc conserver les preuves de dépôt ou de paiement.\n\n"
            "### Procédure\n"
            f"{steps}\n\n"
            "### Sources\n"
            f"- Source officielle : {procedure.get('url', '')}\n"
            f"{self._source_bullets(chunks)}\n\n"
            "### Prudence juridique\n"
            f"{procedure.get('warning', LEGAL_WARNING)}\n\n"
            "### Confiance\n"
            f"{confidence}"
        )

    def _evidence_bullets(self, chunks: list[ScoredChunk]) -> str:
        bullets = []
        seen = set()
        for item in chunks[:4]:
            title = item.chunk.metadata.get("title", item.chunk.source_id)
            if title in seen:
                continue
            seen.add(title)
            bullets.append(f"- {item.chunk.text}")
        return "\n".join(bullets)

    def _source_bullets(self, chunks: list[ScoredChunk]) -> str:
        bullets = []
        seen = set()
        for item in chunks[:4]:
            meta = item.chunk.metadata
            key = (meta.get("authority"), meta.get("title"), meta.get("article_or_section"))
            if key in seen:
                continue
            seen.add(key)
            bullets.append(f"- {item.source_line()}")
        return "\n".join(bullets)

    def _generic_consequences(self, chunks: list[ScoredChunk]) -> str:
        themes = {str(item.chunk.metadata.get("theme", "")) for item in chunks[:3]}
        if "permis_points" in themes or "points" in themes:
            return "La conséquence principale peut être une réduction du capital de points, selon l'infraction établie."
        if "procedure" in themes:
            return "La conséquence dépend surtout du respect des délais et de la qualité des justificatifs fournis."
        if "amendes" in themes:
            return "La conséquence peut être une amende transactionnelle et forfaitaire, selon le texte applicable."
        return "Les conséquences peuvent varier selon le texte applicable, la qualification de l'infraction et la procédure suivie."

    def _generic_procedure(self, chunks: list[ScoredChunk]) -> str:
        themes = {str(item.chunk.metadata.get("theme", "")) for item in chunks[:3]}
        if "paiement" in themes:
            return "Vérifier l'avis, respecter le délai de paiement et utiliser un canal officiel."
        if "procedure" in themes:
            return "Identifier la démarche pertinente, respecter le délai et conserver la preuve de dépôt."
        if "sources" in themes:
            return "Consulter le portail officiel indiqué et vérifier la version consolidée ou publiée."
        return "Vérifier la source officielle citée, identifier le cas exact et demander confirmation à l'autorité compétente en cas de doute."

    def _build_context(self, chunks: list[ScoredChunk]) -> str:
        parts: list[str] = []
        for item in chunks:
            meta = item.chunk.metadata
            parts.append(
                "\n".join(
                    [
                        f"Source: {meta.get('authority')} - {meta.get('title')}",
                        f"Document: {meta.get('document')}",
                        f"Section: {meta.get('article_or_section')}",
                        f"Date: {meta.get('date_source')}",
                        f"URL: {meta.get('url')}",
                        f"Score: {item.score:.3f}",
                        f"Passage: {item.chunk.text}",
                    ]
                )
            )
        return "\n\n---\n\n".join(parts)

    def _confidence(self, chunks: list[ScoredChunk]) -> str:
        if not chunks:
            return "faible"
        best = chunks[0].score
        trust = str(chunks[0].chunk.metadata.get("trust_level", "")).upper()
        if best >= 0.30 and trust in {"A+", "A"}:
            return "élevé"
        if best >= 0.12:
            return "moyen"
        return "faible"

    def _structured_confidence(self, row: dict, fallback: str) -> str:
        trust = str(row.get("confiance", "")).upper()
        if trust in {"A+", "A"}:
            return "élevé"
        return fallback
