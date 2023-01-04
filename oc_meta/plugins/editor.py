#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED 'AS IS' AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.

from __future__ import annotations

import os

import yaml
from oc_ocdm import Storer
from oc_ocdm.graph import GraphSet
from oc_ocdm.prov import ProvSet
from oc_ocdm.reader import Reader
from rdflib import URIRef


class MetaEditor:
    def __init__(self, meta_config: str):
        with open(meta_config, encoding='utf-8') as file:
            settings = yaml.full_load(file)
        self.endpoint = settings['triplestore_url']
        self.base_dir = os.path.join(settings['output_rdf_dir'], 'rdf') + os.sep
        self.info_dir = os.path.join(settings['output_rdf_dir'], 'info_dir', 'creator') + os.sep
        self.base_iri = settings['base_iri']
        self.supplier_prefix = settings['supplier_prefix']
        self.resp_agent = settings['resp_agent']
        self.dir_split = settings['dir_split_number']
        self.n_file_item = settings['items_per_file']
        self.zip_output_rdf = settings['zip_output_rdf']
        self.reader = Reader()
        self.g_set = GraphSet(self.base_iri, supplier_prefix=self.supplier_prefix)
    
    def edit_entity(self, res, property: str, new_value: str|URIRef) -> None:
        self.reader.import_entity_from_triplestore(self.g_set, self.endpoint, res, self.resp_agent, enable_validation=False)
        if isinstance(new_value, URIRef):
            self.reader.import_entity_from_triplestore(self.g_set, self.endpoint, new_value, self.resp_agent, enable_validation=False)
        getattr(self.g_set.get_entity(res), property)(self.g_set.get_entity(new_value))
        provset = ProvSet(self.g_set, self.base_iri, self.info_dir, wanted_label=False)
        provset.generate_provenance()
        graph_storer = Storer(self.g_set, dir_split=self.dir_split, n_file_item=self.n_file_item, zip_output=self.zip_output_rdf)
        prov_storer = Storer(provset, dir_split=self.dir_split, n_file_item=self.n_file_item, zip_output=self.zip_output_rdf)
        graph_storer.store_all(self.base_dir, self.base_iri)
        prov_storer.store_all(self.base_dir, self.base_iri)
        graph_storer.upload_all(self.endpoint)
        self.g_set.commit_changes()