
from moodlexport.python_to_moodle import Category, Question
from moodlexport.string_manager import latex_protect, alias, savestr

import os.path

LATEX_PACKAGE_URL = "https://raw.githubusercontent.com/Guillaume-Garrigos/moodlexport/master/latex/latextomoodle.sty"
LATEX_PACKAGE_NAME = "latextomoodle"

def latexfile_preamble(list_of_packages=[]):
    string = "\documentclass{article}\n"
    string += "\\usepackage{amsmath}\n"
    string += "\\usepackage{amssymb}\n"
    string += "\\usepackage{graphicx}\n"
    
    for package in list_of_packages:
        string += latex_protect("\\usepackage{")+ package +"}\n"
    return string

def latexfile_begin(env_name, option = None):
    string = latex_protect('\begin{' + env_name + '}')
    if option is not None:
        string += '[' + str(option) + ']'        
    return string + '\n'

def latexfile_end(env_name):
    return latex_protect('\end{' + env_name + '}') + '\n'

def latexfile_command(cmd_name, value, option = None):
    string = latex_protect("\\" + cmd_name )
    if option is not None:
        string += '[' + str(option) + ']'
    string += '{' + latex_protect(str(value)) + '}\n'
    return string

def latexfile_environement(env_name, value, option=None):
    string = latexfile_begin(env_name, option)
    string += value + '\n'
    string += latexfile_end(env_name)
    return string

def latexfile_append_question(question): #Given a Question return the latex string
    content = ""
    if question.structure['name']['isset']: # First the title
        content += latexfile_command(alias('name'), question.get_name())
    content += latex_protect(question.get_text()) + '\n'
    option = question.get_type()
    if question.has_answer():
        content += '\n'
        for answer in question.get_answer():
            content += latexfile_command('answer', answer.get_text(), str(answer.get_relativegrade()))
    content += '\n'
    for field in question.structure:
        if field not in ['@type', 'questiontext', 'answer', 'name']: # keep it for later/before
            if question.structure[field]['isset']: # if default we dont print it
                content += latexfile_command(alias(field), question.structure[field]['value'])
    return latexfile_environement('question', content, option)

def latexfile_append_category(category): # Given a category return the latex string
    content = ""
    description = category.get_description()
    if description != "":
        content += latexfile_command('description', description)
    for question in category.get_question():
        content += latexfile_append_question(question)
    return latexfile_environement('category', content, category.get_name())

def latexfile_document(category):
    import_latextomoodle()
    content = latexfile_preamble([LATEX_PACKAGE_NAME])
    content += latexfile_environement('document', latexfile_append_category(category))
    return content
    
def import_latextomoodle():
    # Importing a local template : idea taken from 
    # https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
    import pkgutil, io
    if not os.path.isfile('latextomoodle.sty') :
        string = pkgutil.get_data("moodlexport", "templates/latextomoodle.sty").decode()
        savestr(string, 'latextomoodle.sty')
    
