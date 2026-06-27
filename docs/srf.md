<!--
  Copyright 2026 ESA

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->

# Software reuse file

## Introduction

This section constitutes the Software reuse file (SRF) for
the s2-msi-processor project.

The first level dependencies are listed in the following sections.

For each dependency, the following information is listed:

- software item name;
- short description of the main features;
- version;
- developer name;
- licensing conditions;
- industrial property and exportability constraints, if any;
- implementation language;
- development and execution environment (e.g. platform, and operating system);

## Presentation of the software intended to be reused

### Python

#### Bandit

| Software Item name | Bandit ([docs](https://bandit.readthedocs.io/en/latest/), [github](https://github.com/PyCQA/bandit)) |
| -- | -- |
| Description | Bandit is a tool designed to find common security issues in Python code. |
| Version | 1.7.5 |
| Developer name | [Python Code Quality Authority (PyCQA)][PyCQA] |
| Licensing conditions | [Apache License v 2.0][APL] |
| Industrial property and exportability constraints | None |
| Implementation language | Python |
| Development and execution environment | Python |

#### Flake8

| Software Item name | Flake8 ([docs](https://flake8.pycqa.org/en/latest/), [github](https://github.com/PyCQA/flake8) |
| -- | -- |
| Description | Flake8 is a Python tool that glues together pycodestyle, pyflakes, mccabe, and third-party plugins to check the style and quality of some python code. |
| Version | 6.0.0 |
| Developer name | [Python Code Quality Authority (PyCQA)][PyCQA] |
| Licensing conditions | [Flake8 License (MIT)](https://github.com/PyCQA/flake8/blob/main/LICENSE) |
| Industrial property and exportability constraints | None |
| Implementation language | Python |
| Development and execution environment | Python |

#### Isort

| Software Item name | isort ([docs](https://pycqa.github.io/isort/), [github](https://github.com/PyCQA/isort)) |
| -- | -- |
| Description | A Python utility / library to sort imports. |
| Version | 5.12.0 |
| Developer name | [Python Code Quality Authority (PyCQA)][PyCQA] |
| Licensing conditions | [MIT License](https://github.com/PyCQA/isort/blob/main/LICENSE) |
| Industrial property and exportability constraints | None |
| Implementation language | Python |
| Development and execution environment | Python |

#### Mypy

| Software Item name | mypy ([home](http://mypy-lang.org/), [github](https://github.com/python/mypy/)) |
| -- | -- |
| Description | Mypy is an optional static type checker for Python. |
| Version | 1.4.1 |
| Developer name | [Community project](https://github.com/python/mypy/blob/master/CONTRIBUTING.md) |
| Licensing conditions | [MIT License](https://github.com/python/mypy/blob/master/LICENSE) |
| Industrial property and exportability constraints | None |
| Implementation language | Python |
| Development and execution environment | Python |

#### Pip

| Software Item name | [pip](https://pypi.org/project/pip/) |
| -- | -- |
| Description | Python package installer. |
| Version | 23.2.1 |
| Developer name | The pip developers (community project) |
| Licensing conditions | [MIT License](https://github.com/pypa/pip/blob/main/LICENSE.txt) |
| Industrial property and exportability constraints | None |
| Implementation language | Python |
| Development and execution environment | Python |

#### Pytest

| Software Item name | pytest ([docs](https://docs.pytest.org/en/7.4.x/), [github](https://github.com/pytest-dev/pytest/)) |
| -- | -- |
| Description | pytest is a Python test framework. |
| Version | 7.4.0 |
| Developer name | [pytest collective](https://docs.pytest.org/en/7.4.x/sponsor.html) |
| Licensing conditions | [MIT License](https://github.com/pytest-dev/pytest/blob/main/LICENSE) |
| Industrial property and exportability constraints | None |
| Implementation language | Python |
| Development and execution environment | Python |

#### Pytest-benchmark

| Software Item name | pytest-benchmark ([docs](http://pytest-benchmark.readthedocs.org/en/stable/), [github](https://github.com/ionelmc/pytest-benchmark)) |
| -- | -- |
| Description | py.test fixture for benchmarking code. |
| Version | 4.0.0 |
| Developer name | [Community project](https://github.com/ionelmc/pytest-benchmark/blob/master/CONTRIBUTING.rst) |
| Licensing conditions | [BSD-2-Clause License](https://github.com/ionelmc/pytest-benchmark/blob/master/LICENSE) |
| Industrial property and exportability constraints | None |
| Implementation language | Python |
| Development and execution environment | Python |

#### Pytest-cov

| Software Item name | pytest-cov ([docs](https://pytest-cov.readthedocs.io/en/latest/), [github](https://github.com/pytest-dev/pytest-cov)) |
| -- | -- |
| Description | Coverage plugin for pytest. |
| Version | 4.1.0 |
| Developer name | [pytest collective](https://docs.pytest.org/en/7.4.x/sponsor.html) |
| Licensing conditions | [MIT License](https://github.com/pytest-dev/pytest-cov/blob/master/LICENSE) |
| Industrial property and exportability constraints | None |
| Implementation language | Python |
| Development and execution environment | Python |

#### Python

| Software Item name | [Python](https://www.python.org/) |
| -- | -- |
| Description | Python is a high-level, general-purpose programming language. |
| Version | 3.11 |
| Developer name | [Python Software Foundation](https://www.python.org/psf-landing/) |
| Licensing conditions | [Python Software Foundation License](https://docs.python.org/3.11/license.html) |
| Industrial property and exportability constraints | None |
| Implementation language | Python and C |
| Development and execution environment | Windows, Linux |

## Compatibility of existing software with project requirements

```{note}
The SRF shall describe which part of the project requirements (RB)
are intended to be implemented through software reuse

For each software item, the SRF shall provide the availability and quality status (completeness, correctness, etc.) of the following information:

  1. software requirements documentation;
  2. software architectural and detailed design documentation;
  3. forward and backward traceability between system requirements;
  4. software requirements, design and code;
  5. unit tests documentation and coverage;
  6. integration tests documentation and coverage;
  7. validation documentation and coverage;
  8. verification reports;
  9. performance (e.g. memory occupation, CPU load);
  10. operational performances;
  11. residual non conformance and waivers;
  12. user operational documentation (e.g. user manual);
  13. code quality (adherence to coding standards, metrics).

c. For each of the points in b, the SRF shall document the quality level of the existing software with respect to the applicable project requirements, according to the criticality of the system function implemented.
```

## Software reuse analysis conclusion

```{note}
The SRF shall document the results of the software reuse analysis.

For each software item, the SRF shall provide the following information:

  1. decision to reuse or not reuse, based on the information provided in previous chapters;
  2. estimated level of reuse;
  3. assumptions and methods applied when estimating the level of reuse.
```

## Detailed results of evaluation

```{note}
The SRF shall include the detailed results of the evaluation.

> NOTE The detailed results of the evaluation can be presented in an appendix.
```

## Corrective actions

```{note}
The SRF shall document any corrective actions identified to ensure that the software intended for reuse meets the applicable project requirements.

The SRF shall document the detailed results of the implementation of the identified corrective actions.
```

## Configuration status

```{note}
The SRF shall include the detailed configuration status of the reused software baseline.
```

<!--
  Reference links
  See https://myst-parser.readthedocs.io/en/latest/syntax/cross-referencing.html#markdown-link-syntax
-->

[APL]: https://www.apache.org/licenses/LICENSE-2.0.html "Apache License, version 2.0"
[CNCF]: https://www.cncf.io/ "Cloud Native Computing Foundation (CNCF)"
[PyCQA]: https://meta.pycqa.org/ "Python Code Quality Authority (PyCQA)"
