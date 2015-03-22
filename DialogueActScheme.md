The TBED (Transformation-Based Error-Driven Parser) parser aka TBL parser produces semantic annotation in form of frames and slots.

# Dialogue Act Scheme #

The CUED dialogue act scheme is frame and slot based semantics. Each dialogue act is composed of a dialogue act type and several slots. The dialogue acts are allowed to be without slots. Examples of dialogue acts are provided below:

```
i want to drink wine <=> inform(drinks=wine)
near the castle <=> inform(near=Castle)
serves beer <=> inform(drinks=beer)
does not serve wine <=> inform(drinks!=wine)
serves no wine <=> inform(drinks!=wine)
serves no beer <=> inform(drinks!=beer)
restaurant which serves wine <=> inform(type=restaurant,drinks=wine)
does serve wine serves not beer <=> inform(drinks=wine,drinks!=beer)
it is not near castle and serve wine <=> inform(near!=Castle,drinks=wine)
restaurant near the castle <=> inform(near=Castle,type=restaurant)
somewhere not near the castle <=> inform(near!=Castle)

do they serve draft beer <=> confirm(drinks=beer)
is it somewhere near castle <=> confirm(near=Castle)
is it near castle <=> confirm(near=Castle)
is it near fountain <=> confirm(near="Fountain Inn")

can i get phone number please <=> request(phone)
can I get address and phone of the fountain inn <=> request(address,phone,name="Fountain Inn")
```

Above you can see training data which you can feed into the TBL parser. There is one training example on each line. The utterance and the semantics are separated by the string "<=>". The semantics is composed of the goal and several slots. Each slot is composed of of the slot name, the equal sign and the slot value. The goal, the slot name, and the slot value are domain dependant. The parser is capable to use arbitrary number of goals, slot names and slot values. Only the equal sign is limited to "=" and "!=".

Based on this data, the TBL parser tries to learn a sequence of transformation rules which iteratively correct the initial semantics.

# Details #

More details about the parser how the parsing works can be found in [this article - draft](http://tbed-parser.googlecode.com/svn/trunk/doc/paper-1/is2008.pdf) (PDF).

# Next #

[How to use the parser](HowToUseTheParser.md)