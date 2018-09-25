import logging, gensim, bz2, os
import re, string, timeit
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from nltk.corpus import stopwords
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim import corpora, models, similarities

from six import iteritems

########### extract text from pdf ###########
def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

########### remove punctuation ###########
exclude = set(string.punctuation)
table = string.maketrans("","")
def remove_punctuation(s):
    return s.translate(table, string.punctuation)

#========== TF-IDF read training data ===================

# read from file
if (os.path.exists("deerwester.dict")):
    dictionary = corpora.Dictionary.load('deerwester.dict')
    corpus = corpora.MmCorpus('deerwester.mm')
    print("Found File")
else:
    print("No File found")

#run online LDA
# extract 200 LDA topics, using 1 pass and updating once every 1 chunk (1 documents)
lda = gensim.models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=200, update_every=1, chunksize=1, passes=1)

#To run batch LDA (not online)
# extract 200 LDA topics, using 20 full passes, no online updates
#lda = gensim.models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=20, update_every=0, passes=15)

#========== TF-IDF testing ===================

filename=('test_paper.pdf');

doc = convert_pdf_to_txt(filename)

text_nopunctuation = remove_punctuation(doc) # remove punctuation

stop_words = set(stopwords.words('english'))
stop_words.update(['fig', 'sec']) 
filtered_words = [i for i in text_nopunctuation.lower().split() if i not in stop_words] #remove stop words
#print(filtered_words)

vec_bow = dictionary.doc2bow(filtered_words)

index = similarities.SparseMatrixSimilarity(lda[corpus], num_features=4373)

lda_doc=lda[vec_bow]

sims = index[lda_doc]

sims = sorted(enumerate(sims), key=lambda item: -item[1])

print(sims)


