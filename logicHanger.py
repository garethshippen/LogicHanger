import csv
import sys

""" import sys

f = sys.argv

print(f)
for i in f:
    print(i) """
class Field():
    def __init__(self, row, fieldname):
        self.row = row
        self.field_name = self.row[fieldname]
        self.shown_by = self.set_shown_by()
        self.shown_by_body = self.set_shown_by_body(self.shown_by)
        self.shows = []

    def set_shown_by(self):
        bl = "Branching Logic (Show field only if...)"
        exact = self.row[bl].replace("[event-name]","")
        return exact
    def get_shown_by(self):
        return self.shown_by
    
    def set_shown_by_body(self,text):
        def body(text):
            if text[0] == "(":
                text = text[1:]
            start = text.find('[')
            stop = text.find("]")
            mid = text[start+1:stop]
            fullstop = mid.find("(")
            return mid if fullstop < 0 else mid[:fullstop]
        bodies = []
        for term in text.split():
            if "[" in term:
                bodies.append(body(term))
        return list(set(bodies))
    def get_shown_by_body(self):
        return self.shown_by_body
    
    def add_shows(self, field_obj):
        self.shows.append(field_obj)
    def get_shows(self):
        return self.shows
    
    def get_field_name(self):
        return self.field_name
    def show_field(self):
        print("Field name: {}".format(self.field_name))
        print("Shown by: {}".format(self.shown_by))
        print("Shown by body: {}".format(self.shown_by_body))
        print("Shows: {}".format(self.shows)) # trying to find this out

    
def read_csv(input_file):
    fields = {}
    roots = []
    with open(input_file) as inp:
        data = csv.DictReader(inp)
        for row in data:
            field_name = list(row.keys())[0]
            fields[row[field_name]] = Field(row, field_name)
            if row["Branching Logic (Show field only if...)"] == "":
                roots.append(row[field_name])
    return fields, roots

def find_unknowns(data):
    unknowns = []
    for key, value in data.items():
        parents = value.get_shown_by_body()
        for parent in parents:
            try:
                data[parent].add_shows(value)
            except Exception:
                unknowns.append((parent,key))
    return unknowns

def show_logic(field, level):
    print(level * "\t" + level * "-" + field.get_field_name())
    children = field.get_shows()
    if children:
        for child in children:
            show_logic(child, level + 1)

""" for root in roots:
    show_logic(data[root],  0)
    print() """

def store_logic(field, level, storage, verbose):
    if verbose:
        storage.append(level * "  " + level * "-" + field.get_field_name() + "\t\t" + field.shown_by)
    else:
        storage.append((level * "  " + level * "-" + field.get_field_name()))
    children = field.get_shows()
    if children:
        for child in children:
            store_logic(child, level + 1, storage, verbose)

def traverse(data, roots, verbose):
    lines = []
    for root in roots:
        store_logic(data[root],  0, lines, verbose)
    return lines

def export(file_name, lines, unknowns):
    with open(file_name, "w") as out:
        for line in lines:
            out.write(line + "\n")
        out.write("\nThe following fields depend on other fields that weren't found.\n")
        for unknown in unknowns:
            out.write(unknown[1] + " depends on " + unknown[0] + "\n")
""" 
f = sys.argv
print(f)
for i in f:
    print(i) 
"""
# Defaults
verbose = False
input_file = "source.csv"
output_file = "dependent_fields.txt"

args = sys.argv
args.pop(0)
if "-v" in args:
    verbose = True
    args.remove("-v")


data, roots = read_csv(input_file)
unknowns = find_unknowns(data)
lines = traverse(data, roots, verbose)
export(output_file, lines, unknowns)