# MindWandering
The purpose of this program is to take subjects through an experiment to measure mind wandering with reading tasks and questionnaires. This program will take the subject through two reading tasks which will measure key-logging events while the subject is reading text.

This is implemented as a tkinter GUI, which can be packaged into a macOS app using py2app.

## Building
First, generate a virtual environment and install the required packages:
```
python3 -m venv mindwandering_venv
source mindwandering_venv/bin/activate
pip install -r requirements.txt
```

## Packaging
The py2app tool is used for packaging into a macOS app.

Due to a deficiency of py2app, the Tcl/Tk libraries must be copied into the virtual environment before packaging. This causes them to be packaged into the app; otherwise the app will not launch on machines where Apple's dev tools have not been installed. First, to find the paths of Tcl and Tk, in Python: 
```
import tkinter
root = tkinter.Tk()
tcl_path = root.tk.exprstring('$tcl_library')
tk_path = root.tk.exprstring('$tk_library')
```
Then copy the libraries into the virtual environment:
`cp -r tcl_path tk_path mindwandering_venv/lib`

Now the app can be generated:
`python setup.py py2app --resources fonts,data`

Note that an app built on macOS 13.0 will only run on OS versions later than 11.0 . Building on OSX 10.13 results in an app which will run in 10.13, 10.15, and 11.0 but not 13.0 ; py2app does not currently have facilities for cross-compiling for a broader range of versions.
