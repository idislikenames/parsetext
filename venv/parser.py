import spacy
from spacy import displacy
from spacy.tokens import Span
from tabulate import tabulate
from collections import Counter

import re
import fileinput
import networkx as nx
import csv
import pandas as pd

doc = None
#textfile = "input/m.txt"#"input/oxford_old_babylonian.txt",]
textfile = "input/test_middle_babylonian.txt"
nlp = spacy.load("en_core_web_sm")
people_tokens = []

# delete numbers and symbols like [...], ·,
def clean_nums(textfile):
    for line in fileinput.input(textfile, inplace=True):
        print(re.sub("[0-9]|\[(\s*\.\s*)*\]|[·]", "", line), end='')

# if brackets have words in them, remove only the brackets
def remove_brackets(textfile):
    for line in fileinput.input(textfile, inplace=True):
        print (re.sub(r"\[([^]]+)\]", r"\1", line), end='')

# remove brackets and words in between
def remove_brackets_words(textfile):
    for line in fileinput.input(textfile, inplace=True):
        print(re.sub("[\(\[].*?[\)\]]", "", line), end='')

def read_input (input):
    global doc
    textfile = open(input, "r")
    raw= textfile.read()
    doc= nlp(raw)
    textfile.close()

def get_pos(doc):
    global people_tokens
    people_tokens = [token for token in doc if token.ent_type_ == "PERSON" or token.pos_ == "PRON"]

    adj_token_list = []
    for token in doc:
        if token.pos_ == 'ADJ':
            adj_token_list.append(token)

# get a list of adjs and person if they are in the same sentence and having the same head
    adj_on_person_list = []
    for a in adj_token_list:
        adj_span = doc[a.i:a.i + 1]
        # print(f'e.start_char, end_char: {e.start_char} {e.end_char}')
        sentence_adj = adj_span.sent
        for e in people_tokens:
            if sentence_adj == e.sent and e.head==a.head:
                adj_on_person_list.append((e, a))

    print(f"Tuples of person, pronouns and adj, in same sentence with same head: {adj_on_person_list}")
    print("")
    tokenslist = [(token.i, token.text, token.lemma_, token.pos_, token.head, token.tag_,  # token.dep_,#token.shape_
                   token.is_alpha, token.is_stop, token.ent_type_) for token in doc]

    print("Tokens after parsing:")
    print(tabulate(tokenslist, headers=["tokenid", "text", "lemma_", "pos_", "head", "tag_", "is_alpha", "is_stop",
                                        "ent_type_"]))  # "dep_","shape_",

    # document level ent
    ents_list = [(e.text, e.start_char, e.end_char, e.label_, e.label) for e in doc.ents]
    print("")
    print("Entities at a doc level:")
    print(tabulate(ents_list, headers=["text", "start_char", "end_char", "label_", "label"]))

# add or modify incorrect tags
# TODO: finish func of getting all the list of ents checked & assigned
# TODO: see if new / wrong ent functions can be merged.
def add_ents(doc): #Enkidu as example row 16 in doc.
    candidate_token = [token for token in doc if token.text.lower() in ("cp",)]
    #idx is char offset within the doc
    #for existing incorrect ent
    new_ents = []
    for ent in doc.ents:
        if ent.label_ != "PERSON" and ent.text.lower() =="cp": # TODO: change to check in list
            new_ent = Span(doc, ent.start, ent.end, label="PERSON")
            new_ents.append(new_ent)
        else:
            new_ents.append(ent)
    doc.ents = new_ents

    # for new ent, if a candidate token was not assigned an entity type
    for i in range(len(candidate_token)):
        if candidate_token[i].ent_type_ == '':
            print (f'Here is candidates and their token i {candidate_token[0],candidate_token[0].i}')# , candidate_token[0].idx}')
            start_po = candidate_token[0].i
            new_ent = Span(doc,start_po,start_po+1, label="PERSON") # Enkidu is at 20 , create a Span for the new entity
            print (f'new ent is {new_ent}')
            doc.ents = list(doc.ents) + [new_ent]

    print('After', doc.ents)


def get_verb(doc):
    # list of adj
    adjs = [token for token in doc if token.is_stop != True and token.is_punct != True and token.pos_ == "ADJ"]

    # noun tokens that arent stop words or punctuations
    verbs = [token for token in doc if token.is_stop != True and token.is_punct != True and token.pos_ == "VERB"]

    cnt_adj = Counter()

    for w in adjs:
        cnt_adj[w.text] += 1
    common_adj = cnt_adj.most_common(10)
    print(f'Most freq used adjectives : {common_adj}')

    # verb tokens
    cnt_verb = Counter()
    for word in verbs: #word is type token
        cnt_verb[word.text] += 1 #add one more count according to the key
    common_verbs= cnt_verb.most_common(10)
    print(f'Most freq used verbs : {common_verbs}')
    df= pd.DataFrame(common_verbs,columns=["verb", "appearance"])
    pd.DataFrame(df).to_csv('/Users/wnba/PycharmProjects/readpoem/venv/output/verb_freq.csv', index=False)

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
    #print(f'edges is {edges}')
    adjs_tokens = [token for token in doc if token.is_stop != True and token.is_punct != True and token.pos_ == "ADJ"]
    people_tokens = [token for token in doc if token.ent_type_ == "PERSON" or token.pos_ == "PRON"] #chang to use ent in doc.ents?
    print(f'adj list is {adjs_tokens}')
    print(f'people list is {people_tokens}')

    # first get a dict with token and it's sentence, (bcs no sentence id, it builds a dict for later calculation) .
    #like this: {(key people token, [adj list ] ), (another person as key, [adj list] )...}
    value = []
    people_adj_dict = {key: list(value) for key in people_tokens}
    for k in people_adj_dict.keys():
        for a in adjs_tokens:
            if get_token_sent(k)==get_token_sent(a):
                people_adj_dict[k].append(a)

    # distance_dic stores person and shortest path info.
    distance_dic = {}
    for p in people_adj_dict.keys():
        shortest_path_length_test = 99999 #default length
        shortest_path_test = ''
        for a in people_adj_dict.get(p): # iterate through all the adj under that person, update the shortest path for that person
            path = nx.shortest_path(graph, source=a.text.lower(), target=p.text.lower())
            len = nx.shortest_path_length(graph, source=a.text.lower(), target=p.text.lower())
            if shortest_path_length_test > len:
                shortest_path_length_test = len
                shortest_path_test = path
        distance_dic[p]=(a, shortest_path_test, shortest_path_length_test)
    print(f'Dict with person and distance to the nearest adj is {distance_dic}')

    pd.DataFrame(distance_dic).to_csv('/Users/wnba/PycharmProjects/readpoem/venv/output/dist_to_adj_output.csv', index=False)


clean_nums(textfile)
remove_brackets_words(textfile)
remove_brackets(textfile)

read_input(textfile)
#add_ents(doc)
get_pos(doc)
get_verb(doc)
get_dist(doc)

