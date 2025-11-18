import tkinter as tk
import platform
from datetime import datetime
import os
import time
import math
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import shutil
from tkinter.scrolledtext import ScrolledText
from tkinter.colorchooser import askcolor
import tkinter.colorchooser
from tkinter.dnd import Tester, Icon
import tkinter.dnd
import tkinter.simpledialog as simpledialog
import turtle
import sys
import random
import psutil
import importlib
import subprocess
import asyncio
import warnings
import webbrowser
import webview
from tkinter import ttk
from tkhtmlview import HTMLLabel
from tkinter import Toplevel

variables = {}
functions = {}
classes = {}
objects = {}
customerrors = {}
structures = {}
namespaces = {}
efnvars = {}

efn_root = None
items = 0

true = True
false = False
none = None
Length = len
Int = int
Float = float
String = str
Dictionary = dict
Type = type
customdialog = simpledialog.Dialog
In = lambda item, container: item in container
As = lambda obj, alias: alias
From = lambda source, key: source.get(key)
Pass = lambda: None
Exit = lambda: exit()
Quit = lambda: quit()
Continue = lambda: None
args = sys.argv[1:]
Arguments = args
Argument = args[-1] if args else None
And = lambda a, b: a and b
Or = lambda a, b: a or b
Not = lambda a: not a

def less(a, b): return a < b
def more(a, b): return a > b
def lessorequal(a, b): return a <= b
def moreorequal(a, b): return a >= b
def equal(a, b): return a == b
def notequal(a, b): return a != b

def unlockKeywordArguments(**kwargs):
    KeywordArguments = kwargs
    return KeywordArguments

for arg in args:
    Argument = arg

def write(text):
    print(f"{text}")

def writenoend(text):
    print(f"{text}", end="")

def showmachinefulldata():
    return f"""{platform.platform()}
{platform.system()}
{platform.version()}
{platform.release()}
{platform.architecture()}
{platform.machine()}
{platform.processor()}"""

def showplatformdata():
    return f"{platform.platform()}"

def showsystemdata():
    return f"{platform.system()}"

def showversiondata():
    return f"{platform.version()}"

def showreleasedata():
    return f"{platform.release()}"

def showarchitecturedata():
    return f"{platform.architecture()}"

def showmachinedata():
    return f"{platform.machine()}"

def showprocessordata():
    return f"{platform.processor()}"

def startswith(string, prefix):
    return string.startswith(prefix)

def endswith(string, suffix):
    return string.endswith(suffix)

def Char(value):
    if isinstance(value, str) and len(value) == 1:
        return value
    raise ValueError(f"'{value}' is not a valid char.")

def F(variable):
    return eval(str(variable))

def drawbird():
    return """('>
|//
V_/_"""

def drawcat():
    return '''/\_/\  
( o.o ) 
> ^ <  
/  |  \ 
(   |   )
/    \  \
(      )  )
(        )/
 """""""""'''

def leftshift(num1, num2):
    return num1 << num2

def rightshift(num1, num2):
    return num1 >> num2

def bitwiseor(num1, num2):
    return num1 | num2

def bitwiseand(num1, num2):
    return num1 & num2

def binarytotext(binary):
    def binarytostring(binary):
        return ''.join(chr(int(b, 2)) for b in binary.split())

    binarycode = binary
    text = binarytostring(binarycode)
    return text

def texttobinary(text):
    def stringtobinary(text):
        return ' '.join(format(ord(char), '08b') for char in text)

    binary = stringtobinary(text)
    return binary

def numbertobinary(num):
    number = bin(num)
    return number

def binarytonumber(binarystr):
    return int(binarystr, 2)

def Next(variable):
    global items
    try:
        items += 1
        return f"{variable[items]}"
    except Exception:
        items = 1
        return f"{variable[items]}"

def Previous(variable):
    global items
    try:
        items -= 1
        return f"{variable[items]}"
    except Exception:
        items = 1
        return f"{variable[items]}"

def Item(variable, itemnumber):
    try:
        return f"{variable[itemnumber]}"
    except Exception:
        itemnumber = 0
        return f"{variable[itemnumber]}"

def Map(function, iterable):
    for item in iterable:
        yield function(item)

def palindrome(text):
    cleaned = ''.join(c.lower() for c in text if c.isalnum())
    return cleaned == cleaned[::-1]

def randomflip(text):
    return ''.join(
        c.upper() if random.choice([True, False]) else c.lower()
        for c in text
    )

def getbytememorysizeof(val):
    return sys.getsizeof(val)

def string(value):
    return f"{str(value)}"

def Floatnumber(value):
    return f"{float(value)}"

def bytestring(value):
    return bytes(value, 'utf-8')

def rawstring(value):
    return repr(value)[1:-1]

def Bytes(value, textencoding):
    return bytes(value, textencoding)

def encodetext(variable, textencoding):
    return variable.encode(textencoding)

def decodetext(variable, decoding):
    return variable.decode(decoding)

def evaluate(value):
    return f"{eval(value)}"

def Sort(value):
    return f"{sort(value)}"

def Reversedsort(value):
    toreverse = sort(value)
    return f"{toreverse.reverse()}"

def initobject(name, *args, **kwargs):
    obj = objects.get(name)
    if not obj: return print(f"Object '{name}' not found.")

    classname = obj.get("__class__")
    if classname and classname in classes:
        local_env = {"self": obj}
        exec(classes[classname], {}, local_env)
        init_func = local_env.get("__init__")
        if init_func:
            init_func(obj, *args, **kwargs)
    else:
        print(f"Class '{classname}' not found or not associated with object '{name}'.")

def supercall(objname, methodname, *args, **kwargs):
    obj = objects.get(objname)
    parent = obj.get("__parent__") if obj else None

    if parent and parent in classes:
        env = {"self": obj}
        exec(classes[parent], {}, env)
        super_func = env.get(methodname)
        if super_func:
            return super_func(obj, *args, **kwargs)
        else:
            print(f"Method '{methodname}' not found in superclass '{parent}'.")
    else:
        print(f"No superclass defined for object '{objname}'.")

def injectkeywordarguements(objname, **kwargs):
    obj = objects.get(objname)
    if obj is None:
        return print(f"Object '{objname}' does not exist.")

    for key, value in kwargs.items():
        obj[key] = value

def copytoclipboard(text):
    efn_root.clipboard_clear()
    efn_root.clipboard_append(text)

def typeof(varname):
    val = globals().get(varname)
    return type(val).__name__

def systemuptime():
    seconds = time.time() - psutil.boot_time()
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"

def rollrandom(sides=6):
    return random.randint(1, sides)

def randomto(n1, n2):
    return random.randint(n1, n2)

def listfiles(path="."):
    return os.listdir(path)

def readfile(filename):
    with open(filename, "r") as f:
        content = f.read()
        return content

def appendtextinfile(filename, text):
    with open(filename, "a") as f:
        f.write(text)

