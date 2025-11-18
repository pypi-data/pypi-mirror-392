# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Internationalization, i.e. translation and similar tasks.
"""
import typing as t

import hallyd

import annize.flow.run_context
import annize.data
import annize.i18n


class _ProjectDefinedTranslationProvider(annize.i18n.TranslationProvider):
    """
    Internally created translation provider for backing :py:class:`String` instances.
    """

    def __init__(self):
        self.__translations = {}

    def translate(self, string_name, *, culture):
        return self.__translations_for_string_name(string_name).get(culture.iso_639_1_language_code)

    def add_translations(self, string_name: str, variants: dict[str, str]) -> None:
        self.__translations_for_string_name(string_name).update(variants)

    def __translations_for_string_name(self, string_name: str) -> dict[str, str]:
        result = self.__translations[string_name] = self.__translations.get(string_name) or {}
        return result


_TRANSLATION_PROVIDER__NAME = f"__{hallyd.lang.unique_id()}"


def _translation_provider():
    translation_provider = annize.flow.run_context.object_by_name(_TRANSLATION_PROVIDER__NAME)
    if not translation_provider:
        translation_provider = _ProjectDefinedTranslationProvider()
        annize.flow.run_context.set_object_name(translation_provider, _TRANSLATION_PROVIDER__NAME)
        annize.i18n.add_translation_provider(translation_provider, priority=-100_000)
    return translation_provider


class String(annize.i18n.ProvidedTrStr):
    """
    A translatable text defined in an Annize project.
    """

    def __init__(self, *, string_name: str|None, stringtr: str|None, **variants: str):
        if stringtr:
            stringtr = stringtr.strip()
            if not stringtr.endswith(")"):
                raise ValueError("stringtr specification must end with ')'")
            i_start = stringtr.find("(")
            if i_start == -1:
                raise ValueError("stringtr specification must contain a '('")
            string_name_str = stringtr[i_start+1:-1].strip()
            if ((len(string_name_str) < 3) or (string_name_str[0] != string_name_str[-1])
                    or (string_name_str[0] not in ["'", '"'])):
                raise ValueError("stringtr specification must contain a gettext text id inside quotes")
            string_name = string_name_str[1:-1]

        string_name = string_name or f"__{hallyd.lang.unique_id()}"
        super().__init__(string_name)

        if variants:
            _translation_provider().add_translations(string_name, variants)


class Culture(annize.i18n.Culture):
    """
    A culture defined in an Annize project.
    """

    def __init__(self, *, iso_639_1_language_code: str, region_code: str|None,
                 fallback_cultures: list[annize.i18n.Culture]):
        english_lang_name = annize.i18n.culture_by_spec(iso_639_1_language_code).english_lang_name  # TODO region_code
        super().__init__(english_lang_name, iso_639_1_language_code=iso_639_1_language_code, region_code=region_code,
                         fallback_cultures=fallback_cultures)


class ProjectCultures(list):
    """
    Definition of an Annize project's target cultures.
    """

    def __init__(self, *, cultures: t.Sequence[annize.i18n.Culture]):
        super().__init__(cultures)


def project_cultures() -> t.Sequence[annize.i18n.Culture]:
    """
    Return a list of the current Annize project's target cultures. See also :py:class:`ProjectCultures`.
    """
    return tuple(culture
                 for cultures in annize.flow.run_context.objects_by_type(ProjectCultures)
                 for culture in cultures)
