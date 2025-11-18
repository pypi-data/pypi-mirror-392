# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Annize i18n backend.

The most fundamental mechanism around i18n is to get a translatable text (:py:class:`TrStr`) from somewhere and get a
translation from it, e.g. via :py:meth:`TrStr.translate` or :py:func:`translate`.

Usually the translation is based on the current culture (:py:func:`current_culture`).

There can be :py:class:`TrStr` coming from various sources with various implementations. A common one is
:py:class:`ProvidedTrStr`, which is backed by the so-called "translation providers". One typical translation provider
implementation is internally based on :code:`gettext`. There is always at least one translation provider instance of
that type, fetching translations from Annize own :code:`gettext` translations. In general, translation providers could
be based on arbitrary sources and are not restricted at all to :code:`gettext`.

Other :py:class:`TrStr` might have arbitrary other ways to translate texts, not backed by translation providers. Often
they generate translations dynamically, e.g. by combining other :py:class:`TrStr`.

At higher level, Annize i18n provides the following functionality:

- It hosts Annize own text translations. They are backed by :code:`gettext` and typically referenced by :py:func:`tr`
  internally.
  - Annize projects are allowed to use those texts when convenient. A translation provider for them always exists, so
    a project could contain nodes like :code:`<String xmlns="annize:i18n" string_name="an_int_DebianPackage"/>`. Find
    all available texts in the top level directory :code:`i18n` of Annize.
- It allows Annize projects to define and use own translated texts.
  - Either directly inside project configuration or via :code:`gettext`.
    The former can be done with a node like
    :code:`<String xmlns="annize:i18n"><a:scalar a:arg_name="en">Yes</a:scalar>...</String>`.
    Usage of :code:`gettext` involves the definition of a :py:class:`annize.features.i18n.gettext.TextSource` and nodes
    like :code:`<String xmlns="annize:i18n"><a:scalar a:arg_name="stringtr">tr("myOwnStringName")</a:scalar></String>`.
    More steps are needed to generate the required :code:`.mo`-files (see below).
    Note: Even for texts that are directly defined in the project, if you add a :code:`string_name` to them, you can
    also reference them in the same way as :code:`gettext` based texts.
- It allows Annize projects to override Annize own text translations.
  - Either directly inside project configuration or via :code:`gettext` (mostly like described above). If is also
    possible add new languages or to override only some languages.
- It helps Annize projects to deal with :code:`gettext` :code:`.mo`- and :code:`.po`-files; no matter whether these
  texts are used in the Annize project configuration or in the project's source code. See
  :py:class:`annize.features.i18n.gettext.UpdatePOs` and :py:class:`annize.features.i18n.gettext.GenerateMOs`.