def createfilewithcontent(filename, text):
    with open(filename, "x") as f:
        f.write(text)

def overwritecontentoffile(filename, text):
    with open(filename, "w") as f:
        f.write(text)

def readandoverwritefilecontent(filename, text):
    with open(filename, "r+") as f:
        data = f.read()
        f.seek(0)
        f.write(text)
        return data

def overwriteandreadfilecontent(filename, text):
    with open(filename, "w+") as f:
        f.write(text)
        f.seek(0)
        readfile = f.read()
        return readfile

def appendandreadcontent(filename, text):
    with open(filename, "a+") as f:
        f.write(text)
        f.seek(0)
        readcontent = f.read()
        return readcontent

def inlinefunction(thing, functiontodo):
    if thing:
        return lambda arg: functiontodo(arg)
    else:
        return lambda: functiontodo()

def newlineafter(line, times):
    return line + '\n' * times

def newlinebefore(line, times):
    return '\n' * times + line

def splittext(text, tosplit=None, delimiter=" ", maxsplit=None):
    if tosplit is None:
        if maxsplit is not None:
            return text.split(delimiter, maxsplit)
        else:
            return text.split(delimiter)
    else:
        if maxsplit is not None:
            return tosplit.split(delimiter, maxsplit)
        else:
            return tosplit.split(delimiter)

def jointext(items, delimiter=" "):
    return delimiter.join(items)

def slicefrom(text, start):
    return text[start:]

def sliceto(text, end):
    return text[:end]

def slicerange(text, start, end):
    return text[start:end]

def splitlistfrom(lst, start):
    return lst[start:]

def splitlistto(lst, end):
    return lst[:end]

def splitlistbetween(lst, start, end):
    return lst[start:end]

def slice(obj, start=None, end=None):
    return obj[start:end]

def formattext(text, style=None, color=None, case=None, padding=0, wrap=None, do_print=False):
    if case == "upper":
        text = text.upper()
    elif case == "lower":
        text = text.lower()
    elif case == "title":
        text = text.title()
    elif case == "normal" or case is None:
        pass

    if padding > 0:
        text = " " * padding + text + " " * padding

    if wrap:
        import textwrap
        text = textwrap.fill(text, width=wrap)

    if style:
        text = f"[{style}]{text}[/{style}]"
    if color:
        text = f"<{color}>{text}</{color}>"

    if do_print:
        print(text)
        
    return text

def rgb(efn_root, red, green, blue):
    r = red
    g = green
    b = blue
    return f"#{r:02x}{g:02x}{b:02x}"

def changeatrun(codetochange, changedcode):
    return changedcode

def private(code):
    return None

def protected(name, code, context):
    functions[name] = code
    if context == "disallowed":
        return None
    elif context == "allowed":
        return functions[name]()
    elif context == "protected":
        if caller == "subclass" or caller == "same_class":
            return code
        else:
            return None
    else:
        exit()

def isuppercase(text): return text.isupper()
def islowercase(text): return text.islower()
def countcharacter(text, char): return text.count(char)
def removecharacter(text, char): return text.replace(char, "")
def replacecharacter(text, text2, char): return text.replace(char, text2)
def replaceword(text, old, new): return text.replace(old, new)
def removeword(text, toremove): return text.replace(toremove, "")
def swapcase(text): return text.swapcase()
def reversetext(text): return text[::-1]
def writeuppercase(text): return text.upper()
def writelowercase(text): return text.lower()
def find(text, tofind): return text.find(tofind)
def capitalize(text, tocapitalize): return text.capitalize(tocapitalize)
def removestart(text, starttoremove): return text.removeprefix(starttoremove)
def removeend(text, endtoremove): return text.removesuffix(endtoremove)
def maximum(dictionary, key=None): return max(dictionary, key)
def minimum(dictionary, key=None): return min(dictionary, key)
def sortby(dictionary, key=None): return sorted(dictionary, key)

def msgboxerror(title, text):
    messagebox.showerror(title, text)

def msgboxinfo(title, text):
    messagebox.showinfo(title, text)

def msgboxwarning(title, text):
    messagebox.showwarning(title, text)

def msgboxokcancel(title, text):
    return messagebox.askokcancel(title, text)

def msgboxquestion(title, text):
    return messagebox.askquestion(title, text)

def creategui(title, geometry, bg, icon, fullscreen=False):
    efn_root = tk.Tk()
    efn_root.title(title)
    efn_root.geometry(geometry)
    efn_root.configure(bg=bg)
    if platform.system() == "Windows":
        efn_root.iconbitmap(icon)
    else:
        iconimg = tk.PhotoImage(file=icon)
        efn_root.iconphoto(False, iconimg)
    efn_root.attributes("-fullscreen", fullscreen)
    return efn_root

def fullscreenmode(efn_root, fullscr=False):
    efn_root.attributes("-fullscreen", fullscr)

def bind(efn_root, widgetorroot, how, function):
    widgetorroot.bind(f"<{how}>", function)

def setfocus(efn_root, widgetorroot):
    widgetorroot.focus_set()

def listbox(efn_root, efnframe, width):
    tk.Listbox(efnframe, width=width)

def getsystemarguementvector():
    return sys.argv

def getlengthofsystemarguementvector():
    return len(sys.argv)

def efnimport(module_name):
    return importlib.import_module(module_name)

def efnfromimport(module_name, symbol_name):
    module = importlib.import_module(module_name)
    return getattr(module, symbol_name)

def efnimportas(module_name, alias_name):
    module = importlib.import_module(module_name)
    globals()[alias_name] = module

def efnfromimportas(module_name, symbol_name, alias_name):
    module = importlib.import_module(module_name)
    globals()[alias_name] = getattr(module, symbol_name)

def tryexcept(try_action, except_type=None, except_action=None, finally_action=None):
    if except_type == "AllError":
        except_type = "Exception"
    elif except_type == "InputOutputError":
        except_type = "IOError"
    try:
        try_action()
    except Exception as e:
        if except_type is None or isinstance(e, eval(except_type)):
            if except_action:
                except_action(e)
            else:
                return f"Caught exception: {e}"
        else:
            return f"Unhandled exception: {e}"
    finally:
        if finally_action:
            finally_action()
        
def textingui(efn_root, efnframe, label_id, text, color, bgcolor, fonttype, fontsize, side):
    if efnframe is None:
        efnframe = efn_root

    if not hasattr(efnframe, "textinguiLabels"):
        efnframe.textinguiLabels = {}

    if label_id in efnframe.textinguiLabels and efnframe.textinguiLabels[label_id].winfo_exists():
        label = efnframe.textinguiLabels[label_id]
        label.config(text=text, fg=color, bg=bgcolor, font=(fonttype, fontsize))
    else:
        label = tk.Label(efnframe, text=text, fg=color, bg=bgcolor, font=(fonttype, fontsize))
        label.pack(side=side)
        efnframe.textinguiLabels[label_id] = label

    return label

