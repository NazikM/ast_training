import ast
import sys
from _ast import AST

excluded = []


def change_case(name: str):
    res = [name[0]]
    for c in name[1:]:
        if c.isupper():
            res.extend(('_', c.lower()))
        else:
            res.append(c)
    return ''.join(res)


class MyTransformer(ast.NodeTransformer):
    def generic_visit(self, node):
        for field, old_value in ast.iter_fields(node):
            if field == "id" and node.id not in excluded:
                node.id = change_case(node.id)
            elif field == "name":
                node.name = change_case(node.name)

            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node

    def visit_ClassDef(self, node):
        excluded.append(node.name)
        for value in node.body:
            if isinstance(value, AST):
                self.visit(value)
        return node


if len(sys.argv) != 2:
    exit()

name = sys.argv[1]
visitor = MyTransformer()
with open(name) as f:
    tree = ast.parse(f.read())
node = visitor.visit(tree)
with open(name.replace('.py', '_changed.py'), 'w') as f2:
    f2.write(ast.unparse(node))


