#!/usr/bin/python 
# Copyright (c) 2014-2015 Ken Wu
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#
# -----------------------------------------------------------------------------
#
# Author: Ken Wu
# Date: 2014 Dec - 2015
import operator
import logging
import os
import shutil
import json
import Stemmer
import string
import random
import sys
import operator
import ntpath
import hashlib
import re
import copy
from textblob import TextBlob,Word
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from time import gmtime, strftime
import time
from os import listdir
from os.path import abspath, join, dirname, isfile
from collections import Counter
from nltk.corpus import wordnet as wn
from scrapy.selector import Selector
import xml
import xml.etree
import xml.etree.ElementTree as ET

os.environ['TZ'] = 'UTC'
STOP_WORDS=[u'&', u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between', u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now']
STOP_WORDS_DICT = Counter(STOP_WORDS)
alphabet = 'abcdefghijklmnopqrstuvwxyz'
def get_logger(name):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(name+"--")
    return logger

def copy_dictionary(d):
    dd = {}
    for k, v in d.items():
        dd[k]=v
    return dd

def is_string(x):
    return isinstance(x, basestring)

def is_num(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

###Algorithms part ####################################

#return from 0 to 100 in two decimals representing the percentage
def divide_a_by_b(portion, total, round_to=2):
    portion=float(portion)
    total=float(total)
    return round(portion/total, round_to)
    
def get_percentize(portion, total, round_to=2):
    divide_value = divide_a_by_b(portion, total, round_to)
    return (divide_value * 100.0)

'''
    This method computes the cross-product of all lists, x:
    For example, if x has three lists where x1 as [1,2,3] and x2 as [a,b] and x3 as [r,q,s]
    then it should return:
    [1,a,r],[1,b,r],[2,a,r],[2,b,r],[3,a,r],[3,b,r]
    [1,a,q],[1,b,q],[2,a,q],[2,b,q],[3,a,q],[3,b,q]
    [1,a,s],[1,b,s],[2,a,s],[2,b,s],[3,a,s],[3,b,s]
'''
def cross_product_on_all_lists(m):
    return _cross_product_on_all_lists(m, 0)

def _cross_product_on_all_lists(m, pos):
    if pos + 1 < len(m):
        m[pos+1] = cross_product_on_two_lists(m[pos], m[pos+1])
        return _cross_product_on_all_lists(m, pos+1)
    else:
        return m[pos]

def cross_product_on_two_lists(x,y):
    if not x:
        return [y]
    if not y:
        return [x]
    r = list()
    xx = copy.deepcopy(x)
    yy = copy.deepcopy(y)
    if not is_list(xx):
        xx = [xx]
    if not is_list(yy):
        yy = [yy]
    for a in xx:
        for b in yy:
            r.append(combine_two_lists(a,b))
    return r

def combine_two_lists(a,b):
    l = copy.deepcopy(a)
    if not is_list(a):
       l = list()
       l.append(a) 
    if is_list(b):
        for x in b:
            l.append(x)
    else:
        l.append(b)
    return l
    

def does_list_a_all_exist_in_list_b(a, b, f):
    for x in a:
        this_x_founded_in_b=False
        for y in b:
            if f(x,y):
                this_x_founded_in_b=True
        if not this_x_founded_in_b:
            return False
    return True

def convert_list_to_dict(l):
    return Counter(l)   #converts to dictionary

def get_categories_with_n_highest_score(categories_org, n=1):
    log.debug("Getting categories: %s with %s highest score..." % (categories_org,n)) 
    categories=copy_dictionary(categories_org)
    indcies=list()
    for i in range(0, n):
        if not categories:
            break
        k, value = max(categories.iteritems(), key=operator.itemgetter(1))
        indcies.append((k,value))   #append both the key and value
        del categories[k]
    return indcies

def get_sorted_turple_on_dict_by_value(d, reverse_the_result=False):
    sorted_x = sorted(d.items(), key=operator.itemgetter(1), reverse=reverse_the_result)
    return sorted_x
def generate_token(len):
    datetimestr=get_datetime()
    #pydevd.settrace()
    token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(len))
    return datetimestr+'_'+token

def map_keys_to_the_values(values_without_key, keys):
    new_key_value_list=list()
    #keys=map(lambda x: x.replace('\'', '"'), keys)
    for value in values_without_key:
        new_tuple=list()
        i=0
        obj = {}
        for item in value:
            obj[keys[i]] = item if is_string(item) else str(item)
            i+=1
        new_key_value_list.append(obj)
    return new_key_value_list

def is_list(x):
    return type(x) is list

