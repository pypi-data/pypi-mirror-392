from __future__ import annotations

import io, json, sys
from collections.abc import Iterable, MutableSequence
from dataclasses import dataclass
from pathlib import Path
from subprocess import PIPE, run
from typing import Protocol, TypeAlias, cast
from warnings import warn

import panflute as pf

from epijats import dom
from epijats import (
    BiblioRefPool,
    FormatCondition,
    FormatIssue,
    SimpleFormatCondition,
    ref_list_from_csljson,
)

from . import common
from .common import (
    InlineContentConverter,
    MinitextElementConverter,
    Sink,
    UnsupportedLocation,
)
from .metadata import convert_metadata


JsonData: TypeAlias = (
    None | str | int | float | list['JsonData'] | dict[str, 'JsonData']
)


class IcaElement(Protocol):
    identifier: str
    classes: list[str]
    attributes: dict[str, str]


@dataclass(frozen=True)
class UnsupportedPandocType(FormatCondition):
    """Unsupported Pandoc type"""

    tag: str

    def __str__(self) -> str:
        return f"{self.__doc__} '{self.tag}'"

    @property
    def names(self) -> tuple[str, ...]:
        return (type(self).__name__, self.tag)

    @staticmethod
    def issue(elem: pf.Element) -> FormatIssue:
        return FormatIssue(UnsupportedPandocType(elem.tag))


class UnsupportedPandocFeature(SimpleFormatCondition):
    """Unsupported Pandoc feature"""


class InvalidExternalUrl(SimpleFormatCondition):
    """Invalid external URL"""


class MissingContent(SimpleFormatCondition):
    """Missing content"""


def check_no_ica(src: IcaElement, out: Sink[FormatIssue]) -> None:
    if src.identifier:
        out(UnsupportedPandocFeature.issue("identifier"))
    if src.classes:
        out(UnsupportedPandocFeature.issue("class"))
    if src.attributes:
        out(UnsupportedPandocFeature.issue("attributes"))


