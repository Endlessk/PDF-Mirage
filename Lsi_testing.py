import logging, gensim, bz2, os
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim import corpora, models, similarities

stoplist = set('for a of the and to in'.split())

from six import iteritems

#========== testing text formating ===================

# collect statistics about all tokens
test_dictionary = corpora.Dictionary(line.lower().split() for line in open('/home/dakun/Desktop/CCS review sample/37_format.txt'))

# remove stop words
stop_ids = [test_dictionary.token2id[stopword] for stopword in stoplist if stopword in test_dictionary.token2id]

once_ids = [tokenid for tokenid, docfreq in iteritems(test_dictionary.dfs) if docfreq == 1]

test_dictionary.filter_tokens(stop_ids)  # remove stop words

test_dictionary.compactify()  # remove gaps in id sequence after words that were removed

#print(test_dictionary)
#print(test_dictionary.token2id)

from pprint import pprint  # pretty-printer

class MyCorpus(object):
    def __iter__(self):
        for line in open('/home/dakun/Desktop/CCS review sample/37_format.txt'):
            yield test_dictionary.doc2bow(line.lower().split())
corpus_memory_friendly = MyCorpus()
print(corpus_memory_friendly)
temp_corpus=[]
for vector in corpus_memory_friendly:
    #print(vector)
    temp_corpus.append(vector)

test_doc=temp_corpus[0]


#========== TF-IDF read training data ===================

# read from file
if (os.path.exists("/home/dakun/Desktop/all_paper/deerwester.dict")):
    dictionary = corpora.Dictionary.load('/home/dakun/Desktop/all_paper/deerwester.dict')
    corpus = corpora.MmCorpus('/home/dakun/Desktop/all_paper/deerwester.mm')
    print("Found File")
else:
    print("No File found")

lsi = gensim.models.lsimodel.LsiModel(corpus, id2word=dictionary, num_topics=20)
#========== TF-IDF testing ===================


index = similarities.MatrixSimilarity(lsi[corpus])

lsi_doc=lsi[test_doc]

sims = index[lsi_doc]

sims = sorted(enumerate(sims), key=lambda item: -item[1])

print(sims)


