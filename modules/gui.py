####################################################################################################
# The MIT License (MIT)
#
# Copyright (c) 2015, Alexander I. Mykyta
# All rights reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
####################################################################################################

import copy
import re
import glob
import os
import fnmatch
import logging

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from .python_modules import tk_extensions as tkext
from . import form_data
from . import report_template
from . import report_entries

def trim_path(path, maxlen):
    if(len(path) <= maxlen):
        return(path)
    else:
        path = "..." + path[-maxlen+3:]
        return(path)

####################################################################################################
# GUI Windows
####################################################################################################

class TemplateBrowser(tkext.Dialog):
    
    #---------------------------------------------------------------
    # Widgets
    #---------------------------------------------------------------
    def create_body(self, master_fr):
        
        #--------------------------------------------------------
        # Template list and Description container frame
        template_area_fr = ttk.Frame(
            master_fr,
            padding=3
        )
        template_area_fr.pack(
            side = tk.LEFT,
            fill=tk.BOTH,
            expand = True
        )
        
        # Description box
        desc_fr = ttk.Labelframe(
            template_area_fr,
            text="Description",
            padding=3
        )
        desc_fr.pack(side = tk.BOTTOM, fill = tk.X)
        self.txt_desc = tk.Text(
            desc_fr,
            wrap = tk.WORD,
            width = 50,
            height = 5
        )
        self.txt_desc.pack(
            fill = tk.X,
            expand = True
        )
        self.txt_desc.configure(state=tk.DISABLED)
        
        # Template List
        self.rt_list = tk.Listbox(
            template_area_fr,
            highlightthickness = 0,
            selectmode = "single",
            exportselection = False,
            activestyle = "none"
        )
        self.rt_list.bind('<<ListboxSelect>>', self.ev_rt_list_Select)
        self.rt_list.bind("<Double-Button-1>", self.ev_rt_list_DoubleClick)
        self.rt_list.pack(
            side = tk.LEFT,
            fill = tk.BOTH,
            expand = True
        )
        
        # Template list scrollbar
        rt_list_scroll = ttk.Scrollbar(template_area_fr)
        rt_list_scroll.pack(
            side = tk.RIGHT,
            fill = tk.Y
        )
                                
        # Link scrollbar <--> list
        self.rt_list.configure(yscrollcommand=rt_list_scroll.set)
        rt_list_scroll.configure(command=self.rt_list.yview)
        
        #--------------------------------------------------------
        # Button group container frame
        buttons_fr = ttk.Frame(master_fr,
                               padding=3)
        buttons_fr.pack(side = tk.RIGHT, fill=tk.Y)
        
        # Top button group container frame
        top_buttons_fr = ttk.Frame(buttons_fr)
        top_buttons_fr.pack(side = tk.TOP)
        x = ttk.Button(
            top_buttons_fr,
            text="Create New",
            command = self.ev_but_New
        )
        x.pack(fill=tk.X)
        x = ttk.Button(
            top_buttons_fr,
            text="Edit",
            command = self.ev_but_Edit
        )
        x.pack(fill=tk.X)
        x = ttk.Button(
            top_buttons_fr,
            text="Copy",
            command = self.ev_but_Copy
        )
        x.pack(fill=tk.X)
        x = ttk.Button(
            top_buttons_fr,
            text="Delete",
            command = self.ev_but_Delete
        )
        x.pack(fill=tk.X)
        
        #--------------------------------------------------------
        # Global layout
        
        
        # window is not allowed to be any smaller than default
        self.tkWindow.update_idletasks() #Give Tk a chance to update widgets and figure out the window size
        self.tkWindow.minsize(self.tkWindow.winfo_width(), self.tkWindow.winfo_height())
    
    #---------------------------------------------------------------
    # Helpers
    #---------------------------------------------------------------
    def set_desc_text(self, str):
        self.txt_desc.configure(state=tk.NORMAL)
        self.txt_desc.delete(0.0, tk.END)
        self.txt_desc.insert(tk.END, str)
        self.txt_desc.configure(state=tk.DISABLED)
    
    def set_ev_selection(self, idx):
        if(len(self.S.Templates) == 0):
            # No templates left!
            self.set_desc_text("")
            return
        elif(idx >= len(self.S.Templates)):
            idx = len(self.S.Templates) - 1
        
        self.rt_list.selection_clear(0,tk.END)
        self.rt_list.selection_set(idx)
        self.rt_list.see(idx)
        self.set_desc_text(self.S.Templates[idx].description)
    
    #---------------------------------------------------------------
    # Events
    #---------------------------------------------------------------
    def __init__(self, parent, Settings):
        self.S = Settings
        self.selected_template = None # dialog result
        
        title = "Select Report Template"
        tkext.Dialog.__init__(self, parent, title)
        
    def dlg_initialize(self):
        for T in self.S.Templates:
            self.rt_list.insert(tk.END, T.name)
        
        # preselect something
        self.set_ev_selection(0)

    def ev_rt_list_Select(self, ev):
        idx = self.rt_list.curselection()
        if(len(idx)):
            idx = int(idx[0])
            self.set_desc_text(self.S.Templates[idx].description)
        
    def ev_rt_list_DoubleClick(self, ev):
        self.dlg_pbOK()
        
    def ev_but_New(self):
        options = {}
        options['defaultextension'] = '.pdf'
        options['filetypes'] = [('PDF file', '.pdf')]
        options['title'] = 'Select a Template PDF'
        
        filename = filedialog.askopenfilename(**options)
        if(not filename):
            return
        
        
        try:
            T = report_template.ReportTemplate(filename = filename)
        except ValueError as exc:
            messagebox.showerror(
                title = "New Report Template",
                message = "Selected file is not a valid PDF."
            )
            return
        
        # Initialized. Jump into the editor
        TE = TemplateEditor(self.tkWindow, T, "New Report Template")
        if(TE.result):
            # Template created. Insert edited template into the list & the GUI
            self.S.Templates.append(TE.T)
            self.rt_list.insert(tk.END, TE.T.name)
            self.set_ev_selection(len(self.S.Templates)-1)
    
    def ev_but_Edit(self):
        idx = self.rt_list.curselection()
        if(len(idx)):
            idx = int(idx[0])
            
            TE = TemplateEditor(self.tkWindow, self.S.Templates[idx], "Edit Report Template")
            if(TE.result):
                # edited. replace with edited instance
                self.S.Templates[idx] = TE.T
                self.rt_list.delete(idx)
                self.rt_list.insert(idx, self.S.Templates[idx].name)
                self.set_ev_selection(idx)
                
    
    def ev_but_Copy(self):
        idx = self.rt_list.curselection()
        if(len(idx)):
            idx = int(idx[0])
            
            C = copy.deepcopy(self.S.Templates[idx])
            
            # remove any trailing " (copy ##)"
            C.name = re.sub("\s\(copy(?: \d+)?\)$", "", C.name)
            
            # Augment the copy's name so that it is unique
            newname = C.name + " (copy)"
            n = 0
            while(True):
                for t in self.S.Templates:
                    if(t.name == newname):
                        n = n + 1
                        newname = C.name + " (copy %d)" % n
                        break
                else:
                    break
            C.name = newname
            
            self.S.Templates.insert(idx+1, C)
            self.rt_list.insert(idx+1, C.name)
            self.set_ev_selection(idx+1)
            
        
    def ev_but_Delete(self):
        idx = self.rt_list.curselection()
        if(len(idx)):
            idx = int(idx[0])
            
            res = messagebox.askyesno(
                title = "Delete Report Template",
                icon = messagebox.WARNING,
                message = "Are you sure you want to delete '%s'?" % self.S.Templates[idx].name
            )
            
            if(res):
                del self.S.Templates[idx]
                self.rt_list.delete(idx)
                self.set_ev_selection(idx)
            
    def dlg_validate(self):
        idx = self.rt_list.curselection()
        if(len(idx) == 0):
            messagebox.showerror(
                title = "Select Template",
                message = "You must select a template first."
            )
            return(False)
            
        return True
    
    def dlg_apply(self):
        idx = self.rt_list.curselection()
        idx = int(idx[0])
        
        self.selected_template = self.S.Templates[idx]
    
