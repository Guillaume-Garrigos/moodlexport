
from xml.sax.saxutils import unescape
import xmltodict
import numpy as np  # only for np.bool ... too bad :/
import copy
import os

from moodlexport.string_manager import dict_default_question_moodle, set_oparg
import moodlexport.string_manager as strtools

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
    def __init__(self, name=None):
        self.structure = {
            "name" : "",
            "description" : "",
            "path" : "",
            "question" : []}
        self.name(set_oparg(name, "Default-category-name"))
        self.dict = {}
        
    def name(self, string="Default-category-name"):
        self.structure['name'] = string
        
    def description(self, string=""):
        self.structure['description'] = string
        
    def path(self, string=""): 
        if len(string) > 0:
            if string[-1] == "/":
                self.structure['path'] = string
            else:
                raise ValueError("The path for a Category must end with a /")
                
    def get_question(self, number=None):
        if number is None:
            return self.structure['question']
        else: # we assume it is an integer
            return self.structure['question'][number]
        
    def get_name(self):
        return self.structure['name']
        
    def get_description(self):
        return self.structure['description']
        
    def get_path(self):
        return self.structure['path']
        
    def append(self, question): # adds a Question to a Category
        question.addto(self)
    
    def compilation(self): # extract all the questions the Category contains, and puts it in a dict
        question_init = {
            "@type": "category",
            "category": {"text": "$module$/top/" + self.get_path() + self.get_name() },
            "info": {"@format": "html", "text": strtools.html(self.get_description())}
        }
        self.dict = { "quiz": {"question": [question_init] } }
        for question in self.structure['question']:
            # compiler la question ici pour créer question.dict a partir de sa structure ?
            question.compilation()
            self.dict['quiz']['question'].append(question.dict)
                
    def savexml(self, file_name=None):
        """ Save a category under the format Moodle XML """
        self.compilation()
        if file_name is None:
            file_name = self.get_name()
        category_xml = xmltodict.unparse(self.dict, pretty=True)
        strtools.savestr(unescape(category_xml), file_name + ".xml")
        
    def save(self, file_name=None): #deprecated?
        self.savexml(file_name)
    
    def savetex(self, file_name=None):
        """ Save a category under the format TEX """
        import moodlexport.python_to_latex # SO ANNOYING CIRCULAR IMPORT
        self.compilation()
        if file_name is None:
            file_name = self.get_name()
        string = moodlexport.python_to_latex.latexfile_document(self)
        string = strtools.html_to_latex(string) # we clean the file from all the html tags
        strtools.savestr(string, file_name.replace(' ','-').replace('_','-') + ".tex")
       
    def savepdf(self, file_name=None):
        """ Save a category under the format PDF """
        if file_name is None:
            file_name = self.get_name()
        file_name = file_name.replace(' ','-').replace('_','-')
        self.savetex(file_name)
        import moodlexport.python_to_latex
        moodlexport.python_to_latex.import_latextomoodle()
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
    def __init__(self, question_type=None):
        question_type = set_oparg(question_type, "essay")
        self.structure = copy.deepcopy(dict_default_question_moodle()) # Need deep otherwise mess
        self.dict = {} # The proper question in a dictionary ready to turn into xml
        for field in self.structure:
            self._set(field, self.structure[field]['default'])
        self._set('@type', question_type)
               
    def _set(self, field, value=None):
        """ Assigns a value to a field of a Question. It is stored in both .structure and .dict """
        value = set_oparg(value, "")
        field_structure = self.structure[field]
        field_structure['value'] = value
        field_structure['isset'] = (value != self.structure[field]['default'])
        if 'attribute' not in field_structure: # no attributes, just stupid value to assign 
            self.dict[field] = value
        else: # we have attributes which means the field contains a <text> element
            if 'html' in field_structure['attribute'].values(): # the value is a string to be turned...
                value = strtools.html(value)                             # ... into a html string (tackles latex, <p>'s and stuff)
            # now we just fill the field with a text element, and its attributes
            self.dict[field] = {**field_structure['attribute'], **{"text": value}} # concatenation needs Python >= 3.5
    
    def multi_answer(self): # unlocks the multiple answer mode
        self.dict["single"] = "false" 
        
    def has_answer(self):
        return (self.get_type() == "multichoice") and self.structure['answer']['isset']
    
    def cumulated_grade_correct(self): # sums the fractions of grade of correct answers
        if self.structure['answer']['isset']:
            s = 0
            for answer in self.structure['answer']['list']:
                if answer.structure['relativegrade'] > 0:
                    s += answer.structure['relativegrade']
            return s
        else:
            return 100
        
    def addto(self, category):
        self.compilation()
        category.structure['question'].append(self)
        
    def compilation(self):
        # aussi vérifier que la somme des answer vaut 100 et passer l'option du multiquestion si necessaire?
        if self.has_answer(): # if there are answers
            self.dict["answer"] = [] # instead of "" so far. Also reboots the dict if we did changes
            for answer in self.structure["answer"]["list"]:
                answer.compilation() # refresh the Answer.dict after eventual changes on Answer.structure
                self.dict["answer"].append(answer.dict)
                if answer.structure['relativegrade'] != 0 and answer.structure['relativegrade'] != 100: # we have multiple solutions
                    self._set('single', 'false')
                if self.cumulated_grade_correct() != 100:
                    raise ValueError('In a multichoice Question, the sum of the relative grades/percentages of the correct answers must be exactly 100, but here is '+str(self.cumulated_grade_correct()))
                
    
    def save(self, optional_name="Default-category-name"): 
        # saves the question without category in a single file
        cat = Category(optional_name)
        self.addto(cat)
        cat.save()
    
    def answer(self, answer_text="This is a default answer", grade=0):
        # appends an answer to the question. Calls the Answer class
        ans = Answer(answer_text, grade)
        ans.addto(self)
        #self.structure['answer']['value'].append({'text' : answer_text, 'grade': ans.dict['@fraction'] })
    
    def get_answer(self, number=None): # give access
        if self.has_answer():
            if number is None:
                return self.structure['answer']['list']
            else:
                return self.structure['answer']['list'][number]
        else:
            raise ValueError('This Question has no Answer')

