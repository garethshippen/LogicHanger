import csv

def read_csv(input_file):
    return_list = []
    with open(input_file) as inp:
        data = csv.DictReader(inp)
        for row in data:
            return_list.append(row)
    return return_list
data = read_csv("source.csv")

branching_logic = {}

field_name = list(data[0].keys())[0]
bl = "Branching Logic (Show field only if...)"

for row in data:
    if row[bl] != "":
        if branching_logic.get(row[bl]):
            branching_logic[row[bl]].append(row[field_name])
        else:
            branching_logic[row[bl]] = [row[field_name]]


""" for key, value in branching_logic.items():
    print(key.replace("[event-name]","") + " shows:")
    for item in value:
        print("\t" + item)
    print("\n") """


output = "dependent_fields.txt"
with open(output, "w") as out:
    for key, value in branching_logic.items():
        out.write("\n" + key.replace("[event-name]","") + " shows:\n")
        for item in value:
            out.write("\t" + item + "\n")
    out.write("\n")

print("Finished")