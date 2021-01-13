
from REL.db.generic import GenericLookup
from REL.wikipedia import Wikipedia
from REL.wikipedia_freq import WikipediaFreq
import sqlite3
from constant import invalid_relations_set
from gensim.models import Word2Vec
from gensim import models
import torch
import os
import numpy as np
from numpy import zeros
from numpy import float32 as REAL


sqlite_path = "wiki_data/wiki"
emb = GenericLookup("entity_word_embedding", save_dir=sqlite_path, table_name="wiki")

def Map(head, relations, tail, top_first=True, best_scores = True):
    if head == None or tail == None or relations == None:
        return {}
    head_p_e_m = emb.wiki(str(head), 'wiki')
    if head_p_e_m is None:
        return {}
    tail_p_e_m = emb.wiki(str(tail), 'wiki')
    if tail_p_e_m is None:
        return {}
    tail_p_e_m = tail_p_e_m[0]
    head_p_e_m = head_p_e_m[0]
    model = models.KeyedVectors.load_word2vec_format('wiki_data/wiki/wikipedia2vec_wv2vformat', binary=False)
    similarity = model.most_similar(relations[0], topn=1)[0][0]
    valid_relations = [ r for r in relations if r not in invalid_relations_set and r.isalpha() and len(r) > 0 ]
    valid_relations.append(similarity)
    if len(valid_relations) == 0:
        return {}

    return { 'h': head_p_e_m[0], 't': tail_p_e_m[0], 'r': '_'.join(valid_relations)  }

def deduplication(triplets):
    unique_pairs = []
    pair_confidence = []
    for t in triplets:
        key = '{}\t{}\t{}'.format(t['h'], t['r'], t['t'])
        conf = t['c']
        if key not in unique_pairs:
            unique_pairs.append(key)
            pair_confidence.append(conf)
    
    unique_triplets = []
    for idx, unique_pair in enumerate(unique_pairs):
        h, r, t = unique_pair.split('\t')
        unique_triplets.append({ 'h': h, 'r': r, 't': t , 'c': pair_confidence[idx]})

    return unique_triplets