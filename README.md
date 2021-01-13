# language-model-are-open-knowledge-graph-turkish
Language models are open knowledge graphs

A non official reimplementation of [Language models are open knowledge graphs](https://arxiv.org/abs/2010.11967)

We used stanza nlp in the match stage, cause Spacy nlp does not have Turkish language support.
## Entity linker for Map section
We have created a folder named wiki in wiki_data to extract Entity Disambiguation and Entity Linking. 

```
.
├── wiki_data
|   ├── wiki
|   ├── w2v
```
### Extracting a Wikipedia dump
For all Wikipedia database dumps: [Wikipedia dumps](https://dumps.wikimedia.org/). 

The script is invoked with a Wikipedia dump file as an argument. Use the article dumps which are available as http://dumps.wikimedia.org/trwiki/latest/trwiki-latest-pages-articles.xml.bz2 for turkish language. This is provide `xml.bz2` files that need processing. This file must be inside the wiki folder.

A tool that does this is called [WikiExtractor](https://github.com/attardi/wikiextractor). This tool takes as an input a Wikipedia dump and spits out files that are required for our package. This folder must be inside the wiki folder.

Run the following command inside the wiki file. This process takes a long time. After that, wiki_disambiguation_pages.txt file is obtained. This file must be inside the wiki folder.

```
python wikiextractor/WikiExtractor.py ./trwiki-latest-pages-articles.xml.bz2 --links --filter_disambig_pages --processes 1 --bytes 1G
```
### Extracting Wiki id and name mapping
Use [Wikimapper](https://github.com/jcklie/wikimapper#create-your-own-index) for Wiki id and name mapping. This package can be installed via `pip`
```
pip install wikimapper
```
Run the following two commands to download data.
```
$ wikimapper download trwiki-latest --dir data
```
```
$ wikimapper create trwiki-latest --dumpdir data --target data/index_trwiki-latest.db
```
Last command provides a database for id name mapping. Run the db2txt code inside the wiki file to save them as a txt file.

#### Generate p(e|m) index
Now that we have extracted the necessary data from our Wikipedia corpus, we may create the p(e|m) index. We instantiate a Wikipedia class that loads the wikipedia id/name mapping, disambiguation file.

```
wiki_version = "wiki/"
base_url = "wiki_data/"
wikipedia = Wikipedia(base_url, wiki_version)
```
After that, we instantiate a WikipediaFreq class that loads to create a database with the data we extract.

```
wiki_freq = WikipediaFreq(base_url, wiki_version, wikipedia)
wiki_freq.compute_wiki()
wiki_freq.store()
```
### Training Wikipedia2Vec embeddings
Training new embeddings is based on the [Wikipedia2Vec](https://wikipedia2vec.github.io/wikipedia2vec/) package. Please make sure that the Wikipedia dump is still zipped and thus has the extensions .xml.bz2. The two scripts are located in wiki_data/w2v. You first run preprocess.sh which requires you to enter the location of your Wikipedia dump. After this is done, you can run train.sh which will train a Wikipedia2Vec model and store it in the required word2vec format.

## Execute MAMA(Match and Map) section
First add files in the example folder in txt format for the input text and for the output text.
```
$ python extract.py examples/ornek_metin.txt examples/ornek_cikti.txt
```
## Environment setup
This repo is run using virtualenv with conda
```
$ conda create -n venv python=3.6.9
$ conda activate venv
$ pip install -r requirements.txt
```

