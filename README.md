# moodlexport

This Python module provides code which allows to easily generate families of questions (called *categories* in Moodle) that can be directly exported to Moodle and used to create a test. The main idea is that : 
- it is easier to define mathematical objects in Python than Moodle
- generating random problems is simpler in Python (Moodle provides a way to generate random number but it is quite a mess)

### Features of this module so far :
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

### Simple examples : 

```python
question = Question("essay")
question.text("What is the derivative of $f(x) = e^x + 0.5 \Vert x \Vert^2$?")
question.grade(1.5)
question.save("my first question")
```

```python
question = Question("multichoice")
question.text("Is every symmetric matrix invertible?")
question.grade(2.0)
question.answer("Yes", False)
question.answer("No", True)
question.save("A multichoice question")
```
 
Known issues/missing features :
- Extract list of questions from .txt file is doable online see https://vletools.herokuapp.com/info/help but their code is not shared...
- for multichoice we never check that the sum of the fractions is equal to 100% 
