from tkinter import colorchooser, filedialog, messagebox, font
import tkinter as tk
from os.path import exists, split
from win32print import GetDefaultPrinter
from win32api import ShellExecute
from pickle import dump, load
from time import sleep
import webbrowser
from threading import Thread

app_name = "TextEditor"
class TextEditor:
    def start(self):
        window = tk.Tk()
        base = TextEditorBase(window)
        base.texteditorbase(True)
        window.mainloop()

    # def _nw(self):
    #     win = Tk()
    #     base = TextEditorBase(win)
    #     base.texteditorbase(False)
    #     win.mainloop()

# Base Class
class TextEditorBase(TextEditor):
    def __init__(self,window):
        self.window = window

    def texteditorbase(self,fst):
        self.__startup_loader()
        if fst: self.window.iconphoto(True, tk.PhotoImage(file="media_file/iconphoto.png"))
        else: pass
        self.__window_geometry()
        # string vars
        self.font_style = tk.StringVar()
        self.font_style.set(self.style)
        self.font_size = tk.StringVar()
        self.font_size.set(self.size)
        self.tripemp = tk.StringVar()  # triple emphasis
        self.tripemp.set("None")
        self.statusL_text = tk.StringVar()
        self.statusL_text.set(f"{self.path}")

        # Text Frame
        self.bodyframe = tk.Frame(self.window)
        self.text = tk.Text(self.bodyframe, font=(self.style, self.size))
        self.__startupopen()
        self.scrollbary = tk.Scrollbar(self.bodyframe, command=self.text.yview)
        self.scrollbarx = tk.Scrollbar(self.bodyframe, command=self.text.xview, orient="horizontal")
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.scrollbarx.pack(side="bottom", fill="x")
        self.scrollbary.pack(side="right", fill="y")
        self.text.pack(expand=True, fill="both")
        self.text.config(yscrollcommand=self.scrollbary.set, undo=True, xscrollcommand=self.scrollbarx.set,
                    wrap="none")
        self.bodyframe.grid(row=0,column=0,sticky="n"+"w"+"e"+"s")
        # bottom frame
        self.bottomframe = tk.Frame(self.window)
        self.status_label = tk.Label(self.bottomframe, textvariable=self.statusL_text)

        # creating main menu bar and menus
        self.menubar = tk.Menu(self.window)
        self.window.config(menu=self.menubar)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.editmenu = tk.Menu(self.menubar, tearoff=0)
        self.thememenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)

        # configs
        self.bottomframe.grid(row=1,column=0,sticky="n"+"w"+"e"+"s")
        self.status_label.pack(anchor="w")

        # File Menu
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        self.filemenu.add_command(label="New", command=self.__new, accelerator="Ctrl+N")
        # self.filemenu.add_command(label="New Window", command=self._nw)
        self.filemenu.add_command(label='Open...', command=self.__fopen, accelerator="Ctrl+O")
        self.filemenu.add_command(label='Save', command=self.__fsave, accelerator="Ctrl+S")
        self.filemenu.add_command(label='Save As...', command=self.__fsave_as, accelerator="Ctrl+Shift+S")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Editor Settings", command=self.__es_window)
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Print 🖶', command=self.__print_file, accelerator="Ctrl+P")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.__on_closing)

        # Edit Menu
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)
        self.editmenu.add_command(label="↶ Undo", command=self.__undo, accelerator="Ctrl+Z")
        self.editmenu.add_command(label="↷ Redo", command=self.__redo, accelerator="Ctrl+Y")
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Cut", command=self.__cut, accelerator="Ctrl+X")
        self.editmenu.add_command(label="Copy", command=self.__copy, accelerator="Ctrl+C")
        self.editmenu.add_command(label="Paste", command=self.__paste, accelerator="Ctrl+V")
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Select All", command=self.__selectall, accelerator="Ctrl+A")
        self.editmenu.add_command(label="Delete All", command=self.__delete_all, accelerator="Shift+Del")

        # Theme Menu
        self.menubar.add_cascade(label="Themes", menu=self.thememenu)
        self.thememenu.add_command(label="Dark", command=lambda: self.__set_state(1), activebackground="#242424",
                                   activeforeground="white")
        self.thememenu.add_command(label="Light", command=lambda: self.__set_state(0), activebackground="white",
                                   activeforeground="black")

        # Help Menu
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.helpmenu.add_command(label="About", command=lambda: self.__about())
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Version",
                                  command=lambda: messagebox.showinfo(title="Version", message=f"App Version: 2.0.1"
                                                                                               f"\nTk Version: {tk.TkVersion}"
                                                                                               f"\nTcl Version: {tk.TclVersion}"
                                                                      ))
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Repository",
                                  command=lambda: webbrowser.open("https://github.com/SatzGOD/texteditor"))
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Report a problem ⚠",
                                  command=lambda: webbrowser.open("https://www.youtube.com/watch?v=xvFZjo5PgG0"))

        self.__window_keybinds()

        # To update the state of text in text box(if it saved or not)
        Thread(target=self.__textfileactivity, daemon=True).start()

        # to set theme on startup
        if self.state != None:
            self.__themeSwitcher()
        else:
            self.__set_state(0)
        self.window.update()  # to update idle tasks if any...

        # custom quit protocol
        self.window.protocol("WM_DELETE_WINDOW", self.__on_closing)

    # Helper Functions ................................................................................................
    def __startup_loader(self):
        self.window_cords = {'w': None, 'h': None, 'x': None, 'y': None}
        try:
            with open('data', 'rb') as f:
                loadeddata = load(f)
                self.path = loadeddata['path']
                self.state = loadeddata['state']
                self.style = loadeddata['fontstyle']
                self.size = loadeddata['fontsize']
                self.window_cords['w'] = loadeddata['w']
                self.window_cords['h'] = loadeddata['h']
                self.window_cords['x'] = loadeddata['x']
                self.window_cords['y'] = loadeddata['y']
        except:
            # File Path
            self.path = ""
            # for themes
            self.state = None
            self.size = "15"
            self.style = "Consolas"

    def __dumpjson_and_destroy(self):
        data = {'x': self.window.winfo_x(), 'y': self.window.winfo_y(), 'w': self.window.winfo_width(),
                'h': self.window.winfo_height(),
                'path': self.path, 'state': self.state, 'fontstyle': self.font_style.get(),
                'fontsize': self.font_size.get()}
        with open('data', 'wb') as f:
            dump(data, f)

        self.window.destroy()

    def __on_closing(self):
        if exists(self.path):
            with open(self.path, 'r') as f:
                if f.read() != self.text.get(1.0, "end"):
                    ask = messagebox.askyesnocancel(title="Quit",
                                                    message=f"Do you want to save changes to this \n{self.path} File?")
                    if ask == True:
                        self.__fsave()
                        self.__dumpjson_and_destroy()
                    elif ask == False:
                        self.__dumpjson_and_destroy()
                    else:
                        pass
                else:
                    self.__dumpjson_and_destroy()
        elif self.text.get(1.0, "end") > " ":
            ask = messagebox.askyesnocancel(title="Quit",
                                            message=f"Do you want to save changes to this Untitled File?")
            if ask == True:
                self.__fsave()
                try:
                    with open(self.path, 'r') as f:
                        if f.read() == self.text.get(1.0, "end")[:-1]:
                            self.__dumpjson_and_destroy()
                except:
                    pass
            elif ask == False:
                self.__dumpjson_and_destroy()
            else:
                pass
        else:
            self.__dumpjson_and_destroy()

    # text file activity detector
    def __textfileactivity(self):
        while True:
            if exists(self.path):
                with open(self.path, 'rt') as f:
                    if f.read() == self.text.get(1.0, "end"):
                        self.window.title(f"{(split(self.path)[1])} - {app_name}")
                    else:
                        self.window.title(f"{(split(self.path)[1])}* - {app_name}")
                        self.statusL_text.set(f"{self.path}")
            else:
                if self.text.get(1.0, "end") > "   ":
                    self.window.title(f"Untitled* - {app_name}")
                else:
                    self.window.title(f"Untitled - {app_name}")
            sleep(0.1)  # for smooth experience


    # window geometry setter
    def __window_geometry(self):
        window_width = self.window_cords['w'] if self.window_cords['w'] != None else 720
        window_height = self.window_cords['h'] if self.window_cords['h'] != None else 480
        x = self.window_cords['x'] if self.window_cords['w'] != None else int(
            (self.window.winfo_screenwidth() / 2) - (window_width / 2))
        y = self.window_cords['y'] if self.window_cords['w'] != None else int(
            (self.window.winfo_screenheight() / 2) - (window_height / 2))
        self.window.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))

    def __window_keybinds(self):
        # key binds
        # To Zoom in and Zoom out the text
        self.window.bind("<Control-plus>",
                         lambda _: self.__font_changer(self.font_size.set(str(int(self.font_size.get()) + 5))) if (
                                 int(self.font_size.get()) < 120) else self.font_size.set(120))  # ctr + plus
        self.window.bind("<Control-minus>",
                         lambda _: self.__font_changer(self.font_size.set(str(int(self.font_size.get()) - 5))) if (
                                 int(self.font_size.get()) > 5) else self.font_size.set(5))  # ctr + minus
        # To Save
        self.window.bind("<Control-S>", lambda _: self.__fsave())  # ctr + S
        self.window.bind("<Control-s>", lambda _: self.__fsave())  # ctr + s
        # To Save as
        self.window.bind("<Control-Shift-S>", lambda _: self.__fsave_as())  # ctr + shift + S
        self.window.bind("<Control-Shift-s>", lambda _: self.__fsave_as())  # ctr + shift + s
        # To Open
        self.window.bind("<Control-O>", lambda _: self.__fopen())  # ctr + O
        self.window.bind("<Control-o>", lambda _: self.__fopen())  # ctr + o
        # To New
        self.window.bind("<Control-N>", lambda _: self.__new())  # ctr + N
        self.window.bind("<Control-n>", lambda _: self.__new())  # ctr + n
        # To Delete All
        self.window.bind("<Shift-Delete>", lambda _: self.__delete_all())  # shift + del
        # To Print
        self.window.bind("<Control-P>", lambda _: self.__print_file())  # ctr + P
        self.window.bind("<Control-p>", lambda _: self.__print_file())  # ctr + p

    def __new(self):
        self.text.config(undo=False)
        self.window.title(f"Untitled - {app_name}")
        self.__delete_all()
        self.path = ""
        self.text.config(undo=True)
        self.statusL_text.set("")

    def __fopen(self):
        self.text.config(undo=False)
        opath = filedialog.askopenfilename(title='Open File', filetypes=(
            ("text file", "*.txt"), ("all files", "*.*"), ("Python File", "*.py"), ("HTML File", "*.html")))

        if exists(opath):
            with open(opath, 'r') as f:
                self.__delete_all()
                self.text.insert(1.0, f.read()[:-1])
            self.window.title(f"{(split(opath)[1])} - {app_name}")
            self.path = opath
            self.text.config(undo=False)
        else:
            pass

    def __startupopen(self):
        if exists(self.path):
            with open(self.path, 'rt') as f:
                self.window.title(f"{(split(self.path)[1])} - {app_name}")
                self.text.insert(1.0, f.read()[:-1])
        else:
            self.window.title("Untitled - TextEditor")

        # to save as a new file or save within an existing file

    def __fsave_as(self):
        spath = filedialog.asksaveasfile(title="Where you want you to save your file?", defaultextension=".txt",
                                         filetypes=(
                                             ("text File", "*.txt"), ("HTML File", "*.html"),
                                             ("Python File", "*.py"),
                                             ("all File", "*.*")))

        if spath != None and exists(spath.name):
            filetext = self.text.get(1.0, "end")
            spath.write(filetext)
            spath.close()
            self.window.title(f"{(split(spath.name)[1])} - {app_name}")
            self.path = spath.name
            self.statusL_text.set(f"{self.path} (Saved)")
        else:
            pass

    def __fsave(self):
        if exists(self.path):
            with open(self.path, 'w') as f:
                filetext = self.text.get(1.0, "end")
                f.write(filetext)
                self.window.title(f"{(split(self.path)[1])} - {app_name}")
                self.statusL_text.set(f"{self.path} (Saved)")
        else:
            self.__fsave_as()

    def __print_file(self):
        printer = GetDefaultPrinter()
        if printer:
            self.statusL_text.set(printer)
            ask = messagebox.askokcancel(title="Print", message=f"Click ok to print this file \n{self.path} ")
            if ask and exists(self.path):
                ShellExecute(0, "print", self.path, None, ".", 0)
            else:
                pass
        else:
            self.statusL_text.set("No Printer Available")
            messagebox.showwarning(title=f"{app_name}", message="Cannot Detect a printer:"
                                                                "\nBe sure that your printer is connected properly and use "
                                                                "Control Panel to verify that the printer is configured properly.")
        self.statusL_text.set(f"{self.path}")

    def __cut(self):
        self.text.event_generate("<<Cut>>")

        # copy the selected text

    def __copy(self):
        self.text.event_generate("<<Copy>>")

        # paste the text from the clipboard

    def __paste(self):
        self.text.event_generate("<<Paste>>")

        # select all the text from the text box

    def __selectall(self):
        self.text.tag_add('sel', 1.0, "end")

        # delete all text from the text box

    def __delete_all(self):
        self.text.delete(1.0, "end")

    def __undo(self):
        try:
            self.text.edit_undo()
        except:
            pass

    def __redo(self):
        try:
            self.text.edit_redo()
        except:
            pass

    def __color_fchanger(self):
        fcolor = colorchooser.askcolor(title="Choose a color for font")[1]
        self.fcolorbutton.config(bg=fcolor)
        self.text.config(fg=fcolor)

    def __color_bchanger(self):
        bcolor = colorchooser.askcolor(title="Choose a color for paper")[1]
        self.bcolorbutton.config(bg=bcolor)
        self.text.config(bg=bcolor)

    def __font_changer(self, *args):
        self.text.config(font=(self.font_style.get(), self.font_size.get()))

    def __tripemp_func(self, *args):

        def __helper(style):
            if style in current_tag:
                self.text.tag_remove(style, "sel.first", "sel.last")
                self.tripemp.set("None")
            else:
                self.text.tag_add(style, "sel.first", "sel.last")

        try:
            if self.tripemp.get() == self.tripemp_list[0]:
                self.__selectall()
                bold_font = font.Font(self.text, self.text.cget("font"))
                bold_font.configure(weight="bold")
                self.text.tag_configure("bold", font=bold_font)
                current_tag = self.text.tag_names("sel.first")
                __helper("bold")
            elif self.tripemp.get() == self.tripemp_list[1]:
                self.__selectall()
                italic_font = font.Font(self.text, self.text.cget("font"))
                italic_font.configure(slant="italic")
                self.text.tag_configure("italic", font=italic_font)
                current_tag = self.text.tag_names("sel.first")
                __helper("italic")
            elif self.tripemp.get() == self.tripemp_list[2]:
                self.__selectall()
                underline_font = font.Font(self.text, self.text.cget("font"))
                underline_font.configure(underline=True)
                self.text.tag_configure("underline", font=underline_font)
                current_tag = self.text.tag_names("sel.first")
                __helper("underline")

            else:
                self.tripemp.set("None")
        except:
            self.tripemp.set("None")

    def __about(self):
        messagebox.showinfo("About TextEditor",
                            "A Simple Text editor python application by Satz!\nSource Code at SatzGOD github or Click `Repository` in the Help Menu."
                            "\ninstagram: @satz_._")

    def __es_window(self):
        self.tripemp_list = ["Bold", "Italics", "Underline"]
        self.filemenu.entryconfig(5, state="disabled")
        self.fw = tk.Toplevel()
        self.fw.attributes('-topmost', True)
        self.fw.resizable(False, False)
        self.fw.title("Editor Settings")
        width, height = 300, 130
        x = int((self.window.winfo_screenwidth() / 2) - (width / 2))
        y = int((self.window.winfo_screenheight() / 2) - (height / 2))
        self.fw.geometry(f"{width}x{height}-{x}+{y}")
        self.frame = tk.Frame(self.fw)
        self.l1 = tk.Label(self.frame, text="Font Family:")
        self.l1.grid(row=0, column=0, sticky="w", pady=3)
        self.stylebox = tk.OptionMenu(self.frame, self.font_style, *font.families(), command=self.__font_changer)
        self.stylebox.grid(row=0, column=1, sticky="e", pady=3)
        self.l2 = tk.Label(self.frame, text="Font Style:")
        self.l2.grid(row=1, column=0, sticky="w", pady=3)
        self.tripempbox = tk.OptionMenu(self.frame, self.tripemp, *self.tripemp_list, command=self.__tripemp_func)
        self.tripempbox.grid(row=1, column=1, sticky="w", pady=3)
        self.l3 = tk.Label(self.frame, text="Font Size:")
        self.l3.grid(row=2, column=0, sticky="w", pady=3)
        self.sizebox = tk.Spinbox(self.frame, from_=1, to_=120, textvariable=self.font_size, width=4,
                               command=self.__font_changer)
        self.sizebox.grid(row=2, column=1, sticky="w", pady=3)
        self.fcolorbutton = tk.Button(self.frame, text="Font color", command=self.__color_fchanger)
        self.fcolorbutton.grid(row=3, column=0, sticky="w", pady=3, padx=2)
        self.bcolorbutton = tk.Button(self.frame, text="Paper color", command=self.__color_bchanger)
        self.bcolorbutton.grid(row=3, column=1, sticky="w", pady=3)
        self.frame.grid(row=0, column=0, sticky="w")

        self.__ts_esw()
        self.fw.protocol("WM_DELETE_WINDOW", self.__fwonclosing)
        self.fw.mainloop()

    def __fwonclosing(self):
        self.filemenu.entryconfig(5, state="normal")
        self.fw.destroy()

    def __set_state(self, newstate):
        self.state = newstate
        self.__themeSwitcher()
        try:
            self.__ts_esw()
        except:
            pass

    def __themeSwitcher(self):
        if self.state == 0:
            white = "#FFFFFF"
            defsyswhite = "#F0F0F0"
            black = "#000001"
            relief = "flat"
            highlightgrey = "#b0b0b0"
            font, size = "Consolas", "10"
            self.window.config(bg=defsyswhite)
            self.bottomframe.config(bg=defsyswhite)
            self.text.config(fg=black, bg=white)

            self.status_label.config(fg=black, bg=defsyswhite)
            self.menubar.config(bg=white, fg=black, relief=relief, activebackground=highlightgrey,
                                selectcolor=highlightgrey, font=(font, size))
            self.filemenu.config(bg=white, fg=black, relief=relief, activebackground=highlightgrey,
                                 selectcolor=highlightgrey, font=(font, size))
            self.editmenu.config(bg=white, fg=black, relief=relief, activebackground=highlightgrey,
                                 selectcolor=highlightgrey, font=(font, size))
            self.thememenu.config(bg=white, fg=black, relief=relief, activebackground=highlightgrey,
                                  selectcolor=highlightgrey, font=(font, size))
            self.helpmenu.config(bg=white, fg=black, relief=relief, activebackground=highlightgrey,
                                 selectcolor=highlightgrey, font=(font, size))

        elif self.state == 1:
            white = "white"
            textwhite = '#ebebeb'
            darkgrey = "#242424"
            lightgrey = "#414245"
            relief = "flat"
            font, size = "Consolas", "10"
            self.window.config(bg=darkgrey)
            self.bottomframe.config(bg=darkgrey)
            self.text.config(fg=textwhite, bg=lightgrey)
            self.status_label.config(bg=darkgrey, fg=white)
            self.menubar.config(bg=darkgrey, fg=white, relief=relief, activebackground=lightgrey,
                                selectcolor=lightgrey, font=(font, size))
            self.filemenu.config(bg=darkgrey, fg=white, relief=relief, activebackground=lightgrey,
                                 selectcolor=lightgrey, font=(font, size))
            self.editmenu.config(bg=darkgrey, fg=white, relief=relief, activebackground=lightgrey,
                                 selectcolor=lightgrey, font=(font, size))
            self.thememenu.config(bg=darkgrey, fg=white, relief=relief, activebackground=lightgrey,
                                  selectcolor=lightgrey, font=(font, size))
            self.helpmenu.config(bg=darkgrey, fg=white, relief=relief, activebackground=lightgrey,
                                 selectcolor=lightgrey, font=(font, size))
    def __ts_esw(self):
        if self.state == 0:
            defsyswhite = "#F0F0F0"
            black = "#000001"
            relief = "groove"
            highlightgrey = "#b0b0b0"
            self.stylebox.config(fg=black, bg=defsyswhite, activebackground=highlightgrey, activeforeground=black,
                                 relief=relief, highlightthickness=False)
            self.sizebox.config(fg=black, bg=defsyswhite, relief=relief, highlightthickness=3,
                                highlightbackground=defsyswhite)
            self.fcolorbutton.config(fg=black, bg=defsyswhite, activebackground=highlightgrey, activeforeground=black,
                                     relief=relief)
            self.bcolorbutton.config(fg=black, bg=defsyswhite, activebackground=highlightgrey, activeforeground=black,
                                     relief=relief)
            self.tripempbox.config(fg=black, bg=defsyswhite, activebackground=highlightgrey, activeforeground=black,
                                   relief=relief)
            self.fw.config(bg=defsyswhite)
            self.frame.config(bg=defsyswhite)
            self.l1.config(bg=defsyswhite, fg=black)
            self.l2.config(bg=defsyswhite, fg=black)
            self.l3.config(bg=defsyswhite, fg=black)
        elif self.state == 1:
            white = "white"
            darkgrey = "#242424"
            lightdarkgrey = "#353535"
            lightgrey = "#414245"
            relief = "groove"
            self.stylebox.config(bg=lightdarkgrey, fg=white, activebackground=lightgrey, activeforeground=white,
                                 relief=relief, highlightthickness=False)
            self.sizebox.config(bg=lightdarkgrey, fg=white, relief=relief, highlightthickness=3,
                                highlightbackground=lightdarkgrey)
            self.fcolorbutton.config(bg=lightdarkgrey, fg=white, activebackground=lightgrey, activeforeground=white,
                                     relief=relief)
            self.bcolorbutton.config(bg=lightdarkgrey, fg=white, activebackground=lightgrey, activeforeground=white,
                                     relief=relief)
            self.tripempbox.config(bg=lightdarkgrey, fg=white, activebackground=lightgrey, activeforeground=white,
                                   relief=relief, highlightthickness=False)
            self.fw.config(bg=darkgrey)
            self.frame.config(bg=darkgrey)
            self.l1.config(bg=darkgrey, fg=white)
            self.l2.config(bg=darkgrey, fg=white)
            self.l3.config(bg=darkgrey, fg=white)


