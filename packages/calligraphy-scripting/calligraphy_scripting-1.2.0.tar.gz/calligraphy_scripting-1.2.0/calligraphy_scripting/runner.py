# pylint: disable=R0801, W0703, W0122
"""Module to allow for running Calligraphy scripts from other Python programs"""
import os
import sys
import traceback
import copy
from calligraphy_scripting import parser
from calligraphy_scripting import transpiler
from calligraphy_scripting import utils
import re

here = os.path.dirname(os.path.abspath(__file__))

def interactive() -> None:
    function_pattern = r"def\s*([a-zA-Z0-9_]*)\("
    header = utils.load_header()
    header = header.replace('"PROGRAM_ARGS"', '[]')
    exec(header, globals())
    supplemental_functions = []
    
    contents = ''
    while True:
        line = input("> ")
        contents += line + '\n'
        if line.strip() == 'exit()':
            sys.exit(0)
        # print(f'{len(line.lstrip())} : {len(line)} : {line.endswith(":")}')
        if len(line.lstrip()) == len(line) and not line.endswith(':'):
            supplemental_functions += re.findall(function_pattern, contents)
            # execute(contents, [], False, supplemental_functions)
            # contents = ''
            contents, inline_indices = parser.handle_line_breaks(contents)
            contents = parser.handle_sourcing(contents)
            lines, langs = parser.determine_language(contents, supplemental_functions)
            transpiled = transpiler.transpile(lines, langs, inline_indices)

            # print(f'>>> {transpiled}')
            try:
                exec(transpiled, globals())
            except KeyboardInterrupt:
                sys.exit()
            except Exception as exception:
                trace = traceback.format_exc()
                parts = trace.split("\n")
                idx = 1
                exception_out = [parts[0]]
                while not parts[idx].startswith('  File "<string>"') and idx < len(parts):
                    idx += 1
                while idx < len(parts):
                    exception_out.append(parts[idx])
                    idx += 1
                print("\n".join(exception_out))
            contents = ''
        

def execute(contents: str, args: list, global_dict: dict=None, local_dict: dict=None, raise_exceptions: bool=True, supplemental_functions: list[str] = None) -> None:
    """Run Calligraphy code from another program

    Args:
        contents (str): The Calligraphy code to run
        args: (list): The arguments to pass to the script
    """

    if not supplemental_functions:
        supplemental_functions = []

    # Process the contents
    contents, inline_indices = parser.handle_line_breaks(contents)
    contents = parser.handle_sourcing(contents)
    lines, langs = parser.determine_language(contents, supplemental_functions)
    transpiled = transpiler.transpile(lines, langs, inline_indices)

    # Add the header to enable functionality
    header = utils.load_header()
    header = header.replace('"PROGRAM_ARGS"', str(args))
    code = f"{header}\n\n{transpiled}"

    # Run the code
    try:
        exec(code, globals())
    except KeyboardInterrupt:
        sys.exit()
    except Exception as exception:
        trace = traceback.format_exc()
        parts = trace.split("\n")
        idx = 1
        exception_out = [parts[0]]
        while not parts[idx].startswith('  File "<string>"') and idx < len(parts):
            idx += 1
        while idx < len(parts):
            exception_out.append(parts[idx])
            idx += 1
        print("\n".join(exception_out))
        if raise_exceptions:
            raise exception
