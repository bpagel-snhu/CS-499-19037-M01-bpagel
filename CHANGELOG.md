# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-05-14 (dev branch)

### Added
- Comprehensive test suite with pytest
  - Unit tests for core functionality
  - GUI tests for main window
- Test coverage reporting
- Improved error handling for directory validation
- Mock-based testing infrastructure
- Test utilities for GUI testing
- Enhanced PDF security removal functionality
  - Removes all security certifications
  - Handles edit restrictions
  - Removes digital signatures
  - Clears document permissions
  - Removes encryption

### Changed
- Updated Python version requirement to 3.12+
- Updated customtkinter to version 5.2.2
- Improved documentation with testing instructions
- Enhanced error handling in utility functions
- Refactored code structure for better maintainability
- Cleaned up and standardized code formatting
- Improved month normalization
  - Excludes "May" from full month normalization
  - Better handling of filename collisions
  - More accurate rename counting
  - Enhanced test coverage for normalization

### Fixed
- Directory validation now properly handles None values
- Backup directory creation test reliability
- GUI test stability issues
- PDF unlocking now properly removes all security restrictions
- Month normalization now correctly handles edge cases and collisions

## [1.0.0] - 2025-04-04

### Fixed
- Hotfix: Corrected UI element duplication bug on folder selection change

### Added
- PDF unlock functionality for target folder files before sample file selection

## [0.1.0] - 2025-04-03

### Changed
- Updated requirements.txt with correct customtkinter version
- Removed unused import statement

## [0.0.1] - 2025-03-25

### Added
- Initial project setup
- Basic GUI implementation
- Core renaming functionality
- Backup system using 7-Zip
- Position-based date extraction
- Textual month normalization
- Duplicate prevention system 