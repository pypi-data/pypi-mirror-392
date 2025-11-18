@structure @structure.dependencies @relates_to.strategy.subcommands
Feature: Dependency installation subcommand
  As a user I want the dependency installation command to install project package
  dependencies into a virtual environment so that I have a simple way to initialize
  the virtual environment with necessary dependencies in a pipeline, or in a local
  developer environment.

  @structure.dependencies.s1
  Scenario: dependency installation and virtual environment does not exist
    Given the virtual environment does not exist in the project directory
    When the build harness command is run
    Then the virtual environment is created
    And the virtual environment is populated with necessary project dependencies
    And the utility exits clean

  @structure.dependencies.s2
  Scenario: dependency installation and virtual environment exists
    Given the virtual environment already exists in the project directory
    When the build harness command is run
    Then the virtual environment is populated with necessary project dependencies
    And the utility exits clean

  @structure.dependencies.s3
  Scenario: dependency installation fails
    Given the project includes configuration that will cause the installation to fail
    When the build harness command is run
    Then the utility exits dirty
    And installation error is reported to the console

  @structure.dependencies.s4
  Scenario: check installed dependencies
    Given a virtual environment with the installed project dependencies
    And the project includes a dependency change in pyproject.toml that is not installed in the virtual environment
    And the --check argument is added to the install command run
    When the build harness command is run
    Then the utility exits dirty
    And the dependency installation error is reported to the console
