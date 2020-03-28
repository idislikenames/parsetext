import spacy
from spacy import displacy
from spacy.tokens import Span
from tabulate import tabulate
from collections import Counter

import re
import fileinput
import networkx as nx

doc = None
#textfile = "input/m.txt"#"input/oxford_old_babylonian.txt",]
textfile = "input/oxford_old_babylonian.txt"
nlp = spacy.load("en_core_web_sm")
#textfile = open("input/6bMBUrw.txt", "r")
#textfile = open("input/ETCSL1.txt", "r")


def clean_nums(textfile):
    #raw= textfile.read()
    for line in fileinput.input(textfile, inplace=True):
        print(re.sub("[0-9]", "", line))

def read_input (input):
    global doc
    textfile = open(input, "r")
    raw= textfile.read()
    doc= nlp(raw)
    textfile.close()


def get_pos(doc):
    # doc = nlp("Lisa is happy. Bigbird is hugry. The sky is almost blue everyday. I sit in traffic for hours. Louise is brave. He looks angry. Four seconds is the longest wait.")
    #fb_ent = Span(doc, 20, 21, label="PERSON")  # Enkidu is at 20 , create a Span for the new entity
    # fb_ent = Span(doc, 4, 5, label="PERSON")

    #doc.ents = list(doc.ents) + [fb_ent]
    #ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]
    # print('After', ents)

    #token_span_one = doc[0:1]
    #sentence_one = token_span_one.sent
    # print("sentence is"+sentence_one.text)

    # testing
    '''
    token_test_span = doc[53:54]
    print(token_test_span)
    print(token_test_span.sent)

    token_test_span2 = doc[17:18]
    print(token_test_span2)
    print(token_test_span2.sent)'''

    person_ent_list = []
    for token in doc:
        if token.ent_type_ == 'PERSON' or token.pos_ == 'PRON':
            person_ent_list.append(token)

    # print(person_ent_list)

    adj_token_list = []
    for token in doc:
        if token.pos_ == 'ADJ':
            adj_token_list.append(token)

    # could be optimized by intersect of sentence vector of adj and p
    adj_on_person_list = []

    for a in adj_token_list:
        adj_span = doc[a.i:a.i + 1]
        # print(f'e.start_char, end_char: {e.start_char} {e.end_char}')
        sentence_adj = adj_span.sent
        # for e in doc.ents:
        for e in person_ent_list:
            if sentence_adj == e.sent:  # and e.head==a.head:
                adj_on_person_list.append((e, a))


    """for a in adj_token_list:
        adj_span = doc[a.i:a.i + 1]
        sentence_adj = adj_span.sent
        for x in """

    print("Tuples of person, pronouns and adj, in same sentence with same head:")
    print(adj_on_person_list)
    print("")

    """
    for token in doc_test:
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
                , token.is_alpha, token.is_stop)"""
    print("Tokens after parsing:")
    tokenslist = [(token.i, token.text, token.lemma_, token.pos_, token.head, token.tag_,  # token.dep_,#token.shape_
                   token.is_alpha, token.is_stop, token.ent_type_) for token in doc]
    print("")

    print(tabulate(tokenslist, headers=["tokenid", "text", "lemma_", "pos_", "head", "tag_", "is_alpha", "is_stop",
                                        "ent_type_"]))  # "dep_","shape_",

    # document level ent
    ents_list = [(e.text, e.start_char, e.end_char, e.label_, e.label) for e in doc.ents]
    print("")
    print("Entities at a doc level:")
    print(tabulate(ents_list, headers=["text", "start_char", "end_char", "label_", "label"]))

    # self.label = nlp.vocab.strings[label]
    '''
    # token level ent, ent for a specific token
    ent_san = [doc[0].text, doc[0].ent_iob_, doc[0].ent_type_]
    ent_francisco = [doc[1].text, doc[1].ent_iob_, doc[1].ent_type_]
    print(ent_san)  # ['San', 'B', 'GPE']
    print(ent_francisco)  # ['Francisco', 'I', 'GPE']
    '''

    """
    for ent in doc.ents:
        print(ent.text, ent.start_char, ent.end_char, ent.label_)
    entities=[(i, i.label_, i.label) for i in nytimes.ents]
    entities"""


