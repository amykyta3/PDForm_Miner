#!/usr/bin/env python3

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

import modules.error_handler

import sys
import json
import os
import logging
import atexit

import modules.gui as gui
import modules.report_template as report_template

####################################################################################################
class AppSettings:
    FILENAME = "settings.json"
    def __init__(self):
        # Default Settings
        self.Templates = []
        
    def load(self):
        if(not os.path.exists(self.FILENAME)):
            return
        
        f = open(self.FILENAME,"r")
        dict = json.load(f)
        f.close()
        
        # Load templates
        if('Templates' in dict):
            for td in dict['Templates']:
                t = report_template.ReportTemplate(dict = td)
                self.Templates.append(t)
        
    def save(self):
        dict = {}
        
        # convert templates
        dict['Templates'] = []
        for t in self.Templates:
            td = t.get_dict()
            dict['Templates'].append(td)
            
        # Write out
        f = open(self.FILENAME, "w")
        json.dump(dict, f, indent=2)
        f.close()

####################################################################################################
def main(argv):
    
    logging.basicConfig(
        filename="error.log",
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.WARNING
    )
    
    # dump all log messages to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)
    
    
    S = AppSettings()
    S.load()
    atexit.register(S.save)
    
    # Don't know which template to start with. Ask for one first
    dlg = gui.TemplateBrowser(None, S)
    
    if(dlg.result):
        logging.info("Opening Template: %s" % dlg.selected_template.name)
        app = gui.FormImporter(None, dlg.selected_template, S)
        app.mainloop()
    

####################################################################################################
if __name__ == '__main__':
    sys.exit(main(sys.argv))