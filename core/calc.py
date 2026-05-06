__version__ = "1.3.0"
__description__ = "A built-in terminal calculator that safely evaluates mathematical expressions. Supports interactive REPL mode and advanced math functions."
__author__ = "Souvik"
__website__ = ""

import sys
import math

def main():
    args = sys.argv[1:]
    
    # Create a safe environment with math functions
    safe_env = {k: v for k, v in math.__dict__.items() if not k.startswith('_')}
    safe_env['abs'] = abs
    safe_env['round'] = round
    safe_env['pow'] = pow
    safe_env['max'] = max
    safe_env['min'] = min
    safe_env['pi'] = math.pi
    safe_env['e'] = math.e
    safe_env['sin'] = math.sin
    safe_env['cos'] = math.cos
    safe_env['tan'] = math.tan
    safe_env['sqrt'] = math.sqrt
    safe_env['log'] = math.log
    safe_env['log10'] = math.log10
    
    if not args:
        print("\x1b[36;1m=== Velora Calculator ===\x1b[0m")
        print("  \x1b[90mType an expression to evaluate, or 'exit' to quit.\x1b[0m")
        while True:
            try:
                expr = input("\x1b[33mcalc>\x1b[0m ").strip()
                if expr.lower() in ('exit', 'quit'):
                    break
                if not expr:
                    continue
                result = eval(expr, {"__builtins__": None}, safe_env)
                print(f"  \x1b[32m{result}\x1b[0m")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            except Exception as e:
                print(f"  \x1b[31;1mError:\x1b[0m Invalid expression ({e})")
    else:
        expr = " ".join(args)
        try:
            result = eval(expr, {"__builtins__": None}, safe_env)
            print(f"\x1b[36;1mResult:\x1b[0m {result}")
        except Exception as e:
            print(f"\x1b[31;1mError:\x1b[0m Invalid expression ({e})")

if __name__ == "__main__":
    main()