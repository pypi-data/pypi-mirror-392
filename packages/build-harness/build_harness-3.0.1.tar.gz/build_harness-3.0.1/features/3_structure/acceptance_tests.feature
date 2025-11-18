@notimplemented @structure @structure.bdd @relates_to.strategy.subcommands
Feature: Acceptance tests subcommand
  As a user I want the acceptance tests command to run all acceptance tests in the
  project.

  Scenario: run tests
    Given at least one feature file
    And a corresponding step file
    When the acceptance tests are run
    Then a console summary report of test results is generated

  Scenario: generate snippets of unimplemented features
    Given at least one feature file with the unimplemented tag
    When the acceptance tests are run with the snippets option enabled
    Then template step implementations of the feature are generated on the console

  Scenario: junit report
    Given at least one feature file
    And a corresponding step file
    When the acceptance tests are run with the junit report option enabled
    Then a JUnit style XML summary report of test results is generated

  Scenario: tag filtering
    Given features files containing tags
    When the acceptance tests are run with the tag option specifying the name of a tag
    Then only the items associated with that tag are run
