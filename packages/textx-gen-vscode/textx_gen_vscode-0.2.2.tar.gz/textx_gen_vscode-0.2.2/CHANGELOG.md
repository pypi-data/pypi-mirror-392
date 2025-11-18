# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][keepachangelog],
and this project adheres to [Semantic Versioning][semver].

## [Unreleased]

## [0.2.2] - 2025-11-16

### Fixed
- Restored dependency to textx-gen-coloring.


## [0.2.1] - 2025-05-09

### Fixed
- reverted generating of syntax files for basic comments/numbers syntax hl support


## [0.2.0] - 2025-05-08

### Changed
- migrated project to pyproject.toml
- rework to generate directly without vsce
- use logging module


## [0.1.3] - 12/28/2019

### Fixed

- Fix `vsce` packaging on windows

[#5]: https://github.com/danixeee/textx-gen-vscode/pull/5

## [0.1.2] - 10/08/2019

### Added

- Option to pass _vsce_ command path ([#3])

[#3]: https://github.com/danixeee/textx-gen-vscode/pull/3

## [0.1.1] - 10/03/2019

### Added

- Option to exclude language keywords when generating coloring file ([#1])

[#1]: https://github.com/danixeee/textx-gen-vscode/pull/1

## [0.1.0] - 09/10/2019

### Added

- _VS Code_ extension generator
- _azure-pipelines_ CI setup
- _black_ formatter

[keepachangelog]: https://keepachangelog.com/en/1.0.0/
[semver]: https://semver.org/spec/v2.0.0.html

[Unreleased]: https://github.com/danixeee/textx-gen-vscode/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/danixeee/textx-gen-vscode/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/danixeee/textx-gen-vscode/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/danixeee/textx-gen-vscode/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/danixeee/textx-gen-vscode/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/danixeee/textx-gen-vscode/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/danixeee/textx-gen-vscode/compare/9578ef2b8de1254a24220b413b495439e9c1f355...v0.1.0
