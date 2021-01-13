import torch
import numpy as np
import sys, os
from transformers import BertModel, AutoModel, AutoTokenizer
import stanza
from collections import defaultdict
from multiprocessing import Pool
from copy import copy
from constant import invalid_relations_set



def check_relations_validity(relations):
    for rel in relations:
        if rel.lower() in invalid_relations_set or rel.isnumeric():
            return False
    return True

def global_initializer(nlp_object):
    global spacy_nlp
    spacy_nlp = nlp_object

def filter_relation_sets(params):
    triplet, id2token = params

    triplet_idx = triplet[0]
    confidence = triplet[1]
    head, tail = triplet_idx[0], triplet_idx[-1]
    if head in id2token and tail in id2token:
        head = id2token[head]
        tail = id2token[tail]
        relations = [ spacy_nlp(id2token[idx]).sentences[0].words[0].lemma  for idx in triplet_idx[1:-1] if idx in id2token ]
        if len(relations) > 0 and check_relations_validity(relations) and head.lower() not in invalid_relations_set and tail.lower() not in invalid_relations_set:
            return {'h': head, 't': tail, 'r': relations, 'c': confidence }
    return {}

def bfs(args):
    s, end, graph, max_size, black_list_relation = args
    visited = [False] * (max(graph.keys())+100) 
    
    found_paths = []

    visited[s] = True
    visited[end] = True

    path = [(s,0)]
    for i,conf in graph[s]:
        if visited[i] == False:
            for e, conf1 in graph[i]:
                if e == end:
                    found_paths.append(path+[(i, conf)]+[(e, conf1)])
    
    candidate_facts = []
    for path_pairs in found_paths:
        if len(path_pairs) < 3:
            continue
        path = []
        cum_conf = 0
        for (node, conf) in path_pairs:
            path.append(node)
            cum_conf += conf

        if path[1] in black_list_relation:
            continue

        candidate_facts.append((path, cum_conf))
    candidate_facts = sorted(candidate_facts, key=lambda x: x[1], reverse=True)
    return candidate_facts

def compress_attention(attention_matrix, tokenid2word_mapping):
    new_index = []
    prev = -1
    # isim tamlamalarını aynı array'in içine koyar.
    for idx, row in enumerate(attention_matrix):
        token_id = tokenid2word_mapping[idx]
        if token_id != prev:
            new_index.append([row])
            prev = token_id
        else:
            new_index[-1].append(row)
    new_matrix = []
    for row in new_index:
        new_matrix.append(np.mean(np.array(row), 0)) # isim tamlamaları için her bir kelimenin diziden ortalaması alınarak yeni bir dizi oluşturulur.
    new_matrix = np.array(new_matrix)
    attention_matrix = np.array(new_matrix).T
    #matrisin transpozu alındıktan sonra yine isim öbeklerinin ortalaması alınıp orijinal matris oluşturulur.
    prev = -1
    new_index=  []
    for idx, row in enumerate(attention_matrix):
        token_id = tokenid2word_mapping[idx]
        if token_id != prev:
            new_index.append( [row])
            prev = token_id
        else:
            new_index[-1].append(row)

    
    new_matrix = []
    for row in new_index:
        new_matrix.append(np.mean(np.array(row), 0))
    
    new_matrix = np.array(new_matrix)
    return new_matrix.T
    
def parse_sentence(sentence ,nlp, tokenizer, encoder):

    inputs, tokenid2word_mapping, token2id, noun_chunks  = create_mapping(sentence, nlp, tokenizer, return_pt=True)
    encoder.eval()
    with torch.no_grad(): #Matematiksel işlemlerin hızlı yapılmasını sağlar.
        outputs = encoder(**inputs, output_attentions=True) # attention oluşturur. Yani verilen vektördeki attention ağırlıklarına bakarak bir dizi matris döndürür.
    attention = outputs[2] #son katman dikkatinin ortalaması kullanılır. Çünkü son katman BERT düğünlerinde kümelerin varlığına karşılık gelir.
    attn = torch.mean(attention[0][-1], 0)
    attention_matrix = attn.detach().numpy() # matrisi tensorden çıkarır ve virgülden sonraki sayıları uzatır.
    attention_matrix = attention_matrix[1:-1, 1:-1] #diziden ilk ve son elemanı çıkarır. Çıkan dizi değerlerinin her bir elemanından ilk ve son elemanlarını çıkarır.
    merged_attention = compress_attention(attention_matrix, tokenid2word_mapping)

    graph = defaultdict(list) # dict nesnesinin KeyError vermesini önler
    for idx in range(0, len(merged_attention)):
        for col in range(0, len(merged_attention)):
            graph[idx].append((col, merged_attention[idx][col] ))
    
    tail_head_pairs = []
    for head in noun_chunks:
        for tail in noun_chunks:
            if head != tail:
                if (token2id[tail], token2id[head]) not in tail_head_pairs: # Cümle devrik olursa durum değişir.
                    tail_head_pairs.append((token2id[head], token2id[tail]))
    
    black_list_relation = set([ token2id[n]  for n in noun_chunks ]) #isim öbeklerinin id'si bir değişkene atılır.
    all_relation_pairs = []
    id2token = { value: key for key, value in token2id.items()}

    with Pool(10) as pool:
        params = [  ( pair[0], pair[1], graph, max(tokenid2word_mapping), black_list_relation, ) for pair in tail_head_pairs]
        for output in pool.imap_unordered(bfs, params):
            if len(output):
                all_relation_pairs += [ (o, id2token) for o in output ]
    triplet_text = []
    with Pool(10, global_initializer, (nlp,)) as pool:
        for triplet in pool.imap_unordered(filter_relation_sets, all_relation_pairs):
            if len(triplet) > 0:
                triplet_text.append(triplet)
    return triplet_text

