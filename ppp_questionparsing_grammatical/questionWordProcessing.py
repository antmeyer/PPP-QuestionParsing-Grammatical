import sys
from .preprocessingMerge import Word
from .preprocessing import DependenciesTree

"""
    Taken from: http://www.interopia.com/education/all-question-words-in-english/
    Yes/no question
"""
closeQuestionWord = [
    'is', 'are', 'am', 'was', 'were', 'will', 'do', 'does', 'did', 'have', 'had', 'has', 'can', 'could', 'should', 'shall', 'may', 'might', 'would'
]

"""
    Open-ended questions
    + What... for, What... like, Why don't, Where from
    Rarely used: Wherefore, Whatever, Wherewith, Whither, Whence, However
"""
openQuestionWord = [
    'what', 'what kind', 'what type', 'what sort', 'what time', 'when', 'why', 'where', 'who', 'how', 'how much', 'how many', 'how old', 'how far', 'how long', 'how tall', 'how deep', 'how wide', 'how fast', 'how often', 'how come', 'which', 'whom', 'whose', 'how big'
]

def removeWord(t,word):
    """
        Remove word (of type str*int = word*position_in_sentence) in t
        Assume word has no child
    """
    if word in t.wordList:
        if not t.child:
            t.parent.child.remove(t) 
        else:
            sys.exit('exit: question word has child (please, report your sentence on http://goo.gl/EkgO5l)\n')
    else:
        for c in t.child:
            removeWord(c,word)

def firstWords(t,start):
    """
        Put the 2 first words of the sentence in start (list of size 2)
    """
    for n in t.wordList:
        if n.index == 1:
            start[0] = n
        elif n.index == 2:
            start[1] =n
    for c in t.child:
        firstWords(c,start)

def identifyQuestionWord(t):
    """
        Identify, remove (if open qw) and return the question word.
        If there is no question word, return None.
    """
    start = [None,None]
    firstWords(t,start)
    if not start[0]:
        sys.exit('exit: i don\'t understand (please, report your sentence on http://goo.gl/EkgO5l)')
    if start[1] and start[0].word.lower() + ' ' + start[1].word.lower() in openQuestionWord:
        removeWord(t,start[0])
        removeWord(t,start[1])
        return start[0].word.lower() + ' ' + start[1].word.lower()
    if start[0].word.lower() in openQuestionWord: 
        removeWord(t,start[0])
        return start[0].word.lower()
    if start[0].word.lower() in closeQuestionWord: 
        return start[0].word.lower()
    return None

questionInfo = {
    # how to add info into the son of ROOT
    'what type'     : 'type',
    'what sort'     : 'type',
    'what time'     : 'time',
    'when'          : 'date',
    'why'           : 'reason',
    'where'         : 'place',
    'how'           : 'manner',
    'how much'      : 'amount',
    'how many'      : 'quantity',
    'how old'       : 'age',
    'how far'       : 'distance',
    'how long'      : 'length',
    'how tall'      : 'height',
    'how deep'      : 'depth',
    'how wide'      : 'width',
    'how fast'      : 'speed',
    'how often'     : 'frequency',
    'how come'      : 'reason',
    'which'         : 'choice',
    'whose'         : 'owner',
    'how big'       : 'size'
}

questionWIs = {
    # how to replace the son of ROOT when it's "is" (nounify into identity)
    'what'          : 'definition',
    'what kind'     : 'description',
    'what type'     : 'type',
    'what sort'     : 'type',
    'what time'     : 'time',
    'when'          : 'date',
    'why'           : 'reason',
    'where'         : 'place',
    'who'           : 'identity',
    'how'           : 'manner',
    'how much'      : 'amount',
    'how many'      : 'quantity',
    'how old'       : 'age',
    'how far'       : 'distance',
    'how long'      : 'length',
    'how tall'      : 'height',
    'how deep'      : 'depth',
    'how wide'      : 'width',
    'how fast'      : 'speed',
    'how often'     : 'frequency',
    'how come'      : 'reason',
    'which'         : 'choice',
    'whom'          : 'identity',
    'whose'         : 'owner',
    'how big'       : 'size'
}

questionType = {
    # how to type ROOT
    'what time'     : 'DATE',
    'when'          : 'DATE',
    'where'         : 'LOCATION',
    'who'           : 'PERSON',
    'how much'      : 'NUMBER',
    'how many'      : 'quantity',
    'how old'       : 'NUMBER',
    'how far'       : 'NUMBER',
    'how long'      : 'NUMBER',
    'how tall'      : 'NUMBER',
    'how deep'      : 'NUMBER',
    'how wide'      : 'NUMBER',
    'how fast'      : 'NUMBER',
    'how often'     : 'NUMBER',
    'whom'          : 'PERSON',
    'whose'         : 'PERSON',
    'how big'       : 'NUMBER'
}

def processQuestionType(t,w,typeMap=questionType):
    """
        Add a type to the root of the tree (= type of the answer) depending on the question word
    """
    try:
        t.namedEntityTag = typeMap[w]
    except KeyError:
        pass

def processIdentity(t,w,wisMap=questionWIs):
    """
        If the question is "Wh.. is/are/..." replace the node 'identity' (noun associated to 'is') by a word dependendind on Wh..
    """
    try:
        if t.wordList[0].index >= 1000:
            for n in t.child:
                processIdentity(t,w)
        elif t.getWords() == 'identity':
            t.wordList[0].word = wisMap[w] # if the son of ROOT is 'identity', replace it according to the question word
    except KeyError:
        pass

def processQuestionInfo(t,w,infoMap=questionInfo):
    """
        Add to the first sons of ROOT that are not connectors (ie index < 1000) a word depending on the qw
    """
    try:
        if t.wordList[0].index >= 1000:
            for n in t.child:
                processQuestionInfo(n,w)
        elif t.getWords().find(w) == -1:
            t.wordList.append(Word(infoMap[w],1001))            
    except KeyError:
        pass
          
    
def processQuestionWord(t,w):
    """
        Type the root
        Try to include the info contained in the question word
          into the sons of ROOT (ex: When -> add "date")
    """
    processQuestionType(t,w)  # type the ROOT according to the question word
    processIdentity(t,w)
    processQuestionInfo(t.child[0],w)