#===================================================================================================
class TemplateEditor(tkext.Dialog):
    
    #---------------------------------------------------------------
    # Widgets
    #---------------------------------------------------------------
    def create_body(self, master_fr):
        tabs = ttk.Notebook(master_fr)
        tabs.pack(fill=tk.BOTH, expand=True)
        
        # "General" Tab
        self.tab_General = TE_tab_General(self.T, tabs)
        
        # "Report Entries" Tab
        self.tab_ReportEntries = TE_tab_ReportEntries(self.T, tabs)
        
    #---------------------------------------------------------------
    # Dialog Events
    #---------------------------------------------------------------
    def __init__(self, parent, Template, title = None):
        
        # Make copy of the template for local editing.
        self.T = copy.deepcopy(Template)
        
        tkext.Dialog.__init__(self, parent, title)
    
    def dlg_initialize(self):
        pass
        
    def dlg_validate(self):
        
        if(not self.tab_General.tab_validate()):
            return(False)
        
        if(not self.tab_ReportEntries.tab_validate()):
            return(False)
            
        return(True)
    
    def dlg_apply(self):
        self.tab_General.tab_apply()
        self.tab_ReportEntries.tab_apply()

class TE_tab_General:
    def __init__(self, Template, tab_book):
        self.T = Template
        self.tab_book = tab_book
        self.tab_index = tab_book.index(tk.END)
        
        self.create_widgets(tab_book)
        self.init_widgets()
    
    def show(self):
        self.tab_book.select(self.tab_index)
        
    def create_widgets(self, tab_book):
        
        tab_fr = ttk.Frame(tab_book, padding=5)
        tab_book.add(tab_fr, text="General")
        
        # Row 0 - Name
        x = ttk.Label(tab_fr, text="Template Name")
        x.grid(row=0, column=0, sticky=(tk.N, tk.E))
        self.txt_name = ttk.Entry(tab_fr)
        self.txt_name.grid(row=0, column=1, sticky=(tk.E, tk.W))
        
        # Row 1 - Description
        x = ttk.Label(tab_fr, text="Description")
        x.grid(row=1, column=0, sticky=(tk.N, tk.E))
        self.txt_desc = tk.Text(
            tab_fr,
            wrap = tk.WORD,
            width = 50,
            height = 5
        )
        self.txt_desc.grid(row=1, column=1, sticky=(tk.E, tk.W))
        
        tab_fr.columnconfigure(1, weight=1)
        tab_fr.columnconfigure(tk.ALL, pad=5)
        tab_fr.rowconfigure(tk.ALL, pad=5)
        
        
    def init_widgets(self):
        self.txt_name.insert(tk.END, self.T.name)
        self.txt_desc.insert(tk.END, self.T.description)
        
    def tab_validate(self):
        if(len(self.txt_name.get()) == 0):
            messagebox.showerror(
                title = "Template Name",
                message = "Template name cannot be empty."
            )
            self.show()
            self.txt_name.focus_set()
            return(False)
        
        return(True)
        
    def tab_apply(self):
        self.T.name = self.txt_name.get()
        self.T.description = self.txt_desc.get("1.0",'end-1c')

