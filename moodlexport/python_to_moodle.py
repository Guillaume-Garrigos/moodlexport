
from xml.sax.saxutils import unescape
import copy
import os
import logging

import xmltodict
import numpy as np  # only for np.bool ... too bad :/

from moodlexport.string_manager import dict_default_question_moodle, set_oparg
import moodlexport.string_manager as strtools

####################################
## CLASS : CATEGORY 
####################################

class Category():
    """ 
        Object collecting Questions under the form of a category, ready to export to Moodle.
        Object.dict is a dictionary containing the ifnormation which will be converted into XML
        Object.structure is an other dict, which contains the same information, but more (and we don't want
            this "more" to appear in the XML. For instance text and latex is not encoded/escaped the same 
            in .dict and .structure. For sure we could do better ...
        Methods:
        _set(name, description) : e.g. _set("my_category", "list of questions about ... ")
        append(question) : adds a Question to the Category
        save(file_name) : save the Category into Moodle-XML
    """
    def __init__(self, name=None, path=""):
        self.structure = {
            "name" : "",
            "description" : "",
            "path" : "",
            "question" : []}
        self.name(name)
        self.path(path)
        self.dict = {}
        
    def name(self, string=None):
        if string is None:
            string = "Unnamed category " + strtools.clock()
        self.structure['name'] = string
        
    def description(self, string=""):
        self.structure['description'] = string
        
    def path(self, string=""): 
        if len(string) > 0:
            if string[-1] == "/":
                self.structure['path'] = string
            else:
                raise ValueError("The path for a Category must end with '/' ")
        else:
            self.structure['path'] = ""
                
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
        file_name = strtools.filename_protect(file_name)
        category_xml = xmltodict.unparse(self.dict, pretty=True) # here all bools are converted to strings
        strtools.savestr(unescape(category_xml), file_name + ".xml")
        
    def save(self, file_name=None): #deprecated?
        self.savexml(file_name)
    
    def savetex(self, file_name=None):
        """ Save a category under the format TEX """
        import moodlexport.python_to_latex # SO ANNOYING CIRCULAR IMPORT
        self.compilation()
        if file_name is None:
            file_name = self.get_name()
        file_name = strtools.filename_protect(file_name)
        string = moodlexport.python_to_latex.latexfile_document(self)
        string = strtools.html_to_latex(string) # we clean the file from all the html tags
        strtools.savestr(string, file_name + ".tex")
       
    def savepdf(self, file_name=None):
        """ Save a category under the format PDF """
        if file_name is None:
            file_name = self.get_name()
        file_name = strtools.filename_protect(file_name)
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
            self._set(field, None) # None will trigger the default value
        self._set('@type', question_type)
               
    def _set(self, field, value=None):
        """ Assigns a value to a field of a Question. It is stored in both .structure and .dict """
        #value = set_oparg(value, "")
        field_structure = self.structure[field]
        if value is None: # this happens when creating a question with an empty dict
            value = self.structure[field]['default']
            field_structure['isset'] = False
        else:
            field_structure['isset'] = True
        # now 'value' has the good ... value
        field_structure['value'] = value
        if 'attribute' not in field_structure: # no attributes, just stupid value to assign 
            self.dict[field] = value
        else: # we have "attributes" which means the field contains a "<text>" element
            if 'html' in field_structure['attribute'].values(): # the value is a string to be turned...
                value = strtools.html(value)                    # ... into a html string (tackles latex, <p>'s and stuff)
            # now we just fill the field with a text element, and its attributes
            self.dict[field] = {**field_structure['attribute'], **{"text": value}} # concatenation needs Python >= 3.5
    
    def multi_answer(self): # unlocks the multiple answer mode
        self.dict["single"] = "false" 
        
    def has_answer(self):
        return (self.get_type() == "multichoice") and self.structure['answer']['isset']
    
    def cumulated_grade_correct(self): # sums the grades of *correct* answers
        if self.structure['answer']['isset']:
            s = 0.0
            for answer in self.structure['answer']['list']:
                if answer.structure['relativegrade'] > 0:
                    s += answer.structure['relativegrade']
            return s
        else:
            return 100.0
        
    def should_it_be_single_choice(self):
        # Given the grades of the answers, try to guess whether the question 
        # should be "single choice" or "multi choice".
        # returns a boolean
        # the default value is True (arbitrary choice but consistent with dict_default_question_moodle)
        if self.has_answer(): # if so we return True only if one of the grades is 100
            istheanswer100 = [int(ans.get_relativegrade()) == 100 for ans in self.get_answer()] # bunch of True/False
            return sum(istheanswer100) == 1 # True iff there is only one grade set to 100
        else:
            return True
        
        
    def addto(self, category):
        self.compilation()
        category.structure['question'].append(self)
        
    def compilation(self):
        """ This is where we put the Answers in the Question
            1. Collects all the Answers if any
            2. Check that the Answer's grades are okay
            3. Check that the 'single' parameter is set and compatible with the grades
            4. Check that the sum of positive grades is 100 (tolerance: 1e-3)    
        """
        tolerance = 1e-3
        if self.has_answer(): # if there are answers
            self.dict["answer"] = [] # instead of "" so far. Also reboots the dict if we did changes
            for answer in self.get_answer():
                answer.compilation() # refresh the Answer.dict after eventual changes on Answer.structure
                self.dict["answer"].append(answer.dict) # loads the answer.dict into the question.dict
                
            if not self.structure['single']['isset']: 
                # in that case we need to guess it
                self.single(self.should_it_be_single_choice()) # we give a bool, will be converted to string later in Category.savexml
            else: # in that case we just check nothing weird happens
                if self.get_single() and not self.should_it_be_single_choice():
                    raise ValueError("You have set the 'single' parameter to 'True', meaning that only one answer can be chosen. But it seems that you have more than one valid answers. Please make sure that this is what you want.")
                if not self.get_single() and self.should_it_be_single_choice():
                    logging.warning("You have set the 'single' parameter to 'False' for this Question, meaning that multiple answers can be chosen. But it seems that there is only one valid answer. Please make sure that this is what you want.")
                    
            if abs(self.cumulated_grade_correct() - 100) > tolerance: # makes sure that the sum of grades for good answers is roughly 100
                raise ValueError('In a multichoice Question, the sum of the relative grades/percentages of the correct answers must be 100 (within a tolerance of '+str(tolerance)+'), but it apprears to be '+str(self.cumulated_grade_correct()))
                
    
    def savexml(self, name=None):
        # saves the question without category in a single file
        if name is None:
            name = self.get_name()
        cat = Category(name)
        self.addto(cat)
        cat.savexml()
    
    def savetex(self, name=None):
        # saves the question without category in a single file
        if name is None:
            name = self.get_name()
        cat = Category(name)
        self.addto(cat)
        cat.savetex()
    
    def savepdf(self, name=None):
        # saves the question without category in a single file
        if name is None:
            name = self.get_name()
        cat = Category(name)
        self.addto(cat)
        cat.savepdf()
    
    def answer(self, answer_text="This is a default answer", grade=0):
        # appends an answer to the question. Calls the Answer class
        ans = Answer(answer_text, grade)
        ans.addto(self)
        #self.structure['answer']['value'].append({'text' : answer_text, 'grade': ans.dict['@fraction'] })
    
    def get_answer(self, number=None):
        if self.has_answer():
            if number is None:
                return self.structure['answer']['list']
            else:
                return self.structure['answer']['list'][number]
        else:
            raise ValueError('This Question has no Answer')
            
    def get_relativegrade(self, number=None): # collects the grades of the Answers
        if self.has_answer():
            if number is None:
                return [answer.get_relativegrade() for answer in self.get_answer()]
            else:
                return self.get_answer(number).get_relativegrade()
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
    def __init__(self, answer_text="This is a default answer", grade=0.0):
        self.structure = {
            'text' : answer_text,
            'relativegrade' : strtools.filter_grade(grade),
            'feedback' : "" 
        }
        self.dict = {}

