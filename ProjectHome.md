The Transformation-based Learning (TBL) parser implements a parser which competes with the HVS and EHVS parsers developed for the CUED dialogue act scheme.

  * HVS - Spoken Language Understanding using the Hidden Vector State Model - http://mi.eng.cam.ac.uk/~sjy/papers/heyo06.pdf
  * [EHVS - Extended Hidden Vector State Parser](http://code.google.com/p/extended-hidden-vector-state-parser/)
  * [CUED - Dialogue Systems Group](http://mi.eng.cam.ac.uk/research/dialogue/)

More details about the parser can be found in the WIKI:

  1. [Introduction](Introduction.md)
  1. [Dialogue Act Scheme](DialogueActScheme.md)
  1. [How use the parser](HowToUseTheParser.md)
  1. [Configuration of the experiment](ConfigurationOfTheExperiment.md)

More details about the parser how the parsing works can be found in [this article](http://tbed-parser.googlecode.com/svn/trunk/doc/paper-1/is2008.pdf) (PDF) ([poster](http://tbed-parser.googlecode.com/svn/trunk/doc/paper-1/interspeech09-poster.pdf)).

**If you plan to use the [Extended Hidden Vector State Parser](http://code.google.com/p/extended-hidden-vector-state-parser/), I strongly suggest you to use this (TBL) parser.**
  * First, the TBL parser does not depend on GMTK which is not maintained any more.
  * Second, the TBL parser make use of the database with lexical realizations of slot values. This makes the parser more robust and accurate. One can argue that this is extra information but the true is that real dialogue systems knows what the available slot values are. And most of the time the slot value is its own lexical realization. For example, think of slot value "Fountain Inn". Its lexical realization is "fountain inn". However, it might be also "fountain" or "inn". The last two lexical realization must be added in the database. You can also think about the words "fountain" or "inn" as synonyms for "fountain inn".
  * Third, the TBL parser is much faster. This is even more important for the real-time dialogue systems.
  * Finally, the TBL parser provides state-of-the-art results.


---


&lt;wiki:gadget url="http://www.ohloh.net/projects/tbed-parser/widgets/project\_languages.xml" height="240" width="420" border="1" /&gt;
