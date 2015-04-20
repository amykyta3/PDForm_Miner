####################################################################################################
# Copyright (c) 2015, Alexander I. Mykyta
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
####################################################################################################

import copy

import pyexcel
import pyexcel.ext.xls
import pyexcel.ext.xlsx

import modules.form_data as form_data
import modules.report_entries as report_entries

class ReportTemplate:
    def __init__(self, filename = None, dict = None):
        self.name = ""
        self.description = ""
        self.form_fingerprint = [] # Array of page hashes, in order of appearance.
        
        self.avail_fields = []
        
        # array of report_entry._entry classes
        self.entries = []
        
        if(filename != None):
            self._init_from_pdf(filename)
        elif(dict != None):
            self._init_from_dict(dict)
        
    
    def _init_from_pdf(self, filename):
        # TODO: move factory function here.
        pass
        
    def _init_from_dict(self, dict):
        self.name = dict["name"]
        self.description = dict["description"]
        self.form_fingerprint = dict["form_fingerprint"]
        
        self.avail_fields = dict["avail_fields"]
        
        self.entries = []
        for ED in dict["entries"]:
            E = report_entries.create_from_dict(self,ED)
            self.entries.append(E)
        
    #--------------------------------------------------------------------------
    def get_dict(self):
        """ Convert this to a dictionary data type """
        dict = {}
        dict['name'] = self.name
        dict['description'] = self.description
        dict['form_fingerprint'] = self.form_fingerprint
        dict['avail_fields'] = self.avail_fields
        
        dict['entries'] = []
        for e in self.entries:
            ed = e.get_dict()
            dict['entries'].append(ed)
        
        return(dict)
        
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
        
def create_from_pdf(filename):
    """ Create a new template based off of a PDF Form """
    
    P = form_data.FormData(filename)
    if(P.valid):
        T = ReportTemplate()
        
        names = []
        for k,v in P.fields.items():
            names.append(k)
        
        names.sort()
        
        T.avail_fields = names
        
        T.form_fingerprint = P.get_fingerprint()
        
        return(T)
    else:
        return(None)
    
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

