import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import requests

PYPROJECT_TOML = Path("pyproject.toml")


def in_venv():
    return sys.prefix != sys.base_prefix


def get_latest_versions() -> dict[str, str]:
    latest_versions = {}
    pyproject = tomllib.loads(PYPROJECT_TOML.read_text("UTF-8"))
    for dependency in pyproject["project"]["dependencies"]:
        name = dependency.split(maxsplit=2)[0]
        project = requests.get(f"https://pypi.org/pypi/{name}/json").json()
        version = project["info"]["version"]
        latest_versions[name] = version
    return latest_versions


def bump_dependencies():
    latest_versions = get_latest_versions()
    original_pyproject_content = pyproject_content = PYPROJECT_TOML.read_text(
        encoding="UTF-8"
    )
    for project_name, latest_version in latest_versions.items():
        pyproject_content = re.sub(
            f'"{project_name} >= .*",',
            f'"{project_name} >= {latest_version}",',
            pyproject_content,
        )
    if original_pyproject_content == pyproject_content:
        raise RuntimeError("Nothing changed")
    PYPROJECT_TOML.write_text(pyproject_content)


def bump_version():
    pyproject_content = PYPROJECT_TOML.read_text("UTF-8")
    pyproject = tomllib.loads(pyproject_content)
    major, minor = pyproject["project"]["version"].split(".")
    major = int(major)
    minor = int(minor)
    new_version = f"{major}.{minor+1}"
    pyproject_content = re.sub(
        '^version = "[0-9.]+"',
        f'version = "{new_version}"',
        pyproject_content,
        flags=re.MULTILINE,
    )
    PYPROJECT_TOML.write_text(pyproject_content)
    return new_version


def run(args):
    while True:
        char = input(
            f"Hit enter to run `{" ".join(args)}`. Or type 's' to get a shell."
        )
        if char == "s":
            print("Starting a shell for you. Get back to this script by typing `exit`")
            subprocess.run(os.environ["SHELL"])
        if char == "":
            break
    subprocess.run(args)


def main():
    if not in_venv():
        print("Please run this in a venv.")
    print("You can interrupt the process anytime with C-c")
    bump_dependencies()
    new_version = bump_version()
    run(["git", "add", "-p"])
    run(["git", "commit", "-m", "Bump dependencies."])
    run(["git", "tag", new_version])
    run(["git", "push"])
    run(["git", "push", "--tags"])
    run(["pip", "install", "twine", "build"])
    run(["rm", "-fr", "build", "dist"])
    run(["python", "-m", "build"])
    run(
        ["python", "-m", "twine", "upload"]
        + [str(file) for file in Path("dist").glob("*")]
    )


if __name__ == "__main__":
    main()