# Here we define automatically methods to assign values to Question fields
for key in dict_default_question_moodle().keys():
    if key is not "answer": #  could be misinterpreted with Question.dict["answer"]
        setattr(Question, strtools.alias(key), lambda self, value, key=key: self._set(key, value))
        setattr(Question, key, lambda self, value, key=key: self._set(key, value))

# Here we define automatically methods to get values from Question fields
for key in dict_default_question_moodle().keys():
    if key is not "answer": #  could be misinterpreted with Question.dict["answer"]
        setattr(Question, "get_"+strtools.alias(key), lambda self, key=key: self.structure[key]['value'] )
        setattr(Question, "get_"+key, lambda self, key=key: self.structure[key]['value'] )

####################################
## CLASS : ANSWER 
####################################

class Answer():
    """ 
        Object collecting an answer to a multichoice Question
    """
    def __init__(self, answer_text="This is a default answer", grade=0):
        grade = bool_to_grade(grade) #defined below
        self.structure = {
            'text' : answer_text,
            'relativegrade' : grade,
            'feedback' : "" 
        }
        self.dict = {}

# SET FIELDS     
    def text(self, text):
        self.structure['text'] = text
        
    def relativegrade(self, grade):# must be a number (int?) between -100 and 100, decribing how much it is worth. Or a bool.
        grade = bool_to_grade(grade)
        self.structure['relativegrade'] = bool_to_grade(grade) 
        
    def feedback(self, text):
        self.structure['feedback'] = text
    
    def istrue(self): # Says that this answer is THE good one
        self.relativegrade(100)
        
    def isfalse(self): # Says that this answer is not good
        self.relativegrade(0)

# GET FIELDS         
    def get_text(self):
        return self.structure['text']
    
    def get_relativegrade(self):
        return self.structure['relativegrade']
    
    def get_feedback(self):
        return self.structure['feedback']
    
# OTHER METHODS
    def compilation(self): # prepares the answer by creating a dict
        self.dict = {
            '@fraction': self.structure['relativegrade'],
            '@format': 'html',
            'text': strtools.html(self.structure['text']),
            'feedback': {
                '@format': 'html',
                'text': strtools.html(self.structure['feedback'])
            }
        }
        
    def addto(self, question): # includes the answer into a question, do some checks before.
        self.compilation()
        if question.structure['@type']['value'] != "multichoice":
            raise ValueError("Answers can only be added to a Question of type : multichoice. This can be set with the method Question.type('multichoice')")
        else:
            question.structure["answer"]["isset"] = True
            question.structure["answer"]["list"].append(self)
            if question.cumulated_grade_correct() > 100:
                raise ValueError("In this Question the sum of relative grades/percentages of the correct answers appears to be >100.")

# NEEDED FUNCTIONS
def bool_to_grade(grade):
    # we manage the default value of grade
    # grade can be either a int/float (percentage of the grade) or a bool (is the answer true or not)
    if isinstance(grade, bool) or isinstance(grade, np.bool):
        if grade:
            return 100
        else:
            return 0
    else: # it is already an integer (we hope so)
        grade = int(grade)
        if grade > 100 or grade < -100:
            raise ValueError('For an answer, the (relative) grade must be a number between -100 and 100, representing the percentage of points gained/lost by marking it as correct.')
        else:
            return grade

####################################
## END
####################################










