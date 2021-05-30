import builtins as bbbahfuhva
import io as oafhuihfd
import contextlib as vbnjvd
import traceback as errnsf
import sys as sysiajghf


@vbnjvd.contextmanager
def stdoutIO(stdout=None):
    old = sysiajghf.stdout
    if stdout is None:
        stdout = oafhuihfd.StringIO()
    sysiajghf.stdout = stdout
    yield stdout
    sysiajghf.stdout = old


ofjasfgshs = {}

gkasdfbvvs = [
    'None',
    'False',
    'True',
    'abs',
    'bool',
    'bytes',
    'callable',
    'chr',
    'complex',
    'divmod',
    'dir',
    'dict',
    'float',
    'hash',
    'hex',
    'id',
    'int',
    'input',
    '__import__',
    'isinstance',
    'issubclass',
    'len',
    'list',
    'oct',
    'ord',
    'pow',
    'print',
    'range',
    'repr',
    'round',
    'slice',
    'set',
    'sorted',
    'str',
    'tuple',
    'zip'
]

afuhvbsuasf = [
    'ArithmeticError',
    'AssertionError',
    'AttributeError',
    'BaseException',
    'BufferError',
    'BytesWarning',
    'DeprecationWarning',
    'EOFError',
    'EnvironmentError',
    'Exception',
    'FloatingPointError',
    'FutureWarning',
    'GeneratorExit',
    'IOError',
    'ImportError',
    'ImportWarning',
    'IndentationError',
    'IndexError',
    'KeyError',
    'KeyboardInterrupt',
    'LookupError',
    'MemoryError',
    'NameError',
    'NotImplementedError',
    'OSError',
    'OverflowError',
    'PendingDeprecationWarning',
    'ReferenceError',
    'RuntimeError',
    'RuntimeWarning',
    'StopIteration',
    'SyntaxError',
    'SyntaxWarning',
    'SystemError',
    'SystemExit',
    'TabError',
    'TypeError',
    'UnboundLocalError',
    'UnicodeDecodeError',
    'UnicodeEncodeError',
    'UnicodeError',
    'UnicodeTranslateError',
    'UnicodeWarning',
    'UserWarning',
    'ValueError',
    'Warning',
    'ZeroDivisionError',
]

fghsdva = [
    'asyncio'
    'aiohttp',
    'abc',
    'ast',
    'array',
    'binascii',
    'difflib',
    'base64',
    'boto',
    'calendar',
    'cmath',
    'codecs',
    'crypt',
    'datetime',
    'decimal',
    'enum',
    'hashlib',
    'html',
    'http',
    'json',
    'numbers',
    'numpy',
    'math',
    'operator',
    'random',
    'requests',
    'string',
]

gkasdfbvvs.extend([
    '__build_class__',  # needed to define new classes
])

for name in gkasdfbvvs:
    ofjasfgshs[name] = getattr(bbbahfuhva, name)

for name in afuhvbsuasf:
    ofjasfgshs[name] = getattr(bbbahfuhva, name)


def safe_exec(code):
    split_code = code.splitlines()

    for line in split_code:
        if "import" in line:
            if "os" in line or "sys" in line or "time" in line:
                return f':warning: Your eval job has completed with return code 1.\n\n```{line}\n[Unsupported module]             ```'
            elif any(module in line for module in fghsdva):
                pass
            else:
                return f':x: Your eval job has completed with return code 1.\n\n```{line}\nModuleNotFoundError: No module named \'{line.replace("import ", "")}\'             ```'

    while "`" in code:
        code = code.replace("`", "")
    if code.startswith("""
"""):
        code = code[1:]
    if code.startswith("python"):
        code = code[6:]

    with stdoutIO() as s:
        try:

            exec(code, {'__builtins__': ofjasfgshs})

            if s.getvalue() == "" or s.getvalue is None:
                return f":warning: Your eval job has completed with return code 0.\n\n```[No output]             ```"

            output = s.getvalue()

            split_output = output.splitlines()

            if len(split_output) > 1:
                i = 1
                for line in split_output:
                    if i in range(1, 10):
                        line_num = f"0{i}"
                        split_output[i - 1] = f"{line_num} | {line}"
                    else:
                        split_output[i - 1] = f"{i} | {line}"
                    i += 1

                if len(split_output) > 10:
                    split_output = split_output[:10]
                    split_output.append("... [truncated - too many lines]")

            output = """
""".join(split_output)

            return f":white_check_mark: Your eval job has completed with return code 0.\n\n```{output}```\n"
        except Exception as exc:
            if str(exc) == "end of time":
                return f":warning: Your eval job has completed with return code 143 (SIGTERM).\n\n```... [execution took too long]```\n"

            error = errnsf.format_exception(sysiajghf.exc_info()[0], sysiajghf.exc_info()[1], sysiajghf.exc_info()[2])
            try:
                error_type = error[5]
            except IndexError:
                error_type = error[3]
            error_path = error[2].split()
            i = 0
            for word in error_path:
                if word == "line":
                    line = error_path[i + 1]
                    line = line.replace(",", "")
                i += 1
            try:
                error_line = split_code[int(line) - 1]
            except ValueError:
                return f":x: Your eval job has completed with return code -1.\n\n```\n{error}\n```"

            return f":x: Your eval job has completed with return code -1.\n\n```\nLine {line}: {error_line}\n{error_type}\n```"
