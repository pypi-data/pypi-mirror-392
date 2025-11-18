@notimplemented @structure @structure.formatting @relates_to.strategy.subcommands
Feature: Formatting subcommand
  As a user I want the formatting command to run all necessary formatting on the
  specified source code.

  Scenario: black formatting
    Given a source file requiring black formatting
    When build harness formatting is run
    Then the file is formatted according to black formatting.

  Scenario: isort formatting
    Given a source requiring isort formatting
    When build harness formatting is run
    Then the file is formatted according to isort formatting.

  Scenario: black formatting takes precedence over isort formatting
    Given a source file with formatting that isort and black compete over
    When build harness formatting is run
    Then black formatting takes precedence over isort formating.

  Scenario: check formatting
    Given a source file requiring formatting changes
    When formatting is run with the check option enabled
    Then formatting is not applied to the file
    And the utility exits dirty if applied formatting would change the file.
