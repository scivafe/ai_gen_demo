"""
Build script that:
1. Compiles services/*.py files to .so using Cython
2. Creates a dist/ directory just with the compiled .so and the others .py files
"""

import logging
import shutil
from glob import glob
from pathlib import Path

from Cython.Build import cythonize
from setuptools import Distribution

SRC_DIR = Path("src")


def compile_services() -> None:
    """Compile all src/**/services/*.py files using Cython."""

    # List comprehension that finds every *.py in a services folder except for the __init__
    service_files = [
        f
        for f in glob(f"{SRC_DIR}/**/services/*.py", recursive=True)
        if "__init__" not in f
    ]

    if not service_files:
        logging.getLogger("uvicorn").warning("No service files to compile")
        return

    print(f"Compiling {len(service_files)} service files with Cython...")

    ext_modules = cythonize(
        service_files,
        compiler_directives={
            "language_level": "3",
            "emit_code_comments": False,
            "boundscheck": False,
            "wraparound": False,
        },
    )

    # Hide internal symbols in .so files to hinder reverse engineering
    for ext in ext_modules:
        ext.extra_compile_args = ["-fvisibility=hidden"]

    dist = Distribution({"ext_modules": ext_modules})
    dist.parse_config_files()

    # Build .so files alongside the .py files
    cmd = dist.get_command_obj("build_ext")
    cmd.ensure_finalized()
    cmd.inplace = True
    cmd.run()

    print("Cython compilation complete")


def build_dist() -> None:
    """Create dist/ directory with compiled .so and necessary .py files."""
    dist_dir = Path("dist")
    # Sensible folders
    exclude_dirs = {".git", "src", "scripts", "dist"}

    # Clean and recreate dist/
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()

    # Copy root .py files (outside src/)
    for py_file in glob("*.py"):
        shutil.copy(py_file, dist_dir)

    # Copy src/ directory structure
    dest_src = dist_dir / "src"
    dest_src.mkdir(parents=True, exist_ok=True)

    for src_file in SRC_DIR.rglob("*"):
        if src_file.is_dir():
            continue

        rel_path = src_file.relative_to(SRC_DIR)
        dest_file = dest_src / rel_path

        # Skip .c files and __pycache__
        if src_file.suffix == ".c" or "__pycache__" in src_file.parts:
            continue

        # Handle .py files
        if src_file.suffix == ".py":
            # Always copy __init__.py
            if src_file.name == "__init__.py":
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src_file, dest_file)
            # Copy .py files that are NOT in services/
            elif "services" not in src_file.parts:
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src_file, dest_file)
            # Skip services/*.py (they are compiled to .so)
            continue

        # Copy everything else (.so files, etc.)
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src_file, dest_file)

    # Process other root directories (excluding src and excluded dirs)
    for item in Path(".").iterdir():
        if not item.is_dir():
            continue
        if item.name in exclude_dirs or item.name.startswith("."):
            continue

        dest = dist_dir / item.name
        dest.mkdir(parents=True, exist_ok=True)

        for src_file in item.rglob("*"):
            if src_file.is_dir():
                continue

            rel_path = src_file.relative_to(item)
            dest_file = dest / rel_path

            if src_file.suffix == ".c" or "__pycache__" in src_file.parts:
                continue

            if src_file.suffix == ".py":
                if src_file.name == "__init__.py":
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(src_file, dest_file)
                elif "services" not in src_file.parts:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(src_file, dest_file)
                continue

            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src_file, dest_file)

    print("dist/ created successfully")
    print("Contents:")
    for f in sorted(dist_dir.rglob("*")):
        if f.is_file():
            print(f"  {f.relative_to(dist_dir)}")


def main() -> None:
    compile_services()
    build_dist()

    # Cleanup compiler artifacts for every subfolder
    for build_dir in [Path("build"), SRC_DIR / "build"]:
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print(f"Cleaned up {build_dir}/ directory")


if __name__ == "__main__":
    main()
