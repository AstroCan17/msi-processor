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

# Tutorials

## Introduction

```{note}
The SUM shall describe how to use the software and what the software does, combining tutorials and reference information for both novices and experts.
```

```{note}
Jupyter notebooks can be directly integrated into the documentation
as demonstrated by the [notebooks](./notebooks/index) section.
```

## Getting started

```{note}
The SUM shall include a welcoming introduction to the software.
```

## Using the software on a typical task

```{note}
The SUM shall describe a typical use case of the software, using graphical pictures and diagrams to demonstrate the actions performed by the user.
```

```{note}
Jupyter notebook cells can be used to complete the documentation as
demonstrated below:
```

```{code-cell} ipython3
def some_documented_func(arg_name: str) -> str:
    """
    Description about this function
    :param arg_name: Explanation about this argument
    :return: Explanation about your return value
    """
    return arg_name

some_documented_func('Foo')
```
