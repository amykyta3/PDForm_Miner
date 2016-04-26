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

import pyexcel
import pyexcel.ext.xls
import pyexcel.ext.xlsx

from . import form_data
from . import report_entries

from .python_modules.class_codec import EncodableClass

class ReportTemplate(EncodableClass):
    
    encode_schema = {
        "name": str,
        "description": str,
        "form_fingerprint": [int],
        "avail_fields": [str],
        "entries": [report_entries._entry]
    }
    
    def __init__(self):
        self.name = ""
        self.description = ""
        self.form_fingerprint = [] # Array of page hashes, in order of appearance.
        self.avail_fields = []
        self.entries = [] # array of report_entry._entry classes
    
    @classmethod
    def from_pdf(cls, filename):
        self = cls.__new__(cls)
        P = form_data.FormData(filename)
        if(P.valid):
            self.name = ""
            self.description = ""
            self.entries = []
            
            names = []
            for k,v in P.fields.items():
                names.append(k)
            names.sort()
            
            self.avail_fields = names
            
            self.form_fingerprint = P.get_fingerprint()
            
        else:
            raise ValueError()
        
        return(self)
        
    #--------------------------------------------------------------------------
        
    def is_matching_form(self, form_data):
        """ Checks if the given form_data's fingerprint is compatible with the template's fingerprint """
        return(form_data.has_matching_fingerprint(self.form_fingerprint))
        
    def create_report(self, form_data):
        """ Given a FormData object, returns a dictionary of values"""
        R = {}
        for e in self.entries:
            R[e.name] = e.get_value(form_data)
        
        return(R)
        
    def __deepcopy__(self, memo):
        cls = self.__class__
        C = cls.__new__(cls)
        memo[id(self)] = C
        for k, v in self.__dict__.items():
            setattr(C, k, copy.deepcopy(v, memo))
        
        # Update entries to point to the new instance of parent template (this)
        for e in self.entries:
            e.parent_template = self
        
        return(C)
    



#===================================================================================================
# Completely unrelated functions
# this needs to move somewhere else
#===================================================================================================
class DataTable():
    def __init__(self):
        self.name = "table"
        self.headings = [] # array of column headings (to define column order)
        self.table = {} # dictionary of column arrays
        self.rowcount = 0
        
    def init_blank(self, T):
        """Initialize the table using a template"""
        self.name = T.name
        self.headings = []
        self.table = {}
        self.rowcount = 0
        for e in T.entries:
            self.headings.append(e.name)
            self.table[e.name] = []

    def append_row(self, row_dict):
        """ Append a row to the bottom of the table.
        row_dict is a dict of row data by column name """
        
        for k,v in row_dict.items():
            if(k not in self.table):
                # Heading does not exist yet. Fill in blanks for past items
                self.table[k] = [""] * self.rowcount
                
            self.table[k].append(v)
            
        self.rowcount = self.rowcount + 1
        
        # Even out any columns in DB that were not filled
        for hdr in self.table:
            if(len(self.table[hdr]) < self.rowcount):
                self.table[hdr].append(None)
    
    def export_excel(self, filename):
        """ Export table to a new Excel file """
        # convert table to array of rows
        rows = [self.headings]
        for y in range(self.rowcount):
            row = []
            for h in self.headings:
                row.append(self.table[h][y])
            rows.append(row)
        
        sheet = pyexcel.Sheet(rows, self.name, name_columns_by_row=0)
        sheet.save_as(filename)

