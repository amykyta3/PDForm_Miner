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

import datetime
from datetime import timezone

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

#===================================================================================================
# Base Classes
#===================================================================================================
# Generic class that defines a report entry
class _entry:
    type_name = "INVALID"
    
    def __init__(self, parent_template, name):
        self.parent_template = parent_template
        self.name = name
    
    # Extend this
    def get_dict(self):
        """ Convert this to a dictionary data type """
        D = {}
        D['type_name'] = self.type_name
        D['name'] = self.name
        return(D)
        
    # Extend this
    def set_dict(self, D):
        """ Initialize remainder of the class from a dictionary """
        self.name = D['name']
    
    # override this
    def get_value(self, pdf_object):
        return(None)
    
    # override this
    def __deepcopy__(self, memo):
        cls = self.__class__
        C = cls.__new__(cls)
        memo[id(self)] = C
        
        C.parent_template = self.parent_template
        C.name = self.name
        
        return(C)

#---------------------------------------------------------------------------------------------------
class _settings_gui:
    # associate the gui object with the data object type
    data_t = _entry
    
    def __init__(self, Data, container_frame):
        self.Data = Data
        self.container_frame = container_frame
        
    def force_commit(self):
        """forces widget data to be loaded into the Data object"""
        pass
    
    def destroy(self):
        """Unloads the settings widgets"""
        
        self.force_commit()
        
        for child in self.container_frame.winfo_children():
            child.destroy()

#===================================================================================================
# Basic Helper Functions
#===================================================================================================

def CreateSettings(Data, container_frame):
    """ Factory function for creating a settings widget container object"""
    # Search through all subclasses of _settings_gui and find the one
    # that has a matching data_t to type(Data)
    for class_t in _settings_gui.__subclasses__():
        if(class_t.data_t == type(Data)):
            # Found match. create the settings gui object and return it.
            S = class_t(Data, container_frame)
            return(S)
    
    return(None)

def get_types():
    """ Returns a list of available Report Entry types """
    T = _entry.__subclasses__()
    
    # sort alphabetically by type name
    T.sort(key=lambda x: x.type_name)
    
    return(T)
    
def get_type_names():
    """ Returns a list of names of available Report Entry types """
    T = get_types()
    N = []
    for type in T:
        N.append(type.type_name)
    
    return(N)

def get_type(idx):
    """ Returns the Report Entry type according to its list index

    The index is consistent with the list returned by get_type_names() and get_types()
    """
    T = get_types()
    return(T[idx])
    
def get_default_type():
    return(PDF_Field)

def get_type_idx(type):
    """ Reverse operation of get_type() """
    T = get_types()
    
    for i,v in enumerate(T):
        if(v == type):
            return(i)
    
    return(None)
    
def create_from_dict(T,D):
    """ Creates a _entry class based on a dictionary object"""
    
    # Search through each _entry subtype and find the one with a matching type_name
    for class_t in _entry.__subclasses__():
        if(class_t.type_name == D["type_name"]):
            E = class_t(T, D["name"])
            E.set_dict(D)
            return(E)
    
    return(None)
    
#===================================================================================================
# Report entry from a PDF field
#===================================================================================================
class PDF_Field(_entry):
    type_name = "PDF Field"
    
    def __init__(self, parent_template, name):
        _entry.__init__(self, parent_template, name)
        
        self.field_name = None
        # Default to use the first field in list
        if(len(self.parent_template.avail_fields) != 0):
            self.field_name = self.parent_template.avail_fields[0]
            
    def get_dict(self):
        """ Convert this to a dictionary data type """
        D = _entry.get_dict(self)
        D['field_name'] = self.field_name
        return(D)
        
    def set_dict(self, D):
        """ Initialize remainder of the class from a dictionary """
        _entry.set_dict(self,D)
        self.field_name = D['field_name']
        
    def get_value(self, pdf_object):
        if(self.field_name in pdf_object.fields):
            return(pdf_object.fields[self.field_name])
        else:
            return(None)
    
    def __deepcopy__(self, memo):
        cls = self.__class__
        C = cls.__new__(cls)
        memo[id(self)] = C
        
        C.parent_template = self.parent_template
        C.name = self.name
        C.field_name = self.field_name
        
        return(C)

