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

import os
import datetime
import logging

from . import pdf_parser
from pdfminer.pdftypes import PDFException

log = logging.getLogger("form_data")

class FormData:
    def __init__(self, filename):
        self.valid = False
        self.filename = filename
        self.pages = []
        self.fields = {}
        self.timestamp = None
        
        # check if file exists
        if(not os.path.exists(filename)):
            self.valid = False
            return
        
        self.timestamp = datetime.datetime.fromtimestamp(os.path.getctime(filename))
        
        # Parse!
        try:
            self.pages = pdf_parser.get_pdf_pages(filename)
        except PDFException as E:
            self.valid = False
            log.warning("Call to get_pdf_pages() failed for '%s'" % filename)
            return
        
        # Flatten to fields for easy access
        self.fields = {}
        for pg in self.pages:
            for field in pg.fields:
                self.fields[field.name] = field.value
        
        self.valid = True
    
    def get_fingerprint(self):
        """ Collects the page hashes to construct a form fingerprint """
        fingerprint = []
        for page in self.pages:
            if(page.page_hash != None):
                fingerprint.append(page.page_hash)
        return(fingerprint)
        
    def has_matching_fingerprint(self, ext_fp):
        """ checks if ext_fp is a subset of this form's fingerprint """
        this_fp = self.get_fingerprint()
        
        if(len(ext_fp) > len(this_fp)):
            # Impossible to be a subset because it is bigger than this
            return(False)
        
        # Check if ext_fp is a subset of this_fp
        for i in range(len(this_fp) - len(ext_fp) + 1):
            # for each start position
            
            # check if the substring matches
            for j in range(len(ext_fp)):
                if(this_fp[i+j] != ext_fp[j]):
                    # no match at this start position
                    break
            else:
                # finished loop without finding mismatch.
                return(True)
                
        # Never found a match at any offset
        return(False)
