import argparse, logging, os, shutil, sys, tempfile
from pathlib import Path
from typing import Any

from .out import make_jats_xml, make_baseprint, make_preview


def version() -> str:
    try:
        from ._version import version

        return str(version)
    except ImportError:
        return "0.0.0"


def enable_weasyprint_logging() -> bool:
    try:
        from weasyprint import LOGGER

        LOGGER.setLevel(logging.INFO)
        LOGGER.addHandler(logging.StreamHandler())
        return True
    except ImportError:
        return False


def clear_dir(dirpath: Path) -> None:
    if dirpath.exists():
        assert dirpath.is_dir()
        for entry in dirpath.iterdir():
            if entry.is_dir():
                shutil.rmtree(entry)
            else:
                os.unlink(entry)


class Args:
    infiles: list[Path]
    baseprint: Path | None
    outdir: Path | None
    skip_pdf: bool
    defaults: list[Path]

    @staticmethod
    def make_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog="baseprinter")
        parser.add_argument("--version", action="version", version=version())
        parser.add_argument("infiles", type=Path, nargs="*", help="pandoc input files")
        parser.add_argument(
            "-b", "--baseprint", type=Path, help="baseprint output directory"
        )
        parser.add_argument(
            "-o", "--outdir", type=Path, help="HTML/PDF output directory"
        )
        parser.add_argument(
            "--skip-pdf", action="store_true", help="Do not generate PDF"
        )
        parser.add_argument(
            "-d",
            "--defaults",
            type=Path,
            default=[],
            action="append",
            help="pandoc default option settings",
        )
        return parser

    def error_msg(self) -> str | None:
        if self.outdir and not self.skip_pdf:
            if not enable_weasyprint_logging():
                msg = "PDF can not be generated without weasyprint installed."
                msg += "\nUse the --skip-pdf option or install weasyprint."
                return msg
        if not (self.infiles or self.defaults):
            return "Missing input file or pandoc defaults file"
        if not (self.baseprint or self.outdir):
            msg = "Missing output directory."
            msg += "\nUse the -b (baseprint) or -o (HTML/PDF) output option."
            return msg
        if self.baseprint and self.baseprint.exists():
            if not self.baseprint.is_dir():
                return "Baseprint destination can not be a file"
            entries = [a.name for a in self.baseprint.iterdir()]
            if entries and "article.xml" not in entries:
                return "Aborting: baseprint destination contains non-baseprint content"
        return None

    def run(self) -> int:
        with tempfile.TemporaryDirectory() as tempdir:
            if self.baseprint:
                clear_dir(self.baseprint)
            else:
                self.baseprint = Path(tempdir) / "baseprint"

            if os.getenv("BASEPRINTER_JATS") != "ON":
                from .convert import baseprint_from_pandoc_inputs

                b = baseprint_from_pandoc_inputs(self.infiles, self.defaults)
                make_preview(b, self.baseprint, self.outdir, self.skip_pdf)
                return 0

            pandoc_xml = Path(tempdir) / "pandoc.xml"
            retcode = make_jats_xml(pandoc_xml, self.infiles, self.defaults)
            if retcode != 0:
                return retcode
            ok = make_baseprint(pandoc_xml, self.baseprint, self.outdir, self.skip_pdf)
            return 0 if ok else 1


def main(cmd_line_args: Any = None) -> int:
    parser = Args.make_parser()
    args = Args()
    parser.parse_args(cmd_line_args, args)
    if errmsg := args.error_msg():
        parser.print_help()
        print(errmsg, file=sys.stderr)
        return 1
    return args.run()