class TE_tab_ReportEntries:
    def __init__(self, Template, tab_book):
        self.T = Template
        self.tab_book = tab_book
        self.tab_index = tab_book.index(tk.END)
        
        # Container for type-specific entry settings
        self.entry_type_settings_frame = None
        self.entry_type_settings_widgets = None
        self.current_idx = None
        
        self.create_widgets(tab_book)
        self.init_widgets()
    
    def show(self):
        self.tab_book.select(self.tab_index)
        
    def create_widgets(self, tab_book):
        
        tab_fr = ttk.Frame(tab_book, padding=5)
        tab_book.add(tab_fr, text="Report Entries")
        
        entries_fr = ttk.Labelframe(
            tab_fr,
            text="Entries",
            padding=5
        )
        entries_fr.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Entry list and scrollbar
        entry_list_scroll = ttk.Scrollbar(entries_fr)
        entry_list_scroll.pack(
            side = tk.RIGHT,
            fill = tk.Y
        )
        self.entry_list = tk.Listbox(
            entries_fr,
            highlightthickness = 0,
            activestyle = "none",
            exportselection = False,
            selectmode = "single"
        )
        self.entry_list.bind('<<ListboxSelect>>', self.ev_entry_list_select)
        self.entry_list.pack(
            side = tk.RIGHT,
            fill = tk.BOTH,
            expand = True
        )
        self.entry_list.configure(yscrollcommand=entry_list_scroll.set)
        entry_list_scroll.configure(command=self.entry_list.yview)
        
        # Entry List side buttons
        ent_but_fr = ttk.Frame(entries_fr, padding=5)
        ent_but_fr.pack(
            side = tk.LEFT,
            fill = tk.Y,
            expand = True
        )
        
        x = ttk.Button(ent_but_fr,
            text="Add",
            command=self.pb_new_entry
        )
        x.pack(side = tk.TOP)
        
        x = ttk.Button(ent_but_fr,
            text="Delete",
            command=self.pb_delete_entry
        )
        x.pack(side = tk.TOP)
        
        x = ttk.Button(ent_but_fr,
            text="Down",
            command=self.pb_move_entry_down
        )
        x.pack(side = tk.BOTTOM)
        
        x = ttk.Button(ent_but_fr,
            text="Up",
            command=self.pb_move_entry_up
        )
        x.pack(side = tk.BOTTOM)
        
        # ------------- Entry Settings Section -------------
        self.entry_settings_frame = ttk.Labelframe(tab_fr,
            text="Entry Settings",
            padding=5
        )
        self.entry_settings_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Common Settings
        ent_common_settings_fr = ttk.Frame(self.entry_settings_frame)
        ent_common_settings_fr.pack(side=tk.TOP, fill=tk.X)
        
        x = ttk.Label(ent_common_settings_fr, text="Entry Type")
        x.grid(row=0, column=0, sticky=(tk.N, tk.E))
        self.cmb_ent_type = ttk.Combobox(
            ent_common_settings_fr,
            state= 'readonly',
            values= report_entries.get_type_names()
        )
        self.cmb_ent_type.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E))
        self.cmb_ent_type.bind("<<ComboboxSelected>>", self.cmb_ent_type_Changed)
        
        x = ttk.Label(ent_common_settings_fr, text="Entry Name")
        x.grid(row=1, column=0, sticky=(tk.N, tk.E))
        self.txt_ent_name = ttk.Entry(
            ent_common_settings_fr,
            validatecommand=self.txt_ent_name_Changed,
            validate='focusout'
        )
        self.txt_ent_name.grid(row=1, column=1, sticky=(tk.N, tk.W, tk.E))
        
        ent_common_settings_fr.columnconfigure(1, weight=1)
        ent_common_settings_fr.columnconfigure(tk.ALL, pad=5)
        ent_common_settings_fr.rowconfigure(tk.ALL, pad=5)
        
        x = ttk.Separator(self.entry_settings_frame)
        x.pack(side=tk.TOP, fill=tk.X)
        
        # Type-Specific Settings
        self.entry_type_settings_frame = ttk.Frame(self.entry_settings_frame)
        self.entry_type_settings_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        tab_fr.columnconfigure(1, weight=1)
        tab_fr.rowconfigure(tk.ALL, weight=1)
        
        # Hide settings by default (until something is selected)
        self.entry_settings_frame.grid_remove()
        
    def init_widgets(self):
        # load entry list with names
        for e in self.T.entries:
            self.entry_list.insert(tk.END, e.name)
        
    def tab_validate(self):
        return(True)
        
    # FYI: NOT the apply button, but the apply event when OKing the dialog window
    def tab_apply(self):
        # nothing to do here. fields are applied to self.T automatically
        pass
    
    #---------------------------------------------------------------
    # Helpers
    #---------------------------------------------------------------
    
    def set_entry_selection(self, idx):
        if(len(self.T.entries) == 0):
            # List is empty
            self.entry_settings_frame.grid_remove()
            self.entry_type_settings_widgets = None
            self.current_idx = None
            return
        elif(idx >= len(self.T.entries)):
            idx = len(self.T.entries) - 1
        
        self.entry_list.selection_clear(0,tk.END)
        self.entry_list.selection_set(idx)
        self.entry_list.see(idx)
        
        # set up common entry settings widgets
        self.cmb_ent_type.current(report_entries.get_type_idx(type(self.T.entries[idx])))
        self.txt_ent_name.delete(0, tk.END)
        self.txt_ent_name.insert(tk.END, self.T.entries[idx].name)
        
        # if previous type-specific entry settings are showing, remove them.
        if(self.entry_type_settings_widgets):
            self.entry_type_settings_widgets.destroy()
        
        # show new type-specific entry settings
        self.entry_type_settings_widgets = report_entries.CreateSettings(self.T.entries[idx], self.entry_type_settings_frame)
        self.current_idx = idx;
        
        # unhide settings region
        self.entry_settings_frame.grid()
    
    #---------------------------------------------------------------
    # Widget Events
    #---------------------------------------------------------------
    def ev_entry_list_select(self, ev):
        idx = self.entry_list.curselection()
        if(len(idx)):
            idx = int(idx[0])
            
            # If a previous entry is showing, force the txt_ent_name changed event
            # since the event doesn't fire normally when this is clicked
            if(self.current_idx != None):
                # switch selection back to the previous idx
                self.entry_list.selection_clear(0,tk.END)
                self.entry_list.selection_set(self.current_idx)
                
                # force the "changed" dialog
                res = self.txt_ent_name_Changed()
                if(res == False):
                    return
            self.set_entry_selection(idx)
    
    def pb_move_entry_up(self):
        idx = self.entry_list.curselection()
        if(len(idx) == 0):
            return
        idx = int(idx[0])
        
        if(idx <= 0):
            return
        
        E = self.T.entries.pop(idx)
        self.entry_list.delete(idx)
        
        self.T.entries.insert(idx-1, E)
        self.entry_list.insert(idx-1, E.name)
        self.entry_list.selection_set(idx-1)
        self.current_idx = (idx-1)
        
    def pb_move_entry_down(self):
        idx = self.entry_list.curselection()
        if(len(idx) == 0):
            return
        idx = int(idx[0])
        
        if(idx >= len(self.T.entries)-1):
            return
        
        E = self.T.entries.pop(idx)
        self.entry_list.delete(idx)
        
        self.T.entries.insert(idx+1, E)
        self.entry_list.insert(idx+1, E.name)
        self.entry_list.selection_set(idx+1)
        self.current_idx = (idx+1)
    
    def pb_new_entry(self):
        # determine a unique name
        name = "New Entry"
        
        n = 0
        while(True):
            for e in self.T.entries:
                if(e.name == name):
                    n = n + 1
                    name = "New Entry %d" % n
                    break
            else:
                break
            
        # create new entry data object
        entry_t = report_entries.get_default_type()
        E = entry_t(self.T, name)
        
        # Add it to the template
        self.T.entries.append(E)
        
        # Add it to the GUI
        self.entry_list.insert(tk.END, E.name)
        
        # select it
        self.set_entry_selection(len(self.T.entries)-1)
        
    def pb_delete_entry(self):
        idx = self.entry_list.curselection()
        if(len(idx)):
            idx = int(idx[0])
            del self.T.entries[idx]
            self.entry_list.delete(idx)
            self.set_entry_selection(idx)
    
    def txt_ent_name_Changed(self):
        idx = self.entry_list.curselection()[0]
        new_name = self.txt_ent_name.get()
        # check if name is non-empty
        if(len(new_name) == 0):
            messagebox.showerror(
                title = "Entry Name",
                message = "Entry name cannot be empty."
            )
            self.txt_ent_name.focus_set()
            return(False)
        
        # check if name is unique
        for i,e in enumerate(self.T.entries):
            if(i != idx):
                if(e.name == new_name):
                    messagebox.showerror(
                        title = "Entry Name",
                        message = "Entry name must be unique"
                    )
                    self.txt_ent_name.focus_set()
                    return(False)
        
        self.T.entries[idx].name = new_name
        self.entry_list.delete(idx)
        self.entry_list.insert(idx, self.T.entries[idx].name)
        self.entry_list.selection_set(idx)
        return(True)
    
    def cmb_ent_type_Changed(self,ev):
        type_idx = self.cmb_ent_type.current()
        entry_idx = self.entry_list.curselection()[0]
        
        # create new entry data object. preserve the name
        entry_t = report_entries.get_type(type_idx)
        name =  self.T.entries[entry_idx].name
        E = entry_t(self.T, name)
        
        # replace old entry data object
        self.T.entries[entry_idx] = E
        
        # force redraw of the settings
        self.set_entry_selection(entry_idx)
        
