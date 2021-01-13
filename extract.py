from transformers import BertModel, AutoModel, AutoTokenizer
import argparse
import stanza
import nltk
from match import parse_sentence
from mapper import Map,deduplication
import json

#stanza.download('tr')

parser = argparse.ArgumentParser(description='Process lines of text corpus into knowledgraph')
parser.add_argument('input_filename', type=str, help='text file as input')
parser.add_argument('output_filename', type=str, help='output text file')
parser.add_argument('--language_model',default='dbmdz/bert-base-turkish-cased')
parser.add_argument('--threshold', default=0.003, 
                        type=float, help="Any attention score lower than this is removed")

args = parser.parse_args()
language_model = args.language_model
input_filename = args.input_filename
output_filename = args.output_filename

if __name__ == "__main__":
    nlp = stanza.Pipeline('tr')
    tokenizer = AutoTokenizer.from_pretrained(language_model)
    model = BertModel.from_pretrained(language_model)
    output_map = []
    with open(input_filename, 'r') as f, open(output_filename, 'w') as g:
        data = f.read().replace('\n', '')
        sentences_list = nltk.tokenize.sent_tokenize(data)
        for sentence in sentences_list:
            valid_triplets = []
            for triplets in parse_sentence(sentence, nlp, tokenizer, model):
                valid_triplets.append(triplets)
            if len(valid_triplets) > 0:
                # Map
                mapped_triplets = []
                for triplet in valid_triplets:
                    head = triplet['h']
                    tail = triplet['t']
                    relations = triplet['r']
                    conf = triplet['c']
                    if conf < args.threshold:
                        continue
                    mapped_triplet = Map(head, relations, tail)
                    if 'h' in mapped_triplet:
                        mapped_triplet['c'] = conf
                        mapped_triplets.append(mapped_triplet)
                output = {'sentence': sentence, 'map': deduplication(mapped_triplets) }
                g.write(str(output))
