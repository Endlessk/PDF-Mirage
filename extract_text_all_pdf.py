from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

import re, string, timeit, os, glob

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

path='/Training data/'
n=0
for root, dirnames, filenames in os.walk(path):
    dirnames.sort()
    for filename in sorted(filenames):
        n=n+1
        print "*** Now process paper %d ***" %n
        pdf_file= os.path.join(root, filename)
        print pdf_file
        extractedText = convert_pdf_to_txt(pdf_file)

        ########### remove punctuation ###########
        exclude = set(string.punctuation)
        table = string.maketrans("","")
        def remove_punctuation(s):
            return s.translate(table, string.punctuation)
        text_nopunctuation = remove_punctuation(extractedText)

        ########### remove new line character ######

        text_nonewline = text_nopunctuation.replace('\n', ' ')
        text_nonewline = " ".join(text_nonewline.split())

        ########### store into a txt file ###########
        text_file = open("/Output.txt", "a")
        text_file.write("%s\n" % text_nonewline)
        text_file.close()