def get_verb(doc):
    # list of adj
    adjs = [token for token in doc if token.is_stop != True and token.is_punct != True and token.pos_ == "ADJ"]

    # noun tokens that arent stop words or punctuations
    verbs = [token for token in doc if token.is_stop != True and token.is_punct != True and token.pos_ == "VERB"]

    cnt_adj = Counter()
    # five most common tokens

    for w in adjs: #['red', 'blue', 'red', 'green', 'blue', 'blue']:
        cnt_adj[w.text] += 1
    common_adj = cnt_adj.most_common(10)
    print(f'Most freq used adjectives : {common_adj}')

    # verb tokens
    cnt_verb = Counter()

    for word in verbs: #['red', 'blue', 'red', 'green', 'blue', 'blue']:
        cnt_verb[word.text] += 1
    #print(cnt)
    common_verbs= cnt_verb.most_common(10)
    print(f'Most freq used verbs : {common_verbs}')
    '''c = Counter(verbs)

    #verb_freq = Counter(verbs)
    print(verbs)
    #print (verb_freq)
    common_verbs = c.most_common(10)
    print(f'Most freq used verb : {common_verbs}')'''

def get_token_sent(token):
    token_span = token.doc[token.i:token.i+1]
    return token_span.sent

def get_dist(doc):
    # Load spacy's dependency tree into a networkx graph
    edges = []
    for token in doc:
        for child in token.children:
            edges.append(('{0}'.format(token.lower_),
                          '{0}'.format(child.lower_)))
    graph = nx.Graph(edges)
    print(f'edges is {edges}')
    adjs_tokens = [token for token in doc if token.is_stop != True and token.is_punct != True and token.pos_ == "ADJ"]
    people_tokens = [token for token in doc if token.ent_type_ == "PERSON" or token.pos_ == "PRON"] #chang to use ent in doc.ents?
    print(f'adj list is {adjs_tokens}')
    print(f'people list is {people_tokens}')

    # need a dic with token and it's sentence
    #{(key people token, [adj list ] )}
    '''test_list= ['a','b','c']
    value =[]
    test_d= {key: list(value) for key in test_list}
    test_d['a'].append("ok")
    print (f'{test_d} =========testing if append ')'''
    value = []
    people_adj_dict = {key: list(value) for key in people_tokens}
    for k in people_adj_dict.keys():
        for a in adjs_tokens:
            if get_token_sent(k)==get_token_sent(a):
                people_adj_dict[k].append(a)
    print (f'ok now======people adj dic is {people_adj_dict}')

    #maybe keep it dont change
    '''for p in people_tokens: # given list of adj and people, get shortest distance if they are in same sentence.
        for a in adjs_tokens:
            if get_token_sent(p)==get_token_sent(a):
                print(f'taken in same sentence {a.text.lower()} and {p.text.lower()}')
                dist= nx.shortest_path(graph, source=a.text.lower(), target=p.text.lower())
                print(f'Distance between {a} and {p} is {dist}')'''
    ##### from above
    object_list = [token for token in doc if token.ent_type_ == "PROPN" or token.ent_type_ == "PERSON"]

    distance_dic = {}
    for p in people_adj_dict.keys():
        shortest_path_length_test = 99999
        shortest_path_test = ''
        for a in people_adj_dict.get(p):
            #print(f'really here $$$ a is {a}')
            #if get_token_sent(p) == get_token_sent(a):
            #print(f'taken in same sentence {a.text.lower()} and {p.text.lower()}')
            path = nx.shortest_path(graph, source=a.text.lower(), target=p.text.lower())
            len = nx.shortest_path_length(graph, source=a.text.lower(), target=p.text.lower())
            if shortest_path_length_test > len:
                shortest_path_length_test = len
                shortest_path_test = path
        distance_dic[p]=(a, shortest_path_test, shortest_path_length_test)
    print(f'====finally, dict with length is {distance_dic}')
    ######
    # Get a list of entity & pron in string format



    # Get the length and path from each item in object_list to the nearest adj
    #get sentence id , the compare all adj?
    #for
    '''entity1 = 'sue'.lower()
    entity2 = 'tired'
    print(nx.shortest_path_length(graph, source=entity1, target=entity2))
    print(nx.shortest_path(graph, source=entity1, target=entity2))'''

clean_nums(textfile)
read_input(textfile)
get_pos(doc)
get_verb(doc)
get_dist(doc)


