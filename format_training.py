import logging
import re, string, timeit
from cStringIO import StringIO
from nltk.corpus import stopwords

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim import corpora

stoplist = set(stopwords.words('english'))

from six import iteritems

# collect statistics about all tokens
dictionary = corpora.Dictionary(line.lower().split() for line in open('Output.txt'))

# remove stop words
stop_ids = [dictionary.token2id[stopword] for stopword in stoplist if stopword in dictionary.token2id]

once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]

dictionary.filter_tokens(stop_ids)  # remove stop words

dictionary.compactify()  # remove gaps in id sequence after words that were removed

dictionary.save('deerwester.dict')  # store the dictionary, for future reference

print(dictionary)
print(dictionary.token2id)
# /////////////////////////////////////////////////////////////////////////////////////

from pprint import pprint  # pretty-printer

class MyCorpus(object):
    def __iter__(self):
        for line in open('Output.txt'):
            yield dictionary.doc2bow(line.lower().split())
corpus_memory_friendly = MyCorpus()
print(corpus_memory_friendly)
corpus=[]
for vector in corpus_memory_friendly:
    #print(vector)
    corpus.append(vector)


print(corpus)

corpora.MmCorpus.serialize('deerwester.mm', corpus)

