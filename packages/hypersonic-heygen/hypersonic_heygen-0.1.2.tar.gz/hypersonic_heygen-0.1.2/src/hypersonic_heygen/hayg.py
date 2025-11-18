import argparse
from pathlib import Path
import shutil
import sys

try:
    # Python 3.9+
    from importlib.resources import files as ir_files
except ImportError:
    # Python 3.8 fallback
    from importlib_resources import files as ir_files  # type: ignore


DEFAULT_OUT = "HeyGen.ipynb"
TEMPLATE_REL = "templates/HeyGen.ipynb"


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hayg",
        description="Generate the HeyGen notebook from a bundled educational template.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=DEFAULT_OUT,
        help=f"Output notebook filename (default: {DEFAULT_OUT})",
    )
    return parser


def copy_template(out_path: Path) -> None:
    """
    Locate the packaged template notebook and copy it to out_path.
    """
    tpl = ir_files("hypersonic_heygen").joinpath(TEMPLATE_REL)
    if not tpl.is_file():
        raise FileNotFoundError(
            "Bundled template not found. Ensure 'templates/HeyGen.ipynb' "
            "is included as package data."
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(str(tpl), str(out_path))


def main() -> None:
    args = build_argparser().parse_args()
    out = Path(args.output)

    try:
        copy_template(out)
    except Exception as exc:  # noqa: BLE001
        print(f"[hayg] Failed to create notebook: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[hayg] Notebook created: {out.resolve()}")


if __name__ == "__main__":
    main()