class Converter(InlineContentConverter):
    def __init__(self, biblio: BiblioRefPool | None) -> None:
        self.biblio = biblio
        self._minitext = MinitextElementConverter(self)

    def link(self, link: pf.Link, out: dom.MixedSink) -> None:
        sub: dom.MixedParent
        if link.url.startswith("#"):
            sub = dom.CrossReference(link.url[1:])
        elif link.url.startswith("https:") or link.url.startswith("http:"):
            sub = dom.ExternalHyperlink(link.url)
        else:
            out(InvalidExternalUrl.issue(link.url))
        self.convert_content(link.content, sub.append)
        out(sub)

    def list(
        self,
        src: pf.BulletList | pf.OrderedList,
        out: Sink[dom.Element],
        *,
        ordered: bool,
    ) -> None:
        oul = dom.List(ordered=ordered)
        for item in src.content:
            li = dom.ListItem()
            self.nonsection_blocks(item.content, li.append)
            oul.append(li)
        out(oul)

    def def_list(self, src: pf.DefinitionList, out: Sink[dom.Element]) -> None:
        dl = dom.DList()
        for src_item in src.content:
            dt = dom.DTerm()
            self.convert_content(src_item.term, dt.append)
            di = dom.DItem(dt)
            for src_definition in src_item.definitions:
                dd = dom.DDefinition()
                self.nonsection_blocks(src_definition.content, dd.append)
                di.definitions.append(dd)
            dl.append(di)
        out(dl)

    def cite(self, cite: pf.Cite, out: dom.MixedSink) -> None:
        if not self.biblio:
            out(MissingContent.issue("bibliography for citations"))
        else:
            cite_tuple = dom.CitationTuple()
            for pd_cite in cite.citations:
                bp_cite = self.biblio.cite(pd_cite.id)
                if bp_cite:
                    cite_tuple.append(bp_cite)
                else:
                    msg = f"Reference '{pd_cite.id}' not found in bibliography"
                    out(MissingContent.issue(msg))
            if len(cite_tuple):
                out(cite_tuple)

    def line_block(self, src: pf.LineBlock, out: dom.ArraySink) -> None:
        lines = list(src.content)
        if lines:
            div = dom.MarkupBlock()
            line = lines.pop(0)
            self.convert_content(line.content, div.append)
            for line in lines:
                div.append(dom.LineBreak())
                div.append("\n")
                self.convert_content(line.content, div.append)
            out(div)

    def table_cells(
        self,
        src: Iterable[pf.TableCell],
        out: Sink[dom.TableCell | FormatIssue],
        *,
        header: bool,
    ) -> None:
        for src_cell in src:
            check_no_ica(src_cell, out)
            out_cell = dom.TableCell(header=header)
            if src_cell.alignment != 'AlignDefault':
                out(UnsupportedPandocFeature.issue(src_cell.alignment))
            if src_cell.rowspan != 1:
                out(UnsupportedPandocFeature.issue("Table cell rowspan"))
            if src_cell.colspan != 1:
                out(UnsupportedPandocFeature.issue("Table cell colspan"))
            self.nonsection_blocks(src_cell.content, out_cell.append)
            out(out_cell)

    def table_rows(
        self,
        src: Iterable[pf.TableRow],
        out: Sink[dom.TableRow | FormatIssue],
        *,
        header: bool,
    ) -> None:
        for src_row in src:
            check_no_ica(src_row, out)
            out_row = dom.TableRow()
            self.table_cells(src_row.content, out_row.append, header=header)
            out(out_row)

    def table(self, src: pf.Table, out: dom.ArraySink) -> None:
        check_no_ica(src, out)
        if src.caption:
            if src.caption.content:
                out(UnsupportedPandocFeature.issue("Table caption"))
            if src.caption.short_caption:
                out(UnsupportedPandocFeature.issue("Table short caption"))
        if any(x != ('AlignDefault', 'ColWidthDefault') for x in src.colspec):
            out(UnsupportedPandocFeature.issue("Table colspec"))
        out_table = dom.Table()
        if src.head:
            check_no_ica(src.head, out)
            out_head = dom.TableHead()
            self.table_rows(src.head.content, out_head.append, header=True)
            out_table.head = out_head
        for src_body in src.content:
            check_no_ica(src_body, out)
            if src_body.row_head_columns:
                out(UnsupportedPandocFeature.issue("Row head columns"))
            if src_body.head:
                out(UnsupportedPandocFeature.issue("Body head rows"))
            out_body = dom.TableBody()
            self.table_rows(src_body.content, out_body.append, header=False)
            out_table.bodies.append(out_body)
        if src.foot:
            check_no_ica(src.foot, out)
            out_foot = dom.TableFoot()
            self.table_rows(src.foot.content, out_foot.append, header=False)
            out_table.foot = out_foot
        out(out_table)

    def inline(self, src: pf.Inline, out: dom.MixedSink) -> None:
        if self._minitext.convert_element(src, out):
            return
        elif isinstance(src, pf.LineBreak):
            out(dom.LineBreak())
        elif isinstance(src, pf.Link):
            self.link(src, out)
        elif isinstance(src, pf.Code):
            out(dom.MarkupInline('tt', src.text))
        elif isinstance(src, pf.Cite):
            self.cite(src, out)
        else:
            out(UnsupportedPandocType.issue(src))

    def convert_content(
        self, content: Iterable[pf.Inline], dest: dom.MixedSink
    ) -> None:
        todo = list(content)
        behind = todo.pop(0) if len(todo) else None
        for ahead in todo:
            if isinstance(behind, (pf.Space, pf.SoftBreak)):
                if isinstance(ahead, pf.Cite):
                    behind = None
            if behind is not None:
                self.inline(behind, dest)
            behind = ahead
        if behind is not None:
            self.inline(behind, dest)

    def block(self, block: pf.Block, sink: dom.ArraySink) -> bool:
        if isinstance(block, pf.Para):
            para = dom.Paragraph()
            self.convert_content(block.content, para.append)
            sink(para)
        elif isinstance(block, pf.Plain):
            tb = dom.MarkupBlock()
            self.convert_content(block.content, tb.append)
            sink(tb)
        elif isinstance(block, pf.BlockQuote):
            bq = dom.BlockQuote()
            self.nonsection_blocks(block.content, bq.append)
            sink(bq)
        elif isinstance(block, pf.CodeBlock):
            pre = dom.Preformat()
            pre.append(block.text)
            sink(pre)
        elif isinstance(block, pf.RawBlock):
            pass
        elif isinstance(block, pf.BulletList):
            self.list(block, sink, ordered=False)
        elif isinstance(block, pf.OrderedList):
            self.list(block, sink, ordered=True)
        elif isinstance(block, pf.DefinitionList):
            self.def_list(block, sink)
        elif isinstance(block, pf.LineBlock):
            self.line_block(block, sink)
        elif isinstance(block, pf.Table):
            self.table(block, sink)
        else:
            return False
        return True

    def nonsection_blocks(
        self, content: Iterable[pf.Block], out: dom.ArraySink
    ) -> None:
        for block in content:
            if not self.block(block, out):
                if isinstance(block, pf.Header):
                    out(UnsupportedLocation.issue("Header in non-section content"))
                else:
                    out(UnsupportedPandocType.issue(block))

    def presection_content(
        self, src: MutableSequence[pf.Block], out: dom.ArraySink
    ) -> pf.Header | None:
        while src:
            block = src.pop(0)
            if isinstance(block, pf.Header):
                return block
            if not self.block(block, out):
                out(UnsupportedPandocType.issue(block))
        return None

    def section_content(
        self, level: int, content: MutableSequence[pf.Block], dest: dom.ProtoSection
    ) -> pf.Header | None:
        header = self.presection_content(content, dest.presection.append)
        while header and header.level >= level:
            title = dom.MutableMixedContent()
            self.convert_content(header.content, title.append)
            subsection = dom.Section(header.identifier or None, title)
            header = self.section_content(header.level + 1, content, subsection)
            dest.subsections.append(subsection)
        return header


