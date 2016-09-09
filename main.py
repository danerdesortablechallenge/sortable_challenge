#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from sys import argv

##
# CHECK SYNTAX
if len(argv) != 4:
    print "Invalid operation. Syntax: "+argv[0]+" products_file listings_file results_file"
    exit(1)

##
# SOURCES OF INPUT AND DESTINATION OF OUTPUT
products_file = argv[1]
listings_file = argv[2]
result_file = argv[3]


########### CLASSES ############

##
# general class for all inputs objects. It provides json parsing.
class InputItem(object):
    def __init__(self, text_json):
        o = json.loads(text_json)
        for x in o:
            name = x.replace("-","_").lower()
            self.__dict__[name]=o[x].lower()
        pass
    def __str__(self):
        return str(self.__dict__)

##
# Product item
class Product(InputItem):
    def __init__(self, text_json):
        self.model=None
        self.manufacturer=None
        self.product_name=None
        InputItem.__init__(self,text_json)

##
# Listing item
class Listing(InputItem):
    def __init__(self, text_json):
        self.title=None
        self.manufacturer=None
        InputItem.__init__(self,text_json)

##
# Map from words to indexes of listing items in the listings array
class Index:
    def __init__(self):
        self.index={}

    ##
    # append listing index to all words from this listing
    def append(self, words, listing_id):
        for w in words:
            if w not in self.index: self.index[w] = []
            self.index.get(w).append(listing_id)

    def __str__(self):
        return self.__str__()
    def __iter__(self):
        return self.index.__iter__();
    def __getitem__(self, item):
        return self.index.get(item,[])


########### GLOBAL FUNCTIONS ############

##
# split text to tokens/words
def split_to_words(text):

    ##
    # remove symbols that can be useful in the middle of the word, but not
    # in the suffix of in the prefix
    def remove_excepted_prefix_and_suffix(x):
        if x[0] in '-=': return x[1:]
        if x[len(x) - 1] in '.-=': return x[:-1]
        return x

    ##
    # split text
    def spl(w, s):
        words = set(w)
        done = False
        while not done:
            nwords = []
            for w in words:
                nwords = nwords + w.split(s)
            nwords = set(nwords)
            nwords.discard("")
            done = len(words) == len(nwords)
            words = [remove_excepted_prefix_and_suffix(w) for w in nwords]
        return words

    ##
    # remove suffix of the description after prepositions (in the def. languages)
    def remove_prepositions(w):
        english=set([u" for ", u" with "])
        french =set([u" pour ", u" avec "])
        german =set([u" für ", u" mit "])
        italian=set([u" per ", u"  con "])
        spanish=set([u" para ", u"  con "])

        for p in english | french | german | italian | spanish:
            if p in w:
                w = w[:w.index(p)]
        return w

    words = text
    words = remove_prepositions(words)

    ##
    # replace all delimiters by one universal
    for sum in u",()\"/_  *~^%#@&[]{}!`»·?-":
        words = words.replace(sum, u" ")
    words = [words]

    ##
    # split
    for sep in " ":
        words = spl(words, sep)

    return words


########### MAIN ############


def __main__():

    products=[]
    listings=[]
    listings_index=Index()

    print "INPUT:"
    print "  products file:",products_file
    print "  listings file:",listings_file
    print "OUTPUT:"
    print "  results file :",result_file
    print
    print

    ##
    # READ ALL LISTINGS and BUILD INDEX
    print "Read listings ..."
    file = open(listings_file, 'r')
    for line in file:
        l = Listing(line)
        index = len(listings)
        listings.append(l)
        listings_index.append(split_to_words(l.title) + split_to_words(l.manufacturer), index)
    file.close();
    print "Done."
    print

    ##
    # READ ALL PRODUCTS and WRITE RESULTS
    print "Read products ..."
    file = open(products_file, 'r')
    output = open(result_file, 'w')
    for line in file:
        p = Product(line)
        products.append(p)

        result={}
        result['product_name'] = p.product_name
        result['listings'] = []

        words = split_to_words(p.product_name) + split_to_words(p.manufacturer) + split_to_words(p.model)
        words = set(words)

        i = words.__iter__()
        w = i.next()
        options = set(listings_index[ w ])

        while len(options) > 0 :
            try:
                w = i.next()
            except(StopIteration):
                break
            op = set(listings_index[ w ])

            options = options & op

        if len(options)>0:
            for x in options:
                result['listings'].append(listings[x].__dict__)

        output.write( json.dumps(result) + '\n');
    file.close()
    print "Done."

__main__()