def is_array(o):
    if is_list(o) or type(o) is tuple:
        return True
    else:
        return False

def is_in_the_list(l, search_item, nth=None):
    index=0
    for item in l:
        g=item[nth] if nth != None else item
        if g==search_item:
            return index
        index += 1
    return None

def swap(o1, o2):
    t=o2
    o2=o1
    o1=t
    return o1, o2

def calculate_two_words_distance(w1, w2):
    if len(w1)>len(w2):
        w1,w2=swap(w1,w2)
    dif_count=0
    for l in w1:
        if not l in w2:
            dif_count += 1
    dif_count += (len(w2) - len(w1))
    return dif_count

def stem_word_all_all(ll):
    new_l = list()
    for l1 in ll:
        l1 = stem_word_all(l1)
        new_l.append(l1)
    return new_l

def stem_word_all(l):
    return map((lambda x: stem_word(x)), l)    #stem all words

def small_captalize_all(l):
    return map((lambda x: x.lower()), l)    #stem all words

##Cookie related ########################################
def remove_non_valid_chars(line):
    if line:
        line = line.replace('\n', '')
    return line

##Date/time part ########################################
def add_seconds_to_datetime(d, num_of_secs):
    return d + timedelta(seconds=int(num_of_secs))

'''This will return the datetime object
'''
def get_time_now():
    return datetime.now()

def get_datetime():
    return strftime("%Y%m%d%H%M%S", gmtime())
def convert_date_to_s(d, format='%Y%m%d'):
    return d.strftime(format)
def convert_datetime_to_s(d, format='%Y-%m-%d %H:%M:%S'):
    return d.strftime(format)
def convert_s_to_date(s, format='%Y%m%d'):
    return datetime.strptime(s, format)

def convert_UTC_time_zone_to_Local_time_zone(utc_time, local_time_zone):
    return datetime.fromtimestamp( time.mktime(datetime.strptime(
                                    utc_time, "%Y-%m-%d %H:%M:%S").timetuple()) , pytz.timezone(local_time_zone))

def enum(**enums):
    return type('Enum', (), enums)

#local_time_zone can be 'America/New_York'
def convert_UTC_time_zones_to_Local_time_zones_in_bulk(map_results, time_col_name, local_time_zone='UTC'):
    if map_results:
        for m in map_results:
            utc_time = m[time_col_name]
            local_time = convert_UTC_time_zone_to_Local_time_zone(utc_time, local_time_zone)
            m[time_col_name] = str(local_time) + ' ' + local_time_zone
            
    return map_results

##DEBUG related #########################################
def debug():
    try:
        if not r'/usr/local/share/pysrc' in sys.path:
            sys.path.append(r'/usr/local/share/pysrc') #assuming this is the pydev installation path
        import pydevd
        pydevd.settrace()
    except: 
        pass

