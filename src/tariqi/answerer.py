from __future__ import annotations

from .config import AppConfig
from .calculator import FineCalculator
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

        if self.config.use_openai_answer and self.config.openai_api_key:
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
            return (
                "### Réponse courte\n"
                "Je ne trouve pas cette information dans les documents disponibles.\n\n"
                "### Détails\n"
                "La question doit être vérifiée dans une source officielle complémentaire.\n\n"
                "### Prudence juridique\n"
                f"{LEGAL_WARNING}"
            )

        structured = self._structured_infraction_block(question)
        best = chunks[0]
        details = "\n".join(
            f"- {item.chunk.text}" for item in chunks[:3] if item.score >= 0.03
        )
        sources = "\n".join(f"- {item.source_line()}" for item in chunks[:3])

        return (
            "### Réponse courte\n"
            f"{structured or best.chunk.text}\n\n"
            "### Détails\n"
            f"{details}\n\n"
            "### Conséquences possibles\n"
            "Les conséquences peuvent inclure une amende, un retrait de points ou une "
            "procédure administrative/judiciaire selon la nature de l'infraction.\n\n"
            "### Procédure\n"
            "Vérifier l'avis ou le texte applicable, respecter les délais, conserver les "
            "preuves et utiliser les canaux officiels.\n\n"
            "### Sources\n"
            f"{sources}\n\n"
            "### Prudence juridique\n"
            f"{LEGAL_WARNING}\n\n"
            "### Confiance\n"
            f"{confidence}"
        )

    def _structured_infraction_block(self, question: str) -> str:
        calculator = FineCalculator(self.config.infractions_csv)
        result = calculator.calculate(question)
        if not result.matched or not result.infraction:
            return ""
        row = result.infraction
        parts = [
            f"Infraction reconnue dans le CSV structuré : {row['nom_infraction']}.",
            f"Points à retirer : {row['points_retires']}.",
        ]
        if result.amount:
            parts.append(f"Montant indicatif si paiement dans le délai 24h : {result.amount} DH.")
        else:
            parts.append("Montant non calculé dans la base structurée, car le cas peut relever d'une procédure judiciaire ou spécifique.")
        parts.append(f"Source : {row['source']} - {row['document']} ({row['article_ou_page']}).")
        return " ".join(parts)

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
