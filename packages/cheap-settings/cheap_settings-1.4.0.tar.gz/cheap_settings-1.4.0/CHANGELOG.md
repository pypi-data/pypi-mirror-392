# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2025-11-17

### Added
- Support for custom types with `from_string()` class methods
- Reserved `__cheap_settings__` attribute namespace for future configuration

### Changed
- Extended type documentation with custom type examples

## [1.3.0] - 2025-10-18

### Added

- Support for `datetime`, `date`, and `time` types using ISO format strings
- Support for `Decimal` type for precise financial calculations
- Support for `UUID` type (accepts multiple formats: standard, no hyphens, with braces)
- Command line argument support for all new extended types

## [1.2.2] - 2025-10-17

### Added
- Both --flag and --no-flag for all boolean settings (fixes env var override issues)

## [1.2.1] - 2025-10-16

### Fixed
- Boolean command line flags can now override environment variables in both directions
- Optional types properly handle "none" from command line

## [1.2.0] - 2025-10-15

### Added

- Settings can now be added without initializers

### Fixed
- Name mangling used to prevent conflicts between user settings and internal flags

## [1.1.0] - 2025-10-12

### Added

- `from_env()` class method returns settings that are only sourced from environment variables

## [1.0.0] - 2025-10-12

### Added

- Initial stable release with core functionality
- Improved error handling
- Comprehensive JSON error messages

### Changed

- General cleanup for 1.0

## Previous Releases
For changes before v1.0.0, see the [commit history](https://github.com/evanjpw/cheap-settings/commits/main).

### Added
- Support for basic types: `str`, `int`, `float`, `bool`, `pathlib.Path`
- Support for `Optional` and `Union` types
- Support for `list` and `dict` types via JSON parsing
- Command line argument generation and parsing
- Type inference from default values
- Inheritance support for settings classes
- Pickle support for Ray compatibility
- `to_static()` method for performance-critical code

### Fixed
- Various stability improvements and bug fixes
