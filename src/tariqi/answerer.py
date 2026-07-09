from __future__ import annotations

from .calculator import FineCalculator
from .cleaning import meaningful_tokens, normalize_for_search
from .config import AppConfig
from .procedures import ProcedureGuide
from .retriever import Retriever
from .schemas import DocumentChunk, RAGAnswer, ScoredChunk

LEGAL_WARNING = (
    "Cette réponse est informative. Elle ne remplace pas une décision officielle, "
    "une consultation juridique ou la vérification auprès de l'autorité compétente."
)


class TariqiAssistant:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig.from_env()
        self.retriever = Retriever(self.config)

    def ask(self, question: str, top_k: int = 5) -> RAGAnswer:
        chunks = self._focused_chunks(self.retriever.retrieve(question, top_k=top_k))
        confidence = self._confidence(chunks)
        fine_result = FineCalculator(self.config.infractions_csv).calculate(question)
        procedure = ProcedureGuide(self.config.procedures_path).match(question)

        if chunks and self._asks_for_rule_explanation(question):
            answer_text = self._answer_without_llm(question, chunks, confidence)
            return RAGAnswer(question, answer_text, chunks, confidence, used_llm=False)

        if fine_result.matched and fine_result.infraction:
            structured_confidence = self._structured_confidence(fine_result.infraction, confidence)
            sources = self._with_structured_source(chunks, fine_result.infraction)
            answer_text = self._infraction_answer(
                fine_result,
                sources,
                structured_confidence,
            )
            return RAGAnswer(question, answer_text, sources, structured_confidence, used_llm=False)

        if procedure:
            sources = self._with_procedure_source(chunks, procedure)
            answer_text = self._procedure_answer(
                procedure,
                sources,
                confidence if chunks else "élevé",
            )
            return RAGAnswer(question, answer_text, sources, confidence if chunks else "élevé", used_llm=False)

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

    def _focused_chunks(self, chunks: list[ScoredChunk]) -> list[ScoredChunk]:
        if len(chunks) <= 1:
            return chunks

        best = chunks[0].score
        focused = [item for item in chunks if item.score >= best - 0.08]
        return focused or chunks[:1]

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

    def _with_structured_source(
        self,
        chunks: list[ScoredChunk],
        row: dict[str, str],
    ) -> list[ScoredChunk]:
        source_id = self._source_id_for_structured_row(row)
        if any(item.chunk.source_id == source_id and item.chunk.metadata.get("article_or_section") == row.get("article_ou_page") for item in chunks):
            return chunks

        chunk = DocumentChunk(
            id=f"structured_{row.get('id_infraction', 'infraction')}",
            source_id=source_id,
            text=(
                f"{row.get('nom_infraction', '')}. "
                f"{row.get('sanction_possible', '')}. "
                f"Points: {row.get('points_retires', 'non indiqué')}. "
                f"Montants: {row.get('montant_24h', '')}/{row.get('montant_15j', '')}/{row.get('montant_30j', '')} DH."
            ),
            metadata={
                "authority": row.get("source", ""),
                "title": row.get("document", ""),
                "document": row.get("document", ""),
                "article_or_section": row.get("article_ou_page", ""),
                "date_source": row.get("date_source", ""),
                "theme": "infraction",
                "trust_level": row.get("confiance", ""),
                "url": row.get("source_url", ""),
            },
        )
        return [ScoredChunk(chunk=chunk, score=1.0), *chunks]

    def _with_procedure_source(
        self,
        chunks: list[ScoredChunk],
        procedure: dict,
    ) -> list[ScoredChunk]:
        source_id = str(procedure.get("source_id", "procedure"))
        if any(item.chunk.source_id == source_id for item in chunks):
            return chunks

        chunk = DocumentChunk(
            id=f"procedure_{procedure.get('id', 'guide')}",
            source_id=source_id,
            text=f"{procedure.get('summary', '')} {procedure.get('warning', '')}".strip(),
            metadata={
                "authority": "Khadamat NARSA",
                "title": procedure.get("title", "Procédure"),
                "document": "Guide procédure",
                "article_or_section": procedure.get("title", ""),
                "date_source": "",
                "theme": "procedure",
                "trust_level": "A",
                "url": procedure.get("url", ""),
            },
        )
        return [ScoredChunk(chunk=chunk, score=1.0), *chunks]

    def _source_id_for_structured_row(self, row: dict[str, str]) -> str:
        url = row.get("source_url", "")
        if "khadamatnarsa.ma/fr/services/infractions-routieres/paiement" in url:
            return "khadamat_paiement_infractions"
        if "tableaux%20des%20infractions" in url or "tableaux" in row.get("document", "").lower():
            return "narsa_tableau_points_pdf"
        return row.get("id_infraction", "structured_infraction")

    def _asks_for_rule_explanation(self, question: str) -> bool:
        tokens = set(meaningful_tokens(question))
        normalized = normalize_for_search(question)
        if "combien" in normalized:
            return False

        explanation_terms = {
            "autorise",
            "autorisee",
            "autorises",
            "cas",
            "droit",
            "exception",
            "exceptions",
            "permet",
            "possible",
            "quand",
        }
        explanation_phrases = {
            "dans quel cas",
            "quels cas",
            "quelle sont les cas",
            "me permet",
            "est ce possible",
            "est ce que",
            "consequence",
            "consequences",
            "ai je droit",
        }
        point_evidence_terms = {
            "automatiquement",
            "paiement",
            "paye",
            "payee",
            "perdus",
            "recuperation",
            "recuperer",
            "retrait",
            "retire",
            "retires",
        }
        if "points" in tokens and tokens & point_evidence_terms:
            return True

        return bool(tokens & explanation_terms) or any(
            phrase in normalized for phrase in explanation_phrases
        )
