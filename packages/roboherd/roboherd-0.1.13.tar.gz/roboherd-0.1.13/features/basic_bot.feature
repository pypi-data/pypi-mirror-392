Feature: Just checking that the bot works

    Background: Bot and user
        Given A new user called "Alice"
        And the connection string "ws://herd:pass@cattle_grid/ws/"
        And The "moocow" RoboCow on "cattle_grid" with configuration
            """
            [cow.moocow]
            bot = "roboherd.examples.moocow:moocow"
            """

    Scenario: Can follow
        When "Alice" sends "moocow" a Follow Activity
        Then "Alice" receives an activity
        And the received activity is of type "Accept"
        And The "following" collection of "Alice" contains "moocow"

    Scenario: Gets a moo
        Given "Alice" follows auto-following "moocow"
        When "Alice" sends "moocow" a message saying "Got an encryption key?"
        Then "Alice" receives a message saying "moo"