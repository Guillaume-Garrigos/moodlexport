from moodlexport.python_to_latex import latexfile_document

from xml.dom.minidom import parseString
from xml.sax.saxutils import unescape
import xmltodict
#import json
import io
import numpy as np  # only for np.bool ... too bad :/

import os


####################################
## GLOBAL CONSTANTS 
####################################

# Dirty but needed : all the fields required to create a question
# We also set their default value, and an alias when the fields has a weird/toolong name
DICT_DEFAULT_QUESTION_MOODLE = { 
    # general stuff
    '@type': {'default': "essay", 
              'alias': 'type'
             }, # can be "multichoice" for MCQs
    "name": {'default': "Default question title", 
             'attribute': {'@format': 'txt'}, 
             'alias': 'title'
            },
    "questiontext": {'default': "Default question text", 
                     'attribute': {'@format': 'html'}, 
                     'alias': 'text'
                    },
    "generalfeedback": {'default': "", 'attribute': {'@format': 'html'}},
    "defaultgrade": {'default': 1.0, 
                     'alias': 'grade'
                    },
    "penalty": {'default': 0.0},
    "hidden": {'default': 0},
    "idnumber": {'default': ""},
    # 'essay' specifics
    "responseformat": {'default': "editorfilepicker"}, # by default allow to upload a file as answer. Set "editor" ottherwise
    "responserequired": {'default': 0}, # 0 for no response required, 1 for yes
    "responsefieldlines": {'default': 10},
    "attachments": {'default': -1}, # number of attachments allowed. -1 is infinty
    "attachmentsrequired": {'default': 0}, # 0 for no attachment required, 1 for yes
    "graderinfo": {'default': "", # correction for the grader
                   'attribute': {'@format': 'html'}, 
                   'alias': 'infocorrecteur'
                  }, 
    "responsetemplate": {'default': "", 'attribute': {'@format': 'html'}},
    # 'multichoice' specifics
    "single" : {'default': "true"}, # Says if only a unique answer is possible
    "shuffleanswers" : {'default': "true"}, # Constantly shuffles the possible choices
    "answernumbering" : {'default': "none"}, # Other choices : 'abc', '123', 'iii', and certainly caps
    "correctfeedback": {'default': "Votre réponse est correcte.", 'attribute': {'@format': 'html'}},
    "partiallycorrectfeedback": {'default': "Votre réponse est partiellement correcte.", 'attribute': {'@format': 'html'}},
    "incorrectfeedback": {'default': "Votre réponse est incorrecte.", 'attribute': {'@format': 'html'}},
    "shownumcorrect" : {'default': ""}, # No idea
    "answer" : {'default': ""} # We deal with this in the Answer class
}


# to deal with mess between Latex, python and xml special characters
# \u and \x not supported but useless for inline latex?
UNESCAPE_LATEX = { '\x07':'\\a', '\x0c':'\\f', '\x0b':'\\v', '\x08':'\\b', '\n': '\\n', '\r':'\\r', '\t':'\\t' } 


####################################
## STRING FUNCTIONS
####################################

def alias(field): # easy access to alias
    if 'alias' in DICT_DEFAULT_QUESTION_MOODLE[field]:
        return DICT_DEFAULT_QUESTION_MOODLE[field]['alias']
    else:
        return field

def isfield(string):
    for key in DICT_DEFAULT_QUESTION_MOODLE.keys():
        if string in [key, alias(key)]:
            return True
    return False

def cleanstr(string, raw=False):
    if raw:
        string = string.replace('\t','') # no tabs
        string = string.replace('\n','') # no linebreak
    else:
        string = string.replace('\t','  ') # double space instead of tabs
    return string

def savestr(string, filename="new.txt", raw=False):
    string = cleanstr(string, raw)
    text_file = io.open(filename, "w", encoding='utf8') # essential for accents and other characters
    text_file.write(string)
    text_file.close()

def latex_protect(string):
    return unescape(string, UNESCAPE_LATEX)
    
def html(string):
    if string is "":
        return string
    else:
        return "<![CDATA[<p>\(\)" + latex_protect(string) + "</p>]]>"  # \(\) pour activer latex dans Moodle

def set_oparg(name, default_value, **opargs): #optional argument manager
    if name in opargs:
        return opargs.get(name)
    else:
        return default_value

####################################
## CLASS : CATEGORY 
####################################

