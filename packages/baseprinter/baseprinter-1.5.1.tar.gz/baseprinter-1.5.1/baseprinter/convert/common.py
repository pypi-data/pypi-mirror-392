from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Protocol, TypeAlias, TypeVar
from warnings import warn

import panflute as pf

from epijats import dom
from epijats import (
    SimpleFormatCondition,
)


SinkableT = TypeVar('SinkableT')
Sink: TypeAlias = Callable[[SinkableT], None]


class UnsupportedLocation(SimpleFormatCondition):
    """Unsupported location for Pandoc type"""


def convert_string(content: Iterable[pf.Inline]) -> str:
    strs = []
    for inline in content:
        if isinstance(inline, (pf.Space, pf.SoftBreak)):
            strs.append(" ")
        elif isinstance(inline, pf.Str):
            strs.append(inline.text)
    return "".join(strs)


def get_meta_map_str(meta: pf.MetaMap, key: str) -> str | None:
    value = meta.get(key)
    if value is None:
        return None
    if isinstance(value, pf.MetaString):
        return value.text
    elif isinstance(value, pf.MetaInlines):
        return convert_string(value.content)
    else:
        warn(f"Expecting {key}: to have string value")
        return None


class InlineElementConverter(Protocol):
    def convert_element(self, src: pf.Inline, out: dom.MixedSink, /) -> bool: ...


class InlineContentConverter(Protocol):
    def convert_content(
        self, src: Iterable[pf.Inline], out: dom.MixedSink, /
    ) -> None: ...


def convert_markup(
    tag: str,
    content: Iterable[pf.Inline],
    converter: InlineContentConverter,
    out: dom.MixedSink,
) -> None:
    sub = dom.MarkupInline(tag)
    converter.convert_content(content, sub.append)
    out(sub)


class MinitextElementConverter(InlineElementConverter):
    def __init__(self, content: InlineContentConverter):
        self.content = content

    def convert_element(self, src: pf.Inline, out: dom.MixedSink) -> bool:
        if isinstance(src, pf.Space):
            out(" ")
        elif isinstance(src, pf.SoftBreak):
            out("\n")
        elif isinstance(src, pf.Str):
            out(src.text)
        elif isinstance(src, pf.Span):
            self.content.convert_content(src.content, out)
        elif isinstance(src, pf.Quoted):
            out('“' if src.quote_type == 'DoubleQuote' else "‘")
            self.content.convert_content(src.content, out)
            out('”' if src.quote_type == 'DoubleQuote' else "’")
        elif isinstance(src, pf.Strong):
            convert_markup('b', src.content, self.content, out)
        elif isinstance(src, pf.Emph):
            convert_markup('i', src.content, self.content, out)
        elif isinstance(src, pf.Subscript):
            convert_markup('sub', src.content, self.content, out)
        elif isinstance(src, pf.Superscript):
            convert_markup('sup', src.content, self.content, out)
        elif isinstance(src, pf.RawInline):
            pass
        else:
            return False
        return True


class MinitextConverter(MinitextElementConverter, InlineContentConverter):
    def __init__(self) -> None:
        super().__init__(self)

    def convert_content(self, src: Iterable[pf.Inline], out: dom.MixedSink, /) -> None:
        for inline in src:
            if not self.convert_element(inline, out):
                msg = f"This markup context does not permit: {inline}"
                out(UnsupportedLocation.issue(msg))
        return None


def convert_minitext(meta: pf.MetaValue | None, out: dom.MixedSink) -> None:
    if isinstance(meta, pf.MetaString):
        out(meta.text)
    elif isinstance(meta, pf.MetaInlines):
        MinitextConverter().convert_content(meta.content, out)
