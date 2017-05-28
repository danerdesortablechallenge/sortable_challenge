#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import re
from sys import argv
from sys import stdout

### CHECK SYNTAX
if len(argv) != 4:
    print "Invalid operation. Syntax: "+argv[0]+" products_file listings_file results_file"
    exit(1)

### SOURCES OF INPUT AND DESTINATION OF OUTPUT
products_file = argv[1]
listings_file = argv[2]
result_file = argv[3]


### FORMAT UTILITIES
## search for space sequences and replace them by single space.
def remove_double_space(text):
    return re.sub(' +',' ',text)

## unification of a string. replacmant any sumbol by space
def replace_delimiters(text, d):
    t=[]
    for a in text:
        if ord('A')<=ord(a)<=ord('Z') or a=='.' or ord('0')<=ord(a)<=ord('9'):
            t.append(a)
        else:
            t.append(d)
    return remove_double_space(u"".join(t))
    
### DATA STRUCTURES

class Product:
    def __init__(self):
        self.product_name=''
        self.manufacturer=''
        self.family=''
        self.model=''
        self.u_product_name=''
        self.u_manufacturer=''
        self.u_family=''
        self.u_model=''
        self.announced_date=''
        
    ## simple json parser    
    def from_json(self, text):
        o=json.loads(text)
        
        if u'product_name' in o:
            self.product_name = o[u'product_name']
            self.u_product_name = self.product_name.upper()
            self.u_product_name = replace_delimiters(self.u_product_name, ' ')
        
        if u'manufacturer' in o:
            self.manufacturer = o[u'manufacturer']
            self.u_manufacturer = self.manufacturer.upper()
            self.u_manufacturer = replace_delimiters(self.u_manufacturer, ' ')
        
        if u'family' in o:
            self.family = o[u'family']
            self.u_family = self.family.upper()
            self.u_family = replace_delimiters(self.u_family, ' ')

        if u'model' in o:
            self.model = o[u'model']
            self.u_model = self.model.upper()
            self.u_model = replace_delimiters(self.u_model, ' ')
        
        if u'announced-date' in o:
            self.announced_date = o[u'announced-date'].upper()
                
    ## print debug representation
    def __str__(self):
        s = ""
        s = s + "---------\n"
        s = s + "product_name = "+self.u_product_name+"\n"
        s = s + "manufacturer = "+self.u_manufacturer+"\n"
        s = s + "family = "+self.u_family+"\n"
        s = s + "model = "+self.u_model+"\n"
        #s = s + "announced-date = "+self.announced_date+"\n"
        return s
        
class Listing:
    def __init__(self):
        self.title=''
        self.manufacturer=''
        self.u_title=''
        self.u_manufacturer=''
        self.currency=''
        self.price=''
        
    ## simple json parser
    def from_json(self, text):
        o=json.loads(text)
        
        if u'title' in o:
            self.title = o[u'title']
            self.u_title = self.title.upper()
            self.u_title = replace_delimiters(self.u_title, ' ')

        if u'manufacturer' in o:
            self.manufacturer = o[u'manufacturer']
            self.u_manufacturer = self.manufacturer.upper()
            self.u_manufacturer = replace_delimiters(self.u_manufacturer, ' ')

        if u'currency' in o:
            self.currency = o[u'currency']

        if u'price' in o:
            self.price = o[u'price']
               
    ## print debug representation
    def __str__(self):
        s = ""
        s = s + "   - - - - - - - - -\n"
        s = s + "   title = "+self.u_title+"\n"
        s = s + "   manufacturer = "+self.u_manufacturer+"\n"
        return s
    
    ## serialization to json format
    def to_json(self):
        s={}
        s["title"]=self.title
        if not len(self.manufacturer)==0  : s["manufacturer"]=self.manufacturer
        if not len(self.currency)==0      : s["currency"]=self.currency
        if not len(str(self.price))==0    : s["price"]=str(self.price)
        return s
    
## Result
class Result:
    def __init__(self):
        self.product_name=u''
        self.listings=[]
        
    ## serialization to json format
    def to_json(self):
        result={}
        result['product_name']=self.product_name
        result['listings']=[ x.to_json() for x in self.listings]
        
        return json.dumps(result)

## process progress animation
class Animation:
    def __init__(self,c):
        self.c=c
        self.i=0
        self.a=-1
        self.tlt="|/-\-"
        stdout.flush()
        stdout.write(' '*3)
        self.tick()
        
    def tick(self):
        self.i=self.i+1
        if self.i==self.c:
            self.i=0
            self.animation()
            
    def animation(self):
        self.a=(self.a+1)%len(self.tlt)
        #if self.a>=len(self.tlt): self.a=0
        self.remove()
        stdout.write(' '+self.tlt[self.a]+' ')
        stdout.flush()
    
    def remove(self):
        stdout.write("\b"*3)
        stdout.flush()
        
## read data of products and listings
def read_data(products, listing):
    
    print "Read products ... ",
    anim = Animation(50)
    with open(products_file) as f:
        content = f.readlines()
        anim.tick()
    content = [x.strip() for x in content] 
    anim.remove()
    print "Done."
    
    for c in content:
        p = Product()
        p.from_json(c)
        products.append( p )

    print "Read listings ... ",
    anim = Animation(50)
    with open(listings_file) as f:
        content = f.readlines()
        anim.tick()
    content = [x.strip() for x in content] 
    anim.remove()
    print "Done."

    for c in content:
        l = Listing()
        l.from_json(c)
        listing.append( l )
    
def __main__():    
    products=[]
    listing =[]
    
    print "INPUT:"
    print "  products file:",products_file
    print "  listings file:",listings_file
    print "OUTPUT:"
    print "  results file :",result_file
    print

    read_data(products, listing)

    def briev_compare(p, l):
        # check if manufacturers are equal
        if not p.u_manufacturer in l.u_manufacturer: return False
    
        # check if listing title contains product product name
        # Note: add scpaces (sufix and prefix) to simplify the matching
        a1=u' '+p.u_product_name+u' '
        a2=u' '+l.u_title+u' '
        i=a2.find(a1)
        if i<0 : return False
    
        # check if product name is not in relation to the listing product
        relations_eng = set([u' WITH ', u' FOR '])
        relations_ger = set([u' ZUM ', u' MIT '])
        relations=relations_eng|relations_ger
        for relation in relations:
            ii = a2.find(relation)
            if ii > 0 and i > ii: return False
        
        return True

    results=[]
    print "Matching ... ",
    anim = Animation(50)
    for p in products:
        result=Result()
        result.product_name = p.product_name
        for l in listing:
            if briev_compare(p,l):
                result.listings.append( l )
        results.append(result)
        anim.tick()
    anim.remove()
    print "Done."
            
    print "Save results ... ",
    anim = Animation(50)
    output = open(result_file, 'w')
    for r in results:
        output.write( u"" + r.to_json() + "\n" )
        anim.tick()
    anim.remove()
    print "Done."
            
    return 0
__main__()

