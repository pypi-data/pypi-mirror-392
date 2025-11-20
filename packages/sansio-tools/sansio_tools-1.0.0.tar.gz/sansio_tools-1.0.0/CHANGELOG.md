# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.0.0] - 2025-11-19

### Added

- `parser`: Add utility methods `Parser.feed_from_file()` and `Parser.feed_from_iter()`.
- `queue`: Add an adapter for turning a bytes-yielding generator into a file-like object, named
  `FileAdapterFromGeneratorBytes`.
- Increase test coverage to 100%.

### Changed

- `parser`: BREAKING CHANGE: Use `Parser.feed(None)` to signal end-of-stream instead of using any falsy value.

## [0.1.0] - 2025-08-07

### Added

- Add module `parser` with classes `Parser` and `BinaryParser`.

## [0.0.1] - 2025-08-03

### Added

- Add `SolidQueue` and subclass `BytesQueue`.

## [0.0.0] - 1970-01-01

### Added

- This is an example entry.
- See below for the other types of changes.

### Changed

- Change in functionality.

### Deprecated

- Feature that will be removed soon.

### Removed

- Feature that is now removed.

### Fixed

- Bug that was fixed.

### Security

- Security vulnerability notice.
