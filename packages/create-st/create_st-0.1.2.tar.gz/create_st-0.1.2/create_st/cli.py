import sys
from .parser import normalize_lines, build_structure

BANNER = r'''         _                  _                   _                  
                     | |                | |                 | |                 
   ___ _ __ ___  __ _| |_ ___        ___| |_ _ __ _   _  ___| |_ _   _ _ __ ___ 
  / __| '__/ _ \/ _` | __/ _ \      / __| __| '__| | | |/ __| __| | | | '__/ _ \
 | (__| | |  __/ (_| | ||  __/      \__ \ |_| |  | |_| | (__| |_| |_| | | |  __/
  \___|_|  \___|\__,_|\__\___|      |___/\__|_|   \__,_|\___|\__|\__,_|_|  \___|
                                                                                
                                                                                

usage
create-st "the name of a text file with an extension that is located in the same directory where the command is run"

how it works
takes and in the directory where the command was run, creates a structure of folders and files, the names of files and folders are taken from the file with this command

example text file
├─ app.py
├─ database.db
├─ templates/
│   ├─ login.html
│   ├─ register.html
│   ├─ home.html
│   ├─ chat.html
│   ├─ settings.html
├─ static/
│   ├─ css/
│   │   └─ style.css
│   ├─ js/
│       └─ script.js

or

app.py
database.db
templates/
        login.html
        register.html
        home.html
        chat.html
        settings.html
static/
        css/
            style.css
        js/
            script.js


by aloha v2
'''

def main():
    if len(sys.argv) == 1:
        print(BANNER)
        return
    file_path = sys.argv[1]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        lines = normalize_lines(lines)
        build_structure(lines, ".")
        print("structure created")
    except Exception as e:
        print(f"error: {e}")