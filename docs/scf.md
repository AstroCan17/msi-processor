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

# Software configuration file

## Introduction

This page constitutes the Software configuration file (SCF) for the
msi-processor project, describing the
contents of the software configuration item.

## Software configuration item overview

```{note}
The SCF shall contain a brief description of the software configuration item.

For the software configuration item, the following information shall be provided:

  1. how to get information about the software configuration item;
  2. composition of the software configuration item: code, documents;
  3. means to develop, modify, install, run the software configuration item;
  4. differences from the reference or previous version, cf Software release document
  5. status of software problem reports, software change requests, and software waivers and deviations related to the software configuration item, cf Software release document.
```

## Inventory of materials

The software configuration item is delivered in a Git repository on the EOPF.
The software configuration item is constituted of all files contained on
the `main` branch of the Git repository.

```{note}
Provide a link to the Git repository or repositories constituting
the software configuration item.
```
```{note}
If the software configuration item is also constituted of other elements,
then they shall be listed.
```

## Baseline documents

The following documents are included in the online documentation:

- [Detailed processing model](./dpm/index)
- [Interface control document](./icd)
- Software configuration file (this document)
- [Software design document](./sdd/index)
- [Software installation manual](./sim)
- [Software release note](./srn)
- [Software reuse file](./srf)
- [Software user manual](./sum/index)

```{note}
The SCF shall identify and list all other documents applicable to the
delivered software configuration item version.
```

## Inventory of software configuration item

```{note}
The SCF shall describe the content of the software configuration item.

A link shall be provided to the EOPF Git repositories and the branch(es)
containing the software configuration item.
```

## Means necessary for the software configuration item

```{note}
The SCF shall describe all items (i.e. hardware and software) that are not part of the software configuration item, and which are necessary to develop, modify, generate and run the software configuration item, including:

  1. items related to software development (e.g. compiler name and version, linker, and libraries);
  2. build files and software generation process;
  3. other software configuration items.
```

## Installation instructions

Please see the [Software installation manual](./sim).

```{note}
The SCF shall describe how to install the software configuration item version,
in the case where the general installation instructions do not apply
or in case of specificities linked to this particular version.
```

## Change list

Please see the [Software release note](./srn) for the changes incorporated
into this version of the software configuration item.

## Auxiliary information

```{note}
The SCF shall include any auxiliary information to describe the software configuration.
```

## Possible problems and known errors

Please see the [Software release note](./srn) for the known errors
concerning this software configuration item version.