##File/io part ########################################
def get_file_name_from_path(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_dir(path):
    head, tail = ntpath.split(path)
    return head

def get_base(p):
    return join(abspath(dirname('__file__')), p)

def del_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        log.info("Dir: %s removed!" % dir_path) 

def clear_dir(dir_path):
    del_dir(dir_path)
    os.mkdir(dir_path)       

def del_file(path):
    if os.path.exists(path):
        os.remove(path)
        log.info("File: %s removed!" % path)

def ensure_dir_exists(dir_path, create_multiple=False):
    if not os.path.exists(dir_path):
        if create_multiple:
            os.makedirs(dir_path)
        else:
            os.mkdir(dir_path)
        log.info("Dir: %s created!" % dir_path)

def is_path_exist(p):
    return os.path.exists(p)

def read_lines(file_path, is_critical=False, as_single_line=False):
    file = None
    try:
        file = open(file_path, 'r')
        lines = file.readlines()
        if as_single_line:
            return reduce(lambda x, y: x+ '' +y, lines)
        else:
            return lines
    except:
        errro_str='Failed reading the file: %s' % file_path
        if is_critical:
            log.error(errro_str)
        else:
            log.info(errro_str)
        return None
    finally:
        if file:
            file.close()

def get_files_only_from_dir(dir_p):
    return [ f for f in listdir(dir_p) if isfile(join(dir_p,f)) ]

def get_file_modified_time(p):
     return time.ctime(os.path.getmtime(p))

def read_contents_from_dir(dir_p):
    onlyfiles = get_files_only_from_dir(dir_p)
    contents = []
    for file in onlyfiles:
        lines_list=read_lines(dir_p+'/'+file)
        lines=reduce(lambda x,y: x+y,lines_list)
        contents.append(lines)
    return contents


''' 
refresh_seconds=0 means to overwrite the file immediately.  
Otherwise, overwrite it only if the modification time from today is larger than the refresh_days
'''
def write_to_local(p, content, refresh_seconds=0):
    if is_path_exist(p):
        if refresh_seconds>0:
            modified_dt=convert_s_to_date(get_file_modified_time(p), format="%a %b %d %H:%M:%S %Y")
            modified_dt_plus_refresh = add_seconds_to_datetime(modified_dt, refresh_seconds)
            now=get_time_now()
            if now < modified_dt_plus_refresh:
                return
    d=get_dir(p)
    ensure_dir_exists(d, create_multiple=True)
    f = open(p,'w')
    f.write(content)
    f.close()

##html part ########################################
def enclose_tag (htm, tag):
    return '<%s>%s</%s>'%(tag, htm, tag)

def remove_tag_bracket(t):
    s = t
    bracket_l = index_of(s, '[')
    bracket_r = index_of(s, ']')
    if bracket_l and bracket_r:
        s = s[0:bracket_l-1] + s[bracket_r+1:]
    return s
def remove_tag(t):
    s = ''.join(xml.etree.ElementTree.fromstring(t).itertext())
    return s

def remove_tags(text):
    if is_list(text):
        removed_str = ''
        for e in text:
            try:
                removed_str += remove_tag(e)
            except:
                pass
        return removed_str
    else:
        return remove_tag(text)

##Json part ########################################   
def get_json_value(json_str, field_name):
    decoded = json.loads(json_str)
    return decoded[field_name]

def dumps(data):
    return json.dumps(data)

## Language itselt ##################################
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

##Natural language processing part ########################################   
stemmer = Stemmer.Stemmer('english')

def syn_set(s):
    ss = wn.synsets(s) 
    return ss if ss else None

def get_hyper(s):  
    ss = syn_set(s)
    hyper = lambda s: s.hypernyms()  
    return map(lambda x: x._lemma_names[0], list(ss[0].closure(hyper))) if ss else None    #just take the first synset as this is the most meaningful
def get_hypo(s):
    ss = syn_set(s)
    hypo = lambda s: s.hyponyms()
    return map(lambda x: x._lemma_names[0], list(ss[0].closure(hypo))) if ss else None    #just take the first synset as this is the most meaningful

def get_all_stop_words():
    return STOP_WORDS_DICT

def stem_all_words(word_list):
    stemmed_words = list()
    for word in word_list:
        stemmed_words.append(stemmer.stemWord(word))
    return stemmed_words

def stem_word(word):
    return stemmer.stemWord(word)

def get_word_tag_str(single_word):
    return str(TextBlob(single_word).tags[0][1])

def is_known_word(single_word):
    return is_correct(get_word_tag_str(single_word))

def is_correct(ww, orig_word):
    return len(ww)==1 and ww[0][1]==1.0 and orig_word==ww[0][0]
def is_known_word(single_word):
    c=Word(single_word).spellcheck()
    if is_correct(c, single_word):
      print str(c) + ' --- ' + single_word
    return is_correct(c, single_word)

def is_verb(w):
    t =get_word_tag_str(w)
    return len(t)>1 and t[:2] == 'VB' 

def edits1(word):
    if len(word) < 3:
        return set([])
    splits     = [(word[:i], word[i:]) for i in range(1, len(word))]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1))

def get_similar_words_with_word_tags(word, deep_level=1):
    if deep_level==1:
        ws=edits1(word)
    else:
        ws=edits2(word)
    ws = filter(lambda x: is_known_word(x), ws)
    ws = map(lambda x: (x, get_word_tag_str(x)), ws)
    return ws

def tokenize(query, remove_punctuation=False):
    words = query.split( );
    words = map(lambda x: x.lower().strip(), words)
    if remove_punctuation:
        words = map(lambda x: x.replace('(', '').replace(')', '').replace(',', '').replace('.', '').replace('?', ''), words)
        #now remove the '[xxx]' from the strings
        words = map(lambda x: remove_tag_bracket(x), words)
    return words

#it returns all the words count of a given crawler
# The first parameter is raw_html_doc
# The second parameter is the customized extract function pointer, for example, wiki_extract_html_contents
def words_sum_stats(html_doc, extract_function):
    extracted_html_content = extract_function(html_doc)
    extracted_raw_text_content = remove_tags(extracted_html_content)
    tokenize_words = tokenize(extracted_raw_text_content, remove_punctuation=True)
    removed_stopwords_words=filter((lambda w: not w in get_all_stop_words()), tokenize_words)
    stemmed_words=stem_all_words(removed_stopwords_words)
    
    #Now doing the simple word count statstic
    d=dict()
    for w in stemmed_words:
        if w in d:
            d[w] = d[w] + 1
        else:
            d[w] = 1
    d = get_sorted_turple_on_dict_by_value(d, reverse_the_result=True)
    return d

