This script induces Named Entity taggers for a given target language from 3 source languages using parallel data.
Currently we test 4 languages (English, German, Italian, Spanish), while more languages could be tested.

We develop two projection algorithms: (1)strict match projection algorithm for the aim of high precision; (2) upper-bound projection algorithm. 


# strict match algorithm
This approach considers at least two agreements among 3 source languages to determine the final tag for the target language. If that agreement is not reached, we apply a back-off strategy using the named entity tag obtained from computing the most frequent tag for that token in a large automatically annotated corpus.


## Corpora used:
* parallel corpora: [Europarl parallel corpora](http://www.statmt.org/europarl/index.html)
* back-off corpora: [wikiner corpora](https://hackage.haskell.org/package/chatter-0.9.1.0/docs/NLP-Corpora-WikiNer.html)


## Usage example:
```python strictMatch.py en```

You can also generate Named Entity taggers by replacing en with de for German , es for Spanish, it for Italian.

**en.tag** is the generated file.


# upper-bound algorithm
The approach aims at illustrating how well the system can perform. We run the strict match algorithm on the gold standard test data with the condition that all annotations in the 3 source languages coincide and without the back-off step.


## Corpora used:
* parallel corpora: Europarl NER Gold-Standard


## Usage example:
```python upperBound.py en```

You can also generate Named Entity taggers by replacing en with de for German , es for Spanish, it for Italian.

**en.tag** is the generated file.


