#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Arcangelo Massari <arcangelo.massari@unibo.it>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.

__author__ = 'Arcangelo Massari'

from typing import Tuple
import re

URI_TYPE_DICT = {
    'http://purl.org/spar/fabio/ArchivalDocument': 'archival document', 
    'http://purl.org/spar/fabio/Book': 'book', 
    'http://purl.org/spar/fabio/BookChapter': 'book chapter', 
    'http://purl.org/spar/doco/Part': 'book part', 
    'http://purl.org/spar/fabio/ExpressionCollection': 'book section', 
    'http://purl.org/spar/fabio/BookSeries': 'book series', 
    'http://purl.org/spar/fabio/BookSet': 'book set', 
    'http://purl.org/spar/fabio/DataFile': 'dataset', 
    'http://purl.org/spar/fabio/Thesis': 'dissertation', 
    'http://purl.org/spar/fabio/Journal': 'journal', 
    'http://purl.org/spar/fabio/JournalArticle': 'journal article', 
    'http://purl.org/spar/fabio/JournalIssue': 'journal issue', 
    'http://purl.org/spar/fabio/JournalVolume': 'journal volume', 
    'http://purl.org/spar/fr/ReviewVersion': 'peer_review', 
    'http://purl.org/spar/fabio/AcademicProceedings': 'proceedings', 
    'http://purl.org/spar/fabio/ProceedingsPaper': 'proceedings article', 
    'http://purl.org/spar/fabio/ReferenceBook': 'reference book', 
    'http://purl.org/spar/fabio/ReferenceEntry': 'reference entry', 
    'http://purl.org/spar/fabio/ReportDocument': 'report', 
    'http://purl.org/spar/fabio/Series': 'series', 
    'http://purl.org/spar/fabio/SpecificationDocument': 'standard', 
    'http://purl.org/spar/fabio/WebContent': 'web content'}


def split_ids(literal_values:str) -> str:
    return "\"%s\"" % "\" \"".join(literal_values.split("__")),

def create_metadata_output(results):
    header:list = results[0]
    output_results = [header]
    for result in results[1:]:
        output_result = list()
        for i, data in enumerate(result):
            if i == header.index('type'):
                beautiful_type = __postprocess_type(data[1])
                output_result.append((data[0], beautiful_type))
            else:
                output_result.append(data)
        output_results.append(output_result)
    return output_results, True

def __postprocess_type(types_uris:str) -> str:
    types_uris_list = types_uris.split(' ;and; ')
    types_uris_list.remove('http://purl.org/spar/fabio/Expression')
    if types_uris_list:
        type_uri = types_uris_list[0]
        type_string = URI_TYPE_DICT[type_uri]
    else:
        type_string = ''
    return type_string