def buttonthreed(efn_root, efnframe, text, color, bgcolor, fonttype, fontsize, command, side): 
    tk.Button(efnframe, text=text, fg=color, bg=bgcolor, font=(fonttype, fontsize), command=command).pack(side=side)

def buttonflat(efn_root, efnframe, text, color, bgcolor, fonttype, fontsize, command, side): 
    tk.Button(efnframe, text=text, fg=color, bg=bgcolor, relief="flat", font=(fonttype, fontsize), command=command).pack(side=side)

def waitforguianswer(efn_root, efnframe, name, side):
    globals()[name] = tk.Entry(efnframe)
    globals()[name].pack(side=side)

def readfromentry(efn_root, name):
    return globals()[name].get()

def waittimegui(seconds, function):
    Timer(seconds, function).start()

def integervargui(*args, **kwargs):
    return tk.IntVar(*args, **kwargs)

def floatvargui(*args, **kwargs):
    return tk.FloatVar(*args, **kwargs)

def stringvargui(*args, **kwargs):
    return tk.StringVar(*args, **kwargs)

def booleanvargui(*args, **kwargs):
    return tk.BooleanVar(*args, **kwargs)

def activeguiitem(efn_root, widget):
    widget.configure(state=tk.ACTIVE)

def disabledguiitem(efn_root, widget):
    widget.configure(state=tk.DISABLED)

def normalguiitem(efn_root, widget):
    widget.configure(state=tk.NORMAL)

def atend(efn_root=False):
    return tk.END

def value(variable):
    return variable

def getwidgetstate(efn_root, widget):
    widget.cget("state")

def getwidgetdata(efn_root, widget, toget):
    widget.cget(toget)

def hasattribute(obj, attributename):
    return hasattr(obj, attributename)

def getattribute(obj, attributename):
    return getattr(obj, attributename)

def structure(name, *args, **kwargs):
    structures[name] = {"args": args, "kwargs": kwargs}

def callstructure(name, variablename=None):
    if variablename is not None:
        variablename = exec(structures[name], globals())
    else:
        exec(structures[name], globals())

def createnamespace(name, code):
    namespaces[name] = code

def runnamespace(name):
    exec(namespaces[name], globals())

def Isinstance(obj, type_):
    return isinstance(obj, type_)

def createiterator(value):
    return iter(value)

def calldictionaryvalue(dictionary, value, defualt=None):
    return dictionary.get(value, default)

def flipwidgetstate(efn_root, widget):
    current = widget.cget("state")
    new_state = "normal" if current == "disabled" else "disabled"
    widget.configure(state=new_state)

def setdataonwidget(efn_root, widget, value):
    if hasattr(widget, "set"):
        widget.set(value)
    elif hasattr(widget, "insert"):
        widget.delete(0, tk.END)
        widget.insert(0, value)
    else:
        print("Unsupported widget type for setting data.")

def getdatafromwidget(efn_root, widget, *args, **kwargs):
    return widget.get(*args, **kwargs)

def updategui(efn_root):
    efn_root.update()

def exitfromgui(efn_root):
    efn_root.destroy()

def hidemaingui(efn_root):
    efn_root.withdraw()

def waitguiwindow(efn_root):
    efn_root.wait_window()

def setmodalonguiwindow(efn_root):
    efn_root.grab_set()

def setfocusongui(efn_root):
    efn_root.focus_set()

def keepguiontop(efn_root):
    efn_root.transistent()

def topgeometryofwidget(efn_root, widget, topgeometry):
    widget.top.geometry(topgeometry)
    
def createcanvas(efn_root, width=300, height=200, bg="white"):
    canvas = tk.Canvas(efn_root, width=width, height=height, bg=bg)
    canvas.pack()
    return canvas

def drawoncanvas(canvas, todraw, *args, **kwargs):
    draw_method = getattr(canvas, todraw, None)
    if callable(draw_method):
        return draw_method(*args, **kwargs)
    else:
        print(f"Error: '{todraw}' is not a valid canvas method.")

def dialogaskstring(title, question):
    simpledialog.askstring(title, question)

def dialogaskint(title, question):
    simpledialog.askint(title, question)

def dialogaskfloat(title, question):
    simpledialog.askfloat(title, question)

def colorwindow(color=None, title=None, parent=None, initialcolor=None):
    askcolor(color=color, title=title, parent=parent, initialcolor=initialcolor)

def case(variabletocase, tocase, casingaction, defaultaction=None):
    if variabletocase == tocase:
        exec(casingaction, globals())
    else:
        if defaultaction is not None:
            exec(defaultaction, globals())
        else:
            print("Fell back to default action.")

def scrolledtext(efn_root, efnframe, text, typeof, side):
    if typeof == "readonly":
        scrolled = ScrolledText(efnframe)
        scrolled.pack(side=side)
        
        scrolled.insert("1.0", text)
        scrolled.configure(state="disabled")
        
    elif typeof == "editable":
        scrolled = ScrolledText(efnframe)
        scrolled.pack(side=side)

        scrolled.insert(tk.END, text)
        content = scrolled.get("1.0", tk.END)
        
    else:
        print("Unsupported scrolledtext type.")
    return scrolled

def textwidget(efn_root, efnframe, text, typeof, side):
    if typeof == "readonly":
        txt = tk.Text(efnframe)
        txt.pack(side=side)

        txt.insert(tk.END, text)
        txt.configure(state="disabled")

    elif typeof == "editable":
        txt = tk.Text(efnframe)
        txt.pack(side=side)

        txt.insert(tk.END, text)
        content = txt.get("1.0", tk.END)

    else:
        print("Unsupported textwidget type.")
    return txt

def messagewidget(efn_root, efnframe, text, width, bgcolor, fgcolor, fonttype, fontsize, side):
    tk.Message(efnframe, text=text, width=width, bg=bgcolor, fg=fgcolor, font=(fonttype, fontsize)).pack(side=side)

def checkbutton(efn_root, efnframe, text, side):
    var = tk.IntVar()
    cb = tk.Checkbutton(efnframe, text=text, variable=var)
    cb.pack(side=side)
    return var

def radiobutton(efn_root, efnframe, options, side, variable=None):
    if variable is None:
        variable = tk.StringVar()
    for text, value in options:
        rb = tk.Radiobutton(efnframe, text=text, variable=variable, value=value)
        rb.pack(side=side)
    return variable

def hidewidget(efn_root, widget):
    widget.pack_forget()

def hideplaceforget(efn_root, widget):
    widget.place_forget()

def showwidget(efn_root, widget, side):
    widget.pack(side=side)

def pausewindow(efn_root):
    efn_root.quit()

def minimizewindow(efn_root):
    efn_root.iconify()

def restorewindow(efn_root):
    efn_root.deiconify()