##Torando package util methods ############################################
def get_httpfile(httpfile, field):
    value_str = httpfile[field]
    #if field == 'body':
    #    if value_str[0:5] == 'str: ':   #torando tends to prepend 'str: ' to the uploaded content, so i stripped it out
    #        value_str = value_str[5:]
    return value_str
## String processing part #################################################
def sentences(text):
    blob=TextBlob(text)
    return blob.sentences

def convert_to_str(s):
    return str(s)

def rindex(str, s):
    try:
        return str[str.rindex(s)+1:].strip()
    except:
        return str       

def extract_head_tail(str, n=50, max_intact=150):
    if len(str) < max_intact or n > len(str)/2:
        return str
    else:
        return str[0:n]+'..........'+str[len(str)-n:len(str)]

def extract_head_tail_in_bulk(map_results, category_index):
    if map_results:
        for m in map_results:
            m[category_index] = extract_head_tail(m[category_index]) 
    return map_results


def generate_md5(s):
    if is_array(s):
        s = u''.join(s).encode('utf-8').strip()
    m = hashlib.sha224(s).hexdigest()
    return m

def get_line_and_md5_from_file(f):
    lines = read_lines(f, is_critical=True)
    all_contents_in_one_line = reduce(lambda x,y: x+y, lines)
    return (all_contents_in_one_line, generate_md5(all_contents_in_one_line))

def index_of(s, search_str, beg=0, end=None):
    try:
        if not end:
            end = len(s)
        return s.index(search_str, beg, end)
    except ValueError as e:
        return None

def unescape(s):
    s = convert_to_str(s)
    s = s.replace("%20", " ")
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s

def words(text): return re.findall('[a-z]+', text.lower())

##Reports related #############################################

#It is converting the datatable's draw to the offset which is suitable to the sql palace
def convert_draw_to_offset(draw, length):
    if is_string(draw):
        draw=int(draw)
    if is_string(length):
        length=int(length)
    if draw > 1 and length > 10:    #some bugs in the datalength script..so i have to hardcore it
        draw=draw-1
    return (draw) * length

def convert_to_offset_to_draw(offset, length):
    if is_string(offset):
        offset=int(offset)
    if is_string(length):
        length=int(length)
    return (offset / length) + 1

##SQL util stuffs #############################################
#cols must be a type of list
def columnize_in_sql_way(cols):
    if cols:
        if is_string(cols):
            return cols
        else:
            return reduce(lambda x,y: str(x)+','+str(y), cols)
    else:
        return '*'

def build_ordered_by_sql_clause(ordered_column, ordered_direction):
    sql_ordered_by_str=''
    if ordered_column:
        sql_ordered_by_str='ORDER BY ' + ordered_column
        if ordered_direction:
            sql_ordered_by_str+= ' ' + ordered_direction
    return sql_ordered_by_str

def _build_where_predicate_expr (pred):
    field = pred[0]
    operator = pred[1][0]
    value = pred[1][1]
    tokenized_value = value.split()
    if len(tokenized_value) > 1:
        return reduce(lambda x,y: field + ' ' + sqlize_a_value(operator, x) + ' and ' + field + ' ' + sqlize_a_value(operator, y)
                        , tokenized_value)   
    else:
        return field + ' ' + sqlize_a_value(operator, value)

def build_where_sql_clause(where_filter_dict):
    where_sql=''
    if where_filter_dict:
        if len(where_filter_dict) > 1:
            where_sql='where ' + reduce(lambda x,y: _build_where_predicate_expr(x) + ' and ' + 
                                        _build_where_predicate_expr(y), where_filter_dict.items())
        else:
            where_sql='where ' + _build_where_predicate_expr(where_filter_dict.items()[0])
    return where_sql

#basically enclose with a string if it is a not a number but missing a quote
def sqlize_a_value(operator, x):
    if is_num(x):
        return operator + x
    elif is_string(x):
        if operator.lower() == 'like':
            return operator + '\'%' + x +'%\''
        else:
            return operator + '\'' + x +'\''
    else:
        return str(x)


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Every customized crawler, xxx_extra_html_contents must provide the follow functions to filter out the html docs 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def wiki_extract_html_contents(raw_html):
    extracted = Selector(text=raw_html).xpath('//div[@id="mw-content-text"]/p').extract()
    return extracted

log = get_logger("Utils") 
