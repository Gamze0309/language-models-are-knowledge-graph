import os
from time import time

import numpy as np
from numpy import float32 as REAL
from numpy import zeros

from REL.db.base import DB



class GenericLookup(DB):
    def __init__(
        self,
        name,
        save_dir,
        table_name="wiki",
        columns={"emb": "blob"},
    ):
        """
        Args:
            name: name of the embedding to retrieve.
            d_emb: embedding dimensions.
            show_progress: whether to print progress.
        """
        path_db = os.path.join(save_dir, f"{name}.db")

        self.name = name
        self.table_name = table_name
        self.columns = columns
        self.db = self.initialize_db(path_db, table_name, columns)
        
        
    def wiki(self, mention, table_name, column_name="p_e_m"):
        g = self.lookup_wik(mention, table_name, column_name)
        return g

    def load_wiki(self, p_e_m_index, mention_total_freq, batch_size=5000, reset=False):
        if reset:

            self.clear()

        batch = []
        start = time()

        for i, (ment, p_e_m) in enumerate(p_e_m_index.items()):
            p_e_m = sorted(p_e_m.items(), key=lambda kv: kv[1], reverse=True)
            batch.append((ment, p_e_m, ment.lower(), mention_total_freq[ment]))

            if len(batch) == batch_size:
                print("Another {}".format(batch_size), time() - start)
                start = time()
                self.insert_batch_wiki(batch)
                batch.clear()

        if batch:
            self.insert_batch_wiki(batch)

        self.create_index()