#---------------------------------------------------------------------------------------------------
class PDF_Field_settings_gui(_settings_gui):
    data_t = PDF_Field
    
    def __init__(self, Data, container_frame):
        _settings_gui.__init__(self, Data, container_frame)
        
        # Create GUI widgets inside container_frame
        x = ttk.Label(container_frame, text="PDF Field Name")
        x.grid(row=0, column=0, sticky=(tk.N, tk.E))
        self.cmb_field_name = ttk.Combobox(
            container_frame,
            state= 'readonly',
            values=self.Data.parent_template.avail_fields
        )
        if(self.Data.field_name):
            self.cmb_field_name.set(self.Data.field_name)
        self.cmb_field_name.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E))
        self.cmb_field_name.bind("<<ComboboxSelected>>", self.cmb_field_name_Changed)
        
        container_frame.columnconfigure(1, weight=1)
        container_frame.columnconfigure(tk.ALL, pad=5)
        container_frame.rowconfigure(tk.ALL, pad=5)
    
    def force_commit(self):
        self.Data.field_name = self.cmb_field_name.get()
    
    def cmb_field_name_Changed(self,ev):
        self.Data.field_name = self.cmb_field_name.get()
        

#===================================================================================================
# Timestamp based on the time a report was generated
#===================================================================================================
class Export_Timestamp(_entry):
    type_name = "Time Exported"
    
    def __init__(self, parent_template, name):
        _entry.__init__(self, parent_template, name)
        
    def get_dict(self):
        """ Convert this to a dictionary data type """
        D = _entry.get_dict(self)
        return(D)
        
    def set_dict(self, D):
        """ Initialize remainder of the class from a dictionary """
        _entry.set_dict(self,D)
        
    def get_value(self, pdf_object):
        now = datetime.datetime.now()
        str = now.strftime("%Y-%m-%d %H:%M:%S")
        return(str)
    
    def __deepcopy__(self, memo):
        cls = self.__class__
        C = cls.__new__(cls)
        memo[id(self)] = C
        
        C.parent_template = self.parent_template
        C.name = self.name
        
        return(C)

#---------------------------------------------------------------------------------------------------
class Export_Timestamp_settings_gui(_settings_gui):
    data_t = Export_Timestamp
    
    def __init__(self, Data, container_frame):
        _settings_gui.__init__(self, Data, container_frame)
        # No extra settings
        
    def force_commit(self):
        pass
    
#===================================================================================================
# Timestamp based on the PDF's ctime
#===================================================================================================
class PDF_Timestamp(_entry):
    type_name = "Time PDF Created"
    
    def __init__(self, parent_template, name):
        _entry.__init__(self, parent_template, name)
        
    def get_dict(self):
        """ Convert this to a dictionary data type """
        D = _entry.get_dict(self)
        return(D)
        
    def set_dict(self, D):
        """ Initialize remainder of the class from a dictionary """
        _entry.set_dict(self,D)
        
    def get_value(self, pdf_object):
        str = pdf_object.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return(str)
    
    def __deepcopy__(self, memo):
        cls = self.__class__
        C = cls.__new__(cls)
        memo[id(self)] = C
        
        C.parent_template = self.parent_template
        C.name = self.name
        
        return(C)

#---------------------------------------------------------------------------------------------------
class PDF_Timestamp_settings_gui(_settings_gui):
    data_t = PDF_Timestamp
    
    def __init__(self, Data, container_frame):
        _settings_gui.__init__(self, Data, container_frame)
        # No extra settings
        
    def force_commit(self):
        pass
    
#===================================================================================================
# PDF's Filename
#===================================================================================================
class PDF_Filename(_entry):
    type_name = "Filename"
    
    def __init__(self, parent_template, name):
        _entry.__init__(self, parent_template, name)
    
    def get_dict(self):
        """ Convert this to a dictionary data type """
        D = _entry.get_dict(self)
        return(D)
        
    def set_dict(self, D):
        """ Initialize remainder of the class from a dictionary """
        _entry.set_dict(self,D)
        
    def get_value(self, pdf_object):
        return(pdf_object.filename)
    
    def __deepcopy__(self, memo):
        cls = self.__class__
        C = cls.__new__(cls)
        memo[id(self)] = C
        
        C.parent_template = self.parent_template
        C.name = self.name
        
        return(C)
        
#---------------------------------------------------------------------------------------------------
class PDF_Filename_settings_gui(_settings_gui):
    data_t = PDF_Filename
    
    def __init__(self, Data, container_frame):
        _settings_gui.__init__(self, Data, container_frame)
        # No extra settings
    
    def force_commit(self):
        pass
