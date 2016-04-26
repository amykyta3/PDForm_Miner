#!/usr/bin/env python3

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


import modules.python_modules.tk_extensions as tkext
#tkext.ExceptionHandler.install()

import modules.error_handler

import sys
import json
import os
import logging
import atexit

import modules.gui as gui
import modules.report_template as report_template
from modules.python_modules.class_codec import EncodableClass

####################################################################################################
class AppSettings(EncodableClass):
    FILENAME = "settings.json"
    
    encode_schema = {
        "Templates": [report_template.ReportTemplate]
    }
    
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
        json.dump(dict, f, indent=2, sort_keys = True)
        f.close()

####################################################################################################
def main(argv):
    
    logging.basicConfig(
        filename="run.log",
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.WARNING
    )
    
    # dump all log messages to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)
    
    SETTINGS_FILE = "settings.json"
    if(os.path.exists(SETTINGS_FILE)):
        # Load settings file
        with open(SETTINGS_FILE, 'r') as f:
            S = AppSettings.from_dict(json.load(f))
    else:
        # Create default settings
        S = AppSettings()
    
    # Don't know which template to start with. Ask for one first
    dlg = gui.TemplateBrowser(None, S)
    
    if(dlg.result):
        logging.info("Opening Template: %s" % dlg.selected_template.name)
        app = gui.FormImporter(None, dlg.selected_template, S)
        app.mainloop()
        
    # Write out settings
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(S.to_dict(), f, indent=2, sort_keys = True)

####################################################################################################
if __name__ == '__main__':
    sys.exit(main(sys.argv))