# SET FIELDS     
    def text(self, text):
        self.structure['text'] = text
        
    def relativegrade(self, grade): # must be a number contained in the list 'ACCEPTED_GRADES' in string_manger.py, or a bool (see the doc).
        self.structure['relativegrade'] = strtools.filter_grade(grade) 
        
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
    def compilation(self): # prepares the Answer by creating a dict
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


####################################
## global functionalities
####################################

def gather_questions(name=None):
    # Dependency : COPY
    # Look for all the objects of the class Question ever created
    # and gather them in a Category
    # I'm not sure going through global variables is the best but it seems to work so far
    # Doesn't work if the questions are defined inside a loop so....
    category = Category(name)
    import __main__ # ok thats shameful but it works. So far. Seems fragile though
    current_vars = copy.copy(vars(__main__)) # gets the global variables where the questions should be
    question_list = []
    for stuff in current_vars.values(): # there is a huge bunch of stuff here
        if isinstance(stuff, Question):
            if stuff not in question_list:
                question_list.append(stuff)
                stuff.addto(category)
    return category

def no_category_name_warning():
    logging.warning("Beware, you are exporting some question(s) without specifying a name for the category gathering them. If you want to avoid a default name, you can simply pass an argument to this function, something like : name='the name of my category' ")

def savexml(name=None):
    if name is None:
        no_category_name_warning()
    gather_questions(name).savexml()

def savetex(name=None):
    if name is None:
        no_category_name_warning()
    gather_questions(name).savetex()

def savepdf(name=None):
    if name is None:
        no_category_name_warning()
    gather_questions(name).savepdf()







