import logging, gensim, bz2, os, sys, re
import re, string, timeit, nltk
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from nltk.corpus import stopwords
from collections import Counter
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




if len(sys.argv) < 11 :
    print '\n==============================================='
    print 'ERROR! \nUsage:'
    print 'program.py folder_path PDF_1 targer_reviewer_ID_1 target_paper_ID_1 PDF_2 targer_reviewer_ID_2 target_paper_ID_2 PDF_3 target_review_ID_3 target_paper_ID_3'
    print '===============================================\n'
    sys.exit(0)


#================= Read training data ===================

# read from file
if (os.path.exists("deerwester.dict")):
    dictionary = corpora.Dictionary.load('/deerwester.dict')
    corpus = corpora.MmCorpus('deerwester.mm')
    print("Found File")
else:
    print("No File found")

lsi = gensim.models.lsimodel.LsiModel(corpus, id2word=dictionary, num_topics=200)

#========== read file and remove stopwords ===================

print '\n==============================================='
print 'Folder path:', sys.argv[1], '\n'
print 'Input file 2 :', sys.argv[2], '\n'
print 'Target review ID is :', sys.argv[3], '\n'
print 'Target paper ID is :', sys.argv[4]
print '===============================================\n'

path = sys.argv[1]

filename1 = sys.argv[2]
target_reviewer = int(sys.argv[3])
target_paper = int(sys.argv[4])

filename2 = sys.argv[5]
target_reviewer_2 = int(sys.argv[6])
target_paper_2 = int(sys.argv[7])

filename3 = sys.argv[8]
target_reviewer_3 = int(sys.argv[9])
target_paper_3 = int(sys.argv[10])

#========== process file 2 ===================
#-------- first input 
doc2 = convert_pdf_to_txt(filename1)
doc2=doc2.decode('utf8').encode('ascii', errors='ignore') # remove all non-ASCII characters
# remove punctuation
text_nopunctuation2 = remove_punctuation(doc2)

#remove stop words
stop_words = set(stopwords.words('english'))
stop_words.update(['fig', 'sec'])
filtered_words2 = [i for i in text_nopunctuation2.lower().split() if i not in stop_words]
word_count_list2 = Counter(filtered_words2)

#-------- second input 
doc3 = convert_pdf_to_txt(filename2)
doc3=doc3.decode('utf8').encode('ascii', errors='ignore') # remove all non-ASCII characters
# remove punctuation
text_nopunctuation3 = remove_punctuation(doc3)

#remove stop words
filtered_words3 = [i for i in text_nopunctuation3.lower().split() if i not in stop_words]
word_count_list3 = Counter(filtered_words3)

#-------- third input 
doc4 = convert_pdf_to_txt(filename3)
doc4=doc4.decode('utf8').encode('ascii', errors='ignore') # remove all non-ASCII characters
# remove punctuation
text_nopunctuation4 = remove_punctuation(doc4)

#remove stop words
filtered_words4 = [i for i in text_nopunctuation4.lower().split() if i not in stop_words]
word_count_list4 = Counter(filtered_words4)

#==============process all files one by one ======================