def updaterootidletasks(efn_root):
    efn_root.update_idletasks()

def makewindowtransparent(efn_root, transfloat):
    efn_root.attributes("-alpha", transfloat)

def disableuserinteractiongui(efn_root, userinteraction):
    efn_root.attributes("-disabled", userinteraction)

def shrinkwindowtools(efn_root, shrinktools):
    efn_root.attributes("-toolwindow", shrinktools)

def makeguicolortransparent(efn_root, color):
    efn_root.attributes("-transparentcolor", color)

def guitypelinux(efn_root, typeofgui):
    efn_root.attributes("-type", typeofgui)

def zoomedgui(efn_root, zoomed):
    efn_root.attributes("-zoomed", zoomed)

def stayguiontop(efn_root, stayontop):
    efn_root.attributes("-topmost", stayontop)

def addmenu(efn_root, menus):
    menubar = tk.Menu(efn_root)
    for menu_name, items in menus.items():
        menu = tk.Menu(menubar, tearoff=0)
        for label, command in items:
            menu.add_command(label=label, command=lambda cmd=command: call(cmd))
        menubar.add_cascade(label=menu_name, menu=menu)
    efn_root.config(menu=menubar)

def waittimemillisecondsgui(efn_root, ms, func):
    efn_root.after(ms, func)

def packguielement(efn_root, widget):
    widget.pack()

def internalpaddingofwidget(efn_root, widget, ipadx, ipady):
    try:
        widget.pack_configure(ipadx=ipadx, ipady=ipady)
    except:
        try:
            widget.grid_configure(ipadx=ipadx, ipady=ipady)
        except Exception as e:
            print(f"Error: {e}")

def paddingofwidget(efn_root, widget, padx, pady):
    try:
        widget.pack_configure(padx=padx, pady=pady)
    except:
        try:
            widget.grid_configure(padx=padx, pady=pady)
        except Exception as e:
            print(f"Error: {e}")

def placeofwidget(efn_root, widget, x, y):
    try:
        widget.place(x=x, y=y)
    except Exception as e:
        print(f"Could not place widget: {e}")

def setpositionofwidget(efn_root, widget, anchor):
    try:
        widget.pack_configure(anchor=anchor)
    except:
        try:
            widget.place_configure(anchor=anchor)
        except:
            try:
                widget.grid_configure(sticky=anchor)
            except Exception as e:
                print(f"Could not apply anchor '{anchor}' to widget.")

def alignwidget(efn_root, widget, sticky):
    try:
        widget.grid_configure(sticky=sticky)
    except Exception as e:
        print(f"Couldn't align the widget '{widget}'. Error: {e}")

def rowandcolumnofwidget(efn_root, widget, row, column):
    try:
        widget.grid(row=row, column=column)
    except Exception as e:
        print(f"Could not grid widget: {e}")

def rowspanandcolumnspanofwidget(efn_root, widget, rowspan, columnspan):
    try:
        widget.grid_configure(rowspan=rowspan, columnspan=columnspan)
    except:
        print(f"Could not apply the rowspan and the columnspan. Error: {e}")

def relativepositionofwidget(efn_root, widget, relx, rely):
    try:
        widget.place(relx=relx, rely=rely)
    except Exception as e:
        print(f"Could not apply relative position: {e}")

def sideofwidget(efn_root, widget, side):
    try:
        widget.pack_configure(side=side)
    except Exception as e:
        print(f"Error while applying the side argument. Error: {e}")

def stateofwidget(efn_root, widget, state):
    try:
        widget.pack_configure(state=state)
    except Exception as e1:
        try:
            widget.place_configure(state=state)
        except Exception as e2:
            try:
                widget.grid_configure(state=state)
            except Exception as e3:
                print(f"Error while applying the state of the widget. Error: {e3}")

def widthandheightofwidget(efn_root, widget, width, height):
    try:
        widget.pack_configure(width=width, height=height)
    except Exception as e1:
        try:
            widget.place_configure(width=width, height=height)
        except Exception as e2:
            try:
                widget.grid_configure(width=width, height=height)
            except Exception as e3:
                print(f"Error while applying the width and the height of the widget. Error: {e3}")

def textofwidget(efn_root, widget, text):
    try:
        widget.pack_configure(text=text)
    except Exception as e1:
        try:
            widget.place_configure(text=text)
        except Exception as e2:
            try:
                widget.grid_configure(text=text)
            except Exception as e3:
                print(f"Error while applying the text of the widget. Error: {e3}")

def Set(target, key=None, value=None):
    if key in None:
        return set(target)
    else:
        if hasattr(target, "configure"):
            target.configure({key: value})
        elif isinstance(target, dict):
            target[key] = value
        else:
            setattr(target, key, value)

def setattribute(objectclass, attributetoset, valuetoset):
    return setattr(objectclass, attributetoset, valuetoset)

def createfilter(filtername, tofilter):
    return filter(filtername, tofilter)

def listnumbersorvalues(start, stop):
    return range(start, stop)

def configuretowidget(efn_root, widget, toconfigure):
    widget.configure(toconfigure)

def gridwidget(efn_root, widget):
    widget.grid()

def Event(event):
    return {
        "eventkeysymbol": event.keysym,
        "eventkeypressed": event.char,
        "eventtype": event.type,
        "widgetwithevent": event.widget,
        "vericalpositionroot": event.y_root,
        "horizontalpositionroot": event.x_root,
        "vericalposition": event.y,
        "horizontalposition": event.x,
        "none": None
    }

def windowinfo(widget):
    return {
        "x": widget.winfo_x(),
        "y": widget.winfo_y(),
        "width": widget.winfo_width(),
        "height": widget.winfo_height(),
        "screenwidth": widget.winfo_screenwidth(),
        "screenheight": widget.winfo_screenheight(),
        "ismapped": widget.winfo_ismapped(),
        "exists": widget.winfo_exists(),
        "toplevel": widget.winfo_toplevel(),
        "geometry": widget.winfo_geometry(),
        "class": widget.winfo_class(),
        "name": widget.winfo_name(),
        "id": widget.winfo_id()
    }

def setobjectoperator(objname, op, func):
    objects[objname][f"__{op}__"] = func

