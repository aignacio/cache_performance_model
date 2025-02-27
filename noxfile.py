#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : noxfile.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 08.02.2025
# Last Modified Date: 27.02.2025
import nox


@nox.session(python=["3.12"], reuse_venv=True)
def run(session):
    session.env["AUTHOR"] = "Anderson Ignacio da Silva"
    session.install(
        "pytest",
        "pytest-xdist",
        "pytest-sugar",
        "pytest-cov",
        "pytest-split",
        "numpy",
    )
    session.install("-e", ".")
    session.run(
        "py.test",
        "--log-cli-level=DEBUG",
        # "--log-cli-level=INFO",
        "--cov=cache_performance_model",
        "--cov-branch",
        "--cov-report=xml",
        # "--cov-report=html",
        # "-rf",
        "-rP",
        "-n",
        "1",
        *session.posargs
    )


@nox.session(python=["3.12"], reuse_venv=True)
def lint(session):
    session.install("flake8")
    session.run("flake8")


@nox.session(reuse_venv=True)
def docs(session):
    session.install("-e", ".")
    session.install("sphinx", "sphinx_rtd_theme", "ghp-import",
                    "sphinx_copybutton", "myst_parser", "furo",
                    "ghp-import")
    session.run("rm", "-rf", "docs/_build", external=True)
    session.run("sphinx-apidoc", "-o", "docs", "cache_performance_model")
    session.run("sphinx-build", "-b", "html", "docs", "docs/_build/html")