class Category():
    """ 
        Object collecting Questions under the form of a category, ready to export to Moodle.
        Methods:
        _set(name, description) : e.g. _set("my_category", "list of questions about ... ")
        append(question) : adds a Question to the Category
        save(file_name) : save the Category into Moodle-XML
    """
    def __init__(self, name="Default category name", description=""):
        self.dict = { "quiz": { "question": [{}] } }
        self.questions = self.dict["quiz"]["question"]
        self._set(name, description)
        self.question_objects = [] # will gather the objects themselves
    
    def _set(self, name="Default category name", description=""):
        qcat = {
            "@type": "category",
            "category": {"text": "$module$/top/" + name},
            "info": {"@format": "html", "text": html(description)}
            }
        self.questions[0] = qcat
        
    def name(self, string="Default category name"):
        self.questions[0]['category']['text'] = "$module$/top/" + string
        
    def description(self, string=""):
        self.questions[0]['info']['text'] = html(string)
        
    def getname(self):
        return self.questions[0]['category']['text'][len('$module$/top/'):] # removes the $module$/top/
        
    def getdescription(self):
        return self.questions[0]['info']['text']
        
    def append(self, question): # adds a Question to a Category
        self.questions.append(question.dict)
        self.question_objects.append(question)
                
    def save(self, file_name=None):
        """ Save a category under the format Moodle XML """
        if file_name is None:
            file_name = self.getname()
        category_xml = xmltodict.unparse(self.dict, pretty=True)
        savestr(unescape(category_xml), file_name + ".xml")
    
    def savetex(self, file_name=None):
        """ Save a category under the format TEX """
        if file_name is None:
            file_name = self.getname()
        savestr(python_to_latex.latexfile_document(self), file_name + ".tex")
       
    def savepdf(self, file_name=None):
        """ Save a category under the format PDF """
        if file_name is None:
            file_name = self.getname()
        if not os.path.isfile(file_name+'.tex'):
            self.savetex(file_name)
        os.system("latexmk -pdf "+file_name+".tex")
        os.system("latexmk -c "+file_name+".tex")
    


####################################
## CLASS : QUESTION 
####################################

class Question():
    """ 
        Object collecting the parameters of a question under the form of a dictionary.
        Methods:
        _set(field, value) : e.g. _set("questiontext", "What is $2+2$?")
    """
    def __init__(self, question_type="essay"):
        self.structure = DICT_DEFAULT_QUESTION_MOODLE # IMPORTANT
        # The proper question in a dictionary ready to turn into xml
        self.dict = {}
        for field in self.structure:
            self._set(field, self.structure[field]['default'])
        self._set('@type', question_type)
        self.answer_objects = []
        self.structure['answer']['value'] = []
               
    def _set(self, field, value=""):
        """ Assigns a value to a field of a Question """
        field_structure = self.structure[field]
        field_structure['value'] = value
        field_structure['isset'] = (value != self.structure[field]['default'])
        if 'attribute' not in field_structure: # no attributes, just stupid value to assign 
            self.dict[field] = value
        else: # we have attributes which means the field contains a <text> element
            if 'html' in field_structure['attribute'].values(): # the value is a string to be turned...
                value = html(value)                             # ... into a html string (tackles latex, <p>'s and stuff)
            # now we just fill the field with a text element, and its attributes
            self.dict[field] = {**field_structure['attribute'], **{"text": value}} # concatenation needs Python >= 3.5
    
    def multi_answer(self): # unlocks the multiple answer mode
        self.dict["single"] = "false" #TBA : check sum fractions is 100 or all 0 etc
        
    def addto(self, category):
        category.append(self)
    
    def save(self, optional_name="Default category name"): 
        # saves the question without category in a single file
        cat = Category(optional_name)
        cat.append(self)
        cat.save()
    
    def answer(self, answer_text="This is a default answer", grade=0):
        # appends an answer to the question. Calls the Answer class
        ans = Answer(answer_text, grade)
        ans.addto(self)
        self.structure['answer']['isset'] = True
        self.structure['answer']['value'].append({'text' : answer_text, 'grade': ans.dict['@fraction'] })

# Here we define automatically methods to assign values to Question fields

for key in DICT_DEFAULT_QUESTION_MOODLE.keys():
    if key is not "answer": #  could be misinterpreted with Question.dict["answer"]
        setattr(Question, alias(key), lambda self, value, key=key: self._set(key, value))
        setattr(Question, key, lambda self, value, key=key: self._set(key, value))


####################################
## CLASS : ANSWER 
####################################

class Answer():
    """ 
        Object collecting an answer to a multichoice Question
    """
    def __init__(self, answer_text="This is a default answer", grade=0):
        # we manage the default value of grade
        # grade can be either a int/float (percentage of the grade) or a bool (is the answer true or not)
        if isinstance(grade, bool) or isinstance(grade, np.bool):
            if grade:
                grade = 100
            else:
                grade = 0
        # otherwise it is a number we leave it as it is
        self.dict = {
            '@fraction': grade, # by default an answer is false, and gives no points
            '@format': 'html',
            'text': html(answer_text), # content of the answer
            'feedback': {
                '@format': 'html',
                'text': ""
            }
        }
    
    def text(self, text):
        self.dict['text'] = html(text)
        
    def feedback(self, text):
        self.dict['feedback']['text'] = html(text)
        
    def relativegrade(self, answer_fraction):
        self.dict['@fraction'] = answer_fraction # must be a number (int?) between 0 and 100, decribing how much it is worth
    
    def istrue(self): # Says that this answer is THE good one
        self.relativegrade(100)
        
    def isfalse(self): # Says that this answer is THE good one
        self.relativegrade(0)
        
    def addto(self, question): # includes the answer into a question
        """"""
        if question.dict['@type'] == "multichoice":
            if question.dict["answer"] == "": # if it is the first question we add
                question.dict["answer"] = []
            question.dict["answer"].append(self.dict)
            question.answer_objects.append(self)
        else:
            print('Error : answers can only be added to multichoice questions')
                     

####################################
## END
####################################










