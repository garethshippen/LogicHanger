#!/usr/local/bin/python3

__author__ = "Gareth Shippen"
__date__ = "2024-02-12"

import csv
import copy
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd
from tkinter.ttk import Treeview

class Field():
    def __init__(self, row, fieldname_header):
        self.row = row
        self.field_name = self.row[fieldname_header]
        self.shown_by = self.set_shown_by() # BL field contents
        self.shown_by_body = self.set_shown_by_body(self.shown_by) # List of parents
        self.shows = []

    def set_shown_by(self): # Strips [event-name] from the BL
        bl = "Branching Logic (Show field only if...)"
        exact = self.row[bl].replace("\n","").replace("[event-name]","")
        return exact
    def get_shown_by(self):
        return self.shown_by
    
    def set_shown_by_body(self,text): # Returns a list of parents
        def body(text): # Extracts the field name of the parent field
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
    
    def set_field_name(self, fieldname):
        self.field_name = fieldname
    def get_field_name(self):
        return self.field_name
    def show_field(self):
        print("Field name: {}".format(self.field_name))
        print("Shown by: {}".format(self.shown_by))
        print("Shown by body: {}".format(self.shown_by_body))
        print("Shows: {}".format(self.shows)) # TODO
        print()

#################
### BEGIN GUI ###
#################
''' Open a file '''
lines = []
path = None
def select_file():
    global lines
    global path
    filetypes = [('CSV files', '*.csv')]
    path = fd.askopenfilename(title="Select Data Dictionary", filetypes=filetypes)
    if len(path) > 0:
        lines = gen_tree(path)

def gen_tree(filename):
    def read_csv(input_file):
        fields = {}
        roots = []
        fieldnames = set()
        with open(input_file) as inp:
            data = csv.DictReader(inp)
            for row in data:
                fieldname_header = list(row.keys())[0] # == ï»¿"Variable / Field Name"
                fields[row[fieldname_header]] = Field(row, fieldname_header) # Dictionary of the actual field name pointing to its Field object
                if row["Branching Logic (Show field only if...)"] == "": # This field has no parent
                    roots.append(row[fieldname_header])
                fieldnames.add(row[fieldname_header])
        return fields, roots, fieldnames

    data, roots, fieldnames = read_csv(filename)

    # Get the field names that aren't defined in the data dictionary
    parents = set()
    for value in data.values():
        shown_by = value.get_shown_by_body()
        for shown in shown_by:
            parents.add(shown)
    unknowns = parents - fieldnames
    unknowns = sorted(unknowns)
    
    # Create a blank Field
    empty_field = copy.deepcopy(data[roots[0]])
    empty_field.set_field_name("empty")

    # Add 'unknown' fields to data
    for unknown in unknowns:
        new_field = copy.deepcopy(empty_field)
        new_field.set_field_name(unknown)
        data[unknown] = new_field
        roots.append(unknown)

    # Associate parents with children
    for value in data.values():
        parents = value.get_shown_by_body()
        for parent in parents:
            data[parent].add_shows(value)

    # Inserts items into the tree view
    def gen_branches(fieldname, parent, data, level):
        global lines
        field = data[fieldname]
        my_id = tree.insert(parent=parent, index=END, text = field.get_field_name(), values=field.get_shown_by().replace(" ","\ "), tags=(str(level%5)))
        lines.append((level * "  " + "└" + (level-1) * "─" + field.get_field_name() + "\t\t\t" + field.shown_by))
        children = field.get_shows()
        if children:
            for child in children:
                gen_branches(child.get_field_name(), my_id, data, level+1)
    
    for root in roots:
        gen_branches(root, '', data, 0)

def open_children(child = ""):
    for child in tree.get_children(child):
        tree.item(child, open=True)
        open_children(child)

def close_children(child = ""):
    for child in tree.get_children(child):
        tree.item(child, open=False)
        close_children(child)
    
def save_tree(field, level, storage):
    pass

window = Tk()
window.title("REDCap Logic Tree (Beta)")
window.geometry("600x600")

yscroll = Scrollbar(window)
yscroll.pack(side=RIGHT, fill=Y)
xscroll = Scrollbar(window, orient='horizontal')
xscroll.pack(side=BOTTOM, fill=X)  

menubar = Menu(window)
window.config(menu=menubar)
filemenu = Menu(menubar, tearoff="off")
optionmenu = Menu(menubar, tearoff="off")

menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label = "Open", command= select_file)
filemenu.add_command(label = "Save", command= save_tree)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)

menubar.add_cascade(label="Options", menu=optionmenu)
optionmenu.add_command(label="Open all", command =open_children)
optionmenu.add_command(label="Close all", command =close_children)

tree = Treeview(window, columns=('#1'))
tree.heading('#0', text = 'Field label')
tree.heading('#1', text = 'Branching logic')

tree.pack(fill=BOTH, expand=1)
tree.tag_configure('0', background='#ffffff')
tree.tag_configure('1', background='#91cff2')
tree.tag_configure('2', background='#f4b7ee')
tree.tag_configure('3', background='#9ff497')
tree.tag_configure('4', background='#f1af89')

yscroll.config(command=tree.yview)
xscroll.config(command=tree.xview)

window.mainloop()

###############
### END GUI ###
###############