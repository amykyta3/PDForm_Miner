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

import logging
import traceback
from tkinter import messagebox

#===================================================================================================
import sys
def error_handler(*exc_info):
    exc_type = exc_info[0]
    exc_value = exc_info[1]
    
    text = "".join(traceback.format_exception(*exc_info))
    logging.critical("{0}".format(text))
    
    if(exc_type == ImportError):
        messagebox.showerror(
            title = "Incomplete Installation",
            message = "It looks like this program is missing some parts.\n"
                    + "Please re-run the 'install_packages' script.\n\n"
                    + "Details: %s" % exc_value
        )
    else:
        messagebox.showerror(
            title = "Internal Error",
            message = "Oops! Something went wrong!\n\n"
                    + "Please send the 'error.log' file to amykyta3@gmail.com and I'll try to fix this problem"
        )
    
# Install exception handler
sys.excepthook = error_handler

#===================================================================================================
import tkinter as tk
# By default, tk exceptions occur silently.
# Forward these to our error handler by overriding the default callback
def tk_error_handler(self, *args):
    error_handler(*args)
tk.Tk.report_callback_exception = tk_error_handler



#===================================================================================================
import pdfminer.psparser
# Importing PDFs generates a bunch of noise that I don't care about. Silence these messages
def hide_pdf_syntax_warnings(exctype, msg, strict=False):
    if(check_pdf_exc_type(exctype)):
        logging.warning(msg)

pdfminer.psparser.handle_error = hide_pdf_syntax_warnings

# Filter by exctype
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.psparser import PSEOF

def check_pdf_exc_type(exctype):
    if(exctype == pdfminer.pdfparser.PDFSyntaxError):
        return(False)
    if(exctype == pdfminer.psparser.PSEOF):
        return(False)
    else:
        return(True)


