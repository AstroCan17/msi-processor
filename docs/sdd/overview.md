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

# Software design overview

```{note}
> NOTE The SDD briefly introduces the system context and design and discuss the background to the project detailed as follows.
```

## Software static architecture

```{note}
The SDD shall describe the architecture of the software item, as well as the main relationship with the major components identified.

The SDD shall also describe any system state or mode in which the software operates.

The SDD shall describe the separated mission and configuration data.

> NOTE Data can be classified in the following categories:
- data resulting from the mission analysis and which thus vary from one mission to another;
- reference data which are specific to a family of software product;
- reference data which never change;
- data depending only on the specific mission requirements (e.g. calibration of sensors);
- data required for the software operation which only vary the higher level system design (in which is embedded the software) is changed;
```

## Software dynamic architecture

```{note}
The SDD shall describe the design choices to cope with the real time constraints (e.g. selection and description of the computational model).
```

## Software behaviour

## Interfaces context

```{note}
The SDD shall identify all the external interfaces or refer to the ICD.

The description in should be based on system block diagram or context diagram to illustrate the relationship between this system and other systems.
```

## Long lifetime software

```{note}
The SDD shall describe the design choices to cope with the long planned lifetime of the software, in particular minimum dependency on the operating system and the hardware to improve portability.
```

## Memory and CPU budget

```{note}
The SDD shall document and summarize the allocation of memory and processing time to the software components.
```

## Design standards, conventions and procedures

```{note}
The SDD shall summarize (or reference in the SDP) the software methods adopted for the architectural and the detailed design.

> NOTE A design method offers often the following characteristics:
- decomposition of the software architecture in design objects having integral parts that communicate with each other and with the outside environment
- explicit recognition of typical activities of real‐time systems (i.e. cyclic and sporadic threads, protected resources)
- integration of appropriate scheduling paradigms with the design process
- explicit definition of the application timing requirements for each activity
- static verification of processor allocation, schedulability and timing analysis
- consistent code generation

b. The following information shall be summarized:

  1. software architectural design method;
  2. software detailed design method;
  3. code documentation standards;
  4. naming conventions;
  5. programming standards;
  6. intended list of reuse components
  7. main design trade‐off.
```
