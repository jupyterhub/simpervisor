# Changelog

## 1.0

### 1.0.0 - 2023-05-18

With this release Python >=3.8 is required and Windows is supported.

#### New features added

- Add support for Windows platform [#26](https://github.com/jupyterhub/simpervisor/pull/26) ([@rashedmyt](https://github.com/rashedmyt))

#### Maintenance and upkeep improvements

- pre-commit: remove remnant config for py37 [#34](https://github.com/jupyterhub/simpervisor/pull/34) ([@consideRatio](https://github.com/consideRatio))
- Drop support for Python 3.7 [#30](https://github.com/jupyterhub/simpervisor/pull/30) ([@consideRatio](https://github.com/consideRatio))
- pre-commit: add autoflake hook, use dedicated .flake8 config, detail tweaks to RELEASE.md [#29](https://github.com/jupyterhub/simpervisor/pull/29) ([@consideRatio](https://github.com/consideRatio))
- dependabot: monthly updates of github actions [#28](https://github.com/jupyterhub/simpervisor/pull/28) ([@consideRatio](https://github.com/consideRatio))
- Require Python 3.7+, fix test failures, test against Py 3.10 and 3.11, README/RELEASE update [#19](https://github.com/jupyterhub/simpervisor/pull/19) ([@consideRatio](https://github.com/consideRatio))
- maint: add pre-commit config and run pre-commit [#18](https://github.com/jupyterhub/simpervisor/pull/18) ([@consideRatio](https://github.com/consideRatio))
- maint: remove unused imports [#17](https://github.com/jupyterhub/simpervisor/pull/17) ([@consideRatio](https://github.com/consideRatio))
- General JupyterHub org maintenance [#14](https://github.com/jupyterhub/simpervisor/pull/14) ([@consideRatio](https://github.com/consideRatio))

#### Documentation improvements

- docs: fix github test passing badge [#31](https://github.com/jupyterhub/simpervisor/pull/31) ([@consideRatio](https://github.com/consideRatio))
- Update README badges [#11](https://github.com/jupyterhub/simpervisor/pull/11) ([@consideRatio](https://github.com/consideRatio))

#### Continuous integration improvements

- ci: add dependabot, update gha, test modern python versions, etc [#16](https://github.com/jupyterhub/simpervisor/pull/16) ([@consideRatio](https://github.com/consideRatio))
- ci: use GitHub Workflows and test python 3.6-3.9 [#10](https://github.com/jupyterhub/simpervisor/pull/10) ([@consideRatio](https://github.com/consideRatio))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/simpervisor/graphs/contributors?from=2021-01-05&to=2023-05-18&type=c))

[@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Fsimpervisor+involves%3AconsideRatio+updated%3A2021-01-05..2023-05-18&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyterhub%2Fsimpervisor+involves%3Aminrk+updated%3A2021-01-05..2023-05-18&type=Issues) | [@rashedmyt](https://github.com/search?q=repo%3Ajupyterhub%2Fsimpervisor+involves%3Arashedmyt+updated%3A2021-01-05..2023-05-18&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fsimpervisor+involves%3Ayuvipanda+updated%3A2021-01-05..2023-05-18&type=Issues)

## 0.4

### 0.4 - 2021-01-05

([full changelog](https://github.com/jupyterhub/simpervisor/compare/v0.3...v0.4))

#### Maintenance and upkeep improvements

- Adds tox file for testing against multiple python versions [#8](https://github.com/jupyterhub/simpervisor/pull/8) ([@tdhopper](https://github.com/tdhopper))
- Adds Python 3.9 compatability by fixing asyncio api changes [#7](https://github.com/jupyterhub/simpervisor/pull/7) ([@tdhopper](https://github.com/tdhopper))
- Package the license file [#5](https://github.com/jupyterhub/simpervisor/pull/5) ([@jakirkham](https://github.com/jakirkham))

## 0.3

### 0.3 - 2019-01-05

- Bump version number [08444aa](https://github.com/jupyterhub/simpervisor/commit/08444aa) ([@yuvipanda](https://github.com/yuvipanda))
- Fix \_debug_log to do string formatting properly [ab07119](https://github.com/jupyterhub/simpervisor/commit/ab07119) ([@yuvipanda](https://github.com/yuvipanda))

## 0.2

### 0.2 - 2019-01-04

- Bump version number [b736f11](https://github.com/jupyterhub/simpervisor/commit/b736f11) ([@yuvipanda](https://github.com/yuvipanda))
- Add aiohttp to dev-requirements [1b4299f](https://github.com/jupyterhub/simpervisor/commit/1b4299f) ([@yuvipanda](https://github.com/yuvipanda))
- Remove more f-strings [63c4d79](https://github.com/jupyterhub/simpervisor/commit/63c4d79) ([@yuvipanda](https://github.com/yuvipanda))
- Make compatible with python3.5 [1c55e72](https://github.com/jupyterhub/simpervisor/commit/1c55e72) ([@yuvipanda](https://github.com/yuvipanda))
- Don't use Python3.7 features [8b0ddc5](https://github.com/jupyterhub/simpervisor/commit/8b0ddc5) ([@yuvipanda](https://github.com/yuvipanda))

## 0.1

### 0.1 - 2018-12-28

- Add description to setup.py [058e55e](https://github.com/jupyterhub/simpervisor/commit/058e55e) ([@yuvipanda](https://github.com/yuvipanda))
- Allow passing in custom logger [1d96158](https://github.com/jupyterhub/simpervisor/commit/1d96158) ([@yuvipanda](https://github.com/yuvipanda))
- Handle readyness check timing out [a6c06c3](https://github.com/jupyterhub/simpervisor/commit/a6c06c3) ([@yuvipanda](https://github.com/yuvipanda))
- Add check for readyness of process [2ca085c](https://github.com/jupyterhub/simpervisor/commit/2ca085c) ([@yuvipanda](https://github.com/yuvipanda))
- Throw exception if process is reused [fa08479](https://github.com/jupyterhub/simpervisor/commit/fa08479) ([@yuvipanda](https://github.com/yuvipanda))
- Add tests for reaping-on-signal behavior [bf318b4](https://github.com/jupyterhub/simpervisor/commit/bf318b4) ([@yuvipanda](https://github.com/yuvipanda))
- Don't add signal handler multiple times [bbc3d9e](https://github.com/jupyterhub/simpervisor/commit/bbc3d9e) ([@yuvipanda](https://github.com/yuvipanda))
- Add a bunch of docstrings [37442ba](https://github.com/jupyterhub/simpervisor/commit/37442ba) ([@yuvipanda](https://github.com/yuvipanda))
- Clarify what the lock is for [0666875](https://github.com/jupyterhub/simpervisor/commit/0666875) ([@yuvipanda](https://github.com/yuvipanda))
- Implement kill & terminate methods [892411d](https://github.com/jupyterhub/simpervisor/commit/892411d) ([@yuvipanda](https://github.com/yuvipanda))
- Test adding multiple signal handlers [adb1eac](https://github.com/jupyterhub/simpervisor/commit/adb1eac) ([@yuvipanda](https://github.com/yuvipanda))
- Wait more time in atexitasync test before SIGTERM [b130203](https://github.com/jupyterhub/simpervisor/commit/b130203) ([@yuvipanda](https://github.com/yuvipanda))
- Add setup.py [e47b7fb](https://github.com/jupyterhub/simpervisor/commit/e47b7fb) ([@yuvipanda](https://github.com/yuvipanda))
- Add test for atexitasync [521b011](https://github.com/jupyterhub/simpervisor/commit/521b011) ([@yuvipanda](https://github.com/yuvipanda))
- Move tests to a directory [9a927cc](https://github.com/jupyterhub/simpervisor/commit/9a927cc) ([@yuvipanda](https://github.com/yuvipanda))
- Don't restart process if we're already terminating [693ef93](https://github.com/jupyterhub/simpervisor/commit/693ef93) ([@yuvipanda](https://github.com/yuvipanda))
- Propagate SIGTERM & SIGINT to supervised processes [5b2e558](https://github.com/jupyterhub/simpervisor/commit/5b2e558) ([@yuvipanda](https://github.com/yuvipanda))
- Make simpervisor into a proper module [161d641](https://github.com/jupyterhub/simpervisor/commit/161d641) ([@yuvipanda](https://github.com/yuvipanda))
- Add badges to README [d07b5f0](https://github.com/jupyterhub/simpervisor/commit/d07b5f0) ([@yuvipanda](https://github.com/yuvipanda))
- Upload coverage stats to codecov [da3c487](https://github.com/jupyterhub/simpervisor/commit/da3c487) ([@yuvipanda](https://github.com/yuvipanda))
- Increase sleep_wait_time for circleci [88f8113](https://github.com/jupyterhub/simpervisor/commit/88f8113) ([@yuvipanda](https://github.com/yuvipanda))
- Bring down sleep / sleep wait times for tests [88a69e4](https://github.com/jupyterhub/simpervisor/commit/88a69e4) ([@yuvipanda](https://github.com/yuvipanda))
- Print debug logs with pytest [6a2814c](https://github.com/jupyterhub/simpervisor/commit/6a2814c) ([@yuvipanda](https://github.com/yuvipanda))
- Add lots of logging [7d679d9](https://github.com/jupyterhub/simpervisor/commit/7d679d9) ([@yuvipanda](https://github.com/yuvipanda))
- Bump up wait time for processes to finish [3e13708](https://github.com/jupyterhub/simpervisor/commit/3e13708) ([@yuvipanda](https://github.com/yuvipanda))
- Add circleci config [9b1ad42](https://github.com/jupyterhub/simpervisor/commit/9b1ad42) ([@yuvipanda](https://github.com/yuvipanda))
- Fix typo in name [7405d29](https://github.com/jupyterhub/simpervisor/commit/7405d29) ([@yuvipanda](https://github.com/yuvipanda))
- Add dev requirements [14fee2c](https://github.com/jupyterhub/simpervisor/commit/14fee2c) ([@yuvipanda](https://github.com/yuvipanda))
- Prevent concurrent stop / start attempts [2f87e08](https://github.com/jupyterhub/simpervisor/commit/2f87e08) ([@yuvipanda](https://github.com/yuvipanda))
- Initial commit [e893b83](https://github.com/jupyterhub/simpervisor/commit/e893b83) ([@yuvipanda](https://github.com/yuvipanda))
- Initial commit [8f8a2c1](https://github.com/jupyterhub/simpervisor/commit/8f8a2c1) ([@yuvipanda](https://github.com/yuvipanda))