for root, dirnames, filenames in os.walk(path):
    dirnames.sort()
    for filename in sorted(filenames):
        if filename.endswith(".pdf"):
            n_break=0
            text_loop_n=[]
            text_similarities=[]
	    text_similarities2=[]
            text_word_exchanged1=[]
            text_word_exchanged2=[]
	    text_word_exchanged3=[]

            pdf_file= os.path.join(root, filename)
            print '*********************************************'
            print '*** Now process paper', filename,'***'
            print '*********************************************'

            #========== process file 1 ===================
            doc1 = convert_pdf_to_txt(pdf_file)
            doc1=doc1.decode('utf8').encode('ascii', errors='ignore') # remove all non-ASCII characters
            # remove punctuation
            text_nopunctuation1 = remove_punctuation(doc1)

            #remove stop words
            stop_words = set(stopwords.words('english'))
            stop_words.update(['fig', 'sec'])
            filtered_words1 = [i for i in text_nopunctuation1.lower().split() if i not in stop_words]

            word_count_list1 = Counter(filtered_words1)
            word_count_list2 = Counter(filtered_words2)
	    word_count_list3 = Counter(filtered_words3)
	    word_count_list4 = Counter(filtered_words4)

            ############### exchange top words from file 2 to file 1 and matching #############

            matched_reviewer_ID=0
	    matched_reviewer_ID_2=0

            n_loop=0
            list_exchange_word_1=[]
            list_exchange_word_2=[]
	    stop=0
            while stop==0 :
                
                n_loop=n_loop+1
                print '\n================================='
                print 'Loop ', n_loop, '\n'
                if n_loop > 80 :
                    print 'ERROR!!!\nToo much exchanges!\n'
                    n_break=1
                    break

                vec_bow1 = dictionary.doc2bow(filtered_words1)
                index = similarities.MatrixSimilarity(lsi[corpus])
                vec_lsi = lsi[vec_bow1] # convert the query to LSI space
                sims = index[vec_lsi]

                #======== matcehed reviewer =============
                sims = sorted(enumerate(sims), key=lambda item: -item[1])
                print ("==== Top 5 scores ====\n")
                print sims[0:5], '\n'
                #***** find the target similarities score and matched Reviewer
                # find Similarities
                check_str='('+str(target_paper)
                n_temp=0
                for sub_s in sims :
                    temp1=str(sub_s)
                    if check_str in temp1 :
                        break
                    n_temp=n_temp+1
                temp2 = str(sims[n_temp])
                n1,n2=temp2.split(' ')
                n3,n4=n2.split(')')
                similarities_score = float(n3)

		check_str2='('+str(target_paper_2)
                n_temp2=0
                for sub_s in sims :
                    temp1=str(sub_s)
                    if check_str2 in temp1 :
                        break
                    n_temp2=n_temp2+1
                temp2 = str(sims[n_temp2])
                n1,n2=temp2.split(' ')
                n3,n4=n2.split(')')
                similarities_score_2 = float(n3)

		check_str3='('+str(target_paper_3)
                n_temp3=0
                for sub_s in sims :
                    temp1=str(sub_s)
                    if check_str3 in temp1 :
                        break
                    n_temp3=n_temp3+1
                temp2 = str(sims[n_temp3])
                n1,n2=temp2.split(' ')
                n3,n4=n2.split(')')
                similarities_score_3 = float(n3)
		
		print 'S1=' + str(similarities_score) + 'S2=' + str(similarities_score_2) + 'S3=' + str(similarities_score_3)
		# =======get the stop percentage
		stop_percentage1=0.333
		stop_percentage2=0.333
		stop_percentage3=0.333
		if similarities_score > similarities_score_2:
		    stop_percentage2=0.5+(similarities_score-similarities_score_2)
		    stop_percentage1=1-stop_percentage1
		else:
		    stop_percentage1=0.5+(similarities_score_2-similarities_score)
		    stop_percentage2=1-stop_percentage1
		print '----' + str(stop_percentage1) + ' -- ' + str(stop_percentage2)

                # find matched reviewer
                n=str(sims[0])
                n1,n2=n.split(',')
                n3,n4=n1.split('(')
                n5,n6=n2.split(')')
                index=int(n4)

		nt=str(sims[1])
                nt1,nt2=nt.split(',')
                nt3,nt4=nt1.split('(')
                nt5,nt6=nt2.split(')')
                index2=int(nt4)


                #========== TF-IDF testing file 1 ===================

                #***************** exchange words **********************
                #------words file testing paper
                n=str(word_count_list1.most_common(1))
                n1,n2=n.split(', ')
                word_file_1=n1[3:-1]
		n3,n4=n2.split(')')
		#print '**********' + str(n3) +'**********'
                # remove first element
                del word_count_list1[word_file_1]
		
                #------words file targeting paper 1
                n=str(word_count_list2.most_common(1))
               	n1,n2=n.split(',')
                word_file_2=n1[3:-1]
                # remove first element
                del word_count_list2[word_file_2]

		#------words file targeting paper 2
                n=str(word_count_list3.most_common(1))
               	n1,n2=n.split(',')
                word_file_3=n1[3:-1]
                # remove first element
                del word_count_list3[word_file_3]
                
		

		#exchange words based on different similarities between target 1 targe 2
                print 'Exchange "',word_file_1,'" to "', word_file_2,'"\n'
                #list_exchange_word_1.append(word_file_1)
                #list_exchange_word_2.append(word_file_2)
		percentage=0
		total_changed=0
		diaplay_per=0
                for j,i in enumerate(filtered_words1):
                    if i==word_file_1:
                        filtered_words1[j]=word_file_2
			total_changed=total_changed+1
			percentage=float(total_changed)/float(n3)
			if percentage>stop_percentage1:
				diaplay_per=percentage
				break
		percentage=0
		total_changed=0
		diaplay_per2=0
		for j,i in enumerate(filtered_words1):
                    if i==word_file_1:
                        filtered_words1[j]=word_file_3
			total_changed=total_changed+1
			percentage=float(total_changed)/float(n3)
			diaplay_per2=percentage
			if percentage>stop_percentage2:
				break
		print '****  Percentage: ' + str(diaplay_per) +' + ' + str(diaplay_per2)

                temp_score = Counter(filtered_words1)
                print '==== Tempare count check ===='
                print temp_score.most_common(10), '\n'
                #*************** end exchange words ********************



                if index < 19:
                    matched_reviewer_ID=1
                elif index < 89:
                    matched_reviewer_ID=2
                elif index < 98:
                    matched_reviewer_ID=3
                elif index < 120:
                    matched_reviewer_ID=4
                elif index < 135:
                    matched_reviewer_ID=5
                elif index < 145:
                    matched_reviewer_ID=6
                elif index < 175:
                    matched_reviewer_ID=7
                elif index < 192:
                    matched_reviewer_ID=8
                elif index < 228:
                    matched_reviewer_ID=9
                elif index < 255:
                    matched_reviewer_ID=10
                elif index < 284:
                    matched_reviewer_ID=11
                elif index < 319:
                    matched_reviewer_ID=12
                elif index < 351:
                    matched_reviewer_ID=13
                elif index < 379:
                    matched_reviewer_ID=14
                elif index < 398:
                    matched_reviewer_ID=15
                elif index < 429:
                    matched_reviewer_ID=16
                elif index < 448:
                    matched_reviewer_ID=17
                elif index < 470:
                    matched_reviewer_ID=18
                elif index < 507:
                    matched_reviewer_ID=19
                elif index < 523:
                    matched_reviewer_ID=20
                elif index < 526:
                    matched_reviewer_ID=21
                elif index < 559:
                    matched_reviewer_ID=22
                elif index < 578:
                    matched_reviewer_ID=23
                elif index < 602:
                    matched_reviewer_ID=24
                elif index < 620:
                    matched_reviewer_ID=25
                elif index < 647:
                    matched_reviewer_ID=26
                elif index < 663:
                    matched_reviewer_ID=27
                elif index < 681:
                    matched_reviewer_ID=28
                elif index < 700:
                    matched_reviewer_ID=29
                elif index < 717:
                    matched_reviewer_ID=30
                elif index < 736:
                    matched_reviewer_ID=31
                elif index < 764:
                    matched_reviewer_ID=32
                elif index < 780:
                    matched_reviewer_ID=33
                elif index < 795:
                    matched_reviewer_ID=34
                elif index < 816:
                    matched_reviewer_ID=35
                elif index < 839:
                    matched_reviewer_ID=36
                elif index < 844:
                    matched_reviewer_ID=37
                elif index < 866:
                    matched_reviewer_ID=38
                elif index < 883:
                    matched_reviewer_ID=39
                elif index < 901:
                    matched_reviewer_ID=40
                elif index < 917:
                    matched_reviewer_ID=41
                elif index < 945:
                    matched_reviewer_ID=42
                elif index < 967:
                    matched_reviewer_ID=43
                elif index < 981:
                    matched_reviewer_ID=44
                elif index < 988:
                    matched_reviewer_ID=45
                elif index < 1003:
                    matched_reviewer_ID=46
                elif index < 1018:
                    matched_reviewer_ID=47
                elif index < 1038:
                    matched_reviewer_ID=48
                elif index < 1048:
                    matched_reviewer_ID=49
                elif index < 1070:
                    matched_reviewer_ID=50
                elif index < 1086:
                    matched_reviewer_ID=51
                elif index < 1097:
                    matched_reviewer_ID=52
                elif index < 1116:
                    matched_reviewer_ID=53
                elif index < 1134:
                    matched_reviewer_ID=54
                elif index < 1154:
                    matched_reviewer_ID=55
                elif index < 1176:
                    matched_reviewer_ID=56
                elif index < 1195:
                    matched_reviewer_ID=57
                elif index < 1206:
                    matched_reviewer_ID=58
                elif index < 1213:
                    matched_reviewer_ID=59
                elif index < 1232:
                    matched_reviewer_ID=60
                elif index < 1248:
                    matched_reviewer_ID=61
                elif index < 1269:
                    matched_reviewer_ID=62
                elif index < 1287:
                    matched_reviewer_ID=63
                elif index < 1299:
                    matched_reviewer_ID=64
                elif index < 1306:
                    matched_reviewer_ID=65
                elif index < 1316:
                    matched_reviewer_ID=66
                elif index < 1334:
                    matched_reviewer_ID=67
                elif index < 1351:
                    matched_reviewer_ID=68
                elif index < 1365:
                    matched_reviewer_ID=69
                elif index < 1374:
                    matched_reviewer_ID=70
                elif index < 1380:
                    matched_reviewer_ID=71
                elif index < 1399:
                    matched_reviewer_ID=72
                elif index < 1419:
                    matched_reviewer_ID=73
                elif index < 1436:
                    matched_reviewer_ID=74
                elif index < 1454:
                    matched_reviewer_ID=75
                elif index < 1474:
                    matched_reviewer_ID=76
                elif index < 1493:
                    matched_reviewer_ID=77
                elif index < 1512:
                    matched_reviewer_ID=78
                elif index < 1533:
                    matched_reviewer_ID=79
                elif index < 1553:
                    matched_reviewer_ID=80
                elif index < 1567:
                    matched_reviewer_ID=81
                elif index < 1582:
                    matched_reviewer_ID=82
                elif index < 1602:
                    matched_reviewer_ID=83
                elif index < 1617:
                    matched_reviewer_ID=84
                elif index < 1631:
                    matched_reviewer_ID=85
                elif index < 1651:
                    matched_reviewer_ID=86
                elif index < 1670:
                    matched_reviewer_ID=87
                elif index < 1699:
                    matched_reviewer_ID=88
                elif index < 1713:
                    matched_reviewer_ID=90
                elif index < 1727:
                    matched_reviewer_ID=91
                elif index < 1737:
                    matched_reviewer_ID=92
                elif index < 1752:
                    matched_reviewer_ID=93
                elif index < 1770:
                    matched_reviewer_ID=94
                elif index < 1778:
                    matched_reviewer_ID=95
                elif index < 1972:
                    matched_reviewer_ID=96
                elif index < 1809:
                    matched_reviewer_ID=97
                elif index < 1825:
                    matched_reviewer_ID=98
                elif index < 1844:
                    matched_reviewer_ID=99
                elif index < 1864:
                    matched_reviewer_ID=100
                elif index < 1882:
                    matched_reviewer_ID=101
                elif index < 1896:
                    matched_reviewer_ID=102
                elif index < 1916:
                    matched_reviewer_ID=103
                elif index < 1935:
                    matched_reviewer_ID=104
                elif index < 1947:
                    matched_reviewer_ID=105
                elif index < 1965:
                    matched_reviewer_ID=106
                elif index < 1981:
                    matched_reviewer_ID=107
                elif index < 1999:
                    matched_reviewer_ID=108
                elif index < 2016:
                    matched_reviewer_ID=109
                elif index < 2035:
                    matched_reviewer_ID=110
                elif index < 2055:
                    matched_reviewer_ID=111
                elif index < 2066:
                    matched_reviewer_ID=112
                elif index < 2079:
                    matched_reviewer_ID=113
                elif index < 2095:
                    matched_reviewer_ID=114


		if index2 < 19:
                    matched_reviewer_ID_2=1
                elif index2 < 89:
                    matched_reviewer_ID_2=2
                elif index2 < 98:
                    matched_reviewer_ID_2=3
                elif index2 < 120:
                    matched_reviewer_ID_2=4
                elif index2 < 135:
                    matched_reviewer_ID_2=5
                elif index2 < 145:
                    matched_reviewer_ID_2=6
                elif index2 < 175:
                    matched_reviewer_ID_2=7
                elif index2 < 192:
                    matched_reviewer_ID_2=8
                elif index2 < 228:
                    matched_reviewer_ID_2=9
                elif index2 < 255:
                    matched_reviewer_ID_2=10
                elif index2 < 284:
                    matched_reviewer_ID_2=11
                elif index2 < 319:
                    matched_reviewer_ID_2=12
                elif index2 < 351:
                    matched_reviewer_ID_2=13
                elif index2 < 379:
                    matched_reviewer_ID_2=14
                elif index2 < 398:
                    matched_reviewer_ID_2=15
                elif index2 < 429:
                    matched_reviewer_ID_2=16
                elif index2 < 448:
                    matched_reviewer_ID_2=17
                elif index2 < 470:
                    matched_reviewer_ID_2=18
                elif index2 < 507:
                    matched_reviewer_ID_2=19
                elif index2 < 523:
                    matched_reviewer_ID_2=20
                elif index2 < 526:
                    matched_reviewer_ID_2=21
                elif index2 < 559:
                    matched_reviewer_ID_2=22
                elif index2 < 578:
                    matched_reviewer_ID_2=23
                elif index2 < 602:
                    matched_reviewer_ID_2=24
                elif index2 < 620:
                    matched_reviewer_ID_2=25
                elif index2 < 647:
                    matched_reviewer_ID_2=26
                elif index2 < 663:
                    matched_reviewer_ID_2=27
                elif index2 < 681:
                    matched_reviewer_ID_2=28
                elif index2 < 700:
                    matched_reviewer_ID_2=29
                elif index2 < 717:
                    matched_reviewer_ID_2=30
                elif index2 < 736:
                    matched_reviewer_ID_2=31
                elif index2 < 764:
                    matched_reviewer_ID_2=32
                elif index2 < 780:
                    matched_reviewer_ID_2=33
                elif index2 < 795:
                    matched_reviewer_ID_2=34
                elif index2 < 816:
                    matched_reviewer_ID_2=35
                elif index2 < 839:
                    matched_reviewer_ID_2=36
                elif index2 < 844:
                    matched_reviewer_ID_2=37
                elif index2 < 866:
                    matched_reviewer_ID_2=38
                elif index2 < 883:
                    matched_reviewer_ID_2=39
                elif index2 < 901:
                    matched_reviewer_ID_2=40
                elif index2 < 917:
                    matched_reviewer_ID_2=41
                elif index2 < 945:
                    matched_reviewer_ID_2=42
                elif index2 < 967:
                    matched_reviewer_ID_2=43
                elif index2 < 981:
                    matched_reviewer_ID_2=44
                elif index2 < 988:
                    matched_reviewer_ID_2=45
                elif index2 < 1003:
                    matched_reviewer_ID_2=46
                elif index2 < 1018:
                    matched_reviewer_ID_2=47
                elif index2 < 1038:
                    matched_reviewer_ID_2=48
                elif index2 < 1048:
                    matched_reviewer_ID_2=49
                elif index2 < 1070:
                    matched_reviewer_ID_2=50
                elif index2 < 1086:
                    matched_reviewer_ID_2=51
                elif index2 < 1097:
                    matched_reviewer_ID_2=52
                elif index2 < 1116:
                    matched_reviewer_ID_2=53
                elif index2 < 1134:
                    matched_reviewer_ID_2=54
                elif index2 < 1154:
                    matched_reviewer_ID_2=55
                elif index2 < 1176:
                    matched_reviewer_ID_2=56
                elif index2 < 1195:
                    matched_reviewer_ID_2=57
                elif index2 < 1206:
                    matched_reviewer_ID_2=58
                elif index2 < 1213:
                    matched_reviewer_ID_2=59
                elif index2 < 1232:
                    matched_reviewer_ID_2=60
                elif index2 < 1248:
                    matched_reviewer_ID_2=61
                elif index2 < 1269:
                    matched_reviewer_ID_2=62
                elif index2 < 1287:
                    matched_reviewer_ID_2=63
                elif index2 < 1299:
                    matched_reviewer_ID_2=64
                elif index2 < 1306:
                    matched_reviewer_ID_2=65
                elif index2 < 1316:
                    matched_reviewer_ID_2=66
                elif index2 < 1334:
                    matched_reviewer_ID_2=67
                elif index2 < 1351:
                    matched_reviewer_ID_2=68
                elif index2 < 1365:
                    matched_reviewer_ID_2=69
                elif index2 < 1374:
                    matched_reviewer_ID_2=70
                elif index2 < 1380:
                    matched_reviewer_ID_2=71
                elif index2 < 1399:
                    matched_reviewer_ID_2=72
                elif index2 < 1419:
                    matched_reviewer_ID_2=73
                elif index2 < 1436:
                    matched_reviewer_ID_2=74
                elif index2 < 1454:
                    matched_reviewer_ID_2=75
                elif index2 < 1474:
                    matched_reviewer_ID_2=76
                elif index2 < 1493:
                    matched_reviewer_ID_2=77
                elif index2 < 1512:
                    matched_reviewer_ID_2=78
                elif index2 < 1533:
                    matched_reviewer_ID_2=79
                elif index2 < 1553:
                    matched_reviewer_ID_2=80
                elif index2 < 1567:
                    matched_reviewer_ID_2=81
                elif index2 < 1582:
                    matched_reviewer_ID_2=82
                elif index2 < 1602:
                    matched_reviewer_ID_2=83
                elif index2 < 1617:
                    matched_reviewer_ID_2=84
                elif index2 < 1631:
                    matched_reviewer_ID_2=85
                elif index2 < 1651:
                    matched_reviewer_ID_2=86
                elif index2 < 1670:
                    matched_reviewer_ID_2=87
                elif index2 < 1699:
                    matched_reviewer_ID_2=88
                elif index2 < 1713:
                    matched_reviewer_ID_2=90
                elif index2 < 1727:
                    matched_reviewer_ID_2=91
                elif index2 < 1737:
                    matched_reviewer_ID_2=92
                elif index2 < 1752:
                    matched_reviewer_ID_2=93
                elif index2 < 1770:
                    matched_reviewer_ID_2=94
                elif index2 < 1778:
                    matched_reviewer_ID_2=95
                elif index2 < 1972:
                    matched_reviewer_ID_2=96
                elif index2 < 1809:
                    matched_reviewer_ID_2=97
                elif index2 < 1825:
                    matched_reviewer_ID_2=98
                elif index2 < 1844:
                    matched_reviewer_ID_2=99
                elif index2 < 1864:
                    matched_reviewer_ID_2=100
                elif index2 < 1882:
                    matched_reviewer_ID_2=101
                elif index2 < 1896:
                    matched_reviewer_ID_2=102
                elif index2 < 1916:
                    matched_reviewer_ID_2=103
                elif index2 < 1935:
                    matched_reviewer_ID_2=104
                elif index2 < 1947:
                    matched_reviewer_ID_2=105
                elif index2 < 1965:
                    matched_reviewer_ID_2=106
                elif index2 < 1981:
                    matched_reviewer_ID_2=107
                elif index2 < 1999:
                    matched_reviewer_ID_2=108
                elif index2 < 2016:
                    matched_reviewer_ID_2=109
                elif index2 < 2035:
                    matched_reviewer_ID_2=110
                elif index2 < 2055:
                    matched_reviewer_ID_2=111
                elif index2 < 2066:
                    matched_reviewer_ID_2=112
                elif index2 < 2079:
                    matched_reviewer_ID_2=113
                elif index2 < 2095:
                    matched_reviewer_ID_2=114
			
                print '---------------------------------'
                print 'Target reviewer ID = ', target_reviewer, ' Target reviewer ID 2 = ', target_reviewer_2
		print 'Matched reviewer ID = ', matched_reviewer_ID, ' Matched reviewer ID 2 = ', matched_reviewer_ID_2
		print 'Similarities score = ' ,similarities_score
                print 'Similarities score 2 = ' ,similarities_score_2
		
                text_loop_n.append(n_loop)
                text_similarities.append(similarities_score)
                print '================================='
                if (target_reviewer == matched_reviewer_ID and target_reviewer_2 == matched_reviewer_ID_2) or (target_reviewer == matched_reviewer_ID_2 and target_reviewer_2 == matched_reviewer_ID):
                    print 'Match found by exchanging ', n_loop ,' words!!'
                    print '================================='
		    break
            shown_words=list_exchange_word_1
            actual_words=list_exchange_word_2

            ########### count font file #################
            #count font files
            total_font=0
            extra_font=0
            font_list_actial=[]
            font_list_shown=[]
            n_font=0;
            for i in range(len(shown_words)) :
                # actural words has smaller length
                if len(shown_words[i]) > len(actual_words[i]) :
                    font_list_actial=[]
                    font_list_shown=[]
                    for j in range(len(actual_words[i])):
                        if actual_words[i][j] != shown_words[i][j] :
                            if len(font_list_actial) == 0:
                                font_list_actial.append(actual_words[i][j])
                                font_list_shown.append(shown_words[i][j])
                            else :
                                # check whole list, each element means a font
                                b_font_loop=0
                                word_in_file=0

                                # if charactor is not in any font

                                #if actural charactor is in one of the font, but shown is not
                                if word_in_file==0:
                                    for k in range(len(font_list_actial)) :
                                        if actual_words[i][j] not in font_list_actial[k] :
                                            font_list_actial[k] = ''.join((font_list_actial[k],actual_words[i][j]))
                                            font_list_shown[k] = ''.join((font_list_shown[k],shown_words[i][j]))
                                            break

                                #check whether charactor is in an font
                                for k in range(len(font_list_actial)) :
                                    if b_font_loop == 1:
                                        break
                                    #check each element in font list, which means check each font
                                    for p in range(len(font_list_actial[k])) :
                                        if actual_words[i][j] == font_list_actial[k][p] and shown_words[i][j] == font_list_shown[k][p]:
                                            word_in_file = 1 #this charactor is in one of the font

                                # if charactor is not in any font
                                if word_in_file==0:
                                    for k in range(len(font_list_actial)) :
                                        if b_font_loop == 1:
                                            break
                                        for p in range(len(font_list_actial[k])) :
                                            if actual_words[i][j] == font_list_actial[k][p] and shown_words[i][j] != font_list_shown[k][p]:
                                                font_list_actial.append(actual_words[i][j])
                                                font_list_shown.append(shown_words[i][j])
                                                b_font_loop = 1
                    total_font=total_font+len(font_list_actial)
                # two words has the same length
                if len(shown_words[i]) == len(actual_words[i]) :
                    font_list_actial=[]
                    font_list_shown=[]
                    for j in range(len(actual_words[i])):
                        if actual_words[i][j] != shown_words[i][j] :
                            if len(font_list_actial) == 0:
                                font_list_actial.append(actual_words[i][j])
                                font_list_shown.append(shown_words[i][j])
                            else :
                                # check whole list, each element means a font
                                b_font_loop=0
                                word_in_file=0

                                # if charactor is not in any font

                                #if actural charactor is in one of the font, but shown is not
                                if word_in_file==0:
                                    for k in range(len(font_list_actial)) :
                                        if actual_words[i][j] not in font_list_actial[k] :
                                            font_list_actial[k] = ''.join((font_list_actial[k],actual_words[i][j]))
                                            font_list_shown[k] = ''.join((font_list_shown[k],shown_words[i][j]))
                                            break

                                #check whether charactor is in an font
                                for k in range(len(font_list_actial)) :
                                    if b_font_loop == 1:
                                        break
                                    #check each element in font list, which means check each font
                                    for p in range(len(font_list_actial[k])) :
                                        if actual_words[i][j] == font_list_actial[k][p] and shown_words[i][j] == font_list_shown[k][p]:
                                            word_in_file = 1 #this charactor is in one of the font

                                # if charactor is not in any font
                                if word_in_file==0:
                                    for k in range(len(font_list_actial)) :
                                        if b_font_loop == 1:
                                            break
                                        for p in range(len(font_list_actial[k])) :
                                            if actual_words[i][j] == font_list_actial[k][p] and shown_words[i][j] != font_list_shown[k][p]:
                                                font_list_actial.append(actual_words[i][j])
                                                font_list_shown.append(shown_words[i][j])
                                                b_font_loop = 1
                    total_font=total_font+len(font_list_actial)

                # actural words has bigger length
                elif len(shown_words[i]) < len(actual_words[i]) :
                    font_list_actial=[]
                    font_list_shown=[]
                    for j in range(len(shown_words[i])):
                        if actual_words[i][j] != shown_words[i][j] :
                            if len(font_list_actial) == 0:
                                font_list_actial.append(actual_words[i][j])
                                font_list_shown.append(shown_words[i][j])
                            else :
                                # check whole list, each element means a font
                                b_font_loop=0
                                word_in_file=0

                                # if charactor is not in any font

                                #if actural charactor is in one of the font, but shown is not
                                if word_in_file==0:
                                    for k in range(len(font_list_actial)) :
                                        if actual_words[i][j] not in font_list_actial[k] :
                                            font_list_actial[k] = ''.join((font_list_actial[k],actual_words[i][j]))
                                            font_list_shown[k] = ''.join((font_list_shown[k],shown_words[i][j]))
                                            break

                                #check whether charactor is in an font
                                for k in range(len(font_list_actial)) :
                                    if b_font_loop == 1:
                                        break
                                    #check each element in font list, which means check each font
                                    for p in range(len(font_list_actial[k])) :
                                        if actual_words[i][j] == font_list_actial[k][p] and shown_words[i][j] == font_list_shown[k][p]:
                                            word_in_file = 1 #this charactor is in one of the font

                                # if charactor is not in any font
                                if word_in_file==0:
                                    for k in range(len(font_list_actial)) :
                                        if b_font_loop == 1:
                                            break
                                        for p in range(len(font_list_actial[k])) :
                                            if actual_words[i][j] == font_list_actial[k][p] and shown_words[i][j] != font_list_shown[k][p]:
                                                font_list_actial.append(actual_words[i][j])
                                                font_list_shown.append(shown_words[i][j])
                                                b_font_loop = 1
                    total_font=total_font+len(font_list_actial)
                    extra_font=1

            #print "Need " + str(total_font + extra_font) + " font file"


            ########### store into a txt file ###########
            n1,n2=filename.split('.')
            store_file_name = path + '/' + n1 + '_result.txt'
            #print '****', store_file_name
            text_file = open(store_file_name, "w")
            for l_index in range(len(text_loop_n)) :
                text_file.write("%s " % text_loop_n[l_index])
                text_file.write("%s " % text_similarities[l_index])
                text_file.write('"'+list_exchange_word_1[l_index] + '" -> "' + list_exchange_word_2[l_index] + '"\n')
            #text_file.write('Needs ' + str(total_font + extra_font) + ' font files\n')
            text_file.close()
            if n_break==1:
                text_file = open(store_file_name, "a")
                text_file.write("Can't find a match within 40 exchanges\n")
                text_file.close()