#===================================================================================================
class FormImporter(tk.Tk):
    
    #---------------------------------------------------------------
    # Widgets
    #---------------------------------------------------------------
    def create_widgets(self):
        self.title("Import Forms: %s" % self.T.name)
        
        #--------------------------------------------------------
        # File List
        file_list_fr = ttk.Frame(
            self,
            padding=3
        )
        file_list_fr.pack(
            side = tk.TOP,
            fill=tk.BOTH,
            expand = True
        )
        
        self.file_list = tk.Listbox(
            file_list_fr,
            highlightthickness = 0,
            selectmode = "single",
            exportselection = False,
            activestyle = "none",
            width = 100,
            height = 20
        )
        self.file_list.bind('<<ListboxSelect>>', self.ev_file_list_Select)
        self.file_list.pack(
            side = tk.LEFT,
            fill = tk.BOTH,
            expand = True
        )
        
        # scrollbar
        file_list_scroll = ttk.Scrollbar(file_list_fr)
        file_list_scroll.pack(
            side = tk.RIGHT,
            fill = tk.Y
        )
                                
        # Link scrollbar <--> list
        self.file_list.configure(yscrollcommand=file_list_scroll.set)
        file_list_scroll.configure(command=self.file_list.yview)
        
        #--------------------------------------------------------
        # Bottom Buttons
        bottom_buttons_fr = ttk.Frame(
            self,
            padding=3
        )
        bottom_buttons_fr.pack(
            side = tk.TOP,
            fill=tk.BOTH
        )
        
        x = ttk.Button(
            bottom_buttons_fr,
            text="Import PDFs",
            command = self.ev_but_import
        )
        x.pack(side=tk.LEFT)
        
        x = ttk.Button(
            bottom_buttons_fr,
            text="Import Folder of PDFs",
            command = self.ev_but_import_dir
        )
        x.pack(side=tk.LEFT)
        
        x = ttk.Button(
            bottom_buttons_fr,
            text="Remove",
            command = self.ev_but_remove
        )
        x.pack(side=tk.LEFT)
        
        x = ttk.Button(
            bottom_buttons_fr,
            text="Export to Excel",
            command = self.ev_but_export
        )
        x.pack(side=tk.RIGHT)
        
        # window is not allowed to be any smaller than default
        self.update_idletasks() #Give Tk a chance to update widgets and figure out the window size
        self.minsize(self.winfo_width(), self.winfo_height())
        
        
    #---------------------------------------------------------------
    # Helpers
    #---------------------------------------------------------------
    
    def set_selection(self, idx):
        if(len(self.Forms) == 0):
            # List is empty
            return
        elif(idx >= len(self.Forms)):
            idx = len(self.Forms) - 1
        
        self.file_list.selection_clear(0,tk.END)
        self.file_list.selection_set(idx)
        self.file_list.see(idx)
        
    def add_form(self, filename):
        
        # check if it already exists
        for f in self.Forms:
            if(f.filename == filename):
                return
        
        logging.info("Loading: %s" % filename)
        F = form_data.FormData(filename)
        
        self.Forms.append(F)
        self.file_list.insert(tk.END, F.filename)
        
        # Validate the form
        if(F.valid):
            if(self.T.is_matching_form(F) == False):
                logging.info("Form fingerprint mismatch. Not valid: %s" % F.filename)
                F.valid = False
        
        if(not F.valid):
            self.file_list.itemconfigure(tk.END, background="red")
        
    def remove_form(self, idx):
        if(len(self.Forms) == 0):
            # List is empty
            return
        elif(idx >= len(self.Forms)):
            return
        
        del self.Forms[idx]
        self.file_list.delete(idx)
        self.set_selection(idx)
        
    #---------------------------------------------------------------
    # Events
    #---------------------------------------------------------------
    def __init__(self, parent, Template, Settings):
        self.T = Template
        self.S = Settings
        self.Forms = []
        
        tk.Tk.__init__(self, parent)
        self.create_widgets()
        
    def ev_file_list_Select(self, ev):
        idx = self.file_list.curselection()
        if(len(idx) == 0):
            return
        idx = int(idx[0])
    
    def ev_but_import(self):
        options = {}
        options['defaultextension'] = '.pdf'
        options['filetypes'] = [('PDF files', '.pdf')]
        options['parent'] = self
        options['title'] = 'Open...'
        
        filenames = filedialog.askopenfilenames(**options)
        
        if(not filenames):
            return
        
        # define a separate worker function to import the PDFs
        def worker(dlg_if, filenames):
            dlg_if.set_progress(0)
            n_found = len(filenames)
            n_done = 0;
            
            for f in filenames:
                dlg_if.set_status1("Processing files: %d/%d" % (n_done + 1, n_found))
                dlg_if.set_status2(trim_path(f, 50))
                dlg_if.set_progress(100*n_done/n_found)
                if(dlg_if.stop_requested()):
                    return
                f = os.path.abspath(f)
                self.add_form(f)
        
        # Start the job
        args={'filenames':filenames}
        x = tkext.ProgressBox(
            job_func = worker,
            job_data = args,
            parent = self,
            title = "Importing PDFs..."
        )
        
        self.set_selection(len(self.Forms)-1)
    
    def ev_but_import_dir(self):
        options = {}
        options['mustexist'] = True
        options['parent'] = self
        options['title'] = 'Recursive Open'
        
        dir = filedialog.askdirectory(**options)
        if(not dir):
            return
        dir = os.path.abspath(dir)
        
        # define a separate worker function to import the PDFs
        def worker(dlg_if, start_dir):
            dlg_if.set_progress(0)
            dlg_if.set_status1("Gathering files...")
            n_found = 0
            
            matches = []
            for root, dirnames, filenames in os.walk(dir):
                if(dlg_if.stop_requested()):
                    return
                for filename in fnmatch.filter(filenames, '*.pdf'):
                    matches.append(os.path.join(root, filename))
                    n_found = n_found + 1
                    dlg_if.set_status2("Found: %d" % n_found)
            
            n_done = 0
            for f in matches:
                dlg_if.set_status1("Processing files: %d/%d" % (n_done + 1, n_found))
                dlg_if.set_status2(trim_path(f, 50))
                dlg_if.set_progress(100*n_done/n_found)
                
                if(dlg_if.stop_requested()):
                    return
                self.add_form(f)
                n_done = n_done + 1
        
        # Start the job
        args={'start_dir':dir}
        x = tkext.ProgressBox(
            job_func = worker,
            job_data = args,
            parent = self,
            title = "Importing PDFs..."
        )
        
        self.set_selection(len(self.Forms)-1)
        
    def ev_but_remove(self):
        idx = self.file_list.curselection()
        if(len(idx)):
            idx = int(idx[0])
            self.remove_form(idx)
        
    def ev_but_export(self):
        
        options = {}
        options['defaultextension'] = '.xlsx'
        options['filetypes'] = [('Excel Workbook', '.xlsx'), ('Excel 97-2003 Workbook', '.xls')]
        options['parent'] = self
        options['title'] = 'Export as Excel...'
        filename = filedialog.asksaveasfilename(**options) 
        if(not filename):
            return
        
        TBL = report_template.DataTable()
        TBL.init_blank(self.T)
        
        for form in self.Forms:
            if(form.valid):
                form_report = self.T.create_report(form)
                TBL.append_row(form_report)
        
        TBL.export_excel(filename)

