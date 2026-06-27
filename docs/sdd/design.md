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

# Software design

## General

```{note}
The SDD shall describe the software architectural design.

The architecture structure of the software item shall be described, identifying the software components, their hierarchical relationships, any dependency and interfaces between them.

For flight software, the design shall reflect in flight modification requirements.

The structure in the following sections should be used.
```

## Overall architecture

```{note}
The SDD shall describe the software architectural design, from a static point of view and also, when the software to be developed has real time constraints, from a dynamic point of view, and from a behaviour point of view.

The software static architecture shall be summarized describing its components.

For real–time software, the software dynamic architecture shall be summarized describing its selected computational model.

> NOTE An analysable computational model generally consists in defining:
> - the types of components (objects) participating to the real‐time behaviour, from which the system is constructed (e.g. active‐periodic, active‐sporadic, protected, passive, actors, process, blocks, drivers)
> - the scheduling type (e.g. sequential or multithreaded), the scheduling model (e.g. cyclic or pre‐emptive, fixed or dynamic priority based), and the analytical model (e.g. Rate Monotonic Scheduling, Deadline Monotonic Scheduling, Earliest Deadline First), under which the system is executed and its associated mechanisms
> - the means of communication between components/objects (e.g. mailboxes, entry parameters)
> - the means of synchronization between components or objects (e.g. mutual exclusion, protected object entries, basic semaphores)
> - If applicable , the means of distribution and internode communication (e.g. virtual nodes, Remote Procedure Call)
>
> and (optional for non flight software):
>
> - the means of providing timing facilities (e.g. real clock, with or without interrupt, multiple interrupting count‐down, relative or absolute delays, timers time‐out)
> - the means of providing asynchronous transfer of control (e.g. watchdog to transfer control from anywhere to the reset sequence, software service of the underlying run‐time system to cause transfer of control within the local scope of the thread)

The description above. should consist in the following information:

  1. type of components participating to the real time behaviour,
  2. scheduling type (e.g. single or multi–threads),
  3. scheduling model (e.g. pre-emptive or not, fixed or dynamic priority based),
  4. analytical model (e.g. rate monotonic scheduling, deadline monotonic scheduling),
  5. Tasks identification and priorities,
  6. Means of communication and synchronization,
  7. Time management.

The software behaviour shall be described e.g. with automata or scenarios.

The software static, dynamic and behavioural architecture shall be described in accordance with the selected design method.

The SDD shall describe the error handling and fault tolerance principles (e.g. error detection, reporting, logging, and fault containment regions.)
```

## Software components design ‐ General

```{note}
The SDD shall describe:

  1. The software components, constituting the software item.
  2. The relationship between the software components.
  3. The purpose of each software component.
  4. For each software component, the development type (e.g. new development, software to be reused).
  5. If the software is written for the reuse,
  - its provided functionality from an external point of view,
    and
  - its external interfaces.
  6. Handling of existing reused components.

  > NOTE See Annex SRF.

The following shall apply to the software components specified above:

  1. Each software component is uniquely identified.
  2. When components are expressed as models, the supplier establishes a way to assign identifiers within the model for sake of traceability.
  3. The software requirements allocation provides for each software component;

  > NOTE The documented trace can be provided automatically by tools when models are used to express components.

The description of the components should be laid out hierarchically, in accordance with the following aspects for each component, further described in the next chapter:

- Component identifier
- Type
- Purpose
- Function
- Subordinates
- Dependencies
- Interfaces
- Resources
- References
- Data

  > NOTE Detailed description of the aspects for each component are described in the next section.
```

## Software components design ‐ Aspects of each component

### General

```{note}
This part of the DRD, as well as the next section, may be produced as the detailed design model of a tool, if agreed with the customer.
```

### Component identifier

```{note}
Each component should have a unique identifier.

The component should be named according to the rules of the programming language or operating system to be used.

A hierarchical naming scheme should be used that identifies the parent of the component (e.g. ParentName_ChildName).
```

### Type

```{note}
Component type should be described by stating its logical and physical characteristics.

The logical characteristics should be described by stating the package, library or class that the component belongs to.

The physical characteristics should be described by stating the type of component, using the implementation terminology (e.g. task, subroutine, subprogram, package and file).

> NOTE The contents of some components description clauses depend on the component type. For the purpose of this guide, the following categories are used: executable (i.e. contains computer instructions) or non–executable (i.e. contains only data).
```

### Purpose

```{note}
The purpose of a component should describe its trace to the software requirements that it implements.

> NOTE Backward traceability depends upon each component description explicitly referencing the requirements that justify its existence.
```

### Function

```{note}
The function of a component shall be described in the software architectural design.

The description specified above should be done by stating what the component does.

> NOTE 1 The function description depends upon the component type. Therefore, it can be a description of the process.

> NOTE 2 Process descriptions can use such techniques as structured English, precondition–postcondition specifications and state–transition diagrams.
```

### Subordinates

```{note}
The subordinates of a component should be described by listing the immediate children.

> NOTE 1 The subordinates of a unit are the units that are ’called by’ it. The subordinates of a database can be the files that ’compose’ it.

> NOTE 2 The subordinates of an object are the objects that are ’used by’ it.
```

### Dependencies

```{note}
The dependencies of a component should be described by listing the constraints upon its use by other components.

> NOTE Examples are:
- Operations to take component is called, place before this
- Operations that are excluded when this operation takes place.
```

### Interfaces

```{note}
Both control flow and data flow aspects of an interface shall be described for each “executable” component.

Data aspects of ’non executable’ components should be described.

The control flow to and from a component should be described in terms of how to start (e.g. subroutine call) and terminate (e.g. return) the execution of the component.

If the information above is implicit in the definition of the type of component, a description need not be done.

If control flows take place during execution (e.g. interrupt), they should be described.

The data flow input to and output from each component shall be described.

It should be ensured that data structures:

  1. are associated with the control flow (e.g. call argument list);
  2. interface components through common data areas and files.
```

### Resources

```{note}
The resources’ needs of a component should be described by itemising what the component needs from its environment to perform its function.

> NOTE 1 Items that are part of the component interface are excluded.

> NOTE 2 Examples of resources’ needs of a component are displays, printers and buffers.
```

### References

```{note}
Explicit references should be inserted where a component description uses or implies material from another document.
```

### Data

```{note}
The data internal to a component should be described.

> NOTE The amount of details to be provided depends strongly on the type of the component.

The data structures internal to a program or subroutine should also be described.

Data structure definitions shall include the:

  1. description of each element (e.g. name, type, dimension);
  2. relationships between the elements (i.e. the structure);
  3. range of possible values of each element;
  4. initial values of each element.
```

## Internal interface design

```{note}
The SDD shall describe the internal interfaces among the identified software components.

The interface data specified above, by component, shall be organized showing the complete interfaces map, using as appropriate diagrams or matrices supporting their cross–checking.

For each identified internal interface, all the defined data elements shall be included.

> NOTE The amount of detail to be provided depends strongly on the type of component.

The logical and physical data structure of files that interface major component should be postponed to the detailed design.

Data structure definitions shall include:

  1. the description of each element (e.g. name, type, dimension);
  2. the relationships between the elements (i.e. the structure);
  3. the initial values of each element.
```
