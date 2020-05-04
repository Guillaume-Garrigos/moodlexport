# moodlexport

This Python module provides code which allows to easily generate families of questions (called *categories* in Moodle) that can be directly exported from either Python or Latex to Moodle, and use them to create a test. The main motivation behind this module is that : 
- it is easier to define mathematical objects in Python than Moodle
- it is more comfortable to type maths in Latex
- generating random problems is simpler in Python and can go way beyond what Moodle proposes
- it is easier to store/manipulate locally a Latex or Python file than doing it on the Moodle interface. It also simplifies collaborating projects.



### Simple examples from Python: 


```python
from moodlexport import Question

question = Question("essay")
question.text("What is the derivative of $f(x) = e^x + 0.5 \Vert x \Vert^2$?")
question.grade(1.5)
question.save("my first question")
              
question = Question("multichoice")
question.text("Is every symmetric matrix invertible?")
question.grade(2.0)
question.answer("Yes", False)
question.answer("No", True)
question.save("A multichoice question")
```

### Simple examples from Latex

You can produce the same result as above by defining your question directly in a Latex file. 
Suppose for isntance that you have a Latex file `myquestion.tex` containing one of the following : 

```latex
\documentclass{amsart}
\usepackage{latextomoodle}
\begin{document}
\begin{question}[essay]
What is the derivative of $f(x) = e^x + 0.5 \Vert x \Vert^2$?
\grade{1.5}
\end{question}
\end{document}
```

```latex
\documentclass{amsart}
\usepackage{latextomoodle}
\begin{document}
\begin{question}[multichoice]
Is every symmetric matrix invertible?
\answer[0]{Yes}
\answer[100]{No}
\grade{2.0}
\end{question}
\end{document}
```

Then you can convert this `myquestion.tex` file directly into a `readytoexport.xml` file, by using the following Python commands:

```python
from moodlexport import latextomoodle
latextomoodle('myquestion.tex','readytoexport')
```

Note that if you wish to compile the `.tex` file without errors, you will need to place the Latex package `latextomoodle.sty` in the same folder. This package can be found in the latex folder of this project.

### Exporting many questions at once

If you want to export more than one question, you might want to gather them within a category, which will produce a single file containing all those questions. Here is how to proceed:

In Python:

```python
from moodlexport import Question, Category

category = Category("My little catgory name")

question = Question("essay")
question.text("What is the derivative of $f(x) = e^x + 0.5 \Vert x \Vert^2$?")
question.grade(1.5)
question.addto(category)
              
question = Question("multichoice")
question.text("Is every symmetric matrix invertible?")
question.grade(2.0)
question.answer("Yes", False)
question.answer("No", True)
question.addto(category)

category.save()
```
In Latex, followed by the python command `latextomoodle('file_name.tex')` :

```latex
\documentclass{amsart}
\usepackage{latextomoodle}
\begin{document}
\begin{category}[My little catgory name]
\begin{question}[essay]
What is the derivative of $f(x) = e^x + 0.5 \Vert x \Vert^2$?
\grade{1.5}
\end{question}
\begin{question}[multichoice]
Is every symmetric matrix invertible?
\answer[0]{Yes}
\answer[100]{No}
\grade{2.0}
\end{question}
\end{category}
\end{document}
```

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
 
### Known issues/missing features :
- for multichoice we never check that the sum of the fractions is equal to 100% 
- for the latex package, there is issues with `newcommand` and `renewcommand` because for instance the document class `amsart` defines `text` but it is not the case for `article`.
