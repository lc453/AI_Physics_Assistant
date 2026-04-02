from sympy import (sympify, symbols, solve, diff, integrate, dsolve, 
                   Function, Symbol, Eq, sin, cos, tan, exp, log, sqrt, pi, E, oo, I)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
)

# Define allowed transformations
TRANSFORMATIONS = (
    standard_transformations + (implicit_multiplication_application, convert_xor)
)

# Whitelist of allowed names that can appear in expressions
ALLOWED_LOCALS = {
    # symbols
    'x': symbols('x'),
    'y': symbols('y'),
    'z': symbols('z'),
    't': symbols('t'),
    # functions
    'f': Function('f'),
    'g': Function('g'),
    # Trig
    'sin': sin,
    'cos': cos,
    'tan': tan,
    # exp/log
    'exp': exp,
    'log': log,
    'sqrt': sqrt,
    # constants
    'pi': pi,
    'E': E,
    'oo': oo,
}

def safe_parse(expression: str):
    """
    Safely parese a math expression using sympy
    """
    try:
        expr = parse_expr(expression,local_dict=ALLOWED_LOCALS, transformations=TRANSFORMATIONS, evaluate=True)
        return expr
    except Exception as e:
        return f"Error parsing expression: {e}"
    
def safe_calculator(command: str, expression: str, **kwargs):
    """
    A safe math engine supporting multiple operations.

    Commands:
        - "evaluate": Evaluates/simplifies an expression
        - "solve": Solve an equation for a variable
        - "diff": Differentiates an expression
        - "integrate": Integrates an expression
        - "dsolve": Solves a differential equation
    """
    try:
        expr = safe_parse(expression)
        if isinstance(expr, str):
            return expr  # Return the error message from parsing
        match command:
            case "evaluate":
                result = sympify(expr)

                try:
                    numerical = float(result.evalf())
                    if numerical == int(numerical):
                        return str(numerical)
                    return str(numerical)
                except (TypeError, ValueError):
                    return str(result)
                
            case "solve":
                var = symbols(kwargs.get("variable", "x"))
                solutions = solve(expr, var)
                return str(solutions)
            
            case "diff":
                var = symbols(kwargs.get("variable", "x"))
                order = kwargs.get("order", 1)
                result = diff(expr, var, order)
                return str(result)
            
            case "integrate":
                var = symbols(kwargs.get("variable", "x"))
                bounds = kwargs.get("bounds", None)
                if bounds:
                    result = integrate(expr, (var, bounds[0], bounds[1]))
                else:
                    result = integrate(expr, var)
                return str(result)
            
            case "dsolve":
                func = Function(kwargs.get("function", "f"))
                var = symbols(kwargs.get("variable", "t"))
                # Reparse with the ODE in mind
                eq = Eq(expr, 0)
                result = dsolve(eq, func(var))
                return str(result)
            
            case _:
                return f"Unknown command: {command}"


    except Exception as e:
        return f"Error parsing expression: {e}"

def python_calculator(expression: str):
    """
    Safely executes a math expression. (If the expression is not safe, it had better not run it)
    """
    try:
        # VERY basic sandbox (good enough for demo)
        allowed_names = {"__builtins__": {}}
        result = eval(expression, allowed_names, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"