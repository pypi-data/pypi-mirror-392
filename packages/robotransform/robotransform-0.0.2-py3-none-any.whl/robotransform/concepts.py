from __future__ import annotations
from typing import Type as ClassType, Any, List, Optional, Union


# TODO Flatten this a little bit

class Node:
    def __init__(self, parent: Optional[Any] = None):
        self.parent = parent


class ControllerDef(Node):
    def __init__(self, name, uses, provides, requires, connections, machines, events, operations, variables,
                 parent: Any):
        super().__init__(parent)
        self.name = name
        self.uses = uses
        self.provides = provides
        self.requires = requires
        self.connections = connections
        self.machines = machines
        self.events = events
        self.operations = operations
        self.variables = variables

    def __repr__(self):
        use_count = len(self.uses)
        provide_count = len(self.provides)
        require_count = len(self.requires)
        connection_count = len(self.connections)
        machine_count = len(self.machines)
        event_count = len(self.events)
        operation_count = len(self.operations)
        variable_count = len(self.variables)
        return f"{self.name}: ({use_count} uses), ({provide_count} provides), ({require_count} requires), ({connection_count} connections), ({machine_count} machines, ({event_count} events), ({operation_count} operations), ({variable_count} variables)"


class Variable(Node):
    def __init__(self, name: str, kind, initial, parent: Any):
        super().__init__(parent)
        self.name = name
        self.type = kind
        self.initial = initial


class Type(Node):
    def __init__(self, source: FunctionType, target: Optional[Type], parent: Any):
        super().__init__(parent)
        self.source = source
        self.target = target

    def __repr__(self):
        if self.target:
            return f"{self.source} <-> {self.target}"
        return f"{self.source}"


class Field(Node):
    def __init__(self, name: str, kind: Type, parent: Any):
        super().__init__(parent)
        self.name = name
        self.type = kind

    @property
    def typename(self) -> str:
        return str(self.type)

    def __repr__(self):
        return f"{self.name}[{self.type}]"


class RecordType(Node):
    def __init__(self, name: str, fields: List[Field], parent: Any):
        # Can be datatype or record
        super().__init__(parent)
        self.name = name
        self.fields = fields

    def __repr__(self):
        return f"{self.name}({self.fields})"


class Function(Node):
    def __init__(self, name: str, parameters, kind, body, parent: Any):
        super().__init__(parent)
        self.name = name
        self.parameters = parameters
        self.kind = kind
        self.body = body


class RCModule(Node):
    def __init__(self, name: str, connections, nodes, parent: Any):
        super().__init__(parent)
        self.name = name
        self.connections = connections
        self.nodes = nodes


class VariableList(Node):
    def __init__(self, modifier, variables, parent: Any):
        super().__init__(parent)
        self.modifier = modifier
        self.variables = variables


class Interface(Node):
    def __init__(self, name: str, operations, events, variables: List[VariableList], clocks, parent: Any):
        super().__init__(parent)
        self.name = name
        self.operations = operations
        self.events = events
        self._variables = variables
        self.clocks = clocks

    @property
    def variables(self) -> List[Variable]:
        return [var for v in self._variables for var in v.variables]


class RoboticPlatformDef(Node):
    def __init__(self, name: str, uses, provides, requires, variables, operations, events, parent: Any):
        super().__init__(parent)
        self.name = name
        self.uses = uses
        self.provides = provides
        self.requires = requires
        self._variables = variables
        self.operations = operations
        self.events = events

    @property
    def variables(self) -> List[Variable]:
        return [var for v in self._variables for var in v.variables]


class OperationDef(Node):
    def __init__(self, name: str, parent: Any):
        super().__init__(parent)
        self.name = name


class RCPackage(Node):
    def __init__(self, name: QualifiedName, imports: List[Import], controllers: List[ControllerDef],
                 modules: List[RCModule], functions: List[Function], types: List[RecordType],
                 machines: List[StateMachineDef], interfaces: List[Interface], robots: List[RoboticPlatformDef],
                 operations: List[OperationDef]):
        super().__init__()
        self.name = name
        self.imports = imports
        self.controllers = controllers
        self.modules = modules
        self.functions = functions
        self.types = types
        self.machines = machines
        self.interfaces = interfaces
        self.robots = robots
        self.operations = operations

    def __repr__(self):
        return f"{self.name}"


class QualifiedName(Node):
    def __init__(self, parts: List[str], parent: Any):
        super().__init__(parent)
        self.parts = parts

    def __repr__(self):
        return "".join(self.parts)


class StateMachineDef(Node):
    def __init__(self, name, interfaces, provides, requires, variables, events, nodes, transitions, clocks,
                 parent: Any):
        super().__init__(parent)
        self.name = name
        self.interfaces = interfaces
        self.provides = provides
        self.requires = requires
        self._variables = variables
        self.events = events
        self.nodes = nodes
        self.clocks = clocks
        self.transitions = transitions

    @property
    def variables(self) -> List[Variable]:
        return [var for v in self._variables for var in v.variables]


class Transition(Node):
    def __init__(self, name, source, target, trigger, reset, deadline, condition, action, parent: Any):
        super().__init__(parent)
        self.name = name
        self.source = source
        self.target = target


class QualifiedNameWithWildcard(Node):
    def __init__(self, name, parent: Any):
        super().__init__(parent)
        self.name = name

    def __repr__(self):
        return str(self.name) + "::*"


class Import(Node):
    def __init__(self, name, parent: Any):
        super().__init__(parent)
        self.name = name

    def __repr__(self):
        return str(self.name)


class FunctionType(Node):
    def __init__(self, source: ProductType, target: Optional[FunctionType], parent: Any):
        super().__init__(parent)
        self.source = source
        self.target = target

    def __repr__(self):
        if self.target:
            return f"{self.source} -> {self.target}"
        return f"{self.source}"


class TypeRef(Node):
    def __init__(self, kind, parent: Any):
        super().__init__(parent)
        self.type = kind

    def __repr__(self):
        return f"{self.type}"


class VectorType(Node):
    # def __init__(self, source: Union[VectorDef, MatrixDef, TypeRef], parent: Any):
    def __init__(self, source: Union[TypeRef], parent: Any):
        super().__init__(parent)
        self.source = source

    def __repr__(self):
        return f"{self.source}"


class ProductType(Node):
    def __init__(self, types: List[Union[VectorType, TypeRef]], parent: Any):
        super().__init__(parent)
        self.types = types

    def __repr__(self):
        if len(self.types) > 1:
            joined = "*".join(map(str, self.types))
            return f"{joined}]"
        return f"{self.types[0]}"


class SeqType(Node):
    def __init__(self, domain, parent: Any):
        super().__init__(parent)
        self.domain = domain

    def __repr__(self):
        return f"Seq({self.domain})"


class Event(Node):
    def __init__(self, name: str, broadcast: bool, kind: Type, parent: Any):
        super().__init__(parent)
        self.name = name
        self.broadcast = broadcast
        self.type = kind

    def __repr__(self):
        return f"Event: {self.name} {self.broadcast, self.type}"


def all_concepts() -> List[ClassType]:
    import inspect
    return [
        obj for _, obj in globals().items()
        if inspect.isclass(obj) and obj.__module__ == __name__
    ]
