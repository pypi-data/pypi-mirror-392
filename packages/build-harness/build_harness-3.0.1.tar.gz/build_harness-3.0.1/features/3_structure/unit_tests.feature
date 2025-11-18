@notimplemented @structure @structure.unit_tests @relates_to.strategy.subcommands
Feature: Unit tests subcommands
  As a user I want the unit tests command to run all unit tests.

  Scenario: just run the tests
    Given a project with tests
    When the build harness unit tests command is run
    Then all the tests are run
    And the utility exits dirty if any tests fail.

  Scenario: tests with coverage report
    Given a project with tests
    When the build harness unit tests command is run with a coverage report option
    Then all the tests are run
    And a coverage report is generated

  Scenario: tests with junit report
    Given a project with tests
    When the build harness unit tests command is run with a junit report option
    Then all the tests are run
    And a junit xml file of test run results is generated

  Scenario: coverage check
    Given a project with tests
    When the build harness unit tests command is run with a coverage check option
    Then all the tests are run
    And the utility exits dirty if the total coverage does not exceed a specified threshold
