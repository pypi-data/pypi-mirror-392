@notimplemented @strategy @strategy.subcommands
Feature: build_harness subcommands
  When someone deploys *build_harness* into a CI pipeline, or installed locally for
  developer use, they want subcommands accessible from CLI to drive use of
  pipeline features.

  Scenario: A subcommand exits non-zero on failure.

  Scenario: A subcommand exits zero on success.
