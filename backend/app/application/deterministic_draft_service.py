from datetime import UTC, datetime

from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft


class DeterministicDraftService:
    def create_draft(self, request: DraftGenerationRequest) -> GeneratedDraft:
        brief = request.brief
        model = request.editorial_model
        evidence = "\n".join(f"{index + 1}. {item}" for index, item in enumerate(brief.evidence))
        examples = "\n".join(f"- {item}" for item in brief.examples)
        structure = "\n".join(f"- {item}" for item in brief.structure)

        body = "\n".join(
            [
                brief.title,
                "",
                "Сильное AI-demo само по себе не доказывает, что продукт станет частью рабочего дня.",
                "",
                f"Тезис: {brief.thesis}",
                "",
                f"Конфликт: {brief.conflict}",
                "",
                f"Позиция автора: {brief.author_position}",
                "",
                "Доказательства:",
                evidence,
                "",
                "Как это выглядит в B2B:",
                examples,
                "",
                "Структура заметки:",
                structure,
                "",
                f"Для аудитории: {brief.audience or model.audience}",
                "",
                f"Вывод и CTA: {brief.cta}",
            ]
        )

        return GeneratedDraft(
            id=f"draft-{brief.id}",
            brief_id=brief.id,
            title=brief.title,
            body=body,
            version=1,
            status="draft",
            updated_at=datetime.now(UTC).isoformat(),
        )
