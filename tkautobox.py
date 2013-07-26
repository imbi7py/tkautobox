#!/usr/bin/env python3
"""
TkAutoBox
by Alan D Moore, copyright 2013

Released under the Simplified BSD license.

This file implements a simple, generic data-entry dialog box convience wrapper in Tkinter.
It's useful for things like login boxes or small configuration dialogs.
It requires at least python 3.
The box is extensible with any number of custom fields simply by passing in a list of dicts.
"""
from tkinter import *
from tkinter.ttk import *
from tkinter import font


class Autobox(Tk):
    """
    This class should probably not be instanciated directly, but rather the various wrapper functions should be used.
    """
    variable_types = {"text": StringVar, "hidden_text": StringVar, "checkbox":BooleanVar, "select": StringVar}

    def __init__(self, **kwargs):
        """
        Valid keyword arguments:

        - title_string: String; will be the window title.
        - header_string: String; will display  in the top of the box.
        - fields: List;  These are the form fields to add.
          It should be a list of dictionaries, each with the format:
           {
            "name" : <name of field>, string (required),
            "label" : <label to display for field>, string, if not specified "name" will be used
            "type"  : <one of text, hidden_text, checkbox, or select>, string,
            "default" : <default value of widget>(depends on widget type),
            "options": <options for select; does nothing for others>list or tuple
           }
        - error_message: String; an error message to display
        - theme: String; The TK theme to use. invalid themes will be ignored.
        - padding: Integer; The number of pixels to put around elements.
        - ok_label: String; Text for the OK button, defaults to "OK"
        """
        Tk.__init__(self)
        #Pull in the keyword arguments
        self.title_string = kwargs.get("title_string", "")
        self.header_string = kwargs.get("header_string", "")
        self.fields = kwargs.get("fields", [])
        self.padding = kwargs.get("padding",  5)
        self.error_message = kwargs.get("error_message", None)
        self.theme = kwargs.get("theme")
        self.ok_label = kwargs.get("ok_label", "OK")
        #set theme, if it's valid
        s = Style()
        if self.theme in s.theme_names():
            s.theme_use(self.theme)

        # create fonts and styles
        headerfont = font.Font(size=14)
        errorfont = font.Font(size=12, weight='bold')
        s.configure('Error.TLabel', foreground='#880000', font=errorfont)

        #Create variables
        self.data = {}


        # Fields need, at minimum, a name
        self.fields = [x for x in self.fields if x.get("name")]

        # Create the dictionary of variables for the form
        for field in self.fields:
            fn = field.get("name")
            self.data[fn] = self.variable_types[field.get("type", "text")]()
            self.data[fn].set(field.get("default", ""))

        #Build the UI
        self.title(self.title_string)
        self.widgets = {}
        Label(text=self.header_string, font=headerfont).grid(row=0,column=0, columnspan= 2)

        if self.error_message:
            Label(text=self.error_message, style='Error.TLabel').grid(row=1, column=0, columnspan=2, padx=self.padding, pady=self.padding)
        for n, field in enumerate(self.fields):
            fn = field.get("name")
            ft = field.get("type", "text")
            label = field.get("label", fn)
            rownum = n + 2

            if ft == "select":
                self.widgets[fn] = Combobox(textvariable = self.data[fn], values = field.get("options"), state="readonly")
            elif ft == "checkbox":
                self.widgets[fn] = Checkbutton(variable=self.data[fn])
            elif ft == "hidden_text":
                self.widgets[fn] = Entry(textvariable = self.data[fn], show="*")
            else:
                self.widgets[fn] = Entry(textvariable = self.data[fn])
            Label(text=label).grid(row=rownum, column=0, padx=self.padding, pady=self.padding, sticky=W)
            self.widgets[fn].grid(row=rownum, column=1, padx=self.padding, pady=self.padding, sticky=W)

        #Add a spacer
        Label().grid(row=998, column=0, columnspan=2, pady=20)
        #Login/cancel buttons
        self.ok_button = Button(self, text=self.ok_label, command=self.ok_clicked)
        self.ok_button.grid(row=999, column=0)
        self.cancel_button = Button(self, text="Cancel", command=self.cancel_clicked)
        self.cancel_button.grid(row=999, column=1)

        #Bind keystrokes
        self.bind("<Return>", self.ok_clicked)
        self.bind("<Escape>", self.cancel_clicked)

    def ok_clicked(self, *args):
        self.data = { key : var.get() for key, var in self.data.items() }
        self.quit()

    def cancel_clicked(self, *args):
        self.data = {}
        self.quit()

def autobox(**kwargs):
    ab = Autobox(**kwargs)
    ab.mainloop()
    data = ab.data
    ab.destroy()
    return data

def loginbox(**kwargs):
    """
    This wrapper creates a simple login box with username and password.
    Additional field specifications can be added with the additional_fields keyword.
    The remaining keywords are passed on to the class.
    """
    additional_fields = kwargs.get("additional_fields") and kwargs.pop("additional_fields") or []
    ok_label = kwargs.get("ok_label", "Log In")
    default_username = kwargs.get("default_username") and kwargs.pop("default_username") or ""
    title = kwargs.get("title", "Log In")

    default_fields = [
        {"name":"username", "type": "text", "default": default_username, "label": "Username: " },
        {"name":"password", "type": "hidden_text", "label":"Password: "}
        ]
    fields = default_fields + additional_fields

    return  autobox(fields=fields, ok_label=ok_label, title_string=title, **kwargs)

if __name__ == '__main__':
    """
    This is a test example of how to use this code.
    """
    test_user = "SomeUser"
    test_password = "Password"
    error_message = None
    while True:
        res = loginbox(
            header_string="Log in to secure server", title_string="Login",
            default_username=test_user, error_message=error_message, theme='alt',
            additional_fields = [
                {"name":"domain", "type":"select", "options":["Local", "US.gov", "RU.gov"], "default": "Local", "label" : "Login Domain: "},
                {"name" : "readonly", "type":"checkbox", "default": False, "label" : "Readonly access?"}
                ]
                )
        if res == {}:
            print("Authentication cancelled.")
            exit()
        elif res.get("username") == test_user and res.get("password") == test_password:
            break
        else:
            error_message = "Authentication failed"
    print("Authentication success!")