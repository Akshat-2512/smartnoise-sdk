from snsql._ast.tokens import *
import numpy as np
import operator

ops = {
    "+": operator.add,
    "-": operator.sub,
    "/": operator.truediv,
    "*": operator.mul,
    "%": operator.mod,
}

funcs = {
    "abs": np.abs,
    "ceil": np.ceil,
    "ceiling": np.ceil,
    "floor": np.floor,
    "sign": np.sign,
    "sqrt": np.sqrt,
    "square": np.square,
    "exp": np.exp,
    "ln": np.log,
    "log": np.log,
    "log10": np.log10,
    "log2": np.log2,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "asin": np.arcsin,
    "acos": np.arccos,
    "atan": np.arctan,
    "atanh": np.arctanh,
    "degrees": np.degrees,
}

bare_funcs = {
    "pi": lambda: np.pi,
    "rand": lambda: np.random.uniform(),
    "random": lambda: np.random.uniform(),
    "newid": lambda: "-".join(
        [
            "".join([hex(np.random.randint(0, 65535)) for v in range(2)]),
            [hex(np.random.randint(0, 65535))],
            [hex(np.random.randint(0, 65535))],
            [hex(np.random.randint(0, 65535))],
            "".join([hex(np.random.randint(0, 65535)) for v in range(3)]),
        ]
    ),
}


