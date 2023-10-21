import nltk
import re
from num2words import num2words

# nltk.download('omw-1.4')

from nltk.corpus import stopwords
# nltk.download('stopwords')

# nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer

lm = WordNetLemmatizer()

def numberTowords(word):
  if(word.isnumeric()):
    return num2words(word)
  else:
    return word
  
  
def removeStop(tokens):
  stop = set(stopwords.words('english'))
  f_tokens = []
  
  for w in tokens:
    if w not in stop:
      f_tokens.append(w)
  
  return f_tokens


def tokenise(docs):
  i = 0
  lem_words = []

  for k in docs:
    tokens = k.split()
    f_tokens = removeStop(tokens)

    for j in f_tokens:
      lem_words.append(lm.lemmatize(j))
    
  return lem_words


def pre_process(file):
  f = open(file,'r',encoding="ISO-8859-1")
  data = f.readlines()
  docs = []

  for sent in data:
    sent = re.sub(r'[\.•,;:!#=?$%^&*_~><\(\)\{\}\[\]\"\'\|]','',sent)
    docs.append(sent.lower())
  return docs


def pre_process_query(query):
  query = (re.sub(r'[\.•,;:?!#=$%^&*_~><\-\(\)\{\}\[\]\"\']','',query)).lower()

  q_tokens = []

  temp = removeStop(query.split())

  for j in temp:
    q_tokens.append(lm.lemmatize(j))

  q_terms = []

  for i in q_tokens:
    q_terms.append(numberTowords(i))

  return q_terms