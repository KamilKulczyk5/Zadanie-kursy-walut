Feature: Currencies API

  Scenario: Fetch rates for a date and read them from database
    Given NBP returns rates
    When I fetch and save rates for "2025-10-09"
    Then reading rates for "2025-10-09" returns 3 items

  Scenario: Read rates in date range
    Given NBP returns rates
    When I fetch and save rates for "2025-10-09"
    And I fetch and save rates for "2025-10-10"
    Then reading range from "2025-10-09" to "2025-10-10" returns 6 items