class ArithmeticExpression(SqlExpr):
    """A simple arithmetic expression with left and right side and operator"""

    def __init__(self, left, op, right):
        self.left = left
        self.right = right
        self.op = op

    def type(self):
        if self.op == "/":
            return "float"
        elif self.op == "%":
            return "int"
        elif self.op in ["*", "+", "-"]:
            return min([self.left.type(), self.right.type()])

    def _lower(self):
        ll = self.left._lower()
        ul = self.left._upper()
        ur = self.right._upper()
        lr = self.right._lower()
        if ( ur is None or lr is None ) and (ul is None or ll is None):
            return None
        if ( ur is None or lr is None ) and type(self.right) is Literal and self.right.type() in ["int", "float"]:
            v = self.right.value
            if self.op in ["+"]:
                return min(ll+v , ul+v)
            elif self.op in ["-"]:
                return min(ll-v , ul-v)
            elif self.op == "%":
                if v ==0:
                    raise ValueError(f"undefined")
                return 0
            elif self.op == "*":
                return min(ll*v , ul*v)
            elif self.op == "/":
                if v == 0:
                    raise ValueError(f"division by zero")
                else:
                    return min(ll/v , ul/v)
            else:
                return None
            
        if (ul is None or ll is None) and type(self.left) is Literal and self.left.type() in ["int", "float"]:
            v = self.left.value
            if self.op in ["+"]:
                return min(v+lr, v+ur)
            elif self.op in ["-"]:
                return min(v-lr, v-ur)
            elif self.op == "%":
                if lr*ur<=0:
                    raise ValueError(f"undefined")
                return 0
            elif self.op == "*":
                return min(v*lr, v*ur)
            elif self.op == "/":
                if lr*ur<=0:
                    raise ValueError(f"unbounded output")
                else:
                    return min(v/lr, v/ur)
            else:
                return None
        if (ul is not None and ll is not None)  and ( ur is not None and lr is not None ):
            if self.op in ["+"]:
                return min((ll+lr),(ul+ur), (ul+lr), (ll+ur))
            elif self.op in ["-"]:
                return min((ll-lr),(ul-ur), (ul-lr), (ll-ur))
            elif self.op == "%":
                if lr*ur<=0:
                    raise ValueError(f"undefined")
                return min((ll%lr),(ul%ur), (ul%lr), (ll%ur))
            elif self.op == "*":
                return min((ll*lr),(ul*ur), (ul*lr), (ll*ur))
            elif self.op == "/":
                if lr*ur<=0:
                    raise ValueError(f"unbounded output")
                else:
                    return  min((ll/lr),(ul/ur), (ul/lr), (ll/ur))
            else:
                return None
    def _upper(self):
        ll = self.left._lower()
        ul = self.left._upper()
        ur = self.right._upper()
        lr = self.right._lower()
        if ( ur is None or lr is None ) and (ul is None or ll is None):
            return None
        if ( ur is None or lr is None ) and type(self.right) is Literal and self.right.type() in ["int", "float"]:
            v = self.right.value
            if self.op in ["+"]:
                return max(ll+v , ul+v)
            elif self.op in ["-"]:
                return max(ll-v , ul-v)
            elif self.op == "%":
                if v ==0:
                    raise ValueError(f"undefined")
                return 0
            elif self.op == "*":
                return max(ll*v , ul*v)
            
            elif self.op == "/":
                if v == 0:
                    raise ValueError(f"division by zero")
                else:
                    return max(ll/v , ul/v)
            else:
                return None
            
        if (ul is None or ll is None) and type(self.left) is Literal and self.left.type() in ["int", "float"]:
            v = self.left.value
            if self.op in ["+"]:
                return max(v+lr, v+ur)
            elif self.op in ["-"]:
                return max(v-lr, v-ur)
            elif self.op == "%":
                if lr*ur<=0:
                    raise ValueError(f"undefined")
                return 0
            elif self.op == "*":
                return max(v*lr, v*ur)
            elif self.op == "/":
                if lr*ur<=0:
                    raise ValueError(f"unbounded output")
                else:
                    return max(v/lr, v/ur)
            else:
                return None
        if (ul is not None and ll is not None) and ( ur is not None and lr is not None ):
            if self.op in ["+"]:
                return max((ll+lr),(ul+ur), (ul+lr), (ll+ur))
            elif self.op in ["-"]:
                return max((ll-lr),(ul-ur), (ul-lr), (ll-ur))
            elif self.op == "%":
                if lr*ur<=0:
                    raise ValueError(f"undefined")
                return max((ll%lr),(ul%ur), (ul%lr), (ll%ur))
            elif self.op == "*":
                return max((ll*lr),(ul*ur), (ul*lr), (ll*ur))
            elif self.op == "/":
                if lr*ur<=0:
                    raise ValueError(f"unbounded output")
                else:
                    return  max((ll/lr),(ul/ur), (ul/lr), (ll/ur))
            else:
                return None

    def sensitivity(self):
        ls = self.left.sensitivity()
        rs = self.right.sensitivity()
        ll = self.left._lower()
        ul = self.left._upper()
        ur = self.right._upper()
        lr = self.right._lower()
        # not sure about modulus sensitivty calculation
        if rs is None and ls is None:
            return None
        if rs is None and type(self.right) is Literal and self.right.type() in ["int", "float"]:
            v = self.right.value
            if self.op in ["+"]:
                return max(abs(ll+v), abs(ul+v))
            elif self.op in ["-"]:
                return max(abs(ll-v), abs(ul-v))
            elif self.op == "%":
                if v ==0:
                    raise ValueError(f"undefined")
                return self.right.value
            elif self.op == "*":
                return max(abs(ll*v), abs(ul*v))
            elif self.op == "/":
                if v == 0:
                    raise ValueError(f"division by zero")
                else:
                    return max(abs(ll/v), abs(ul/v))
            else:
                return None
        if ls is None and type(self.left) is Literal and self.left.type() in ["int", "float"]:
            v = self.left.value
            if self.op in ["+"]:
                return max(abs(v+lr), abs(v+ur))
            elif self.op in ["-"]:
                return max(abs(v-lr), abs(v-ur))
            elif self.op == "%":
                if lr*ur<=0:
                    raise ValueError(f"undefined")
                return max(abs(v%lr),abs(v%ur))
            elif self.op == "*":
                return max(abs(lr*v), abs(ur*v))
            elif self.op == "/":
                if lr*ur<=0:
                    raise ValueError(f"unbounded output")
                else:
                    return max(abs(v/lr), abs(v/ur))
            else:
                return None
        if ls is not None and rs is not None:
            if self.op in ["+"]:
                return max(abs(ll+lr), abs(ul+ur)  , abs(ul+lr), abs(ll+ur))
            elif self.op in ["-"]:
                return max(abs(ll-lr), abs(ul-ur) , abs(ul-lr), abs(ll-ur))
            elif self.op == "%":
                if lr*ur<=0:
                    raise ValueError(f"undefined")
                return max(abs(ll%lr), abs(ul%ur) , abs(ul%lr), abs(ll%ur))
            elif self.op == "*":
                return max(abs(ll*lr), abs(ul*ur)  , abs(ul*lr), abs(ll*ur))
            elif self.op == "/":
                if lr*ur<=0:
                    raise ValueError(f"unbounded output")
                else:
                    return  max(abs(ll/lr), abs(ul/ur)  , abs(ul/lr), abs(ll/ur))
            else:
                return None

    def children(self):
        return [self.left, self.op, self.right]

    def evaluate(self, bindings):
        l = self.left.evaluate(bindings)
        r = self.right.evaluate(bindings)
        if self.op == '/' and int(r) == 0:
            return 0
        else:
            return ops[self.op](l, r)

    def symbol(self, relations):
        return ArithmeticExpression(
            self.left.symbol(relations), self.op, self.right.symbol(relations)
        )


