# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Version numbers. See :py:class:`Version`.
"""
import abc
import functools
import re
import typing as t


@functools.total_ordering
class Version:
    """
    A version number. It has a :py:attr:`text` (and a :py:attr:`pattern`), but also its :py:attr:`segments_tuples`.
    """

    def __init__(self, *, text: str|None = None, pattern: "VersionPattern", **segment_values: t.Any):
        """
        :param text: The textual representation of the version number. If set, :py:attr:`segments_tuples` will be
                     derived from it.
        :param pattern: The version pattern behind the textual representation of the version number.
        :param segment_values: Segment values that define this version number. Well known names are :code:`"major"`,
                               :code:`"minor"` and :code:`"build"`. This is an alternative to :code:`text`. Values are
                               often of type :code:`int`.
        """
        self.__text = text
        self.__pattern = pattern
        self.__segment_values = segment_values

    def __str__(self):
        return self.text

    def __eq__(self, other):
        return isinstance(other, Version) and self.segments_tuples == other.segments_tuples

    def __hash__(self):
        return hash(self.segments_tuples)

    def __lt__(self, other):
        if self == other:
            return False
        if not isinstance(other, Version):
            return super().__lt__(other)

        self_segments_tuples = list(self.segments_tuples)
        other_segments_tuples = list(other.segments_tuples)
        while True:
            self_segments_tuple = self_segments_tuples.pop(0)
            other_segments_tuple = other_segments_tuples.pop(0)
            if self_segments_tuple[0] != other_segments_tuple[0]:
                raise ValueError(f"versions {self!r} and {other!r} are not comparable")
            if self_segments_tuple[1] == other_segments_tuple[1]:
                continue
            return self_segments_tuple[1] < other_segments_tuple[1]

    @property
    def segments_tuples(self) -> t.Sequence["_SegmentTuple"]:
        """
        This version number's segment tuples. Each tuple contains the segment name (well known ones are :code:`"major"`, 
        :code:`"minor"` and :code:`"build"`) and the value. The value is usually an :code:`int`, but it could also be a 
        :code:`str` or anything else that is comparable.

        If this version number was constructed with a :code:`text`, segment tuples are derived from it (using
        :py:attr:`pattern`). If not, segment tuples come from the :code:`segment_values` specified during construction.
        """
        if self.__text is not None:
            return self.pattern.text_to_segments_tuples(self.__text)

        result = []
        for segment in self.pattern.parts:
            for segment_name in segment.segment_names:
                if (segment_value := self.__segment_values.get(segment_name, self)) != self:
                    result.append((segment_name, segment_value))

        return tuple(result)

    @property
    def segments_values(self) -> dict[str, t.Any]:
        """
        Like :py:attr:`segments_tuples`, but as a dictionary.
        """
        return {name: value for (name, value) in self.segments_tuples}

    @property
    def text(self) -> str:
        """
        The textual representation of this version.
        """
        return self.pattern.segments_tuples_to_text(self.segments_tuples) if self.__text is None else self.__text

    @property
    def pattern(self) -> "VersionPattern":
        """
        The version pattern.
        """
        return self.__pattern


type _SegmentTuple = tuple[str, t.Any]


class VersionPattern:
    """
    A version pattern. Mostly used for translation between the textual representation and the segment tuples of a
    :py:class:`Version`.
    """

    def __init__(self, *, parts: t.Iterable["VersionPatternPart"]):
        """
        :param parts: The pattern parts.
        """
        self.__parts = tuple(parts)
        self.__outer_part = ConcatenatedVersionPatternPart(parts=self.__parts)

    @property
    def parts(self) -> t.Sequence["VersionPatternPart"]:
        """
        The pattern parts.
        """
        return self.__parts

    @property
    def segment_names(self):
        """
        The pattern segment names.
        """
        return self.__outer_part.segment_names

    def text_to_segments_tuples(self, text: str) -> t.Sequence[_SegmentTuple]:
        """
        Extract and return segment tuples from a given text.
        
        :param text: The text to extract.
        """
        match = re.fullmatch(self.__outer_part.regexp_string, text)
        if not match:
            raise ValueError(f"version string {text!r} not according to pattern")
        match_group_dict = match.groupdict()
        
        result = []
        for segment_name in self.segment_names:
            if (segment_value_str := match_group_dict.get(segment_name, None)) is not None:
                result.append((segment_name, self.__outer_part.str_to_value(segment_name, segment_value_str)))
                
        return tuple(result)

    def segments_tuples_to_text(self, segments_tuples: t.Iterable[_SegmentTuple]) -> str:
        """
        Return a textual representation for the given segment tuples.

        :param segments_tuples: The segment tuples.
        """
        return self.__outer_part.segments_tuples_to_text(tuple(segments_tuples))


class VersionPatternPart(abc.ABC):
    """
    A part of a :py:class:`VersionPattern`. This can span the entire version pattern, or just one segment of it, or
    anything between.
    """

    @property
    @abc.abstractmethod
    def segment_names(self) -> t.Sequence[str]:
        """
        Names of all segments of this pattern part.
        """

    @property
    @abc.abstractmethod
    def regexp_string(self) -> str:
        """
        Return a regexp for this pattern part.
        """

    @abc.abstractmethod
    def segments_tuples_to_text(self, segments_tuples: t.Sequence[_SegmentTuple]) -> str:
        """
        Return a textual representation for the given segment tuples.

        :param segments_tuples: The segment tuples.
        """

    @abc.abstractmethod
    def str_to_value(self, segment_name: str, s: str) -> t.Any:
        """
        Return a value of the correct type (often :code:`int`) for a given text representation of a segment.

        :param segment_name: The segment name.
        :param s: The text to convert.
        """


class NumericVersionPatternPart(VersionPatternPart):
    """
    A version pattern part that represents one numeric segment of a version number.
    """

    def __init__(self, *, name: str):
        """
        :param name: The segment name.
        """
        super().__init__()
        self.__segment_name = name

    @property
    def segment_names(self):
        return (self.__segment_name,)

    @property
    def regexp_string(self):
        return rf"(?P<{self.__segment_name}>\d+)"

    def segments_tuples_to_text(self, segments_tuples):
        for segment_name, segment_value in segments_tuples:
            if segment_name == self.__segment_name:
                return str(segment_value)
        raise ValueError(f"invalid segment tuples: {segments_tuples}")

    def str_to_value(self, segment_name, s):
        if segment_name != self.__segment_name:
            raise ValueError(f"invalid segment name: {segment_name}")
        return int(s)


class SeparatorVersionPatternPart(VersionPatternPart):
    """
    A version pattern part that represents a separator in a version number.
    """

    def __init__(self, *, text: str):
        """
        :param text: The separator text.
        """
        super().__init__()
        self.__text = text

    @property
    def segment_names(self):
        return ()

    @property
    def regexp_string(self):
        return re.escape(self.__text)

    def segments_tuples_to_text(self, segments_tuples):
        return self.__text

    def str_to_value(self, segment_name, s):
        raise RuntimeError("invalid operation")


class OptionalVersionPatternPart(VersionPatternPart):
    """
    A version pattern part that represents an optional part of a version number.
    """

    def __init__(self, *, parts: t.Iterable[VersionPatternPart]):
        """
        :param parts: The inner parts.
        """
        super().__init__()
        self.__outer_part = ConcatenatedVersionPatternPart(parts=parts)

    @property
    def segment_names(self):
        return self.__outer_part.segment_names

    @property
    def regexp_string(self):
        return f"({self.__outer_part.regexp_string})?"

    def segments_tuples_to_text(self, segments_tuples):
        return self.__outer_part.segments_tuples_to_text(segments_tuples) if segments_tuples else ""

    def str_to_value(self, segment_name, s):
        return self.__outer_part.str_to_value(segment_name, s)


class ConcatenatedVersionPatternPart(VersionPatternPart):
    """
    A version pattern part that represents the concatenation of other parts.
    """

    def __init__(self, *, parts: t.Iterable[VersionPatternPart]):
        super().__init__()
        self.__parts = tuple(parts)

    @property
    def segment_names(self):
        return tuple(segment_name for part in self.__parts for segment_name in part.segment_names)

    @property
    def regexp_string(self):
        return "".join(part.regexp_string for part in self.__parts)

    def segments_tuples_to_text(self, segments_tuples):
        return "".join(part.segments_tuples_to_text(segments_tuples) for part in self.__parts)

    def str_to_value(self, segment_name, s):
        for segment in self.__parts:
            if segment_name in segment.segment_names:
                return segment.str_to_value(segment_name, s)
        raise ValueError(f"invalid segment name: {segment_name}")
