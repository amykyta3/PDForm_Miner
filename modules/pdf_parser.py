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

import sys
import re
import logging

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdftypes import PDFObjRef
from pdfminer.psparser import PSLiteral

#===================================================================================================
Ff_RADIO = 0x00010000
Ff_PUSHBUTTON = 0x00020000
#===================================================================================================
def decode_pdf_string(bytestring):
    """
    PDF Strings can sometimes be UTF-16. Detect and convert if necessary
    """
    if(bytestring.startswith(b'\xfe\xff') or bytestring.startswith(b'\xff\xfe')):
        string = bytestring.decode("utf-16")
    else:
        string = bytestring.decode("ascii")
    
    return(string)

#===================================================================================================
class Field:
    def __init__(self, obj):
        self.valid = False
        
        # bulletproof checks
        if('Subtype' not in obj): return
        if(isinstance(obj['Subtype'], PSLiteral) == False): return
        if(obj['Subtype'].name != "Widget"): return
        if('T' not in obj): return
        if(not isinstance(obj['T'], bytes)): return
        if('FT' not in obj): return
        if(not isinstance(obj['FT'], PSLiteral)): return
        
        # Get the field name
        self.name = decode_pdf_string(obj['T'])
        
        # Determine the type of field, and get the value
        if(obj['FT'].name == "Tx"):
            # Text Field
            if('V' in obj):
                self.value = decode_pdf_string(obj['V'])
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
                self.value = decode_pdf_string(obj['V'])
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
    
    # Initialize pdfminer
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = PDFDevice(rsrcmgr)
    
    
    # Gather all the pages
    pages = []
    for pg in PDFPage.create_pages(doc):
        P = Page(pg)
        pages.append(P)
        
    fp.close()
    
    return(pages)