class MathFunction(SqlExpr):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression
    def symbol_name(self):
        prefix = self.name.lower() + "_"
        return self.prepend(prefix, self.expression.symbol_name())

    def prepend(self, prefix, value):
        # handles generation of a new identifier while honoring escaping rules
        if value == "" or not value[0] in ['"', "`", "["]:
            return prefix + value
        value = value.replace("`", '"').replace("[", '"').replace("]", '"')
        parts = value.split('"')
        if len(parts) == 3:
            return '"' + prefix + parts[1] + '"'
        else:
            return prefix + "_x_" + value.replace('"', "").replace(" ", "")

    def children(self):
        return [self.name, Token("("), self.expression, Token(")")]

    def type(self):
        return "float"

    def _lower(self):
        l = self.expression._lower()
        u = self.expression._upper()
        if funcs[self.name.lower()] == "abs":
            if l*u<=0:
                return 0
        elif funcs[self.name.lower()] == "square":
            if l*u<=0:
                return 0
        elif funcs[self.name.lower()] == "sin":
            k = 3 * np.pi / 2

            # Find the smallest integer n such that L <= k + 2n*pi
            n_start = np.ceil((l - k) / (2 * np.pi))
            
            # Find the largest integer n such that k + 2n*pi <= U
            n_end = np.floor((u - k) / (2 * np.pi))
            
            # Check if there exists a valid n within the range
            if n_start <= n_end:
                x = k + 2 * n_start * np.pi
                return -1
            else: 
                return min(np.sin(l),np.sin(u))
            
        elif funcs[self.name.lower()] == "cos":
            k =np.pi  # This is the base case where cos(x) = -1

            # Find the smallest integer n such that L <= k + 2n*pi
            n_start = np.ceil((l- k) / (2 * np.pi))

            # Find the largest integer n such that k + 2n*pi <= U
            n_end = np.floor((u - k) / (2 * np.pi))

            # Check if there exists a valid n within the range
            if n_start <= n_end:
                x = k + 2 * n_start * np.pi  # Any valid x in the range
                return -1
            else: 
                return min(np.cos(l),np.cos(u))
        elif funcs[self.name.lower()] == "tan":
            k = -np.pi / 2  # This is the base point where the asymptote occurs.

            # Find the smallest integer n such that L <= k + n*pi
            n_start = np.ceil((l - k) / np.pi)

            # Find the largest integer n such that k + n*pi <= U
            n_end = np.floor((u - k) / np.pi)

            # Check if there exists a valid n within the range
            if n_start <= n_end:
                x = k + n_start * np.pi  # Any valid x in the range
                return -np.inf
            else:
                return min(np.tan(l),np.tan(u))
        return min(funcs[self.name.lower()](l),funcs[self.name.lower()](u))
    
    def _upper(self):
        l = self.expression._lower()
        u = self.expression._upper()
        if funcs[self.name.lower()] == "sin":
            k = np.pi / 2

            # Find the smallest integer n such that L <= k + 2n*pi
            n_start = np.ceil((l - k) / (2 * np.pi))
            
            # Find the largest integer n such that k + 2n*pi <= U
            n_end = np.floor((u - k) / (2 * np.pi))
            
            # Check if there exists a valid n within the range
            if n_start <= n_end:
                x = k + 2 * n_start * np.pi
                return 1
            else: 
                return max(np.sin(l),np.sin(u))
            
        elif funcs[self.name.lower()] == "cos":
            k = 0 # This is the base case where cos(x) = -1

            # Find the smallest integer n such that L <= k + 2n*pi
            n_start = np.ceil((l- k) / (2 * np.pi))

            # Find the largest integer n such that k + 2n*pi <= U
            n_end = np.floor((u - k) / (2 * np.pi))

            # Check if there exists a valid n within the range
            if n_start <= n_end:
                x = k + 2 * n_start * np.pi  # Any valid x in the range
                return 1
            else: 
                return max(np.cos(l),np.cos(u))
        elif funcs[self.name.lower()] == "tan":
            k = np.pi / 2  # This is the base point where the asymptote occurs.

            # Find the smallest integer n such that L <= k + n*pi
            n_start = np.ceil((l - k) / np.pi)

            # Find the largest integer n such that k + n*pi <= U
            n_end = np.floor((u - k) / np.pi)

            # Check if there exists a valid n within the range
            if n_start <= n_end:
                x = k + n_start * np.pi  # Any valid x in the range
                return np.inf
            else:
                return max(np.tan(l),np.tan(u))
        return max(funcs[self.name.lower()](l),funcs[self.name.lower()](u))
    
    def sensitivity(self):
        return max(abs(self._lower()), abs(self._upper()))

    def evaluate(self, bindings):
        exp = self.expression.evaluate(bindings)
        return funcs[self.name.lower()](exp)

    def symbol(self, relations):
        return MathFunction(self.name, self.expression.symbol(relations))


