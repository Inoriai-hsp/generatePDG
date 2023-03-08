import networkx as nx
import os, copy
import torch
from tqdm import tqdm
import dgl
from dgl import save_graphs

# print(len(os.listdir("./CallGraphs")))
# print(len(os.listdir("./PDGs")))
tac_OPs = []
number = 0
with open("./tac_instructions.txt", "r") as f:
    for line in f.readlines():
        tac_OPs.append(line.strip())
with open("./address_labels_gigahorse.txt", "r") as f:
    lines = f.readlines()
    for i in tqdm(range(0, len(lines))):
        line = lines[i]
        address = line.strip().split("\t")[0]
        tac_ops = {}
        with open("./.temp/" + address + "/out/TAC_Op.csv") as ops:
            for line in ops.readlines():
                [pc, op] = line.strip().split("\t")
                tac_ops[pc] = op
        tac_ops['arg'] = 'ARG'
        functionnames = []
        files = os.listdir("./.temp/" + address + "/out")
        for filename in files:
            if "cfg" in filename:
                functionnames.append(filename[4:])
        name_functions = {}
        with open("./.temp/" + address + "/out/HighLevelFunctionName.csv", "r") as f:
            for line in f.readlines():
                [function, name] = line.strip().split("\t")
                name_functions[name] = function
        PDGs = []
        functions = []
        for functionname in functionnames:
            function_cfg = "cfg_" + functionname
            function_ddg = "ddg_" + functionname
            CFG = nx.DiGraph(address = address)
            with open("./.temp/" + address + "/out/" + function_cfg, "r") as f:
                for line in f.readlines():
                    [pre, next] = line.strip().split("\t")
                    CFG.add_edge(pre, next)
            nodes = copy.deepcopy(CFG.nodes)
            if len(nodes) < 1:
                continue
            for node in nodes:
                # CFG.nodes[node]['tac_op'] = torch.tensor(tac_OPs.index(tac_ops[node]), dtype=torch.int64)
                if len(list(CFG.successors(node))) < 1:
                    CFG.add_edge(node, "end")
            DF = sorted((u, sorted(df)) for u, df in nx.dominance_frontiers(CFG.reverse(), "end").items())
            PDG = nx.DiGraph(address = address)
            PDG.add_nodes_from(CFG.nodes(data=True))
            for (next, pres) in DF:
                for pre in pres:
                    PDG.add_edge(pre, next, type=torch.tensor(0, dtype=torch.long))
            edges = copy.deepcopy(PDG.edges)
            with open("./.temp/" + address + "/out/" + function_ddg, "r") as f:
                for line in f.readlines():
                    [pre, next] = line.strip().split("\t")
                    # pre1 =pre
                    if pre not in tac_ops.keys():
                        if 'v' in pre or 'V' in pre:
                            pre = pre.replace('v', '0x').replace('V', '')
                        elif '_' in pre:
                            pre = pre.split("_")[0]
                        elif 'arg' in pre:
                            pre = 'arg'
                        # else:
                        #     print("pre: " + pre)
                        #     exit()
                    if next not in tac_ops.keys():
                        if 'v' in next or 'V' in next:
                            next = next.replace('v', '0x').replace('V', '')
                        elif '_' in next:
                            next = next.split("_")[0]
                        elif 'arg' in next:
                            next = 'arg'
                        # else:
                        #     print("next: " + next)
                        #     exit()
                    if pre not in tac_ops.keys() or next not in tac_ops.keys():
                        # print(pre, next)
                        # exit()
                        number += 1
                        continue
                    PDG.add_edge(pre, next, type=torch.tensor(1, dtype=torch.long))
            nodes = copy.deepcopy(PDG.nodes)
            for node in nodes:
                if len(list(PDG.successors(node))) == 0 and len(list(PDG.predecessors(node))) == 0:
                    PDG.remove_node(node)
                else:
                    PDG.nodes[node]['tac_op'] = torch.tensor(tac_OPs.index(tac_ops[node]), dtype=torch.int64)
            PDGs.append(dgl.from_networkx(PDG, node_attrs=['tac_op'], edge_attrs=['type']))
            functions.append(name_functions[functionname[0:-4]])
        ir_functions = {}
        with open("./.temp/" + address + "/out/InFunction.csv", "r") as f:
            for line in f.readlines():
                [ir, function] = line.strip().split("\t")
                ir_functions[ir] = function
        callgraph = open("./CallGraphs/" + address + ".txt", "w")
        with open("./.temp/" + address + "/out/IRFunctionCall.csv", "r") as f:
            for line in f.readlines():
                [ir, function] = line.strip().split("\t")
                if ir_functions[ir] in functions and function in functions:
                    callgraph.write(str(functions.index(ir_functions[ir])) + "\t" + str(functions.index(function)) + "\n")
        callgraph.close()
        try:
            save_graphs("./PDGs/" + address + ".txt", PDGs)
        except Exception as e:
            print(e)
            print(i)
            exit()
print("done!")
print(number)