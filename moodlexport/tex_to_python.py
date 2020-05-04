from moodlexport.python_to_moodle import *

from TexSoup import TexSoup
from TexSoup.data import TexNode
from TexSoup.utils import TokenWithPosition

# Given a latex question, returns a python question
# we have to parse a lot here, and the parser isn't super smart so the code is a bit messy
def read_latex_question(latex_question):
    if len(latex_question.args) == 1: # we got a optional argument for the type of question
        question = Question(latex_question.args[0].value)
        list_contents = list(latex_question.contents)[1:] # we skip the 1st content which should be option
    else:
        question = Question()
        list_contents = list(latex_question.contents)
    text = ""
    # we read all the contents and puts it in the structure
    for content in list_contents:
        # we check the type of the content : either a parameter or the main text
        if isinstance(content, TokenWithPosition): # main field
            text = text + content.text
        elif isinstance(content, TexNode): # optional parameter but careful because math is treated as TexNode...
            field = content.name # a string giving us the name of the option
            if isfield(field): # is it a field defined in DICT_DEFAULT_QUESTION_MOODLE ?
                if field == 'answer': # cas un peu compliqué
                    if len(content.args) == 1: # pas d'option donc faux par défaut
                        question.answer(content.args[0].value, False)
                    elif len(content.args) == 2: # optional value for grade percentage
                        question.answer(content.args[1].value, content.args[0].value)
                else: # general field, easy to manage
                    value = content.string # a string containing the value of the said option
                    getattr(question, field)(value)
            else: # annoying, certainly valid latex, most RISKY part of the code
                text = text + str(content)
    question.text(cleanstr(text, raw=True))
    return question

def read_latex_category(category_latex):
    if len(category_latex.args) == 1: # we got a optional argument for category name
        category = Category(category_latex.args[0].value)
        list_contents = list(category_latex.contents)[1:] # we skip the 1st content which should be option
    else:
        category = Category()
        list_contents = list(category_latex.contents)
    # we read all the contents and puts it in the structure
    for content in list_contents:
        if isinstance(content, TexNode): # There should be just stuff like that
            field = str(content.name) # a string giving us the name of the option
            if field == 'name': # not is for some dark reason. same content, but not identity
                category.name(content.string)
            elif field == 'description':
                category.description(content.string)
            elif field == 'question':
                question = read_latex_question(content)
                question.addto(category)
    return category

def latextopython(file_name):
    # converts a latex file into a list of Category
    with open(file_name, 'r', encoding='utf-8') as file:
        latex = file.read()
    soup = TexSoup(latex)
    category_list = []
    category_latex_list = list(soup.find_all('category'))
    if len(category_latex_list) > 0: # we list the categories and return them
        for category_latex in category_latex_list:
            category_list.append(read_latex_category(category_latex))
    else: # well at least we hope to find questions so we create a dummy category
        category = Category()
        question_latex_list = list(soup.find_all('question'))
        for question_latex in question_latex_list:
            read_latex_question(question_latex).addto(category)
        category_list = [category,]
    return category_list

def latextomoodle(file_name, save_name = None):
    # converts a latex file into an XML file ready to export into Moodle
    category_list = latextopython(file_name)
    counter = 1
    for category in category_list:
        if save_name is None:
            category.save()
        else:
            if len(category_list) == 1:
                string = save_name
            else:
                string = save_name + '_' + str(counter)  
                counter = counter + 1              
            category.save(string)

















