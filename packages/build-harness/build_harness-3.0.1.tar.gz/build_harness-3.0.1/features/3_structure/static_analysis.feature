@notimplemented @structure @structure.static_analysis @relates_to.strategy.subcommands
Feature: Static analysis subcommand
  As a user I want the static_analysis command to run all necessary analysis on the
  specified source code.

  Scenario: flake8 analysis
    Given source code to be analysed
    When build harness static analysis is run
    Then flake8 analysis is included in the run
    And flake8 analysis includes docstrings.

  Scenario: mypy analysis
    Given source code to be analysed
    When build harness static analysis is run
    Then mypy analysis is included in the run.

  Scenario: all static analysis in one run
    Given source code to be analysed
    When build harness static analysis is run
    Then the utility exits dirty if any of the static analyses fails.

  Scenario: flake8, mypy formatting
#    Static analysis tools complain about some formatting conventions. Run formatting
#    before any static analysis.
    Given source code to be analysed
    When build harness static analysis is run
    Then build harness formatting is run before the static analysis run.
