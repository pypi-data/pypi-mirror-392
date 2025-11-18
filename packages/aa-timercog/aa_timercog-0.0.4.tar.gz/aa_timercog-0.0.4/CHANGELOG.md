# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/0.0.1/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.4] - 2025-11-14

added /timer parse functionalaty to autoparse system names

## [0.0.3] - 2025-11-14

added /timer parse functionalaty and removed friendly structures from the timer list

## [0.0.2] - 2025-11-14

added /timer list Cog to get a list of timers in discord with a date option

## [0.0.1] - 2025-10-25

### Added

- Initial release of AA Timer Cog
- `/timer add` Discord slash command for creating structure timers
- Autocomplete support for:
  - Solar systems
  - Structure types
  - Timer types
  - Objectives (Friendly/Hostile/Neutral)
- Role-based permission system via `TIMERCOG_ALLOWED_ROLE_IDS`
- Channel restriction support via `TIMERCOG_ALLOWED_CHANNELS`
- Alliance Auth authentication integration
- Rich Discord embeds for timer confirmations
- Comprehensive error handling and user feedback
- Full integration with aa-structuretimers

### Features

- Create timers with all standard fields:
  - System, structure type, owner, timer type
  - Days, hours, minutes until expiration
  - Custom structure name
  - Location details
  - Objective (friendly/hostile/neutral)
  - Notes
- Automatic calculation of timer expiration from duration
- Support for Timer Types from aa-structuretimers
- Real-time autocomplete suggestions from Eve Universe data
- Permission validation before timer creation
- Detailed logging for audit trails

[0.0.1]: https://github.com/yourusername/aa-timercog/releases/tag/v1.0.0
