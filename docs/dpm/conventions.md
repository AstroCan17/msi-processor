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

# Notations and conventions

```{note}
This page shall summarise symbols, stylistics conventions, and command syntax conventions used in the DPM.
```

## Block diagram symbols

Block diagrams can be created using
[Mermaid flowcharts](https://mermaid.js.org/syntax/flowchart.html).

The following conventions apply:

A plain node illustrates an algorithm step:

```{mermaid}
flowchart
  step[Algorithm/Processing step]
```

A node in a subroutine shape illustrates an
algorithm step for which a further breakdown exists:

```{mermaid}
flowchart
  step[[Function]]
```

A node in a parallelogram shape illustrates data, e.g. internal data:
```{mermaid}
flowchart
  data[/Data/]
```

A node in a cylindrical shape illustrates external data, e.g. a database:
```{mermaid}
flowchart
  externalData[(Database)]
```

A node (rhombus) illustrates a decision step:
```{mermaid}
flowchart
  decision{Decision step}
```

A node with in a trapezoid shape illustrates the start of a loop:
```{mermaid}
flowchart
  start[/Start\]
```

A node with in an alternative trapezoid shape illustrates the end of a loop:
```{mermaid}
flowchart
  e[\End/]
```

Arrows in block diagrams indicate precedence: data input/output
to a step or logical succession of steps:
```{mermaid}
flowchart LR
  a[Step A]
  b[Step B]
  a --> b
```

Example diagram:
```{mermaid}
flowchart TD
  packet[/Packets/]
  annot[/Annotations/]
  a[Step A]
  b[Step B]
  packet --> a
  annot --> a
  a --> b
```
