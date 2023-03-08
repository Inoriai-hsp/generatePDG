# import pandas as pd
# with open("/home/huangshiping/data/bytecodes_47398.txt") as f:
    # for line in f.readlines():
    #     [address, hex] = line.strip().split(":")
    #     with open("./bytecodes_47398/" + address + ".hex", "w") as bytecode:
    #         bytecode.write(hex)

# with open("./.temp/0xf4dfe5e127df0986b2ba2cc15e173eaec507713a/out/TAC_Op.csv", "r") as f:
# dataFrame = pd.read_csv("./.temp/0xf89a8ba3eeab8c1f4453caa45e76d87f49f41d25/out/TAC_Op.csv")
# print(dataFrame.shape[0])
import json
f = open("./results.json", "r")
results = json.load(f)
f.close()
address_labels = {}
with open("/home/huangshiping/test/address_labels.txt", "r") as f:
    for line in f.readlines():
        [address, label] = line.strip().split("\t")
        address_labels[address] = label
# timeout_num = 0
# hit_num = 0
# positive_num = 0
f = open("./address_labels_gigahorse.txt", "w")
for result in results:
    # print(result)
    if len(result[2]) == 0:
        address = result[0].split(".")[0]
        if address in address_labels.keys():
            f.write(address + "\t" + address_labels[address] + "\n")
f.close()
print("done!")
