import csv

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
    #return_list = []
    with open(input_file) as inp:
        data = csv.DictReader(inp)
        for row in data:
            field_name = list(row.keys())[0]
            fields[row[field_name]] = Field(row, field_name)
            if row["Branching Logic (Show field only if...)"] == "":
                roots.append(row[field_name])
    return fields, roots
data, roots = read_csv("source.csv") # fieldname points to Field object

unknowns = []
for key, value in data.items():
    parents = value.get_shown_by_body()
    for parent in parents:
        try:
            #data[dependent].add_shows(key)
            data[parent].add_shows(value)
        except Exception:
            unknowns.append((parent,key))



def show(field, level):
    print(level * "\t" + level * "-" + field.get_field_name())
    children = field.get_shows()
    if children: # field shows other fields
        for child in children:
            show(child, level + 1)

for root in roots:
    show(data[root],  0)
    print()
exit()













def show(field_object, level, fields):
    print(field_object.get_field_name())
    children = field_object.get_shows()
    if len(children) == 0:
        return #field_object.get_field_name()
    else:
        for child in children:
            print(level * "\t" + level * "----" + show(child, level + 1, fields))

for root in roots:
    show(data[root], 0, data)


""" for name, field in data.items():
    if field.get_shown_by() != None: #this field is dependent on another
        pass """
#fields[55].show_field()

# iter through fields
# if field has a shown_by, look up that shown by, and add the field to the parents "shows"


exit()
for name, field in data.items():
    if field.get_shown_by():
        data[field.get_shown_by_body()].set_shows(field)
a = data["s_obstetric"].get_shown_by_body()
data[a].show_field()

exit()
branching_logic = {}

#field_name = list(data[0].keys())[0]
bl = "Branching Logic (Show field only if...)"

for row in data:
    if row[bl] != "":
        if branching_logic.get(row[bl]):
            branching_logic[row[bl]].append(row[field_name])
        else:
            branching_logic[row[bl]] = [row[field_name]]

for fields in branching_logic.values():
    for field in fields:
        for key in branching_logic.keys():
            #print(key.replace("[event-name]",""))
            if field in key.replace("[event-name]",""):
                print(key, field)
print("Finished")
exit()


for key, value in branching_logic.items():
    print(key)
    print(value)
    print()
exit()
key = "[" + branching_logic["[occu_expose]"] + "]"
print(branching_logic[key])

exit()
output = "dependent_fields.txt"
with open(output, "w") as out:
    for key, value in branching_logic.items():
        out.write("\n" + key.replace("[event-name]","") + " shows:\n")
        for item in value:
            out.write("\t" + item + "\n")
    out.write("\n")

def show_bl(bl_dict, term, level):
    terms = bl_dict.get(term)
    if terms != None:
        for term in terms:
            sublevel = show_bl(bl_dict, None, None)