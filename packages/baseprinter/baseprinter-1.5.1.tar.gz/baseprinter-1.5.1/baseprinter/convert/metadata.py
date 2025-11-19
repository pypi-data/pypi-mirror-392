from __future__ import annotations

from warnings import warn

import panflute as pf

from epijats import dom

from .common import Sink, convert_minitext, get_meta_map_str


def convert_title(meta: pf.MetaValue | None) -> dom.MutableMixedContent | None:
    if meta is None:
        return None
    if not isinstance(meta, (pf.MetaString, pf.MetaInlines)):
        warn("Expecting title to be of pandoc MetaString or MetaInlines type")
        return None
    ret = dom.MutableMixedContent()
    convert_minitext(meta, ret.append)
    if ret.blank():
        warn("Title is blank")
    return ret


def orcid_from_str(s: str | None) -> dom.Orcid | None:
    if s is not None:
        try:
            return dom.Orcid.from_url(s)
        except ValueError:
            warn(f"Invalid ORCID: {s}")
    return None


def convert_author(meta: pf.MetaMap, sink: Sink[dom.Author]) -> None:
    surname = get_meta_map_str(meta, 'surname')
    givens = get_meta_map_str(meta, 'given-names')
    suffix = get_meta_map_str(meta, 'suffix')
    if surname or givens:
        name = dom.PersonName(surname, givens, suffix)
        email = get_meta_map_str(meta, 'email')
        orcid = orcid_from_str(get_meta_map_str(meta, 'orcid'))
        author = dom.Author(name, email, orcid)
        sink(author)
    else:
        warn("Expecting under 'author:' a 'surname:' key and/or 'given-names:' key")


def convert_authors(meta: pf.MetaValue | None, sink: Sink[dom.Author]) -> None:
    if meta is None:
        return
    if isinstance(meta, pf.MetaMap):
        convert_author(meta, sink)
    if isinstance(meta, pf.MetaList):
        for author in meta:
            if isinstance(author, pf.MetaMap):
                convert_author(author, sink)


def convert_link(meta: pf.MetaValue | None) -> str | None:
    if meta is None:
        return None
    link_text = ''
    if isinstance(meta, pf.MetaString):
        link_text = meta.text
    elif isinstance(meta, pf.MetaInlines):
        if inlines := list(meta.content):
            link = inlines[0]
            if len(inlines) > 1:
                warn("Expecting single URL for license reference link")
            if isinstance(link, pf.Str):
                link_text = link.text
    if link_text.startswith(('https:', 'http:')):
        return link_text
    warn("Expecting https URL value for 'link:' key under 'license:'")
    return None


def convert_license(meta: pf.MetaValue | None) -> dom.License | None:
    if meta is None:
        return None
    text = None
    link = None
    if isinstance(meta, pf.MetaMap):
        text = meta.content.get('text')
        link = meta.content.get('link')
    if not text and not link:
        warn("Expecting under 'license:' a 'link:' key and/or 'text:' key")
        return None
    lic = dom.License()
    convert_minitext(text, lic.license_p.append)
    lic.license_ref = convert_link(link) or ''
    lic.cc_license_type = dom.CcLicenseType.from_url(lic.license_ref)
    if lic.blank():
        return None
    else:
        return lic


def convert_copyright(meta: pf.MetaValue | None) -> dom.Copyright | None:
    if meta is None:
        return None
    copyright = dom.Copyright()
    if isinstance(meta, pf.MetaMap):
        convert_minitext(meta.content.get('statement'), copyright.statement.append)
    if copyright.blank():
        warn("Expecting string value for 'statement:' under 'copyright:'")
        return None
    return copyright


def convert_metadata(meta: pf.MetaMap, dest: dom.Article) -> None:
    dest.title = convert_title(meta.content.get('title'))
    convert_authors(meta.content.get('author'), dest.authors.append)
    license = convert_license(meta.content.get('license'))
    if license:
        copyright = convert_copyright(meta.content.get('copyright'))
        dest.permissions = dom.Permissions(license, copyright)
