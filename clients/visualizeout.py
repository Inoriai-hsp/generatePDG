#!/usr/bin/env python3
from typing import Mapping, Set, TextIO

import os
import sys

# IT: Ugly hack; this can be avoided if we pull the script at the top level
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from clientlib.facts_to_cfg import Statement, Block, Function, construct_cfg, load_csv_map # type: ignore


def emit(s: str, out: TextIO, indent: int=0):
    # 4 spaces
    INDENT_BASE = '    '

    print(f'{indent*INDENT_BASE}{s}', file=out)


def emit_stmt(stmt: Statement, out: TextIO):
    def render_var(var: str):
        if var in tac_variable_value:
            return f"v{var.replace('0x', '')}({tac_variable_value[var]})"
        else:
            return f"v{var.replace('0x', '')}"

    defs = [render_var(v) for v in stmt.defs]
    uses = [render_var(v) for v in stmt.operands]

    if defs:
        emit(f"{stmt.ident}: {', '.join(defs)} = {stmt.op} {', '.join(uses)}", out, 1)
    else:
        emit(f"{stmt.ident}: {stmt.op} {', '.join(uses)}", out, 1)


def pretty_print_block(block: Block, visited: Set[str], out: TextIO):
    emit(f"Begin block {block.ident}", out, 1)

    prev = [p.ident for p in block.predecessors]
    succ = [s.ident for s in block.successors]

    emit(f"prev=[{', '.join(prev)}], succ=[{', '.join(succ)}]", out, 1)
    emit(f"=================================", out, 1)

    for stmt in block.statements:
        emit_stmt(stmt, out)

    emit('', out)

    for block in block.successors:
        if block.ident not in visited:
            visited.add(block.ident)
            pretty_print_block(block, visited, out)


def pretty_print_tac(functions: Mapping[str, Function], out: TextIO):
    for function in sorted(functions.values(), key=lambda x: x.ident):
        visibility = 'public' if function.is_public else 'private'
        emit(f"function {function.name}({', '.join(function.formals)}) {visibility} {{", out)
        pretty_print_block(function.head_block, set(), out)

        emit("}", out)
        emit("", out)

def save_cfg_and_ddg(block:Block, visited: Set[str], cfg: TextIO, ddg: TextIO, ident = None):
    pre = ident
    for statement in block.statements:
        if pre is not None:
            cfg.write(pre + "\t" + statement.ident + "\n")
        pre = statement.ident
        for operand in statement.operands:
            ddg.write(operand + "\t" + statement.ident + "\n")
    for block in block.successors:
        if block.ident not in visited:
            visited.add(block.ident)
            save_cfg_and_ddg(block, visited, cfg, ddg, pre)
        else:
            if len(block.statements) > 0:
                cfg.write(pre + "\t" + block.statements[0].ident + "\n")

def generate_cfg_and_ddg(functions: Mapping[str, Function]):
    for function in sorted(functions.values(), key=lambda x: x.ident):
        cfg = open("cfg_" + function.name + ".txt", "w")
        ddg = open("ddg_" + function.name + ".txt", "w")
        save_cfg_and_ddg(function.head_block, set(), cfg, ddg)
        cfg.close()
        ddg.close()



def main():
    global tac_variable_value
    tac_variable_value = load_csv_map('TAC_Variable_Value.csv')

    _, functions,  = construct_cfg()

    with open('contract.tac', 'w') as f:
        pretty_print_tac(functions, f)
    generate_cfg_and_ddg(functions)

    


if __name__ == "__main__":
    main()