def loadplugin(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("plugin", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "register"):
        mod.register()

def createtoplevelwindow(
    master,
    title,
    geometry,
    bg,
    icon,
    fullscreen
):
    popup = Toplevel(master)
    popup.title(title)
    popup.geometry(geometry)
    popup.configure(bg=bg)

    if icon:
        popup.iconbitmap(icon)

    popup.attributes("-fullscreen", fullscreen)

    return popup

def placewidget(widgetname, horizontal, vertical):
    widgetname.place(x=horizontal, y=vertical)

def frame(efn_root, width, side):
    efnframe = tk.Frame(efn_root, width=width)
    efnframe.pack(side=side)
    return efnframe

def showimagegui(efn_root, efnframe, image_path, width, height, side):
    img1 = Image.open(image_path).resize((width, height))
    photo1 = ImageTk.PhotoImage(img1)
    tk.Label(efn_root, image=photo1).pack(side=side)

def sharecharacter(text, text2, custom_action=None, custom_action2=None):
    shared = set(text) & set(text2)
    
    if shared:
        if custom_action:
            custom_action(text, text2)
        else:
            print("True")
        return True
    else:
        if custom_action2:
            custom_action2(text, text2)
        else:
            print("False")
        return False

def showdatetime():
    return datetime.now()

def twodigityear():
    return datetime.now().strftime("%y")

def fourdigityear():
    return datetime.now().strftime("%Y")

def fullweekdayname():
    return datetime.now().strftime("%A")

def threeletterweekdayname():
    return datetime.now().strftime("%a")

def weekdaynumbersundayfirst():
    return datetime.now().strftime("%w")

def daynumber():
    return datetime.now().strftime("%d")

def dayofyear():
    return datetime.now().strftime("%j")

def weeknumbersundayfirst():
    return datetime.now().strftime("%U")

def weeknumbermondayfirst():
    return datetime.now().strftime("%W")

def shortenedmonthname():
    return datetime.now().strftime("%b")

def fullmonthname():
    return datetime.now().strftime("%B")

def monthinnumbers():
    return datetime.now().strftime("%m")

def twentyfourhourtimeformat():
    return datetime.now().strftime("%H")

def twelvehourtimeformat():
    return datetime.now().strftime("%I")

def minutes():
    return datetime.now().strftime("%M")

def seconds():
    return datetime.now().strftime("%S")

def microseconds():
    return datetime.now().strftime("%f")

def amorpm():
    return datetime.now().strftime("%p")

def timezoneoffset():
    return datetime.now().strftime("%z")

def timezonename():
    return datetime.now().strftime("%Z")

def localedatetime():
    return datetime.now().strftime("%c")

def localedate():
    return datetime.now().strftime("%x")

def localetime():
    return datetime.now().strftime("%X")

def literalpercent():
    return datetime.now().strftime("%%")

def systemdo(todo):
    os.system(todo)

def systemstart(filename):
    os.startfile(filename)

def systemdeletefile(filename):
    os.remove(filename)

def systemdeletefolder(foldername):
    shutil.rmtree(foldername)

def systemcopyfile(file, towhere):
    shutil.copy(file, towhere)

def systemcopydir(directory, towhere):
    shutil.copytree(directory, towhere)

def systemmove(fileorfolder, towhere):
    shutil.move(fileorfolder, towhere)

def wait(timewait):
    time.sleep(timewait)

def c(text):
    pass

def o(line):
    return f"# {line}"

def multistring(text):
    return '"""{text}"""'

def executecode(code):
    exec(code, globals())

def preprocess(code, tocode, fromcode):
    return code.replace(f"{tocode}", f"{fromcode}")

def varplusplus(variable):
    variables[variable] += 1

def varminusminus(variable):
    variables[variable] -= 1

def varmultiplymultiply(variable):
    variables[variable] *= 2

def vardividedivide(variable):
    variables[variable] /= 2

def addto(var, amount):
    variables[var] += amount

def subtractto(var, amount):
    variables[var] -= amount

def multiplyto(var, amount):
    variables[var] *= amount

def divideto(var, amount):
    if amount == 0:
        if variables[var] == 0:
            variables[var] = float("nan")
        else:
            variables[var] = float("inf")
    else:
        variables[var] /= amount

def If(condition, action):
    if eval(condition, {}, variables):
        exec(action)

def elseif(condition, action):
    if not variables.get("__last_condition", False):
        if eval(condition, {}, variables):
            variables["__last_condition"] = True
            exec(action)

def Else(action):
    if not variables.get("__last_condition", False):
        exec(action)
    variables["__last_condition"] = False

def define(name, code):
    functions[name] = code

def updatefunction(name, code):
    if name in functions:
        functions[name] = code
    else:
        print(f"Function '{name}' not found.")

def limitedexecution(name, timeout):
    if name in functions:
        def exitfromfunc():
            return None
        exec(functions[name], globals())
        Timer(timeout, exitfromfunc).start()
    else:
        print(f"Function '{name}' not found.")

def intfunction(name, code):
    nameint = "int" + name 
    functions[nameint] = code

def floatfunction(name, code):
    namefloat = "float" + name 
    functions[namefloat] = code

def call(name, undo=False, *args, **kwargs):
    if undo:
        return None
    else:
        if name in functions:
            return functions[name](*args, **kwargs)
        else:
            print(f"Function '{name}' not found.")

def callintfunction(nameint, undo=False, *args, **kwargs):
    if undo:
        return None
    else:
        if nameint in functions:
            return functions[nameint](
            *map(int, args),
            **{k: int(v) for k, v in kwargs.items()})
        else:
            print(f"Integer function '{nameint}' not found.")

def callfloatfunction(namefloat, undo=False, *args, **kwargs):
    if undo:
        return None
    else:
        if namefloat in functions:
            return functions[namefloat](
            *map(float, args),
            **{k: float(v) for k, v in kwargs.items()})
        else:
            print(f"Float function '{namefloat}' not found.")

def Class(name, body):
    classes[name] = body

def newobject(name, classname):
    if classname in classes:
        objects[name] = {"__class__": classname}
        exec(classes[classname], {}, {"self": objects[name], "write": write})
    else:
        print(f"Class {classname} was not found.")

def contains(textct, text, custom_action=None, custom_action2=None):
    if textct in text:
        if custom_action:
            custom_action(textct, text)
        else:
            print(f"'{textct}' found in '{text}' but no custom action was specified.")
            return True
    else:
        if custom_action2:
            custom_action2(textct, text)
        else:
            print(f"'{textct}' not found in '{text}' and no custom action was specified.")
            return False

def Break():
    return False

def repeat(thing, times, custom_action=None):
    for thing in range(times):
        if custom_action:
            result = custom_action(thing)
            if Break():
                break
        else:
            print("No custom action was specified.")

def whilerepeat(condition, custom_action=None):
    while condition():
        if custom_action:
            result = custom_action()
            if Break():
                break
        else:
            print("No custom action was specified.")

def whiletrue(custom_action=None):
    if custom_action:
        while True:
            result = custom_action()
            if Break():
                break
    else:
        print("No custom action was specified.")

def until(condition, custom_action=None):
    if custom_action:
        while not condition():
            result = custom_action()
            if result is None:
                break
    else:
        print("No custom action was specified.")

def foreach(varname, collection, custom_action=None):
    for item in collection:
        if custom_action:
            result = custom_action(item)
            if Break():
                break
        else:
            print(f"No custom action was specified.")

def let(name, value=None):
    if value is not None:
        efnvars[name] = value
    return efnvars.get(name)

def Makeitemglobal(name, value):
    globals()[name] = value

def Getfromglobalitem(name):
    globals()[name].get()

def inputconsole(varname, text, inputtype):
    if inputtype == "float":
        value = float(input(text))
    elif inputtype == "int":
        value = int(input(text))
    elif inputtype == "standard":
        value = input(text)
    else:
        exit()

    globals()[varname.__name__] = value
    return value

def createlist(lst, sep=", "):
    return sep.join(map(str, lst))

def Sepjoin(*args, sep=" ", start="", end=""):
    parts = [str(arg) for arg in args]
    joined = sep.join(parts)
    return f"{start}{joined}{end}"

def Isdigit(*args):
    return [str(arg).isdigit() for arg in args]

def connectdraw(title, bg):
    screen = turtle.Screen()
    screen.title(title)
    screen.bgcolor(bg)
    return screen

def drawcircle(color, size):
    turtle.color(color)
    turtle.begin_fill()
    turtle.circle(size)
    turtle.end_fill()

def drawtriangle(color):
    turtle.color(color)
    turtle.begin_fill()
    for _ in range(3):
        turtle.forward(100)
        turtle.left(120)
    turtle.end_fill()

def drawsquare(color):
    turtle.color(color)
    turtle.begin_fill()
    for _ in range(4):
        turtle.forward(100)
        turtle.left(90)
    turtle.end_fill()

def Return(value=None):
    if value is not None:
        return value
    else:
        return

def Yieldpause(value=None):
    if value is not None:
        yield value
    else:
        yield

def represent(value):
    return repr(value)

def List(listvariable):
    return f"{list(listvariable)}"

def getvalue(dictionary, key):
    return dictionary.get(key)

def popvalue(d, key):
    return dictionary.pop(key, None)

def listkeys(dictionary):
    return list(dictionary.keys())

def listvalues(dictionary):
    return list(dictionary.values())

def listitems(dictionary):
    return list(dictionary.items())

def updateitems(dictionary, newitems):
    dictionary.update(newitems)
    return dictionary

def cleardictionary(dictionary):
    dictionary.clear()
    return dictionary

def Raise(errororclass):
    raise errororclass

def attachto(variable, toattach):
    variable.attach(toattach)

def draganddropicon(text):
    Icon(text)

def draganddropbase(efn_root):
    Tester(efn_root)

def createcustomerror(name, code):
    customerrors[name] = code

def raisecustomerror(name):
    exec(customerrors[name], globals())

def removecustomerror(name):
    customerrors.remove(name)

def concat(args):
    result = ""
    for arg in args:
        result += str(arg)
    return result

def Append(variable, toappend):
    variable.append(toappend)

def Extend(variable, toextend):
    variable.extend(toextend)

def Insert(variable, index, toinsert):
    variable.insert(index, toinsert)

def Remove(variable, toremove):
    variable.remove(toremove)

def Removebyindex(variable, index):
    variable.pop(index)

def Clear(variable):
    variable.clear()

def Findbyindex(variable, tofind):
    return variable.index(tofind)

def Sort(variable):
    variable.sort()

def Reverse(variable):
    variable.reverse()

def Shallowcopy(variable):
    return variable.copy()

def randomchoice(options):
    return random.choice(options)

def shufflelist(lst):
    random.shuffle(lst)
    return lst

def add(num1, num2):
    return num1 + num2

def subtract(num1, num2):
    return num1 - num2

def multiply(num1, num2):
    return num1 * num2

def divide(num1, num2):
    if num2 == 0:
        if num1 == 0:
            return "NaN"
        else:
            return "Infinity"
    else:
        return num1 / num2           

def sin(num1):
    return math.sin(num1)

def cos(num1):
    return math.cos(num1)

def tan(num1):
    return math.tan(num1)

def log(num1, num2):
    return math.log(num1, num2)

def factorial(num1):
    return math.factorial(num1)

def percentage(num1):
    return num1 / 100

def bxor(num1, num2):
    return num1 ^ num2

def root(num1, num2):
    return math.pow(num1, 1/num2)
    
def pi():
    return "3.1415926535897932384626433832795028831971"

def e():
    return math.e

def phi():
    phi = (1 + math.sqrt(5)) / 2
    return phi

def gamma():
    return "0.577215664901"

def apery():
    return "1.2020569031595942"

def feigenbaumdelta():
    return "4.6692016091029"

def naturallogoftwo():
    return "0.69314718055994530941723212145"

def imaginaryself():
    return "0.2078795763507619085469556198349787700339"

def liouvillenumber():
    return "0.110001000000000000000001000"

def G():
    return "4.2432723820187182387231789037807870238466580344023094560327632965932456329650965065936563656953042693043456635496532497128778237652238970466650426065095346534625630245602546590345639630469536594695346594969650659046326953434372372898198278760665353663727818818187548745789548326721073279378467839416854707760346704737734875834784365653627812899087264664553537178891907276464646738282847387743282818018271872128273247381244536271890186535353632897650134267832632735909234304936543693926543921649304528967541302298056347145"

def floatG():
    return float(G())

def modulo(num1, num2):
    return num1 % num2

def sqrt(num):
    return math.sqrt(num)

def rounddowntopreviousnumber(num):
    return math.floor(num)

def rounduptonextnumber(num):
    return math.ceil(num)

def roundbyone(num):
    if num % 1 == 0.5 or num % 1 == -0.5:
        return math.ceil(num)
    else:
        return round(num)

def roundbyten(num):
    remainder = num % 10

    if remainder > 5:
        return num + (10 - remainder)
    elif remainder < 5:
        return num - remainder
    elif remainder == 5:
        if num < 0:
            return num - 5
        else:
            return num + 5
    else:
        return num

def roundbyonehundred(num):
    remainder = num % 100

    if remainder > 50:
        return num + (100 - remainder)
    elif remainder < 50:
        return num - remainder
    elif remainder == 50:
        if num < 0:
            return num - 50
        else:
            return num + 50
    else:
        return num

def roundbyonethousand(num):
    remainder = num % 1000

    if remainder > 500:
        return num + (1000 - remainder)
    elif remainder < 500:
        return num - remainder
    elif remainder == 500:
        if num < 0:
            return num - 500
        else:
            return num + 500
    else:
        return num

def parentheses(*args):
    return tuple(float(arg) for arg in args)

def immutable(*args):
    {"args": args}
    return tuple(args)

def leftstrip(text, tostrip=None):
    return text.lstrip(tostrip)

def rightstrip(text, tostrip=None):
    return text.rstrip(tostrip)

def everyitem(dictionarytoread):
    return all(dictionarytoread)

def anyitemnotall(dictionarytoread):
    return any(dictionarytoread)

def fontofwidget(efn_root, widget, fonttype, fontsize):
    try:
        widget.configure(font=((fonttype, fontsize)))
    except Exception as e:
        print(f"Error while applying the font of the widget. Error: {e}")

def red(efn_root, quantity):
    r = quantity
    return f"{r:02x}"

def green(efn_root, quantity):
    g = quantity
    return f"{g:02x}"

def blue(efn_root, quantity):
    b = quantity
    return f"{b:02x}"

def alpha(efn_root, quantity):
    a = int(quantity * 255)
    return f"{a:02x}"

def rgba(efn_root, red, green, blue, alpha):
    Alpha = int(alpha * 255)
    return f"#{red:02x}{green:02x}{blue:02x}{Alpha:02x}"

def ForIn(forarg, inarg):
    return [forarg(x) for x in inarg]

def subprocesspop(subprocessname):
    subprocess.Popen(subprocessname)

def Typeofvariablevalue(variable):
    return type(variable)

def Stringstr(variable):
    return str(variable)

def integernumber(variable):
    return int(variable)

def assignwithwalrus(value):
    return (temp := value)

def mediatype(variablename, typeofmedia):
    return variablename[typeofmedia]

def asyncdef(functionname, code, *args, **kwargs):
    func_code = f"""
async def {functionname}(*args, **kwargs):
    {code}
"""
    exec(func_code, globals())

    return globals()[functionname]

def runasync(func, *args, **kwargs):
    return asyncio.run(func(*args, **kwargs))

def removeprefix(prefix, variable):
    if variable.startswith(prefix):
        return variable[len(prefix):]
    return variable

def addprefix(prefix, variable):
    return prefix + variable

def createtask(taskname):
    return asyncio.create_task(taskname)

def sleepwait(delay, result=None):
    return asyncio.sleep(delay, result)
    return result

def awaitfor(coro):
    async def runner():
        await coro
    asyncio.run(runner())

def createwarning(text: str, classofwarning=None):
    warnings.warn(text, classofwarning)

def addsuffix(suffix, variable):
    return variable + suffix

def removesuffix(suffix, variable):
    if variable.endswith(suffix):
        return variable[:-len(suffix)]
    return variable

def openinbrowser(link):
    webbrowser.open(link)

def createwebview(title, link, height=None, width=None, resizable=False):
    webview.create_window(title, link, height=height, width=width, resizable=resizable)

def startwebview():
    webview.start()

def stopwebview():
    webview.stop()

def isnumeric(variable):
    return variable.isnumeric()

def isalphanumeric(variable):
    return variable.isalnum()

def findallin(variable, whattofind):
    return [item for item in variable if item == whattofind]

def guihorizontal(widget):
    widget.configure(orient=tk.HORIZONTAL)

def guivertical(widget):
    widget.configure(orient=tk.VERTICAL)

def commandinguiwidget(widget, command):
    widget.configure(command=command)

def scalewidget(efnframe, fromdata, todata, orient=None):
    scale = tk.Scale(efnframe, from_=fromdata, to=todata, orient=tk.HORIZONTAL if orient is None else orient)
    scale.pack()
    return scale

def bothgui(efn_root):
    return tk.BOTH

def selectorwidget(efnframe, values, orient=None):
    if orient is None or tk.HORIZONTAL or guihorizontal():
        class HorizontalCombo(tk.Frame):
            def __init__(self, master, items, command=None, **kwargs):
                super().__init__(master, **kwargs)
                self.items = items
                self.command = command
                self.selected = tk.StringVar()
        
                self.entry = tk.Entry(self, textvariable=self.selected, state="readonly", width=20)
                self.entry.pack(side="left")
        
                self.button = tk.Button(self, text="▼", command=self.toggle_menu)
                self.button.pack(side="left")

                self.menu_frame = tk.Frame(self)
                self.menu_buttons = []
                for item in items:
                    btn = tk.Button(self.menu_frame, text=item, command=lambda i=item: self.select(i))
                    btn.pack(side="left", padx=2)
                    self.menu_buttons.append(btn)

                self.menu_visible = False

            def toggle_menu(self):
                if self.menu_visible:
                    self.menu_frame.pack_forget()
                else:
                    self.menu_frame.pack(side="bottom", pady=5)
                self.menu_visible = not self.menu_visible

            def select(self, item):
                self.selected.set(item)
                self.toggle_menu()
                if self.command:
                    self.command(item)
                    
        combo = HorizontalCombo(efn_root, items=values)
        combo.pack(padx=20, pady=20)
                    
        return combo

    elif orient is tk.VERTICAL or guivertical():
        combo = ttk.Combobox(efnframe, values=values)
        combo.pack()
        return combo

    else:
        warnings.warn("The GUI element selectorwidget() excepts tk.VERTICAL, tk.HORIZONTAL or None. You can also set the orient up with these predefined functions: horizontalgui() and verticalgui().")

def setselectorcurrent(efn_root, selectorwidgetvariable, number):
    selectorwidgetvariable.current(number)

def guianalogclock(efn_root):
    class GUIAnalogClock(tk.Canvas):
        def __init__(self, master, size=300):
            super().__init__(master, width=size, height=size, bg="white", highlightthickness=0)
            self.size = size
            self.center = size // 2
            self.radius = self.center - 10
            self.hands = {
                "hour": self.create_line(0, 0, 0, 0, width=6, fill="#222"),
                "minute": self.create_line(0, 0, 0, 0, width=4, fill="#444"),
                "second": self.create_line(0, 0, 0, 0, width=2, fill="#e33")
            }
            self.draw_face()
            self.update_clock()

        def draw_face(self):
            self.create_oval(10, 10, self.size-10, self.size-10, outline="#aaa", width=2)
            for i in range(12):
                angle = math.radians(i * 30 - 90)
                x = self.center + self.radius * 0.85 * math.cos(angle)
                y = self.center + self.radius * 0.85 * math.sin(angle)
                self.create_text(x, y, text=str(i if i != 0 else 12), font=("Arial", 12, "bold"))

        def update_clock(self):
            now = time.localtime()
            self.draw_hand("hour", (now.tm_hour % 12 + now.tm_min / 60) * 30, self.radius * 0.5)
            self.draw_hand("minute", now.tm_min * 6, self.radius * 0.75)
            self.draw_hand("second", now.tm_sec * 6, self.radius * 0.9)
            self.after(1000, self.update_clock)

        def draw_hand(self, name, angle_deg, length):
            angle_rad = math.radians(angle_deg - 90)
            x = self.center + length * math.cos(angle_rad)
            y = self.center + length * math.sin(angle_rad)
            self.coords(self.hands[name], self.center, self.center, x, y)
            
    analogclock = GUIAnalogClock(efn_root)
    return analogclock

def gcw(green, cyan, white):
    greenRGB = (0, 255, 0)
    cyanRGB = (0, 255, 255)
    whiteRGB = (255, 255, 255)

    red   = int(green * greenRGB[0] + cyan * cyanRGB[0] + white * whiteRGB[0])
    green = int(green * greenRGB[1] + cyan * cyanRGB[1] + white * whiteRGB[1])
    blue  = int(green * greenRGB[2] + cyan * cyanRGB[2] + white * whiteRGB[2])

    red = max(0, min(255, red))
    green = max(0, min(255, green))
    blue = max(0, min(255, blue))

    return f"#{red:02x}{green:02x}{blue:02x}"

def rungui(efn_root):
    efn_root.mainloop()

def updatewidget(efn_root, widget):
    widget.update()

def afterwidget(efn_root, widget, milliseconds, function):
    widget.after(milliseconds, function)

def buttonflat(efn_root, efnframe, text, color, bgcolor, fonttype, fontsize, command, side):
    target = efnframe if efnframe else efn_root
    flag = f"buttonflat_{text}_created"
    if not hasattr(target, flag):
        tk.Button(target, text=text, fg=color, bg=bgcolor, relief="flat", font=(fonttype, fontsize), command=command).pack(side=side)
        setattr(target, flag, True)

def buttonthreed(efn_root, efnframe, text, color, bgcolor, fonttype, fontsize, command, side):
    target = efnframe if efnframe else efn_root
    flag = f"buttonthreed_{text}_created"
    if not hasattr(target, flag):
        tk.Button(target, text=text, fg=color, bg=bgcolor, font=(fonttype, fontsize), command=command).pack(side=side)
        setattr(target, flag, True)

def waitforguianswer(efn_root, efnframe, name, side):
    target = efnframe if efnframe else efn_root
    flag = f"entry_{name}_created"
    if not hasattr(target, flag):
        globals()[name] = tk.Entry(target)
        globals()[name].pack(side=side)
        setattr(target, flag, True)

def scrolledtext(efn_root, efnframe, text, typeof, side):
    target = efnframe if efnframe else efn_root
    flag = f"scrolledtext_{text[:10]}_created"
    if not hasattr(target, flag):
        scrolled = ScrolledText(target)
        scrolled.pack(side=side)
        if typeof == "readonly":
            scrolled.insert("1.0", text)
            scrolled.configure(state="disabled")
        elif typeof == "editable":
            scrolled.insert(tk.END, text)
        setattr(target, flag, True)
        return scrolled

def textwidget(efn_root, efnframe, text, typeof, side):
    target = efnframe if efnframe else efn_root
    flag = f"textwidget_{text[:10]}_created"
    if not hasattr(target, flag):
        txt = tk.Text(target)
        txt.pack(side=side)
        if typeof == "readonly":
            txt.insert(tk.END, text)
            txt.configure(state="disabled")
        elif typeof == "editable":
            txt.insert(tk.END, text)
        setattr(target, flag, True)
        return txt

def messagewidget(efn_root, efnframe, text, width, bgcolor, fgcolor, fonttype, fontsize, side):
    target = efnframe if efnframe else efn_root
    flag = f"message_{text[:10]}_created"
    if not hasattr(target, flag):
        tk.Message(target, text=text, width=width, bg=bgcolor, fg=fgcolor, font=(fonttype, fontsize)).pack(side=side)
        setattr(target, flag, True)

def checkbutton(efn_root, efnframe, text, side):
    target = efnframe if efnframe else efn_root
    flag = f"checkbutton_{text}_created"
    if not hasattr(target, flag):
        var = tk.IntVar()
        tk.Checkbutton(target, text=text, variable=var).pack(side=side)
        setattr(target, flag, True)
        return var

def radiobutton(efn_root, efnframe, options, side, variable=None):
    target = efnframe if efnframe else efn_root
    flag = f"radiobutton_{str(options)}_created"
    if not hasattr(target, flag):
        if variable is None:
            variable = tk.StringVar()
        for text, value in options:
            tk.Radiobutton(target, text=text, variable=variable, value=value).pack(side=side)
        setattr(target, flag, True)
        return variable

def digitaldatetimewidget(efn_root):
    target = efn_root
    if not hasattr(target, "digitaldatetime_created"):
        label = tk.Label(target)
        label.pack()
        def updatetime():
            label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            label.after(1000, updatetime)
        updatetime()
        setattr(target, "digitaldatetime_created", True)
        return label

def analogclock(efn_root):
    target = efn_root
    if not hasattr(target, "analogclock_created"):
        canvas = tk.Canvas(target, width=200, height=200, bg="white")
        canvas.pack()
        def drawclock():
            canvas.delete("all")
            canvas.create_oval(10, 10, 190, 190)
            now = datetime.now()
            sec = now.second
            min = now.minute
            hr = now.hour % 12
            sec_angle = math.radians(sec * 6)
            min_angle = math.radians(min * 6)
            hr_angle = math.radians(hr * 30 + min * 0.5)
            canvas.create_line(100, 100, 100 + 80 * math.sin(sec_angle), 100 - 80 * math.cos(sec_angle), fill="red")
            canvas.create_line(100, 100, 100 + 60 * math.sin(min_angle), 100 - 60 * math.cos(min_angle), width=2)
            canvas.create_line(100, 100, 100 + 40 * math.sin(hr_angle), 100 - 40 * math.cos(hr_angle), width=4)
            canvas.after(1000, drawclock)
        drawclock()
        setattr(target, "analogclock_created", True)
        return canvas

def numstrscale(efn_root, efnframe, items, fromdata):
    target = efnframe if efnframe else efn_root
    flag = f"stringscale_{str(items)}_created"
    if not hasattr(target, flag):
        values = items if isinstance(items, list) else []
        var = tk.IntVar()
        scale = tk.Scale(target, from_=fromdata if fromdata else 0, to=len(values) - 1, orient="horizontal", variable=var)
        scale.pack()
        label = tk.Label(target, text=values[0] if values else "")
        label.pack()
        def update_label(*_):
            index = var.get()
            label.config(text=values[index] if 0 <= index < len(values) else "")
        var.trace_add("write", update_label)
        setattr(target, flag, True)
        return scale

def customvarscale(efn_root, efnframe, values, orient, bg):
    parent = efnframe if efnframe else efn_root
    flag = f"customvarscale_{str(values)}_created"
    if not hasattr(parent, flag):
        mainframe = tk.Frame(parent, bg=bg if bg else "white")
        mainframe.pack()
        var = tk.StringVar(value=values[0])
        index = tk.IntVar(value=0)
        display = tk.Label(mainframe, text=values[0], bg=bg if bg else "white")
        display.pack()
        scale = tk.Scale(
            mainframe,
            from_=0,
            to=len(values) - 1,
            orient=orient if orient else tk.HORIZONTAL,
            showvalue=0,
            tickinterval=0,
            variable=index,
            command=lambda v: (var.set(values[int(v)]), display.config(text=values[int(v)])),
            bg=bg if bg else "white"
        )
        scale.pack()
        setattr(parent, flag, True)
        return mainframe, var
