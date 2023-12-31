# Changelog

## [2.0.0] - 2023-12-31

### Changed

- Replaced `AsyncCasbin` with `PyCasbin` for streamlined asyncio support. ([I.#7](https://github.com/thearchitector/casbin-tortoise-adapter/issues/7))

### Fixed

- Boolean return types from adapter function stub implementations.
- More static typing.
- Support for Python 3.12.

## [1.2.2] - 2023-11-24

### Fixed

- Improved and corrected static typing.

## [1.2.1] - 2023-11-23

### Added

- Support for Python 3.11.

### Fixed

- Support for Python 3.7. (credit @hubertshelley with [PR.#6](https://github.com/thearchitector/casbin-tortoise-adapter/pull/6))

## [1.2.0] - 2022-06-22

### Added

- Support for update policy management API. ([I.#4](https://github.com/thearchitector/casbin-tortoise-adapter/issues/4))

## [1.1.0] - 2022-04-16

### Changed

- Bumped minimum Tortoise version to 0.18.0. ([I.#2](https://github.com/thearchitector/casbin-tortoise-adapter/issues/2))

## [1.0.1] - 2021-08-03

### Fixed

- Removal of normal and filtered non-filled models doesn't work due to wrong query (credit @DarcJC with [PR.#1](https://github.com/thearchitector/casbin-tortoise-adapter/pull/1)).

## [1.0.0] - 2021-07-21

Initial release.
