import os
from urllib.parse import unquote

"""
Class responsible for loading Wikipedia files. Required when filling sqlite3 database with e.g. p(e|m) index.
"""


class Wikipedia:
    def __init__(self, base_url, wiki_version):
        self.base_url = base_url + wiki_version
        # if include_wiki_id_name:
        self.wiki_disambiguation_index = self.generate_wiki_disambiguation_map()
        print("Loaded wiki disambiguation index")
        self.wiki_id_name_map = self.gen_wiki_name_map()
        print("Loaded entity index")

    def trim1(self,s):
        return s.replace("^%s*(.-)%s*$", "%1")


    def first_letter_to_uppercase(self,s):
        if len(s) < 1:
            return s
        if len(s) == 1:
            return s.upper()
        return s[0].upper() + s[1:]

    def preprocess_ent_name(self, ent_name):
        """
        Preprocesses entity name.

        :return: Preprocessed entity name.
        """
        ent_name = ent_name.strip()
        ent_name = self.trim1(ent_name)
        ent_name = ent_name.replace("&amp;", "&")
        ent_name = ent_name.replace("&quot;", '"')
        ent_name = ent_name.replace("_", " ")
        ent_name = self.first_letter_to_uppercase(ent_name)
        
        return ent_name

    def ent_wiki_id_from_name(self, entity):
        """
        Preprocesses entity name and verifies if it exists in our KB.

        :return: Returns wikiID.
        """

        entity = self.preprocess_ent_name(entity)
        if not entity or (entity not in self.wiki_id_name_map["ent_name_to_id"]):
            return -1
        else:
            return self.wiki_id_name_map["ent_name_to_id"][entity]

    def generate_wiki_disambiguation_map(self):
        """
        Generates disambiguation index.

        :return: disambiguation index
        """

        wiki_disambiguation_index = {}
        path = os.path.join(self.base_url, "wiki_disambiguation_pages.txt")

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:
            for line in f:
                line = line.rstrip()
                if '<doc id' in line:
                    parts = line.split("\t")[0].split('doc id=')[1].split('"')
                    assert int(parts[1])
                    wiki_disambiguation_index[int(parts[1])] = 1
        return wiki_disambiguation_index

    def gen_wiki_name_map(self):
        """
        Generates wiki id/name and name/id index.

        :return: disambiguation index
        """

        wiki_id_name_map = {"ent_name_to_id": {}, "ent_id_to_name": {}}
        path = os.path.join(self.base_url, "wiki_name_id_map.txt")
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip()
                parts = line.split(" ")
                ent_wiki_id = int(parts[0])
                ent_name = unquote(parts[1])

                if ent_wiki_id not in self.wiki_disambiguation_index:
                    wiki_id_name_map["ent_name_to_id"][ent_name] = ent_wiki_id
                    wiki_id_name_map["ent_id_to_name"][ent_wiki_id] = ent_name

        return wiki_id_name_map