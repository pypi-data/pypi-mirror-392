""" A simple Python Module for Educational Purpose"""

import pyperclip
from .content import answer_dict

def get(arg_string):
    arg_string = arg_string.replace(" ", "").replace("_", "").lower()
    answer_text = answer_dict.get(arg_string, None) 
    if answer_text is None:
        print("Not found")
    else:
        pyperclip.copy(answer_text)
        print("Success")


