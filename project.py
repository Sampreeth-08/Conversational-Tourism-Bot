
from collections import defaultdict
from collections import Counter
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from sklearn.manifold import TSNE

import re
import os
import math
import nltk
# nltk.download('omw-1.4')
import numpy as np
import heapq
import matplotlib.pyplot as plt
from preprocessor import *



path="data"
mapping=defaultdict(int)
count=0
flist=os.listdir(path)
for i in flist:
  count=count+1
  mapping[i]=count

inverted_index = defaultdict(list)

term_frequencies = defaultdict(lambda:defaultdict(lambda:0))      # 2D dictionary that stores term frequency(tf) wd_count
doc_frequencies = defaultdict(lambda:0)                           # 1D dictionary that stores document frequency(df) w_count

docs = 0                       # represents total number of docs in the collection
fileList = []
fileList = os.listdir(path)
d="data"
for i in fileList:
    docs = docs+1
    # meta_data(d,i)
    pre_processed = pre_process(path+'/'+i)
    lemma_list = tokenise(pre_processed)

    for element in lemma_list:
      element = numberTowords(element)
      inverted_index[element].append(mapping.get(i))
      term_frequencies[mapping[i]][element] += 1
      doc_frequencies[element] = doc_frequencies[element] + 1

tf = defaultdict(lambda:defaultdict(lambda:0.0))
idf = defaultdict(lambda:0.0)

for i in term_frequencies:
  for j in term_frequencies[i]:
    temp = term_frequencies[i][j]
    tf[i][j] = 1 + math.log((1 + temp),10)

for j in doc_frequencies:
  temp = 1 + doc_frequencies[j]
  idf[j]= math.log((docs/temp),10)
  
updated_index = defaultdict(lambda:defaultdict(lambda:0.0))

for i in term_frequencies:
  for j in term_frequencies[i]:
    updated_index[i][j] = tf[i][j] * idf[j]

# print(updated_index)

vocab = []
for i in inverted_index:
  vocab.append(i)
  
# print(len(vocab))

def magnitude(v):
  n = len(v)
  mag = 0
  for i in v:
    mag = mag + v[i]*v[i]
  mag = mag **0.5
  return mag

def generate_vector(q_terms):
  q_vector = defaultdict(lambda:0.0)
  q_tf = Counter(q_terms)
  for i in q_terms:
    q_vector[i] = (1 + math.log((1 + q_tf[i]),10))*(math.log((docs/(1+doc_frequencies[i])),10))
  return q_vector

def centroid(doc_list):
  print(doc_list)
  sumd = 0
  d_list = []
  centroid_vector = defaultdict(lambda:0.0)
  #calculating centroid
  for w in vocab:
    for d in doc_list:
      if w in updated_index[d]:
        centroid_vector[w] = centroid_vector[w] + updated_index[d][w]
        # sumd = sumd + updated_index[d][w]
  #normalising the centroid vector
  n = len(doc_list)
  for i in centroid_vector:
    centroid_vector[i] = centroid_vector.get(i)/n
  
  return centroid_vector

def similarity(q_vector):
  cosine = 0
  scores = []
  q_mag = magnitude(q_vector)
  for d in updated_index:
    d_mag = magnitude(updated_index[d])
    product = 0
    for w in q_vector:
      # if(q_vector[w]!=0):
      product = product + (q_vector[w] * updated_index[d][w])
    cosine = product/(q_mag * d_mag)
    scores.append((cosine,d))
  topmost = heapq.nlargest(k,scores)
  return topmost

def display_result(topmost):

    print("\nThe top ",k," results are :")
    print("DocID \t Document Name")
    for i in range(k):
        # print(len(topmost))
        # print(len(topmost[i]))
        dID = topmost[i][1]
        for j in mapping.items():
            if(j[1]==dID):
                if(j[1] in rel_docs):
                    print("*",j[1],"\t",j[0])         # j[0] contains doc name and j[1] contains docID
                # else:
                #   print(j[1],"\t",j[0]) 
                # break;
    
    for i in range(k):
        # print(len(topmost))
        # print(len(topmost[i]))
        dID = topmost[i][1]
        for j in mapping.items():
            if(j[1]==dID):
                if(j[1] not in rel_docs):
                    print(j[1],"\t",j[0])
          