def convert_bibliography(metalist: pf.MetaValue | None) -> BiblioRefPool | None:
    if metalist is None:
        return None
    if not isinstance(metalist, pf.MetaList):
        warn("Expecting bibliography to be of pandoc MetaList type")
        return None
    sources = []
    for s in metalist.content:
        if isinstance(s, pf.MetaString):
            sources.append(Path(s.text))
        elif isinstance(s, pf.MetaInlines):
            sources.append(Path(common.convert_string(s.content)))
        else:
            warn(
                "Expecting bibliography entries to be of "
                "pandoc MetaString or MetaInlines types"
            )
    ref_list = ref_list_from_csljson(csljson_from_bibliography(sources))
    return BiblioRefPool(ref_list.references) if ref_list else None


def baseprint_from_pandoc_ast(doc: pf.Doc) -> dom.Article:
    ret = dom.Article()
    convert_metadata(doc.metadata, ret)
    biblio = convert_bibliography(doc.metadata.content.get('bibliography'))
    convert = Converter(biblio)
    abstract = doc.metadata.content.get('abstract')
    if isinstance(abstract, pf.MetaBlocks):
        ret.abstract = dom.Abstract()
        convert.nonsection_blocks(abstract.content, ret.abstract.content.append)
    convert.section_content(1, doc.content, ret.body)
    if biblio and len(biblio.used):
        ret.ref_list = dom.BiblioRefList(biblio.used)
    return ret


def csljson_from_bibliography(sources: Iterable[Path]) -> JsonData:
    args = [str(s) for s in sources]
    if not args:
        warn("Expecting pandoc to find bibliography files")
        return []
    cmd = ["pandoc", "--to", "csljson"] + args
    result = run(cmd, stdout=PIPE, stderr=sys.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError("Error with command: " + " ".join(cmd))
    try:
        return cast(JsonData, json.loads(result.stdout))
    except json.JSONDecodeError as ex:
        raise RuntimeError(f"Pandoc command returned invalid JSON: {ex}")


def baseprint_from_pandoc_inputs(
    sources: Iterable[Path], defaults: Iterable[Path]
) -> dom.Article:
    cmd = ["pandoc"]
    cmd += [str(s) for s in sources]
    for d in defaults:
        cmd += ["-d", str(d)]
    cmd += ["--to", "json"]
    result = run(cmd, stdout=PIPE, stderr=sys.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError("Error with command: " + " ".join(cmd))
    try:
        doc = pf.load(io.StringIO(result.stdout))
        return baseprint_from_pandoc_ast(doc)
    except json.JSONDecodeError as ex:
        raise RuntimeError(f"Pandoc command returned invalid JSON: {ex}")
