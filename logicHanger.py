import csv
from tkinter import *
from tkinter import filedialog

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

def gen_tree(filepath): # Takes a filepath and returns a list of strings making a tree
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
    data, roots = read_csv("source.csv")

    unknowns = []
    for key, value in data.items():
        parents = value.get_shown_by_body()
        for parent in parents:
            try:
                data[parent].add_shows(value)
            except Exception:
                unknowns.append((parent,key))

    def show_logic(field, level):
        print(level * "\t" + level * "-" + field.get_field_name())
        children = field.get_shows()
        if children:
            for child in children:
                show_logic(child, level + 1)


    def store_logic(field, level, storage):
        storage.append((level * "  " + level * "-" + field.get_field_name()))
        children = field.get_shows()
        if children:
            for child in children:
                store_logic(child, level + 1, storage)

    lines = []
    for root in roots:
        store_logic(data[root],  0, lines)
    return lines

def list_to_string(list_of_strings):
    output = [line + "\n" for line in list_of_strings]
    return output

lines = list_to_string(gen_tree('source.csv'))
for line in lines:
    print(line)

exit()
#################
### BEGIN GUI ###
#################
window = Tk()
window.title("REDCap Logic Tree")
window.geometry("300x600")

menubar = Menu(window)
window.config(menu=menubar)
filemenu = Menu(menubar)
optionmenu = Menu(menubar)

menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label = "Open")
filemenu.add_command(label = "Save")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)

menubar.add_cascade(label="Options", menu=optionmenu)
optionmenu.add_checkbutton(label="Verbose Mode")

label_space = Label(window, text = "Open a Data Dictionary\nfrom the file menu above", justify=LEFT)
label_space.place(x=0, y=0)

""" for line in lines:
    match line.count("-")%5:
        case 1:
            text.insert(END, line + "\n", 'one')
        case 2: 
            text.insert(END, line + "\n", 'two')
        case 3:
            text.insert(END, line + "\n", 'three')
        case 4:
            text.insert(END, line + "\n", 'four')
        case _:
            text.insert(END, line + "\n")
for unknown in unknowns:
    text.insert(END, "\n" + unknown[1] + " " + unknown[0])

yscroll.config(command=text.yview) """

window.mainloop()

###############
### END GUI ###
###############