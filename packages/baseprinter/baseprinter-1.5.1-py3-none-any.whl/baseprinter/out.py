from __future__ import annotations

import os, shutil, subprocess
from importlib import resources
from pathlib import Path
from typing import Any, Iterable, TYPE_CHECKING

import jinja2

if TYPE_CHECKING:
    from epijats import FormatIssue
    from epijats import dom


class WebPageGenerator:
    jenv: jinja2.Environment | None = None

    @staticmethod
    def render(
        tmpl_subpath: Path | str,
        dest: Path,
        ctx: dict[str, Any] = dict(),
    ) -> None:
        if WebPageGenerator.jenv is None:
            loader = jinja2.PackageLoader(__name__, "templates")
            WebPageGenerator.jenv = jinja2.Environment(
                loader=loader,
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
                extensions=["jinja2.ext.do"],
            )
        tmpl = WebPageGenerator.jenv.get_template(str(tmpl_subpath))
        tmpl.stream(**ctx).dump(str(dest), "utf-8")


def run_pandoc(args: Iterable[Any], echo: bool = True) -> int:
    cmd = ["pandoc"] + [str(a) for a in args]
    if echo:
        print(" ".join(cmd))
    result = subprocess.run(cmd)
    return result.returncode


def make_jats_xml(
    target: Path, sources: Iterable[Path], defaults: Iterable[Path]
) -> int:
    rp = resources.files(__package__).joinpath("pandoc")
    bd_path = rp.joinpath("baseprint.yaml")
    csl_path = rp.joinpath("citation-hack.csl")
    xml_path = rp.joinpath("baseprint-jats.xml")
    with (
        resources.as_file(bd_path) as bd,
        resources.as_file(csl_path) as csl,
        resources.as_file(xml_path) as xml,
    ):
        os.makedirs(target.parent, exist_ok=True)
        opts = ["-d", bd, "--csl", csl, "--template", xml, "-o", target]
        for d in defaults:
            opts += ["-d", d]
        return run_pandoc(opts + list(sources))


class IssuesPage:
    def __init__(self, issues: Iterable[FormatIssue]):
        self.issues = list(issues)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @staticmethod
    def issue_facade(src: FormatIssue) -> dict[str, Any]:
        return {
            'condition': src.condition.as_pod(),
            'str': str(src),
        }

    def write(self, dest_dir: Path) -> None:
        os.makedirs(dest_dir, exist_ok=True)
        ctx = dict(issues=[self.issue_facade(i) for i in self.issues])
        WebPageGenerator.render("issues.html.jinja", dest_dir / "index.html", ctx)


class PandocIssuesPage(IssuesPage):
    def __init__(self, pandoc_xml: Path, issues: Iterable[FormatIssue]):
        super().__init__(issues)
        self.pandoc_xml = pandoc_xml

    def write(self, dest_dir: Path) -> None:
        super().write(dest_dir)
        shutil.copy(self.pandoc_xml, dest_dir / "pandoc.xml")


def make_preview(
    src: dom.Article, baseprint_dest: Path, outdir: Path | None, skip_pdf: bool
) -> None:
    import epijats

    if not outdir:
        epijats.write_baseprint(src, baseprint_dest)
    else:
        config = epijats.EprinterConfig(dsi_domain="perm.pub")
        config.show_pdf_icon = not skip_pdf
        config.header_banner_msg = "WORKING DRAFT"
        epijats.eprint_article(
            config, src, baseprint_dest, outdir, issues_page=IssuesPage(src.issues)
        )


def make_baseprint(
    pandoc_xml: Path, restyle_dest: Path, outdir: Path | None, skip_pdf: bool
) -> bool:
    import epijats

    issues: list[FormatIssue] = []
    ok = epijats.restyle_xml(pandoc_xml, restyle_dest, issues.append)
    if outdir:
        issues_page = PandocIssuesPage(pandoc_xml, issues)
        if ok:
            config = epijats.EprinterConfig(dsi_domain="perm.pub")
            config.show_pdf_icon = not skip_pdf
            config.header_banner_msg = "WORKING DRAFT"
            epijats.eprint_dir(config, restyle_dest, outdir, issues_page=issues_page)
        else:
            issues_page.write(outdir)
    return ok
