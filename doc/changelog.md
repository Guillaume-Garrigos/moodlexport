
# Changelog

*Go back to the [main page](../README.md)*

- v.0.0.32 Implements the option `path` for categories for Latex->Moodle conversion.
- v.0.0.30
    - Solves a bug for Latex->Moodle conversion with multichoice question. The text of the question was being erased by the text of the answers.
    - Make the feedback(s) appear on the .pdf documents, when provided. Proposed by [@jcerezochem](https://github.com/jcerezochem) in issue #10
    - Updates in the documentation. Proposed by [@theresiavr](https://github.com/theresiavr) in issue #13 
- v.0.0.25 Solves two bugs for multichoice questions from issue #6, with code from [@Stivanification](https://github.com/Stivanification)
- v.0.0.24 Solves issue #5
- v.0.0.23 Forgot to load some modules. [PR](https://github.com/Guillaume-Garrigos/moodlexport/pull/4) from [@gregnordin](https://github.com/gregnordin)
- v.0.0.22 Add a new feature to insert images.
- v.0.0.21 The parser used to handle `$`'s was wayyy to slow. This is corrected now.
- v.0.0.20
    - I realized that depending on Moodle's version, or depending on how the administrator implements it, inline math like `$e^x$` can not be recognized. Moodle's doc [says](https://docs.moodle.org/3x/fr/Utilisation_de_la_notation_TeX) it is not supported. So, now, every inline math `$e^x$` is converted into `\(e^x\)` just before exporting the data into XML. This allows the user to painlessly type latex as usual with `$`'s.
    - Now TEX files are generated without spaces or `_` in the filename. Because latexmk wasn't happy when generating pdfs.
- v.0.0.19
    - Corrects bug #3 for multichoice questions, allowing now for negative grades for wrong answers. Proposed by [@Stivanification](https://github.com/Stivanification).
    - Corrects bug #2 caused by a broken backcompatibility from the TexSoup Module. Now this module requires the exact needed version