class PowerFunction(SqlExpr):
    def __init__(self, expression, power):
        self.expression = expression
        self.power = power

    def children(self):
        return [Token("POWER"), Token("("), self.expression, Token(","), self.power, Token(")")]

    def type(self):
        return self.expression.type()

    def _lower(self):
        l = self.expression._lower()
        u = self.expression._upper()
        if self.power%2==0 and l*u<=0:
            return 0
        return min(l**self.power, u**self.power)
    
    def _upper(self):
        l = self.expression._lower()
        u = self.expression._upper()
        return max(l**self.power, u**self.power)
    
    def sensitivity(self):
        return max(abs(self._lower()), abs(self._upper()))

    def evaluate(self, bindings):
        exp = self.expression.evaluate(bindings)
        return np.power(exp, self.power.value)

    def symbol(self, relations):
        return PowerFunction(self.expression.symbol(relations), self.power.symbol(relations))


class BareFunction(SqlExpr):
    def __init__(self, name):
        self.name = name

    def children(self):
        return [self.name, Token("("), Token(")")]

    def evaluate(self, bindings):
        vec = bindings[list(bindings.keys())[0]]  # grab the first column
        return [bare_funcs[self.name.lower()]() for v in vec]


class RoundFunction(SqlExpr):
    def __init__(self, expression, decimals):
        if not isinstance(decimals.value, int):
            raise ValueError("Decimals argument must be integer")
        self.expression = expression
        self.decimals = decimals

    def children(self):
        start = [Token("ROUND"), Token("("), self.expression]
        end = [Token(")")]
        middle = [] if not self.decimals else [Token(","), self.decimals]
        return start + middle + end

    def evaluate(self, bindings):
        decimals = self.decimals.evaluate(bindings)
        exp = self.expression.evaluate(bindings)
        return np.round(exp, decimals if decimals else 0)

    def symbol(self, relations):
        return RoundFunction(self.expression.symbol(relations), self.decimals)


class TruncFunction(SqlExpr):
    def __init__(self, expression, decimals):
        if not isinstance(decimals.value, int):
            raise ValueError("Decimals argument must be integer")
        self.expression = expression
        self.decimals = decimals
    def children(self):
        start = [Token("TRUNCATE"), Token("("), self.expression]
        end = [Token(")")]
        middle = [] if not self.decimals else [Token(","), self.decimals]
        return start + middle + end
    def evaluate(self, bindings):
        decimals = self.decimals.evaluate(bindings)
        exp = self.expression.evaluate(bindings)
        if decimals == None:
            decimals = 0
        shift = float(10 ** decimals)
        v = float(exp * shift)
        v = np.floor(v)
        v = v / shift
        if isinstance(exp, int):
            v = int(v)
        return v
    def symbol(self, relations):
        return TruncFunction(self.expression.symbol(relations), self.decimals)
