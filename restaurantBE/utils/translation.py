import logging

from django.conf import settings
from rest_framework import serializers

logger = logging.getLogger(__name__)


class TranslationProvider:
    def translate(self, text, source_language, target_language):
        raise NotImplementedError()


class GoogleCloudTranslationProvider(TranslationProvider):
    def __init__(self):
        self.project_id = settings.GOOGLE_TRANSLATION_PROJECT_ID
        self.location = settings.GOOGLE_TRANSLATION_LOCATION
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google.cloud import translate

            self._client = translate.TranslationServiceClient()
        return self._client

    def translate(self, text, source_language, target_language):
        if not self.project_id:
            raise ValueError("GOOGLE_TRANSLATION_PROJECT_ID is required")

        client = self._get_client()
        response = client.translate_text(
            parent=f"projects/{self.project_id}/locations/{self.location}",
            contents=[text],
            mime_type="text/plain",
            source_language_code=source_language,
            target_language_code=target_language,
        )
        if not response.translations:
            return text

        translated_text = response.translations[0].translated_text
        return translated_text or text


class NoopTranslationProvider(TranslationProvider):
    def translate(self, text, source_language, target_language):
        return text


def get_translation_provider():
    if not settings.GOOGLE_TRANSLATION_ENABLED:
        return NoopTranslationProvider()

    return GoogleCloudTranslationProvider()


def build_multilingual_value(source_text, source_language="vi", target_languages=None):
    languages = tuple(target_languages or settings.LOCALIZED_FIELD_LANGUAGES)
    provider = get_translation_provider()

    value = {source_language: source_text}

    for language in languages:
        if language == source_language:
            continue

        try:
            value[language] = provider.translate(source_text, source_language, language)
        except Exception:
            logger.exception(
                "Failed to translate localized field from %s to %s",
                source_language,
                language,
            )
            value[language] = source_text

    return value


def normalize_localized_field(
    value,
    field_key,
    source_language="vi",
    target_languages=None,
    required_keys=None,
    allow_extra_keys=True,
):
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            raise serializers.ValidationError(f"{field_key}_required")
        return build_multilingual_value(
            normalized,
            source_language=source_language,
            target_languages=target_languages,
        )

    if not isinstance(value, dict):
        raise serializers.ValidationError(f"{field_key}_must_be_json")

    if not value:
        raise serializers.ValidationError(f"{field_key}_required")

    if required_keys:
        missing_keys = [key for key in required_keys if key not in value]
        if missing_keys:
            raise serializers.ValidationError(f"{field_key}_required")

    if target_languages and not allow_extra_keys:
        extra_keys = set(value.keys()) - set(target_languages)
        if extra_keys:
            raise serializers.ValidationError(
                f"unsupported_language_keys_in_{field_key}"
            )

    return value
