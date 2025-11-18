{{cookiecutter.project_name}}
{{'='*(cookiecutter.project_name|length)}}

{{cookiecutter.project_summary}}

.. contents::

.. section-numbering::


Installation
------------

The ``{{cookiecutter.project_slug}}`` package is available from PyPI. Installing into a virtual
environment is recommended.

.. code-block::

   python3 -m venv .venv; .venv/bin/pip install {{cookiecutter.project_slug}}
