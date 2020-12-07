# moodlexport

This Python module provides code which allows to easily generate families of questions (called *categories* in Moodle) that can be directly exported from either Python or Latex to Moodle, and use them to create a test. The main motivation behind this module is that : 
- it is easier to define mathematical objects in Python than Moodle
- it is more comfortable to type maths in Latex
- generating random problems is simpler in Python and can go way beyond what Moodle proposes
- it is easier to store/manipulate locally a Latex or Python file than doing it on the Moodle interface. It also simplifies collaborating projects.

It can be installed with a pip command : `pip install moodlexport`

Some internal links within this documentation:
- [Main features of this module so far](#Main-features-of-this-module-so-far)
- [Quick start](#Quick-start)
    - [Simple examples from Python](#Simple-examples-from-Python)
    - [Simple examples from Latex](#Simple-examples-from-Latex)
    - [Exporting many questions at once](#Exporting-many-questions-at-once)
- [Documentation](#Documentation)
    - [Main commands from Python](#Main-commands-from-Python)
    - [Main commands from Latex](#Main-commands-from-Latex)
- [Changelog](#Changelog)
- [Known issues/missing features](#Known-issues/missing-features)




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

## Documentation

### Main commands from Python

#### The Category Class

`category = Category(string)` creates an object of class Category. `string` here specifies the name of the category, which will appear in Moodle. It comes with a few methods:

- `category.savexml(string)` creates an XML file under the XML Moodle format, ready to import within Moodle. The name of the file is the name of the category by default. If a `string` is given, the name of the file will be `string.xml`.
- `category.savetex(string)` creates a TEX file, containing all the questions of the category, nicely displayed. The name of the file is the name of the category by default (spaces and underscores will be replaced with `-`). If a `string` is given, the name of the file will be `string.tex`.
- `category.savepdf(string)` creates a TEX file as above and then compiles it to generated a PDF file.
- `category.description(string)` Adds a description to the category, which will appear in Moodle.

#### The Question Class

`question = Question(type)` creates an object of class Question. The `type` of the question can be `essay` (default) or `multichoice`. It comes with a family of methods `question.OPTION(value)` where `OPTION` describes every possible option that you can set in Moodle. The most important ones are:

- `question.title(string)` sets the title of the question
- `question.text(string)` sets the text (main body) of the question
- `question.grade(float)` sets the grade of the quesiton
- `question.graderinfo(string)` sets the information to be given to the grader
- `question.addto(category)` adds the question to a `category`

Methods specific to the `essay` type (answer via a text editor):
- `question.responseformat(string)` : `editorfilepicker` lets the student upload a file as an answer (default) , `editor` forbids it.
- `question.responserequired(bool)` : `0` if no response is required (default), `1` if a response is required.

Methods specific to the `multichoice` type (finite number of possible answers):
- `question.answer(string, value)` : Adds a possible answer to the question. `string` is the text of the answer, `value` describes if this answer is correct or no. It can be described in two ways:
    - as a boolean `True` or `False` (default)
    - as a percentage (integer between 0 and 100), which represents the fraction of the grade attributed to the answer. This is typically used for questions with more than 2 answers. A unique true answer has 100, a wrong answer has 0 (default)
- `question.single(value)` : `true` if only one answer is possible (default), `false` if more than one answer can be selected by the student.

#### Misc.

Inserting an image: to do so, use the `includegraphics` function:

```python
from moodlexport import includegraphics

text = 'here is a cool image:' + includegraphics("./some_folder/my_image.png", width=256, height=128)

question = Question()
question.text(text)
```

Options:
- `width` and `height` (integer). Modify the size of the image, in pixels. If no argument is passed, the image is displayed in its original shape.
- `style` (string). Two possible values:
    * `"centered"` (default). The image is displayed in a new line and centered.
    * `"inline"`. The image is displayed next to the text.

### Main commands from Latex

It is possible to use a similar syntax within a TEX document :

- `\begin{category}[name] ... \end{category}` defines the  environment corresponding to a category. It is possible to write various categories within the same document. `name` is the name of the category.
- `\begin{question}[type] ... \end{question}` defines the  environment corresponding to a question. It is possible to write various question within the same category. `type` is the type of the question, `essay` by default.
- All the methods mentioned above can be used in latex. The analogue of `.OPTION(value)` becomes `\OPTION{value}` in Latex (and must be placed within the corresponding environment). For instance :
    - `\description{string}` sets the description of a category
    - `\grade{float}` sets the grade of a question
    - `\answer[value]{string}` adds an answer to a multichoice question
- Inserting images is done with the command `\includegraphics[width=256px, height=128px]{./some_folder/my_image.png}` from the package `graphicx`
    * for the options `width` and `height` the only supported unit is `px`
    * the option `scale` is not supported
    * if the command `\includegraphics` is called within an environment `\begin{center} ... \end{center}`, the image will be centered as well in Moodle. If not it will be displayed inline.

The corresponding latex package can be found in `moodlexport/moodlexport/templates`, should be [https://github.com/Guillaume-Garrigos/moodlexport/tree/master/moodlexport/templates](here).

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





## Changelog

- v.0.0.22
    - Add a new feature to insert images.
- v.0.0.21
    - The parser used to handle `$`'s was wayyy to slow. This is corrected now.
- v.0.0.20
    - I realized that depending on Moodle's version, or depending on how the administrator implements it, inline math like `$e^x$` can not be recognized. Moodle's doc [says](https://docs.moodle.org/3x/fr/Utilisation_de_la_notation_TeX) it is not supported. So, now, every inline math `$e^x$` is converted into `\(e^x\)` just before exporting the data into XML. This allows the user to painlessly type latex as usual with `$`'s.
    - Now TEX files are generated without spaces or `_` in the filename. Because latexmk wasn't happy when generating pdfs.
- v.0.0.19
    - Corrects bug #3 for multichoice questions, allowing now for negative grades for wrong answers. Proposed by [@Stivanification](https://github.com/Stivanification).
    - Corrects bug #2 caused by a broken backcompatibility from the TexSoup Module. Now this module requires the exact needed version

## Known issues/missing features
- for the latex package, there is issues with `newcommand` and `renewcommand` because for instance the document class `amsart` defines `text` but it is not the case for `article`.
- So far I have a bad time handling breaklines in a text written in python. Using explicit `<br/>` tags should do the job.
