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

# Interface control document

## Introduction

This section constitutes the Interface control document (ICD) for the
msi-processor project.

It defines the public interfaces of the software.

## Software overview

```{note}
The ICD may reference the software overview done in the SRS,
if included in the on-line documentation.
```

## Requirements and design

### General provisions to the requirements in the IRD

```{note}
a. Each requirement shall be uniquely identified.

b. When requirements are expressed as models, the supplier shall establish a way to assign identifiers within the model for sake of traceability.

c. The traceability information of each requirement derived from higher level documentation, to the applicable higher level requirement, shall be stated.

> NOTE: The documented trace can be provided automatically by tools when models are used to express requirements.
```

### Interface requirements

```{note}
a. In case the requirements of the IRD need to be further detailed, the ICD shall list and describe the software item external interfaces.

b. The following interfaces shall be fully described:

  1. Interfaces between the software item and other software items;
  2. Interfaces between the software item and hardware products;
  3. Interfaces requirements relating to the man–machine interaction.
  4. This can be also information about e.g. :

  - detailed requirements on database structure
  - logical interface architecture
  - requirements on signal
  - timing requirements
  - required behaviour in case of error
  - telecommands (e.g. PUS selection, words contents)
  - observable data
  - telemetry
```

### Interface design

```{note}
a. The ICD shall describe the external interfaces design of the software item

b. The external interface may be expressed by models.

c. The following interfaces shall be fully described:

  1. Interfaces between the software item and other software items;
  2. Interfaces between the software item and hardware products;
  3. Interfaces requirements relating to the man–machine interaction.
  4. This can be also information about e.g.:

  - Physical interface architecture
  - Complete TM/TC plan
  - Design of all commands and telemetry stream
  - Protocol detailed implementation
  - Specific design requirements to be applied if the software is specified to be designed for intended reuse

d. The definition of each interface shall include at least the provided service, the description (name, type, dimension), the range and the initial value.

e. For each interface external to the software , this can be e.g. organized as follows:

  - Data item (Name , description, unique identifier, description, source, destination, unit of measure, limit/range, accuracy, precision, frequency, rate, legality checks, data type, data representation)
  - Message item
  - Communication protocol (by reference to the applicable documents)
```

## Validation requirements

```{note}
a. The ICD shall describe, per each uniquely identified requirement in <5>, the validation approach.

b. A validation matrix (requirements to validation approach correlation table) shall be utilized to describe the validation approach applicable to each requirement.
```

## Traceability

```{note}
a. The ICD shall report the traceability matrices

  1. from the upper level specification requirements to the requirements contained in <5> (forward traceability table), and
  2. from the requirements contained in <5> to the upper level applicable specification (backward traceability table).

In case the information in <7>a.1. is separately provided in the DJF, reference to this documentation shall be clearly stated.
```