class TextSearch():
    def __init__(self, text:str):
        self.text = text

    def get_text_search_on_id(self, ts_index:bool) -> str:
        schema_and_literal_value = self.text.split(':')
        schema = self.text = schema_and_literal_value[0]
        literal_value = schema_and_literal_value[1]
        return f'''
            {self.__gen_text_search('tsId', literal_value, True, ts_index)}
            ?res a fabio:Expression; datacite:hasIdentifier ?tsIdentifier{ts_index}.
            ?tsIdentifier{ts_index} datacite:usesIdentifierScheme datacite:{schema};
                          literal:hasLiteralValue ?tsId.
        '''
    
    def get_text_search_on_title(self, ts_index:bool) -> str:
        return f'''
            {self.__gen_text_search(f'tsTitle{ts_index}', self.text, False, ts_index)}
            ?res dcterm:title ?tsTitle{ts_index}.
        '''
    
    def get_text_search_on_person(self, role:str, ts_index:bool) -> str:
        family_name = None
        given_name = None
        name = None
        if ',' in self.text:
            name_parts = [part.strip() for part in self.text.split(',')]
            if name_parts:
                family_name = name_parts[0]
                if len(name_parts) == 2:
                    given_name = name_parts[1]
                    given_name = '. '.join(given_name.split('.'))
                    given_name = ' '.join([f"{name_part.rstrip('.')}.+?" if len(name_part.rstrip('.')) == 1 else name_part for name_part in given_name.split()])
                    given_name = given_name.replace('*', '.*?')
        else:
            name = self.text
        role = role.title()
        text_search = ''
        base_query = f'''
            ?res pro:isDocumentContextFor ?ts{role}{ts_index}.
            ?ts{role}{ts_index} pro:withRole pro:{role.lower()};
                    pro:isHeldBy ?ts{role}Ra{ts_index}.
        '''
        if name:
            text_search += f"{self.__gen_text_search(f'ts{role}Name{ts_index}', name, True, ts_index)}"
            base_query += f'?ts{role}Ra{ts_index} foaf:name ?ts{role}Name.'
        else:
            if family_name:
                text_search += f"{self.__gen_text_search(f'ts{role}Fn{ts_index}', family_name, True, ts_index)}"
                base_query += f'?ts{role}Ra{ts_index} foaf:familyName ?ts{role}Fn{ts_index}.'
                if given_name:
                    base_query += f'?ts{role}Ra{ts_index} foaf:givenName ?ts{role}Gn{ts_index}.'
                    text_search += f"FILTER REGEX (?ts{role}Gn{ts_index}, '^{given_name}$', 'i')"
            elif given_name:
                base_query += f'?ts{role}Ra{ts_index} foaf:givenName ?ts{role}Gn{ts_index}.'
                text_search += f"{self.__gen_text_search(f'ts{role}Gn{ts_index}', given_name, True, ts_index)}"
        return base_query + text_search

    def get_text_search_on_publisher(self, ts_index:bool) -> str:
        return f'''
            ?res pro:isDocumentContextFor ?tsPublisher{ts_index}.
            FILTER NOT EXISTS {{
                ?res a ?type.
            VALUES (?type) {{(fabio:JournalIssue) (fabio:JournalVolume)}}}}
            ?tsPublisher{ts_index} pro:withRole pro:publisher;
                    pro:isHeldBy ?tsPublisherRa{ts_index}.
            ?tsPublisherRa{ts_index} foaf:name ?tsPublisherName{ts_index}.
            {self.__gen_text_search(f'tsPublisherName{ts_index}', self.text, False, ts_index)}
        '''
        
    def get_text_search_on_vi(self, vi:str, ts_index:bool) -> str:
        v_or_i = vi.title()
        return f'''
            ?res frbr:partOf+ ?ts{v_or_i}{ts_index}.
            ?ts{v_or_i} a fabio:Journal{v_or_i}{ts_index};
                    fabio:hasSequenceIdentifier ?ts{v_or_i}Number{ts_index}.
            {self.__gen_text_search(f'ts{v_or_i}Number{ts_index}', self.text, False, ts_index)}
        '''
    
    def get_text_search_on_venue(self, ts_index:bool) -> str:
        return f'''
            ?res frbr:partOf+ ?tsVenue{ts_index}.
            FILTER NOT EXISTS {{
                ?res a ?type.
            VALUES (?type) {{(fabio:JournalIssue) (fabio:JournalVolume)}}}}
            ?tsVenue{ts_index} a fabio:Journal;
                    dcterm:title ?tsVenueTitle{ts_index}.
            {self.__gen_text_search(f'tsVenueTitle{ts_index}', self.text, False, ts_index)}
        '''

    def __gen_text_search(self, variable:str, text:str, match_all_terms:bool, ts_index:int) -> str:
        if str(ts_index).startswith('0'):
            text = f'"{text}"' if match_all_terms else f'{text}'
            min_relevance = f"?{variable} bds:minRelevance '0.7'." if match_all_terms else ''
            text_search = f"?{variable} bds:search '{text}'. hint:Prior hint:runFirst true. ?{variable} bds:matchAllTerms 'true'. {min_relevance}"
        else:
            pattern = f'^{text}$' if match_all_terms else text
            text_search = f"FILTER REGEX (?{variable}, '{pattern}', 'i')"
        return text_search


def __parse_request(request:str, ts_index:bool) -> Tuple[str, str]:
    field_value = re.search('(id|title|author|editor|publisher|venue)=(.+)', request)
    if not field_value:
        pass
    field = field_value.group(1)
    value = field_value.group(2)
    text_search = None
    ts = TextSearch(value)
    if field in {'editor', 'author'}:
        text_search = getattr(ts, f'get_text_search_on_person')(field, ts_index)
    elif field in {'volume', 'issue'}:
        text_search = getattr(ts, f'get_text_search_on_vi')(field, ts_index)
    else:
        text_search = getattr(ts, f'get_text_search_on_{field}')(ts_index)
    return text_search

def generate_text_search(text_search:str) -> str:
    requests = re.split('&&|\|\|', text_search)
    text_searches = ''
    for i, request in enumerate(requests):
        if i == 0:
            text_searches += f'{__parse_request(request, i)}'
        else:
            split_by_request = list(filter(None, text_search.split(request)))
            cur_sep = split_by_request[0][-2:]
            if cur_sep == '&&':
                text_searches += f'{__parse_request(request, i)}'
            elif cur_sep == '||':
                text_searches += f'UNION{__parse_request(request, f"0{i}")}'
    if text_searches and 'UNION' in text_searches:
        query = '{' + '} UNION {'.join(text_searches.split('UNION')) + '}'
    elif text_searches and not 'UNION' in text_searches:
        query = text_searches
    return 'WITH { SELECT DISTINCT ?res WHERE {' + query + r'} LIMIT 10000} AS %results',