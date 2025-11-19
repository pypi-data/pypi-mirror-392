from __future__ import annotations

import pytest

import json, os, tempfile, tomllib
from dataclasses import dataclass
from pathlib import Path
from subprocess import run
from typing import Any

from bs4 import BeautifulSoup

from baseprinter import __main__


PREVIEW_CASE = Path(__file__).parent / "cases" / "preview"


def load_chdir(case: str) -> dict[str, Any]:
    os.chdir(PREVIEW_CASE / case / "src")
    with open(PREVIEW_CASE / case / "case.toml", "rb") as f:
        return tomllib.load(f)


def _run(args) -> int:
    if isinstance(args, str):
        args = args.split()
    return __main__.main(args)


@dataclass
class PdfInfo:
    num_pages: int
    title: str | None

    @staticmethod
    def loadf(path: Path | str) -> PdfInfo:
        args = ["exiftool", "-j", "-Title", "-PageCount", str(path)]
        res = run(args, capture_output=True)
        assert 0 == res.returncode
        d = json.loads(res.stdout)[0]
        return PdfInfo(d['PageCount'], d.get('Title'))


@dataclass
class Output:
    html: BeautifulSoup
    pdf: PdfInfo | None = None

    @staticmethod
    def get(args: str, skip_pdf: bool) -> Output:
        with tempfile.TemporaryDirectory() as tmp:
            cmdline = f"{args} -o {tmp}/preview"
            if skip_pdf:
                cmdline += " --skip-pdf"
        assert 0 == _run(cmdline)
        with open(f"{tmp}/preview/index.html") as preview_html:
            ret = Output(BeautifulSoup(preview_html, "xml"))
            if not skip_pdf:
                ret.pdf = PdfInfo.loadf(f"{tmp}/preview/article.pdf")
        return ret


def check_html(expected, html):
    if title := expected.get('title'):
        assert title == html.title.string
        assert title == html.h1.string
    if abstract := expected.get('abstract'):
        assert abstract.strip() == html.p.string.strip()


@pytest.mark.slow
@pytest.mark.parametrize("case", os.listdir(PREVIEW_CASE))
def test_with_pdf(case):
    load = load_chdir(case)
    out = Output.get(load['args'], skip_pdf=False)
    expected = load['expected']
    check_html(expected, out.html)
    assert expected['num_pages'] == out.pdf.num_pages
    if title := expected.get('title'):
        assert title == out.pdf.title


@pytest.mark.parametrize("case", os.listdir(PREVIEW_CASE))
def test_without_pdf(case):
    load = load_chdir(case)
    out = Output.get(load['args'], skip_pdf=True)
    check_html(load['expected'], out.html)
