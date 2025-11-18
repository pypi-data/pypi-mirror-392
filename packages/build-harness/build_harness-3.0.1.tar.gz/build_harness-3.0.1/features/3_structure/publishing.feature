@structure @structure.publishing @relates_to.strategy.publishing
Feature: Publishing subcommand
  As a user I want specified artifacts to be uploaded to my preferred site for
  publishing so that end users can consume my artifacts as needed.

  For starters support PyPI and ReadTheDocs. Add support for other archives later.
  Some kind of custom method would also be attractive.

  @notimplemented @structure.publishing.s1
  Scenario: publishing wheel and sdist packages to pypi.org
    Given wheel and sdist packages in the dist subfolder
    When the publishing command is run
    Then the packages are uploaded to pypi.org

  @notimplemented @structure.publishing.s2
  Scenario: publishing sphinx documentation to readthedocs.io
    Given sphinx generated HTML documentation files in the dist subfolder
    When the publishing command is run
    Then the packages are uploaded to readthedocs.io