def create_mapping(sentence, nlp, tokenizer , return_pt=True):

    token2id = {}
    token_ids = []
    tokenid2word_mapping = []
    doc = nlp(sentence)
    sentence_mapping,chunk_bin = create_noun_chunk(doc)
    for i in range(len(sentence_mapping)):
        token2id[sentence_mapping[i]] = len(token2id)
    

    for token in sentence_mapping:
        subtoken_ids = tokenizer(str(token), add_special_tokens=False)['input_ids']
        tokenid2word_mapping += [ token2id[token] ]*len(subtoken_ids) # Diziyi maskeler, dönen matris değerlerine tokenın id'sini atar.
        token_ids += subtoken_ids   

    outputs = {
            'input_ids': [tokenizer.cls_token_id] + token_ids + [tokenizer.sep_token_id],
            'attention_mask': [1]*(len(token_ids)+2),
            'token_type_ids': [0]*(len(token_ids)+2)
        }
    
    if return_pt:
        for key, value in outputs.items():
            outputs[key] = torch.from_numpy(np.array(value)).long().unsqueeze(0) #diziyi attention için tensorlere çevirir.
    return outputs, tokenid2word_mapping, token2id, chunk_bin    

def create_noun_chunk(doc):

    sentence_mapping = []
    chunk_bin = []
    c_id = 0
    
    for sentence in doc.sentences:
        for word in sentence.words:	
				
            rel = word.deprel
            nrel = ''
            nword = ''
            chunk = []
            chunk_text = []
            control = 0

            for nword0 in sentence.words: 
                if nword0.id == word.id + 1:
                    nrel = nword0.deprel
                    nword = nword0
            
            chunk_text.append(word.lemma)
            if word.deprel == 'nsubj' or word.deprel == 'obj' or word.deprel == 'obl' or word.deprel == 'compound':
                control = 1
            # start=word.misc.split('|')[0].split('=')[1]
            # end = word.misc.split('|')[1].split('=')[1]
            if word.id != len(sentence.words):
                while (nrel != 'sen' and nrel != 'root') or nword.xpos == 'Noun':
                    if nrel == 'det' or nrel == 'amod':
                        #end = nword.misc.split('|')[1].split('=')[1]
                        chunk_text.append(nword.lemma)
                    elif rel == 'det' or rel == 'amod' or rel == 'nmod:poss':
                        #end = nword.misc.split('|')[1].split('=')[1]
                        chunk_text.append(nword.lemma)
                    elif rel != 'nsubj' and rel != 'obj' and rel != 'cc' and word.xpos != 'Punc':
                        if nword.xpos == 'Noun':
                            #end = nword.misc.split('|')[1].split('=')[1]
                            chunk_text.append(nword.lemma)
                    
                    
                    currentWord = nword
                    rel = nrel
                    if nword.id == len(sentence.words) or chunk_text[-1] != nword.text:
                        break
                    
                    for nword0 in sentence.words: 
                        if nword0.id == currentWord.id + 1:
                            nrel = nword0.deprel
                            nword = nword0

            if len(sentence_mapping) == 0:
                chunk_text = " ".join(chunk_text)
                sentence_mapping.append(chunk_text)
                if len(chunk_text.split(' ')) > 1:
                    chunk_bin.append(chunk_text)
                elif control == 1:
                    chunk_bin.append(chunk_text)
                c_id +=1
            else:
                for cb in sentence_mapping:
                    cont = True
                    for c in chunk_text:
                        if cb.find(c) != -1:
                            cont = False
                            break
                if cont:
                    chunk_text = " ".join(chunk_text)
                    sentence_mapping.append(chunk_text)
                    if len(chunk_text.split(' ')) > 1:
                        chunk_bin.append(chunk_text)
                    elif control == 1:
                        chunk_bin.append(chunk_text)
                    c_id +=1

    return sentence_mapping, chunk_bin
