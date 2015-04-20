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

import os
import datetime

import modules.pdf_parser as pdf_parser

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
        self.pages = pdf_parser.get_pdf_pages(filename)
        
        # Flatten to fields for easy access
        self.fields = {}
        for pg in self.pages:
            for field in pg.fields:
                self.fields[field.name] = field.value
        self.fields = pdf_parser.get_pdf_fields(filename)
        
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
