#!/usr/bin/env python3
"""Create a new python project."""

import os
import shutil
from pathlib import Path
from typing import Annotated, Literal

import typer
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel

load_dotenv()

PACKAGE_DIR = Path(__file__).parent.absolute()
RC_DIR = PACKAGE_DIR / "templates"
COMMON_DIR = RC_DIR / "common"

__VERSION__ = "1.27.0"


def version_callback(*, value: bool) -> None:
    """Show the version and exit.

    Args:
        value: Whether to show version or not.

    Raises:
        typer.Exit: When version is requested.

    """
    if value:
        typer.echo(__VERSION__)
        raise typer.Exit()


class Project(BaseModel):
    """Pydantic model for project data."""

    project_type: Literal["py", "js", "go"] = "py"
    sub_type: Literal["vue", "uniapp"] | None = None
    project_dir: Path
    project_name: str
    version: str = "0.0.1"
    author: str = ""
    email: str = ""
    description: str = ""


class Renderer:
    """A class to render templates."""

    def __init__(self, searchpath: str | os.PathLike[str]) -> None:
        """Initialize the Renderer.

        Args:
            searchpath: The path to search for templates.

        """
        self.searchpath = searchpath
        self.env = Environment(
            loader=FileSystemLoader(self.searchpath),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(),
        )

    def render(
        self,
        template: str | os.PathLike[str],
        output_file: str | os.PathLike[str] = "",
        kwargs: dict | None = None,
    ) -> str:
        """Render a template.

        Args:
            template: The name of the template to render.
            output_file: The path to write the rendered output to. If not
              provided, the output is not written to a file.
            kwargs: A dictionary of keyword arguments to pass to the template.

        Returns:
            The rendered template as a string.

        """
        t = self.env.get_template(str(template))
        output = t.render(**(kwargs or {}))
        if output_file:
            Path(output_file).write_text(output, encoding="utf-8")
        return output


def process_py(project: Project, src_dir: Path, render_kwargs: dict) -> None:
    PY_DIR = RC_DIR / "py"
    shutil.copytree(PY_DIR, project.project_dir, dirs_exist_ok=True)

    pkg_dir = src_dir / project.project_name
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").touch()
    (pkg_dir / "main.py").touch()

    r = Renderer(searchpath=PY_DIR)
    r.render("MANIFEST.in", project.project_dir / "MANIFEST.in", render_kwargs)
    r.render(
        "pyproject.toml",
        project.project_dir / "pyproject.toml",
        {**render_kwargs, "pypjt_version": __VERSION__},
    )


def process_js(project: Project, src_dir: Path, render_kwargs: dict) -> None:
    JS_DIR = RC_DIR / "js"
    shutil.copytree(JS_DIR, project.project_dir, dirs_exist_ok=True)

    (project.project_dir / ".env.development").touch()
    (project.project_dir / ".prettierignore").touch()

    if project.sub_type == "uniapp":
        UNIAPP_DIR = RC_DIR / "js_uniapp"
        shutil.copytree(UNIAPP_DIR, project.project_dir, dirs_exist_ok=True)

        r = Renderer(searchpath=UNIAPP_DIR)
        r.render("package.json", project.project_dir / "package.json", render_kwargs)
        r.render("bun.lock", project.project_dir / "bun.lock", render_kwargs)

    elif project.sub_type == "vue":
        VUE_DIR = RC_DIR / "js_vue"
        shutil.copytree(VUE_DIR, project.project_dir, dirs_exist_ok=True)

        r = Renderer(searchpath=VUE_DIR)
        r.render("package.json", project.project_dir / "package.json", render_kwargs)
        r.render("bun.lock", project.project_dir / "bun.lock", render_kwargs)


def process(project: Project) -> None:
    """Process the project creation.

    Args:
        project: A Project object containing project details.

    """
    shutil.copytree(COMMON_DIR, project.project_dir, dirs_exist_ok=True)
    (project.project_dir / "CHANGELOG.md").touch()
    src_dir = project.project_dir / "src"
    src_dir.mkdir()

    shutil.copy2(COMMON_DIR / ".env.example", project.project_dir / ".env")

    render_kwargs = project.model_dump()

    r = Renderer(searchpath=COMMON_DIR)
    r.render("compose.yml", project.project_dir / "compose.yml", render_kwargs)
    r.render("Dockerfile", project.project_dir / "Dockerfile", render_kwargs)
    r.render("README.rst", project.project_dir / "README.rst", render_kwargs)
    r.render(".releaserc", project.project_dir / ".releaserc", render_kwargs)
    r.render(
        "docs/source/conf.py",
        project.project_dir / "docs/source/conf.py",
        render_kwargs,
    )
    r.render(
        "docs/source/index.rst",
        project.project_dir / "docs/source/index.rst",
        render_kwargs,
    )

    if project.project_type == "py":
        process_py(project, src_dir, render_kwargs)
    elif project.project_type == "js":
        process_js(project, src_dir, render_kwargs)


def main(
    version: Annotated[  # noqa: FBT002 ARG001
        bool,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    """Run the command-line interface for creating a new project."""
    project_type = typer.prompt("Project type [py/js/go]", default="py")
    if project_type not in {"py", "js", "go"}:
        typer.echo("Invalid project type. Choose from 'py', 'js', or 'go'.", err=True)
        raise typer.Exit(code=1)
    if project_type == "js":
        sub_type = typer.prompt("Sub type [vue/uniapp]", default="vue")
        if sub_type not in {"vue", "uniapp"}:
            typer.echo("Invalid sub type. Choose from 'vue' or 'uniapp'.", err=True)
            raise typer.Exit(code=1)
    else:
        sub_type = None
    project_name = typer.prompt("Project name")
    project_dir = Path.cwd() / project_name
    if project_dir.exists():
        msg = (
            f"Project dir '{project_dir}' already exists, "
            f"please choose another name or delete it first."
        )
        typer.echo(msg, err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Project will create at '{project_dir}'")
    project_version = typer.prompt("Version", default="0.0.1")
    author = typer.prompt("Author", default="a")
    email = typer.prompt("Email", default="a@b.c")
    description = typer.prompt("Description", default="A python project.")

    project = Project(
        project_dir=project_dir,
        project_name=project_name,
        project_type=project_type,
        sub_type=sub_type,
        version=project_version,
        author=author,
        email=email,
        description=description,
    )
    process(project)


if __name__ == "__main__":
    typer.run(main)
