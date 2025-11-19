from __future__ import annotations

import pytest

import os, tempfile
from pathlib import Path

from baseprinter import cli
from baseprinter.convert import baseprint_from_pandoc_inputs


BASEPRINT_CASE_DIR = Path(__file__).parent / "cases" / "baseprint"
BASEPRINT_CASES = os.listdir(BASEPRINT_CASE_DIR)


def _run(args) -> int:
    if isinstance(args, str):
        args = args.split()
    return cli.main(args)


@pytest.mark.parametrize("case", BASEPRINT_CASES)
def test_baseprint_output(case):
    expect_xml = BASEPRINT_CASE_DIR / case / "expect/article.xml"
    src_dir = BASEPRINT_CASE_DIR / case / "src"
    src_files = os.listdir(src_dir)
    assert len(src_files), f"Source files missing from {src_dir}"
    if len(src_files) == 1:
        args = src_files[0]
    else:
        args = "-d pandocin.yaml"
    os.chdir(src_dir)
    with tempfile.TemporaryDirectory() as tmp:
        assert 0 == _run(f"{args} -b {tmp}/baseprint")
        got = Path(f"{tmp}/baseprint/article.xml").read_text()
    assert got == expect_xml.read_text()


@pytest.mark.parametrize("case", BASEPRINT_CASES)
def test_no_issue(case):
    src_dir = BASEPRINT_CASE_DIR / case / "src"
    src_files = os.listdir(src_dir)
    assert len(src_files), f"Source files missing from {src_dir}"
    os.chdir(src_dir)
    if len(src_files) == 1:
        article = baseprint_from_pandoc_inputs(src_files, [])
    else:
        article = baseprint_from_pandoc_inputs([], ["pandocin.yaml"])
    issues = list(article.issues)
    assert not issues
