# Diagrams

We are using [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) to document the architecture and design of Tock.  C4-PlantUML combines the benefits of PlantUML and the C4 model for providing a simple way of describing and communicate software architectures.  [PlantUML](http://en.plantuml.com/) is an open source project that allows you to create UML diagrams using code.  [C4 model](https://c4model.com/) for software architecture is an "abstraction-first" approach to diagramming, based upon abstractions that reflect how software architects and developers think about and build software.

## Structures
Each `.puml` file in this folder represents one diagram written in C4-PlantUML.  The file structure is as follows:
- `@startuml`
- included files - specific type of C4 diagram this file represents and other files it uses
- styling - styling for this particular file if it differs from those specified in included files
- elements - define elements like system, container, person
- relationships - define relationships between elements
- `@enduml`


## Styling
Currently we are using C4 styling as a starting point, but we may add specific styling for each diagram.  We are using [**skinparam**](https://plantuml.com/de/skinparam) instead of [**style**](https://plantuml.com/de/style-evolution).  The reasion is that:
- C4-Plantuml is still using **skinparam**
- if we use **style** in file, it wipes out all C4-Plantuml existing styling, which means we need to rewrite all styling, which we do not need to at this point.
