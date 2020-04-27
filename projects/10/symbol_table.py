from dataclasses import dataclass


class SymbolTable:
    def __init__(self):
        self.static_scope = Scope()
        self.cur_scope = self.static_scope

    def add(self, name, var_type, kind):
        self.cur_scope.add_variable(name, var_type, kind)

    def lookup(self, name):
        return self.cur_scope.lookup(name)

    def enter_new_scope(self):
        self.cur_scope = Scope(enclosing_scope=self.cur_scope)

    def close_scope(self):
        if self.cur_scope is not self.static_scope:
            self.cur_scope = self.cur_scope.enclosing_scope

    def n_locals(self):
        return self.cur_scope.get_idx('local')

    def n_fields(self):
        return self.static_scope.get_idx('field')


class Scope:
    def __init__(self, enclosing_scope=None):
        self.enclosing_scope = enclosing_scope
        self.variables = {}

    def add_variable(self, name, var_type, kind):
        assert name not in self.variables, 'Variable already declared'
        idx = self.get_idx(kind)
        var = Variable(var_type, kind, idx)
        self.variables[name] = var

    def lookup(self, name):
        if name not in self.variables:
            if self.enclosing_scope is not None:
                return self.enclosing_scope.lookup(name)
            else:
                raise KeyError(f'ERROR: variable {name} not found')
        return self.variables[name]

    def get_idx(self, kind):
        return len([k for k, v in self.variables.items() if v.kind == kind])


@dataclass
class Variable:
    var_type: str
    kind: str
    idx: int
