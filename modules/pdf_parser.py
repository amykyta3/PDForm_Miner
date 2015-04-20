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

import sys
import re
import logging

from pdfminer.psparser import PSLiteral
from pdfminer.pdfparser import PDFDocument, PDFParser
from pdfminer.pdftypes import PDFObjRef

#===================================================================================================
Ff_RADIO = 0x00010000
Ff_PUSHBUTTON = 0x00020000
#===================================================================================================

class Field:
    def __init__(self, obj):
        self.valid = False
        
        # bulletproof checks
        if('Subtype' not in obj): return
        if(isinstance(obj['Subtype'], PSLiteral) == False): return
        if(obj['Subtype'].name != "Widget"): return
        if('T' not in obj): return
        if(not isinstance(obj['T'], str)): return
        if('FT' not in obj): return
        if(not isinstance(obj['FT'], PSLiteral)): return
        
        # Get the field name
        self.name = obj['T']
        # check if it is a UTF-16 string.
        if(type(self.name) == bytes):
            self.name = self.name.decode("utf-16")
        
        # Determine the type of field, and get the value
        if(obj['FT'].name == "Tx"):
            # Text Field
            if('V' in obj):
                self.value = obj['V']
                
                # check if it is a UTF-16 string.
                if(type(self.value) == bytes):
                    self.value = self.value.decode("utf-16")
            else:
                self.value = ""
        elif(obj['FT'].name == "Btn"):
            # "button" Field (could be radio or checkbox)
            if('Ff' in obj):
                Ff = obj['Ff']
            else:
                Ff = 0;
            
            if(Ff & Ff_RADIO):
                # is a radio button
                # not supported yet
                
                # Exit violently in case I forget to implement this
                raise Exception("Radio buttons not implemented yet")
                sys.exit()
                
                return
            elif(Ff & Ff_PUSHBUTTON):
                # is a pushbutton
                return
            else:
                # is a checkbox
                if('V' in obj):
                    if(obj['V'].name == "Yes"):
                        self.value = 1
                    else:
                        self.value = 0
                else:
                    self.value = 0
            
        elif(obj['FT'].name == "Ch"):
            # Choice Field
            if('V' in obj):
                self.value = obj['V']
                
                # check if it is a UTF-16 string.
                if(type(self.value) == bytes):
                    self.value = self.value.decode("utf-16")
            else:
                self.value = ""
        else:
            return
            
        # Get geometry info
        # Units are multiples of 1/72 inch
        # 4 entry array
        # I THINK it is: [x1,y1,x2,y2]
        # where x1, y1 are the smallest of the two
        # coordinates seem to be counted from the bottom left of the page
        self.rect = obj['Rect']
        
        self.valid = True
        
#===================================================================================================
def fnv_hash32(s):
    """ 32-bit Fowler–Noll–Vo Hash function """
    h = 0x811C9DC5;
    for c in s:
        h = (h*0x1000193) & 0xFFFFFFFF
        h = h ^ ord(c)
    
    return(h)

#===================================================================================================
class Page:
    """ Wrapper class for the PDFMiner page class """
    def __init__(self, pdfminer_page):
        self.valid = False
        
        # Get the page dimensions
        self.mediabox = pdfminer_page.mediabox
        
        # Gather all the fields
        self.fields = []
        
        # Integer page hash
        self.page_hash = None
        
        # annots parameter type varies. Clean it up
        if(pdfminer_page.annots == None):
            # no annots. Make an empty list
            pdfminer_page.annots = []
        elif(type(pdfminer_page.annots) != list):
            # not a list. Pack into an array and let the eval function deal with it
            pdfminer_page.annots = [pdfminer_page.annots]
            
        self.eval_annot_list(pdfminer_page.annots)
        
        self.hash_fields()
        
        self.valid = True
        
    def eval_annot_list(self, annots):
        for objref in annots:
            obj = objref.resolve()
            
            # Check if there is a sublist of even more annots. If so, then recurse!
            if(isinstance(obj, list)):
                self.eval_annot_list(obj)
            
            # skip anything that isnt a dict
            if obj is None: continue
            if(isinstance(obj, dict) == False): continue
            
            # All fillable field objects have the attribute Subtype=Widget
            # Skip other Annot objects
            if('Subtype' not in obj): continue
            if(isinstance(obj['Subtype'], PSLiteral) == False): continue
            if(obj['Subtype'].name != "Widget"): continue
            
            F = Field(obj)
            if(F.valid):
                self.fields.append(F)
    
    def hash_fields(self):
        """ Calculates a 32-bit hash based on the fields on this page """
        if(len(self.fields) == 0):
            self.page_hash = None
        else:
            self.page_hash = 0
            for F in self.fields:
                h = fnv_hash32(F.name)
                self.page_hash = self.page_hash ^ h
    
#===================================================================================================
# Instead of looping through every object ever, traverse the page tree and get the fields
# directly via the Annot entry of each page.
# Bonus: they seem to be sorted in tab-order
def get_pdf_pages(filename):
    
    # Load PDF
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    
    # Connect parser to document
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    
    doc.initialize()

    # Gather all the pages
    pages = []
    for pg in doc.get_pages():
        P = Page(pg)
        pages.append(P)
    
    fp.close()
    
    return(pages)

#===================================================================================================
def get_pdf_fields(filename):
    """ Legacy wrapper function to get a flattened dict of field k/v pairs """
    pages = get_pdf_pages(filename)
    
    # Blank dict.
    F = {}
    
    # decompose page tree into a flat dict of all fields
    for pg in pages:
        for field in pg.fields:
            F[field.name] = field.value
    
    return(F)
