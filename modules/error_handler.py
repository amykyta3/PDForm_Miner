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
                    + "Please submit an issue report at https://github.com/amykyta3/PDForm_Miner/issues\n"
                    + "Be sure to include the 'run.log' file and I'll try to fix this problem"
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


