from moodlequestion.python_to_moodle import *
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
                        Answer(content.args[0].value, False).addto(question)
                    elif len(content.args) == 2: # optional value for grade percentage
                        Answer(content.args[1].value, content.args[0].value).addto(question)
                else: # general field, easy to manage
                    value = content.string # a string containing the value of the said option
                    getattr(question, field)(value)
            else: # annoying, certainly valid latex, most RISKY part of the code
                text = text + str(content)
    question.text(cleanstr(text, raw=True))
    return question

def read_latex_category(category_latex):
    category = Category()
    # we read all the contents and puts it in the structure
    for content in list(category_latex.contents):
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
    for category_latex in category_latex_list:
        category_list.append(read_latex_category(category_latex))
    return category_list

def latextomoodle(file_name):
    # converts a latex file into an XML file ready to export into Moodle
    category_list = latextopython(file_name)
    for category in category_list:
        category.save()

