def feedback(topmost):

  output=[]
  rel = []
  nrel = []
  for i in topmost:
    output.append(i[1])
    

  u_input = input("\nEnter the relevant docIDs: ").split()
#   u_input="34 1294 35".split()
  
  for i in u_input:
    rel.append(int(i))
  
  nrel = set(output)-set(rel)

  return rel,list(nrel)


def pr_curve(res):
  precision = list()
  recall = list()
  map_val = 0

  rel_total = 1000
  rel_retrieved = 0
  retrieved_docs =0
  relevancy = 0

  i = 0
  for i in range(0,k):
    retrieved_docs = i+1
    
    if(res[i][1] in rel_docs):
      rel_retrieved += 1
      relevancy = 1
    else:
      relevancy = 0

    p_val = rel_retrieved/retrieved_docs
    r_val = rel_retrieved/rel_total
    map_val += p_val * relevancy

    precision.append(p_val)
    recall.append(r_val)
    i += 1

  print("\nMean Average Precision(MAP) for the above query is: ", map_val/rel_retrieved)
  plt.plot(recall,precision)
  plt.xlabel('Recall')
  plt.ylabel('Precision')
  plt.title("PRECISION-RECALL CURVE")
  plt.show()
  
def tnse_plot(rel_docs,non_rel_docs,query):
  tnse = TSNE(n_components=2, perplexity=3, random_state=0)

  data = []
  labels =[]

  for d in rel_docs:
    d_vector = []
    for w in vocab:
      d_vector.append(updated_index[d][w])
    data.append(d_vector)
    labels.append(0)
  
  for d in non_rel_docs:
    nd_vector = []
    for w in vocab:
      nd_vector.append(updated_index[d][w])
    data.append(nd_vector)
    labels.append(1)

  vec = []
  for w in vocab:
    vec.append(query[w])
  data.append(vec)
  labels.append(2)

  transformed_data = tnse.fit_transform(np.array(data))
  k = np.array(transformed_data)
  t = ("Relevant", "Non Relevant", "Query")
  plt.scatter(k[:, 0], k[:, 1], c=labels, s=60, alpha=0.8, label="Violet=Rel\nAqua=NonRel\nYellow=query")
  plt.title("TNSretrieved_docsE plot")
  plt.legend()
  # plt.grid(True)
  plt.show()
  

def find_result(query):
 
  qtokens = pre_process_query(query)
  q_vector = generate_vector(qtokens)
  q_new = defaultdict(lambda:0.0)

  for i in range(iterations):
    if(i==0):
      q_new = q_vector
    else:
    #   print("\nRelevance Feedback ",i+1,"\n")

      rel = centroid(rel_docs)
      non_rel = centroid(non_rel_docs)

      for l in rel:
        rel[l] = rel.get(l) * beta

      for j in non_rel:
        non_rel[j] = non_rel.get(j) * gamma
      
      for k in q_old:
        q_old[k] = q_old[k] * alpha
      
      #computing modified query vector
      for w in vocab:
        q_new[w] = q_old[w] + abs(rel[w] - non_rel[w])

    res = similarity(q_new)
    print(res)
    display_result(res)
    if iterations==1:
        r, nr = feedback(res)

        # updating the list of relevant documents, 
        # r contains the docIDs entered by the user in this iteration
        for d in r:
            rel_docs.add(d)

        # for storing the non-relevant documents of this iteration
        nr_current = []

        for d in nr:
            if(d not in rel_docs):
                non_rel_docs.add(d)
                nr_current.append(d)
        
        print("\nRelevant docIDs uptil now for the user given query: ",rel_docs)

        pr_curve(res)
        print("TNSE plot for iteration",i," :-\n")

        # print(r,nr_current,q_new)
        tnse_plot(r,nr_current,q_new)
        
        #after the end of iteration, the modified query vector now becomes old
        q_old = q_new
    else:
        break


alpha = 1
beta = 0.7
gamma = 0.25

iterations=1
k=10

rel_docs = set()
non_rel_docs = set()
# find_result(query4)
it=True
round=0
while it == True:
    if(round==0):
        query = input("\nPlease enter your query: ")
    else:
        query = input("\nPlease enter your Expanded query: ")
    find_result(query)
    # it=False
    # print("To continue, press 1")
    # print("To exit, press 0")
    ip=int(input("To continue, press 1\nTo exit, press 0: "))
    if(ip==1):
        continue
    if(ip==0):
        it=False
    round+=1