"""
import abc
import dataclasses
import gettext
import locale
import os
import subprocess
import threading
import typing as t

import hallyd
import pycountry

import annize.asset
import annize.flow.run_context
import annize.fs


class TrStr(abc.ABC):
    """
    Base class for translatable texts.

    Each instance can hold the translation for one text for different cultures.
    In order to translate it to the current culture, the simplest way is to just apply :code:`str()` on it.

    See also :py:meth:`translate` and :py:meth:`_translation_for_culture`.
    """

    def __str__(self):
        return self.translate()

    def translate(self, culture: "CultureSpecT" = None) -> str:
        """
        Return the translation of this text for the current culture or any other one, or raise
        :py:class:`TranslationUnavailableError` if no translation is available for that culture (or its fallbacks; see
        :py:attr:`Culture.fallback_cultures`).

        :param culture: The culture.
        """
        culture = culture_by_spec(culture)
        for culture_ in culture.culture_list():
            if (result := self._translation_for_culture(culture_)) is not None:
                return result

        raise TranslationUnavailableError(self, culture.english_lang_name)

    def format(self, *args, **kwargs) -> "TrStr":
        """
        Return a formated variant of this text (i.e. similar to Python :code:`str.format()`).

        :param args: Formatting args.
        :param kwargs: Formatting kwargs.
        """
        return _FormatedTrStr(self, args, kwargs)

    @staticmethod
    def tr(string_name: str) -> "TrStr":
        """
        Return a translatable text (by querying the registered translation providers).
        Note: Both :code:`tr` functions are to be used by Annize only. External feature packages can only use them for
        own strings if they take care to add a translation provider for them.

        :param string_name: The string name.
        """
        return ProvidedTrStr(string_name)

    @abc.abstractmethod
    def _translation_for_culture(self, culture: "Culture") -> str|None:
        """
        Return the translation of this text for a given culture (or :code:`None` if there is no translation for it).

        Note: This is implemented by subclasses, but usually not called directly from outside. See :py:meth:`translate`.
        This does NOT obey the culture's fallbacks.

        :param culture: The culture.
        """


#: Type annotation for something that can be either a :code:`str` or a :py:class:`TrStr`.
type TrStrOrStr = TrStr|str


def translate(text: TrStrOrStr, *, culture: "CultureSpecT" = None) -> str:
    """
    Translate a given text (if it is not a plain :code:`str`) to the current culture or any other one, or raise
    :py:class:`TranslationUnavailableError` if no translation is available for that culture (or its fallbacks; see
    :py:attr:`Culture.fallback_cultures`).

    :param text: The text to translate.
    :param culture: The culture.
    """
    if (not text) or isinstance(text, str):
        return text
    return text.translate(culture=culture)


def trstr(text: TrStrOrStr) -> TrStr:
    """
    Return a translatable text for a given text.

    This is a no-op for translatable texts, but returns a (technically) translatable text for a plain :code:`str`. In
    the latter case, the translation will be the input text for all cultures.

    This is useful when you need a translatable text (e.g. as input parameter) but maybe only have a plain :code:`str`.

    :param text: The text.
    """
    return _FixedTrStr(text) if isinstance(text, str) else text


class TranslationProvider(abc.ABC):
    """
    Base class for objects that provide translations for some strings in some languages (here usually called: cultures).

    Most translatable texts are backed by translation providers (some only indirectly or not at all).
    This class is a fundamental part of the Annize i18n API, although only small parts of Annize code need to deal with
    them directly.

    See :py:meth:`translate` and also :py:func:`add_translation_provider`.
    """

    @abc.abstractmethod
    def translate(self, string_name: str, *, culture: "Culture") -> str|None:
        """
        Return the translation of a given text for a given culture (or :code:`None` if there is no translation for it).

        Note: This does NOT obey the culture's fallbacks (see :py:attr:`Culture.fallback_cultures`)! That functionality
        is implemented in higher level parts of the API.

        :param string_name: The string name.
        :param culture: The culture.
        """


def add_translation_provider(provider: TranslationProvider, *, priority: int = 0) -> None:
    """
    Add a new translation provider.

    When inside an Annize run context (see :py:mod:`annize.flow.run_context`), the translation provider will
    automatically be removed after the run context and will not affect other run contexts.

    :param provider: The new translation provider.
    :param priority: The priority. Providers with lower priority value are queried earlier.
    """
    current_translation_providers_list = _current_translation_providers_lists()[0]
    current_translation_providers_list.append((provider, priority))


class Culture:
    """
    Representation for an Annize culture.
    This includes the specification of a language and an optional language variant.

    The major purpose of Annize i18n backend is to generate culture-specific translations for some texts.

    Enter the culture context (:code:`with`-block) in order to make it the current culture. This can also be done in a
    nested way (the former current culture does not take any effect meanwhile, but becomes the current culture again
    after this context). This is done by the UI, but also during the execution of an Annize project (iterating over its
    target cultures).

    Annize projects choose their target cultures by means of :py:class:`annize.features.i18n.common.Culture`.
    """

    def __init__(self, english_lang_name: str, iso_639_1_language_code: str, region_code: str|None,
                 fallback_cultures: t.Iterable["Culture"]):
        """
        Do not use directly. See e.g. :py:meth:`from_iso_639_1_lang_code` and :py:func:`culture_by_spec`.

        :param english_lang_name: The language name in English.
        :param iso_639_1_language_code: The ISO-639-1 language code, like :code:`"en"`.
        :param region_code: Optional language variant region_code, like :code:`"US"`.
        :param fallback_cultures: List of fallback cultures. See :py:attr:`fallback_cultures`.
        """
        self.__english_lang_name = english_lang_name
        self.__iso_639_1_language_code = iso_639_1_language_code.lower()
        self.__region_code = region_code.upper() if region_code else None
        self.__fallback_cultures = tuple(
            (*fallback_cultures,
             *((Culture.from_iso_639_1_lang_code(iso_639_1_language_code),) if region_code else ())))

    def __enter__(self):
        _culture_stack.stack = stack = getattr(_culture_stack, "stack", [])
        stack.append((self, Culture.__current_system_locale_setup()))
        system_locale = self.__best_system_locale()
        Culture.__set_system_locale_setup(Culture._TSystemLocaleSetup(system_locale, self.full_name))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _, old_system_locale_setup = _culture_stack.stack.pop()
        if len(_culture_stack.stack) == 0:
            delattr(_culture_stack, "stack")
        Culture.__set_system_locale_setup(old_system_locale_setup)

    @staticmethod
    def from_iso_639_1_lang_code(iso_639_1_language_code: str, region_code: str|None = None, *,
                                     fallback_cultures: t.Iterable["Culture"] = ()) -> "Culture":
        """
        Return a culture by its ISO-639-1 language code (and an optional region_code).

        :param iso_639_1_language_code: The ISO-639-1 language code, like :code:`"en"`.
        :param region_code: Optional language variant region_code, like :code:`"US"`.
        :param fallback_cultures: List of fallback cultures. See :py:attr:`fallback_cultures`.
        """
        language = pycountry.languages.get(alpha_2=iso_639_1_language_code.upper())
        return Culture(language.name if language else iso_639_1_language_code, iso_639_1_language_code, region_code,
                       fallback_cultures)

    @property
    def english_lang_name(self) -> str:
        """
        The language name in English.
        """
        return self.__english_lang_name + (f" ({self.__region_code})" if self.__region_code else "")

    @property
    def iso_639_1_language_code(self) -> str:
        """
        The ISO-639-1 language code, like :code:`"en"`.
        See also :py:attr:`region_code` and :py:attr:`full_name`.

        Note: This is :code:`""` for the :py:data:`unspecified_culture`.
        """
        return self.__iso_639_1_language_code

    @property
    def region_code(self) -> str|None:
        """
        Optional language variant region_code, like :code:`"US"`.
        See also :py:attr:`iso_639_1_language_code` and :py:attr:`full_name`.
        """
        return self.__region_code

    @property
    def full_name(self) -> str:
        """
        The full culture code (incl. the region code), like :code:`"en_US"` or :code:`"en"`.
        See also :py:attr:`iso_639_1_language_code` and :py:attr:`region_code`.

        Note: This is :code:`""` for the :py:data:`unspecified_culture`.
        """
        result = self.iso_639_1_language_code
        if self.region_code:
            result += f"_{self.region_code}"
        return result

    @property
    def fallback_cultures(self) -> t.Sequence["Culture"]:
        """
        Fallback cultures.

        Most parts of the API (unless documented otherwise) try those fallback cultures when an operation was not
        possible with this culture (i.e. there was no translation available for this culture). For that it would try
        with the 1st fallback culture, then maybe with its 1st fallback culture, and so on, then maybe with the 2nd
        fallback culture, until one of them finally succeeds the operation.

        Note: For a culture with a region code, fallbacks usually contain the region-less culture implicitly, so e.g.
        :code:`de_DE` and :code:`de_CH` automatically fall back to :code:`de`.

        See also :py:data:`unspecified_culture`. That is always implicitly assumed to be a final fallback even if not
        part of this list.
        """
        return self.__fallback_cultures

    def culture_list(self) -> t.Iterable["Culture"]:
        """
        Return a list that starts with this culture and then all fallback cultures in an expanded way, i.e. including
        their fallback cultures (recursively).

        The result does never contain duplicates and also handles circular references of fallback cultures.

        It will always contain :py:data:`unspecified_culture` and its fallbacks as last resort!

        For any function that explicitly regards fallback cultures, this is the list they iterate over.
        """
        remaining_cultures_stack = [unspecified_culture, self]
        seen_culture_names = set()

        while remaining_cultures_stack:
            next_culture = remaining_cultures_stack.pop()
            if next_culture.full_name not in seen_culture_names:
                seen_culture_names.add(next_culture.full_name)

                yield next_culture

                for next_fallback_culture in reversed(next_culture.fallback_cultures):
                    remaining_cultures_stack.append(next_fallback_culture)

    def __best_system_locale(self) -> str:
        system_locale_names = [lcc.strip() for lcc in subprocess.check_output(["locale", "-a"]).decode().split("\n")]
        for culture in (*self.culture_list(), annize_user_interaction_culture):
            for locale_name in system_locale_names:
                if culture.full_name and locale_name.split(".")[0].lower() == culture.full_name.lower():
                    return locale_name

        raise RuntimeError(f"unable to find a locale for culture {self.english_lang_name!r}")

    @staticmethod
    def __current_system_locale_setup() -> "_TSystemLocaleSetup":
        return Culture._TSystemLocaleSetup(os.environ.get("LC_ALL", None), os.environ.get("LANGUAGE", None))

    @staticmethod
    def __set_system_locale_setup(system_locale_setup: "_TSystemLocaleSetup") -> None:
        Culture.__set_env__var("LC_ALL", system_locale_setup.LC_ALL)
        Culture.__set_env__var("LANGUAGE", system_locale_setup.LANGUAGE)
        locale.setlocale(locale.LC_ALL, system_locale_setup.LC_ALL or "")

    @staticmethod
    def __set_env__var(key: str, value: str|None) -> None:
        if value is None:
            if key in os.environ:
                os.environ.pop(key)
        else:
            os.environ[key] = value

    @dataclasses.dataclass(frozen=True)
    class _TSystemLocaleSetup:
        LC_ALL: str|None
        LANGUAGE: str|None


#: Types that can specify a particular culture. See e.g. :py:func:`culture_by_spec`.
type CultureSpecT = Culture|str|None


def current_culture() -> Culture:
    """
    Return the current culture. If there is no current culture, raise :py:class:`NoCurrentCultureError`.

    During Annize task executions, this is :py:data:`unspecified_culture` most of the time, but feature implementations
    may enter contexts for a different current culture, e.g. iterating over the project's target cultures.
    In UI contexts it is equal to :py:data:`annize_user_interaction_culture`
    """
    if stack := getattr(_culture_stack, "stack", None):
        return stack[-1][0]
    raise NoCurrentCultureError()


def tr(string_name: str, *, culture: "CultureSpecT" = None) -> str:
    """
    Return the translation for a text (by querying the registered translation providers) in the current culture or any
    other one, or raise :py:class:`TranslationUnavailableError` if no translation is available for that culture (or its
    fallbacks; see :py:attr:`Culture.fallback_cultures`).

    Instead of this function, depending on the use case, :py:meth:`TrStr.tr` might be the right choice.
    Note: Both :code:`tr` functions are to be used by Annize only. External feature packages can only use them for own
    strings if they take care to add a translation provider for them.

    :param string_name: The string name.
    :param culture: The culture.
    """
    return ProvidedTrStr(string_name).translate(culture)


class GettextTranslationProvider(TranslationProvider):
    """
    A translation provider that is backed by :code:`.mo`-files from :code:`gettext`.
    """

    def __init__(self, mo_path: "annize.fs.TInputPath", domain_name: str|None = None):
        self.__mo_path = annize.fs.Path(mo_path)
        self.__domain_name = domain_name
        self.__gettext_translations_by_code = {}

    def translate(self, string_name, *, culture):
        culture = culture_by_spec(culture)

        if not (gettext_translations := self.__gettext_translations_by_code.get(culture.full_name, None)):
            if not (domain_name := self.__domain_name):
                for sub_dir in self.__mo_path.iterdir():
                    if mo_files := list(sub_dir("LC_MESSAGES").glob("*.mo")):
                        domain_name = mo_files[0].stem
            gettext_translations = gettext.translation(domain_name, self.__mo_path, languages=[culture.full_name],
                                                       fallback=True)
            gettext_translations.add_fallback(GettextTranslationProvider._NoneTranslations())
            self.__gettext_translations_by_code[culture.full_name] = gettext_translations

        return gettext_translations.gettext(string_name)

    class _NoneTranslations(gettext.NullTranslations):

        def __getattribute__(self, name: str):
            return lambda *_, **__: None


class ProvidedTrStr(TrStr):
    """
    Representation for a translatable text backed by the translations providers.
    """

    def __init__(self, string_name: str):
        """
        Do not use directly. See :py:meth:`tr`.

        :param string_name: The string name.
        """
        super().__init__()
        self.__string_name = string_name

    @property
    def string_name(self):
        return self.__string_name

    def _translation_for_culture(self, culture):
        culture = culture_by_spec(culture)
        for provider in _translation_providers():
            result = provider.translate(self.__string_name, culture=culture)
            if result is not None:
                return result
        return None


#: The last resort culture. In some internal places, this is used as the final fallback if the specified culture (incl.
#: its fallbacks) is not available.
_last_resort_culture = Culture.from_iso_639_1_lang_code("en", "US")


#: The 'unspecified' culture.
#:
#: To be taken by default whenever no particular culture is specified, e.g. regarding projects that do not declare any
#: project cultures at all. It is also the :py:func:`current_culture` during Annize task executions, unless a feature
#: implementation explicitly enters a context for another current culture (e.g. iterating over all project cultures).
#:
#: In translation operations, the unspecified culture will fall back to US English (which falls back to 'regionless'
#: English).
#:
#: Also, any translation operation that takes fallbacks into account (i.e. all that should regularly be used by external
#: code) will finally fall back to the unspecified culture as the last resort.
unspecified_culture = Culture(english_lang_name="Unspecified", iso_639_1_language_code="", region_code=None,
                              fallback_cultures=(_last_resort_culture,))


def culture_by_spec(culture: "CultureSpecT") -> Culture:
    """
    Return a culture for a given culture spec (i.e. a culture, a string representing one or :code:`None`).

    This is a no-op for a culture, return the current culture for :code:`None` or uses
    :py:meth:`Culture.from_iso_639_1_lang_code` for a string (after maybe splitting it into the language code and
    the region code). For an empty string, this is the :py:data:`unspecified_culture`.

    :param culture: The culture spec.
    """
    if culture is None:
        return current_culture()

    if culture == "":
        return unspecified_culture

    if isinstance(culture, str):
        culture_parts = culture.replace("-", "_").split("_")
        if len(culture_parts) == 1:
            iso_639_1_lang_code, region_code = culture_parts[0], None
        elif len(culture_parts) == 2:
            iso_639_1_lang_code, region_code = culture_parts
        else:
            raise ValueError(f"invalid culture string {culture!r}")
        culture = Culture.from_iso_639_1_lang_code(iso_639_1_lang_code, region_code)

    return culture


def friendly_join_string_list(texts: t.Iterable[TrStrOrStr]) -> TrStr:
    """
    Return a translatable string for a list of texts. They usually get concatenated with :code:`", "` between, but with
    something like :code:`" and "` as the last separator; like :code:`"foo, bar and baz"`.

    :param texts: The input texts.
    """
    trstr_list = [trstr(text) for text in texts]
    class ATrStr(TrStr):
        def _translation_for_culture(self, culture):
            and_str = tr("an_And")
            text_list = [text._translation_for_culture(culture) for text in trstr_list]
            return ", ".join(text_list[:-1]) + (f" {and_str} " if len(text_list) > 1 else "") + text_list[-1]
    return ATrStr()


class NoCurrentCultureError(TypeError):
    """
    Error that occurs when the current culture was requested when there is no current culture.
    """

    def __init__(self):
        super().__init__("there is no current Annize i18n culture")


class TranslationUnavailableError(TypeError):
    """
    Error that occurs when a translatable text was asked for translation to a language where no translation is
    available for.
    """

    def __init__(self, text: TrStr, language: str):
        super().__init__(f"there is no translation for {text!r} to language {language!r}")


_TRANSLATION_PROVIDERS__NAME = f"__{hallyd.lang.unique_id()}"


_global_translation_providers = []


_culture_stack = threading.local()


def _translation_providers() -> t.Sequence[TranslationProvider]:
    """
    Return all translation providers (ordered ascending by their priority).

    See also :py:func:`add_translation_provider`.
    """
    return tuple(_[0] for _ in sorted((_ for providers_list in _current_translation_providers_lists()
                                       for _ in providers_list), key=lambda _: _[1]))


def _current_translation_providers_lists():
    lists = []

    try:
        lists.append(annize.flow.run_context.object_by_name(_TRANSLATION_PROVIDERS__NAME, [],
                                                            create_nonexistent=True))
    except annize.flow.run_context.OutOfContextError:
        pass

    lists.append(_global_translation_providers)
    return lists


def _annize_user_interaction_culture() -> Culture:
    user_culture_specs = []
    for env_var_name in ("LC_ALL", "LANGUAGE", "LC_MESSAGES", "LANG"):
        for user_culture_spec_raw in os.environ.get(env_var_name, "").split(":"):
            if user_culture_spec_raw:
                user_culture_spec_raw = user_culture_spec_raw.split(".")[0]
                user_culture_spec_tuple = user_culture_spec_raw.split("_")
                if len(user_culture_spec_tuple) == 1:
                    user_culture_spec_tuple.append(None)
                user_culture_specs.append(tuple(user_culture_spec_tuple))
    user_culture_specs.append((_last_resort_culture.iso_639_1_language_code, _last_resort_culture.region_code))

    return Culture.from_iso_639_1_lang_code(
        user_culture_specs[0][0], user_culture_specs[0][1],
        fallback_cultures=[Culture.from_iso_639_1_lang_code(user_culture_lang_code, user_culture_lang_subcode)
                           for user_culture_lang_code, user_culture_lang_subcode in user_culture_specs[1:]])


class _FixedTrStr(TrStr):

    def __init__(self, text: str):
        self.__text = text

    def _translation_for_culture(self, culture):
        return self.__text


class _FormatedTrStr(TrStr):

    def __init__(self, original_trstr: TrStr, args, kwargs):
        super().__init__()
        self.__original_trstr = original_trstr
        self.__args = args
        self.__kwargs = kwargs

    def _translation_for_culture(self, culture):
        original_str = self.__original_trstr._translation_for_culture(culture)
        return None if original_str is None else original_str.format(*self.__args, **self.__kwargs)


#: The culture for interaction with the user.
#: During project execution, this is potentially not the same as the :py:func:`current_culture`.
annize_user_interaction_culture = _annize_user_interaction_culture()


add_translation_provider(GettextTranslationProvider(annize.asset.data.mo_dir), priority=100_000)
