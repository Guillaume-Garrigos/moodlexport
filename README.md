# moodle_test_generator

The Jupyter Notebook `Moodle_generator` contains Python code which allows to easily generate families of questions (called *categories* in Moodle) that can be directly exported to Moodle and used to create a test. The main idea is that : 
- it is easier to define mathematical objects in Python than Moodle
- generating random problems is simpler in Python (Moodle provides a way to generate random number but it is quite a mess)

Features of this module so far :
- Creating a question. Supported classes of questions are:
    -  "essay" : the student answers in a white text box. Options are :
        - Possibility for the student to upload a file as an answer as well. 
    -  "multichoice" : the question comes with at least 2 possible answers. Options are :
        - Possibility to specify "multiple answers allowed" or "unique answer allowed"
- All the options available in Moodle are available here (defining a grade, information for the grader, feedback, etc)
- Creating a category (family) of questions
- Adding a question to a given category
- Export a category of questions under the format Moodle XML, which can be imported directly into Moodle.
- Supports Unicode éàê ...
- Supports Latex syntax : correctly supports inline latex with `$e^x$`, and equation with `$$ f(x) = \sum_i x_i^2 $$, \begin{equation*}...\end{equation*}, \begin{cases}` etc

Simple examples : 

```
category = Category("Questions for exam 2")
question = Question("essay") # new question
question.text("What is the derivative of $f(x) = e^x + 0.5 \Vert x \Vert^2$.") # question with latex
question.grade(1.5)
category.append(question) # adds the question to the category
category.save("my_category") # creates a dirty my_category.xml file ready to import in Moodle
```

```
category = Category("Question for exam 2")

```
 
Known issues/missing features :
- problem with the latex command \frac because \f in python strings means something. Could be fixed with custom unescape.
- Extract list of questions from a latex file. Would be useful to type a list of questions in Latex (in a itemize environment) and to feed it to Python.
- Extract list of questions from .txt file is doable online see https://vletools.herokuapp.com/info/help but their code is not shared...
- for multichoice we never check that the sum of the fractions is equal to 100% 
