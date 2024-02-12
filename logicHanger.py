import csv
import copy
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd

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

def gen_lines(filename):
    def store_logic(field, level, storage):
        storage.append((level * "  " + level * "-" + field.get_field_name() + full_logic.get() * ("\t\t" + field.shown_by)))
        children = field.get_shows()
        if children:
            for child in children:
                store_logic(child, level + 1, storage)

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

    ########################
    ###### BEGIN MAIN ######
    ########################

    data, roots, fieldnames = read_csv(filename)

    # Get the field names that aren't defined in the data dictionary
    parents = set()
    for value in data.values():
        shown_by = value.get_shown_by_body()
        for shown in shown_by:
            parents.add(shown)
    unknowns = parents - fieldnames

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
    unknowns = []
    for key, value in data.items():
        parents = value.get_shown_by_body()
        for parent in parents:
            try:
                data[parent].add_shows(value)
            except Exception:
                unknowns.append((parent,key))

    lines = []
    for root in roots:
        store_logic(data[root],  0, lines)
    
    return lines

#################
### BEGIN GUI ###
#################
lines = "Open a Data Dictionary\nfrom the File menu."
path = None
def select_file():
    global lines
    global path
    filetypes = [('CSV files', '*.csv')]
    path = fd.askopenfilename(title="Select Data Dictionary", filetypes=filetypes)
    if len(path) > 0:
        lines = gen_lines(path)
        show_logic()

def get_level(input):
    for i in range(len(input)):
        if input[i] != " ":
            return i

def show_logic():
    global lines
    global path
    if path:
        lines = gen_lines(path)
    if isinstance(lines, str):
        text.config(state=NORMAL)
        text.insert(END, lines)
        text.config(state=DISABLED)
    else:
        text.config(state=NORMAL)
        text.delete('1.0', END)
        if not level_colours.get():
            for line in lines:
                match get_level(line)%5:
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
        else:
            for line in lines:
                text.insert(END, line + "\n")
        text.config(state=DISABLED)

def save_logic():
    global lines
    if isinstance(lines, str):
        messagebox.showwarning(title="Error", message="Please open a Data Dictionary first.")
        return
    save_path = fd.asksaveasfile(initialfile="logic.txt",\
                                defaultextension=".txt",\
                                filetypes=[('Text Files','*.txt'),('All Files','*.*')],\
                                mode='w')
    if save_path:
        for line in lines:
            save_path.write(line + '\n')
        save_path.close()
                
window = Tk()
window.title("REDCap Logic Tree")
window.geometry("600x600")

menubar = Menu(window)
window.config(menu=menubar)
filemenu = Menu(menubar)
optionmenu = Menu(menubar)

menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label = "Open", command= select_file)
filemenu.add_command(label = "Save", command=save_logic)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)

menubar.add_cascade(label="Options", menu=optionmenu)
full_logic = IntVar()
optionmenu.add_checkbutton(label="Show logic", onvalue=1, offvalue=0, variable=full_logic, command=show_logic)
level_colours = IntVar()
optionmenu.add_checkbutton(label="Hide level colours", onvalue=1, offvalue=0, variable=level_colours, command=show_logic)

yscroll = Scrollbar(window)
yscroll.pack(side=RIGHT, fill=Y)

xscroll = Scrollbar(window, orient='horizontal')
xscroll.pack(side=BOTTOM, fill=X)             

text = Text(window,yscrollcommand = yscroll.set, xscrollcommand=xscroll.set, wrap=NONE)
text.pack(side=LEFT, fill = BOTH, expand=1)
text.tag_config('one', foreground = "red")
text.tag_config('two', foreground = "blue")
text.tag_config('three', foreground = "#1d5c11")
text.tag_config('four', foreground="#7c206f")

show_logic()

yscroll.config(command=text.yview)
xscroll.config(command=text.xview)
window.mainloop()

###############
### END GUI ###
###############