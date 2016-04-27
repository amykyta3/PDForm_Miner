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

import modules.gui as gui
import modules.report_template as report_template

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
    
    Templates = load_templates()
    
    # Don't know which template to start with. Ask for one first
    dlg = gui.TemplateBrowser(None, Templates)
    
    if(dlg.result):
        logging.info("Opening Template: %s" % dlg.selected_template.name)
        app = gui.FormImporter(None, dlg.selected_template)
        app.mainloop()
        
    save_templates(Templates)

#---------------------------------------------------------------------------------------------------
TEMPLATE_DIR = "templates"

def save_templates(templates):
    # create template dir if necessary
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    
    for T in templates:
        path = os.path.join(TEMPLATE_DIR, "%s.json" % (T.name))
        with open(os.path.join(path), 'w') as f:
            json.dump(T.to_dict(), f, indent=2, sort_keys = True)
            
def load_templates():
    templates = []
    
    if(os.path.exists(TEMPLATE_DIR)):
        for p in os.listdir(TEMPLATE_DIR):
            if(p.endswith(".json")):
                with open(os.path.join(TEMPLATE_DIR, p), 'r') as f:
                    templates.append(report_template.ReportTemplate.from_dict(json.load(f)))
    
    return(templates)
    
    
####################################################################################################
if __name__ == '__main__':
    sys.exit(main(sys.argv))