# Documentation

*Go back to the [main page](../README.md)*


Table of contents of this documentation:
- [Main features of this module so far](#Main-features-of-this-module-so-far)
- [Quick start](#Quick-start)
    - [Simple examples from Python](#Simple-examples-from-Python)
    - [Simple examples from Latex](#Simple-examples-from-Latex)
    - [Exporting many questions at once](#Exporting-many-questions-at-once)
- [Advanced documentation](#Advanced-documentation)
    - [Main commands from Python](#Main-commands-from-Python)
    - [Main commands from Latex](#Main-commands-from-Latex)
    - [Miscellaneous](#Miscellaneous)
        - [Inserting an image](#Inserting-an-image)
        - [Turning variables into Latex](#Turning-variables-into-Latex)
        




## Main features of this module so far
- Creating a question. The only supported classes of questions are:
    -  "essay" : the student answers in a white text box.
    -  "multichoice" : the question comes with at least 2 possible answers.
- All the options available in Moodle are available here (defining a grade, information for the grader, feedback, etc). See more details below.
- Creating a category (family) of questions.
- Supports Unicode within python and latex : éàê ...
- Supports Latex syntax, whether you write from latex or python, in way that Moodle understands. Supports inline latex with `$e^x$`, `\(e^x\)`, and equation with `$$ f(x) = \sum_i x_i^2 $$, \begin{equation*}...\end{equation*}, \begin{cases}` etc
- Supports export to Moodle via a XML MOODLE file, but also to .tex and .pdf files (which allow more easily to see what you are doing)
- Supports inserting images

## Quick start

### Simple examples from Python: 


```python
from moodlexport import Question

question = Question("essay")
question.text("What is the derivative of $f(x) = e^x + 0.5 \Vert x \Vert^2$?")
question.grade(1.5)
question.save("my first question")
```

### Simple examples from Latex

You can produce the same result as above by defining your question directly in a Latex file. 
Suppose for isntance that you have a Latex file `myquestion.tex` containing the following : 

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

Then you can convert this `myquestion.tex` file directly into a `readytoexport.xml` file, by using the following Python commands:

```python
from moodlexport import latextomoodle
latextomoodle('myquestion.tex','my first question')
```

Note that if you wish to compile the `.tex` file without errors, you will need to place the Latex package `latextomoodle.sty` in the same folder. This package can be found in `moodlexport/templates`

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

## Advanced documentation

### Main commands from Python

#### The Category Class

`category = Category(string)` creates an object of class Category. `string` here specifies the name of the category, which will appear in Moodle. It comes with a few methods:

- `category.savexml(string)` creates an XML file under the XML Moodle format, ready to import within Moodle. The name of the file is the name of the category by default. If a `string` is given, the name of the file will be `string.xml`.
- `category.savetex(string)` creates a TEX file, containing all the questions of the category, nicely displayed. The name of the file is the name of the category by default (spaces and underscores will be replaced with `-`). If a `string` is given, the name of the file will be `string.tex`.
- `category.savepdf(string)` creates a TEX file as above and then compiles it to generated a PDF file.
- `category.description(string)` Adds a description to the category, which will appear in Moodle.
- `category.path(string)` by default the category is imported at the root of the class. But you might want to order your categories with a tree structure (Moodle allows for subacategories). For instance `category.path("Default/main category/subcategory12/)` will ensure that after import you category will be a subcategory of `subcategory12`. Pay attention to the final `"/"`!

#### The Question Class

`question = Question(type)` creates an object of class Question. The `type` of the question can be `essay` (default) or `multichoice`. It comes with a family of methods `question.OPTION(value)` where `OPTION` describes every possible option that you can set in Moodle. The most important ones are:

- `question.title(string)` sets the title of the question
- `question.text(string)` sets the text (main body) of the question
- `question.grade(float)` sets the grade of the quesiton
- `question.graderinfo(string)` sets the information to be given to the grader
- `question.addto(category)` adds the question to a `category`

Methods specific to the `essay` type (answer via a text editor):
- `question.responseformat(string)` : 
  - `editorfilepicker` the student can upload a file as an answer or type in the textbox (default) 
  - `editor` the student can only use the textbox, upload of a file is unavailable
  - `noinline` the textbox is unavailable, upload of a file is mandatory
- `question.responserequired(bool)` : `0` if no response is required (default), `1` if a response is required.
Methods specific to the `essay` type (answer via a text editor):
- `question.responseformat(string)` : `editorfilepicker` lets the student upload a file as an answer (default) , `editor` forbids it, `noinline` gets rid of the text box and forces the student to upload at least a file
- `question.responserequired(bool)` : `0` if no response is required (default), `1` if a response is required.
- `question.attachments(int)`: lets the student upload at most `int` files.
- `question.attachmentsrequired(int)`: student must upload at most `int` files.

Methods specific to the `multichoice` type (finite number of possible answers):
- `question.answer(string, value)` : Adds a possible answer to the question. `string` is the text of the answer, `value` describes if this answer is correct or no. It can be described in two ways:
    - as a boolean `True` or `False` (default)
    - as a percentage (integer between 0 and 100), which represents the fraction of the grade attributed to the answer. This is typically used for questions with more than 2 answers. A unique true answer has 100, a wrong answer has 0 (default)
- `question.single(value)` : `true` if only one answer is possible (default), `false` if more than one answer can be selected by the student.



### Main commands from Latex

It is possible to use a similar syntax within a TEX document :

- `\begin{category}[name] ... \end{category}` defines the  environment corresponding to a category. It is possible to write various categories within the same document. `name` is the (optional) name of the category.
    - `\description{string}` and `\path{string}` are commands working similarly to their python counterpart.
- `\begin{question}[type] ... \end{question}` defines the  environment corresponding to a question. It is possible to write various question within the same category. `type` is the type of the question, `essay` by default.
- All the methods mentioned in the Python section can be used in latex. The analogue of `.OPTION(value)` becomes `\OPTION{value}` in Latex (and must be placed within the corresponding environment). For instance :
    - `\description{string}` sets the description of a category
    - `\grade{float}` sets the grade of a question
    - `\answer[value]{string}` adds an answer to a multichoice question


The corresponding latex package can be found in `moodlexport/moodlexport/templates`, should be [here](https://github.com/Guillaume-Garrigos/moodlexport/tree/master/moodlexport/templates).

To convert a .tex file into an .xml, use

```python
from moodlexport import latextomoodle
latextomoodle('file_name.tex')
```

You can also import the contents of your .tex file directly into python (you might want to do some modifications before exporting to Moodle). You .tex file must contain one or more categories of questions. To do so, use : 

```python
from moodlexport import latextopython
# it outputs a list of Category objects, even if you have only one category.
list_of_categories = latextopython('file_name.tex') 
```



### Miscellaneous

#### Inserting an image

From latex, the command `includegraphics` is supported. More exactly you can use a command like `\includegraphics[width=256px, height=128px]{./some_folder/my_image.png}` from the package `graphicx`
- for the options `width` and `height`, the only supported unit is `px`
- the option `scale` is not supported
- if the command `\includegraphics` is called inline then it will be displayed inline in Moodle as well.
- if the command is called in an environment `\begin{center} ... \end{center}`, the image will be centered as well in Moodle.
- no other environments controlling the position of the image is supported for now.

From python, the `moodlexport` module provides you with a `includegraphics` function, whose api is as close as possible to the Latex one:

```python
from moodlexport import includegraphics

text = 'here is a cool image:' + includegraphics("./some_folder/my_image.png", width=256, height=128)

question = Question()
question.text(text)
```

Options of this `includegraphics` python function:
- `width` and `height` (integer). Modify the size of the image, in pixels. If no argument is passed, the image is displayed in its original shape.
- `style` (string). Two possible values:
    * `"centered"` (default). The image is displayed in a new line and centered.
    * `"inline"`. The image is displayed next to the text.

#### Turning variables into Latex

When generating questions from python you will end up with mathematical objects (real number, vector, matrix, etc) that you want to use in your question or answer. This means that at some point you will need to convert those objects into a string, that can eventually be rendered as a Latex expression by Moodle's MathJax feature.

The function [latexify](https://github.com/Guillaume-Garrigos/latexify) does exactly this for you. Note that it is part of `moodlexport`'s dependencies, so you likely have this module already installed in your environment.