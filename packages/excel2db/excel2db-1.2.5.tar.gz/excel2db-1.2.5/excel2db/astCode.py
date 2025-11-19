import ast

class SafeExpressionValidator(ast.NodeVisitor):
    allowed_nodes = {
        ast.Expression,
        ast.BoolOp, ast.BinOp, ast.UnaryOp,
        ast.Compare,
        ast.Name, ast.Load,
        ast.Constant,  # for numbers
        ast.And, ast.Or, ast.Not,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
        ast.Mod, ast.Pow,
        ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    }

    allowed_names = {"row"}

    def visit(self, node):
        if type(node) not in self.allowed_nodes:
            raise ValueError(f"Unsafe expression: {type(node).__name__}")
        super().visit(node)

    def visit_Name(self, node):
        if node.id not in self.allowed_names:
            raise ValueError(f"Unsupported variable: {node.id}")

def compile_safe_expr(expr: str):
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        raise ValueError("Invalid expression syntax")

    SafeExpressionValidator().visit(tree)

    code = compile(tree, "<user_expr>", "eval")

    def func(row: int):
        return eval(code, {"__builtins__": {}}, {"row": row})

    return func


if __name__=="__main__":
    expr = "row > 10 and row % 3 == 1"
    f = compile_safe_expr(expr)

    print(f(11))  # True
    print(f(9))  # False
    print(f(13))  # True