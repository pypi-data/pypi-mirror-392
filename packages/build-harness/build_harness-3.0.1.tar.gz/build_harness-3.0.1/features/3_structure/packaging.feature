@structure @structure.packaging @relates_to.strategy.subcommands
Feature: Packaging subcommand
  As a user I want the packaging command to create an appropriate Python distribution
  package such as wheel.

  @structure.packaging.s1
  Scenario: flit packaging
    Given a flit project directory to be packaged
    When the build harness command is run
    Then the wheel package is created

  @notimplemented @structure.packaging.s2
  Scenario: poetry packaging

  @notimplemented @structure.packaging.s3
  Scenario: setuptools packaging

  @notimplemented @structure.packaging.s4
  Scenario: unidentifiable packager
    Given a project directory using a non-supported packaging utility
    When the build harness command is run
    Then the correct packaging tool cannot be identified
    And the utility exits dirty

  @structure.packaging.s5
  Scenario: package release data
    Given a flit project directory to be packaged
    And a PEP440 compliant release id
    When the build harness command is run
    Then the wheel package file identifies itself with the release id
    And when installed the package identifies itself with the release id

  @structure.packaging.s6
  Scenario: default package release
    Given a flit project directory to be packaged
    And no release id specified
    When the build harness command is run
    Then the wheel package file identifies itself with the default release id
