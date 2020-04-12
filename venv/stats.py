import numpy as np
import pandas as pd

'''ctxs = [
    'krayyem like candy crush more then coffe',
    'krayyem like plays candy crush all days'

]'''

'''
#l_unique = list(set((' '.join(ctxs)).split(' ')))
l_unique = ['i', 'like,','cp','and','very','much']
print(l_unique)
mat = np.zeros((len(l_unique), len(l_unique)))

nei = []
nei_size = 3


words = ['i', 'like,','cp','and','like','cp','very','much']

for i, _ in enumerate(words):
    nei.append(words[i])

    if len(nei) > (nei_size * 2) + 1:
        nei.pop(0)

    pos = int(len(nei) / 2)

    for j, _ in enumerate(nei):
        if nei[j]  in l_unique and words[i] in l_unique:
            mat[l_unique.index(nei[j]), l_unique.index(words[i])] += 1

mat = pd.DataFrame(mat)
mat.index = l_unique
mat.columns = l_unique
print(mat)
'''


def distinct_words(corpus):
    """ Determine a list of distinct words for the corpus.
        Params:
            corpus (list of list of strings): corpus of documents
        Return:
            corpus_words (list of strings): list of distinct words across the corpus, sorted (using python 'sorted' function)
            num_corpus_words (integer): number of distinct words across the corpus
    """
    corpus_words = []
    num_corpus_words = -1

    # ------------------
    # Write your implementation here.
    corpus_words = [word for line in corpus for word in line]
    corpus_words_set = set(corpus_words)
    corpus_words = sorted(list(corpus_words_set))
    num_corpus_words = len(corpus_words)

    # ------------------

    return corpus_words, num_corpus_words

def compute_co_occurrence_matrix(corpus, window_size=2):
    """ Compute co-occurrence matrix for the given corpus and window_size (default of 4).

        Note: Each word in a document should be at the center of a window. Words near edges will have a smaller
              number of co-occurring words.

              For example, if we take the document "START All that glitters is not gold END" with window size of 4,
              "All" will co-occur with "START", "that", "glitters", "is", and "not".

        Params:
            corpus (list of list of strings): corpus of documents
            window_size (int): size of context window
        Return:
            M (numpy matrix of shape (number of corpus words, number of corpus words)):
                Co-occurence matrix of word counts.
                The ordering of the words in the rows/columns should be the same as the ordering of the words given by the distinct_words function.
            word2Ind (dict): dictionary that maps word to index (i.e. row/column number) for matrix M.
    """
    words, num_words = distinct_words(corpus)
    print(f"words is {words}")
    #words=  ['i', 'like,','cp','and','like','cp','very','much']
    num_words = len(words)
    M = None
    word2Ind = {}

    # ------------------
    # Write your implementation here.
    '''for i in range(num_words): #num_words is len(words)
        word2Ind[words[i]] = i # word[i] is key, and 0,1.... as index is value'''
    word2Ind = {'All': 0, 'that': 1, 'glitters': 2, 'is': 3, 'not': 4, 'gold': 5, 'well': 6, 'ends': 7}
    print(f"word2Ind is {word2Ind}")

    M = np.zeros((num_words, num_words)) #init array
    for line in corpus:
        print(f"line is {line}")
        for i in range(len(line)):
            target = line[i]
            print(f"target is {target}")
            target_index = word2Ind[target]

            left = max(i - window_size, 0)
            right = min(i + window_size, len(line) - 1)
            for j in range(left, i):
                window_word = line[j]
                print(f"window_word is {window_word}")
                M[target_index][word2Ind[window_word]] += 1
                M[word2Ind[window_word]][target_index] += 1
            print("one ADD round")
        print("one round")


    # ------------------

    return M, word2Ind


corpus = [["I"," like"," cp", "and" ,"I",", like", "her", "very", "much"],["another" ,"thing"]]


#test_corpus= ["I"," like"," cp", "and" ,"I",", like", "her", "very", "much"]
test_corpus = ["All that glitters is not gold".split(" "), "All is well that ends well".split(" ")]
print(test_corpus)
test_corpus_words, num_corpus_words = distinct_words(test_corpus)

M, word2Ind =compute_co_occurrence_matrix (test_corpus)

print(test_corpus_words)
print(num_corpus_words)
print(M)
print(word2Ind)
