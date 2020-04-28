# moodle_test_generator

Python function to easily generate files that Moodle can use to create a test.

Features so far :
- Creating a question
- Creating a category of questions
- Adding a question to a given category
- Export a category of questions under the format Moodle XML, which can be imported directly into Moodle.
- Supports Unicode éàê ...

How to use : 
```
category = Category("ma super catégorie")
question = Question(" Calculer la dérivée de $f(x) = e^x + \frac{1}{2} \Vert x \Vert^2$.")
question._set("graderinfo", "$e^x + x$") # optional
category.append(question) # ajoute la question à la catégorie
category.save("ma_categorie") # crée un fichier déguelasse mais prêt à l'export dans Moodle
```
 
To do:
- Support other kinds of questions than "composition". Like QCM or other stuff
- Extract list of questions from a latex file
- Import/export of the test itself? See https://www.youtube.com/watch?v=0D6uNCXk_MQ
- Extract data from .txt see https://vletools.herokuapp.com/info/help
