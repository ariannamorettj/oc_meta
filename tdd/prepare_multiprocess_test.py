from csv import DictReader
from meta.plugins.multiprocess.prepare_multiprocess import prepare_relevant_items, split_by_publisher, _do_collective_merge, _get_relevant_venues, _find_multi_pub_venues, _get_resp_agents
import os
import shutil
import unittest


BASE = os.path.join('meta', 'tdd', 'prepare_multiprocess')
TMP_DIR = os.path.join(BASE, 'tmp')
CSV_DIR = os.path.join(BASE, 'input')


class TestPrepareMultiprocess(unittest.TestCase):
    def test_prepare_relevant_venues(self):
        prepare_relevant_items(csv_dir=CSV_DIR, output_dir=TMP_DIR, items_per_file=3, verbose=False)
        output = list()
        for root, _, files in os.walk(TMP_DIR):
            for file in files:
                if file.endswith('.csv'):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        output.extend(list(DictReader(f)))
        expected_output = [
            {'id': '', 'title': '', 'author': 'NAIMI, ELMEHDI [orcid:0000-0002-4126-8519]', 'pub_date': '', 'venue': '', 'volume': '', 'issue': '', 'page': '', 'type': '', 'publisher': '', 'editor': ''}, 
            {'id': '', 'title': '', 'author': 'Chung, Myong-Soo [orcid:0000-0002-9666-2513]', 'pub_date': '', 'venue': '', 'volume': '', 'issue': '', 'page': '', 'type': '', 'publisher': '', 'editor': ''}, 
            {'id': '', 'title': '', 'author': 'Cheigh, Chan-Ick [orcid:0000-0003-2542-5788]', 'pub_date': '', 'venue': '', 'volume': '', 'issue': '', 'page': '', 'type': '', 'publisher': '', 'editor': ''}, 
            {'id': '', 'title': '', 'author': 'Kim, Young-Shik [orcid:0000-0001-5673-6314]', 'pub_date': '', 'venue': '', 'volume': '', 'issue': '', 'page': '', 'type': '', 'publisher': '', 'editor': ''}, 
            {'id': '', 'title': '', 'author': '', 'pub_date': '', 'venue': 'The Korean Journal of Food And Nutrition [issn:1225-4339]', 'volume': '25', 'issue': '1', 'page': '', 'type': 'journal issue', 'publisher': '', 'editor': ''},
            {'id': '', 'title': '', 'author': '', 'pub_date': '', 'venue': 'The Korean Journal of Food And Nutrition [issn:1225-4339]', 'volume': '26', 'issue': '', 'page': '', 'type': 'journal volume', 'publisher': '', 'editor': ''}, 
            {'id': '', 'title': '', 'author': '', 'pub_date': '', 'venue': 'The Korean Journal of Food And Nutrition [issn:1225-4339]', 'volume': '', 'issue': '2', 'page': '', 'type': 'journal issue', 'publisher': '', 'editor': ''}]
        shutil.rmtree(TMP_DIR)
        self.assertEqual(sorted(output, key=lambda x: x['id']+x['title']+x['author']+x['issue']+x['volume']+x['type']), sorted(expected_output, key=lambda x: x['id']+x['title']+x['author']+x['issue']+x['volume']+x['type']))

    def test_split_by_publisher(self):
        split_by_publisher(csv_dir=CSV_DIR, output_dir=TMP_DIR, verbose=False)
        output = dict()
        for root, _, files in os.walk(TMP_DIR):
            for file in files:
                if file.endswith('.csv'):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        output[file] = list(DictReader(f))
        expected_output = {
            'crossref_4768.csv': [
                {'id': 'doi:10.9799/ksfan.2012.25.1.069', 'title': 'Nonthermal Sterilization and Shelf-life Extension of Seafood Products by Intense Pulsed Light Treatment', 'author': 'Cheigh, Chan-Ick [orcid:0000-0003-2542-5788]; Mun, Ji-Hye; Chung, Myong-Soo', 'pub_date': '2012-3-31', 'venue': 'The Korean Journal of Food And Nutrition [issn:1225-4339]', 'volume': '25', 'issue': '1', 'page': '69-76', 'type': 'journal article', 'publisher': 'The Korean Society of Food and Nutrition [crossref:4768]', 'editor': 'Chung, Myong-Soo [orcid:0000-0002-9666-2513]'}, 
                {'id': 'doi:10.9799/ksfan.2012.25.1.077', 'title': 'Properties of Immature Green Cherry Tomato Pickles', 'author': 'Koh, Jong-Ho; Shin, Hae-Hun; Kim, Young-Shik [orcid:0000-0001-5673-6314]; Kook, Moo-Chang', 'pub_date': '2012-3-31', 'venue': 'The Korean Journal of Food And Nutrition [issn:1225-4339]', 'volume': '', 'issue': '2', 'page': '77-82', 'type': 'journal article', 'publisher': 'The Korean Society of Food and Nutrition [crossref:4768]', 'editor': ''}], 
            'crossref_6623.csv': [{'id': 'doi:10.17117/na.2015.08.1067', 'title': '', 'author': '', 'pub_date': '', 'venue': 'The Korean Journal of Food And Nutrition [issn:1225-4339]', 'volume': '26', 'issue': '', 'page': '', 'type': 'journal article', 'publisher': 'Consulting Company Ucom [crossref:6623]', 'editor': 'NAIMI, ELMEHDI [orcid:0000-0002-4126-8519]'}]}
        self.assertEqual(output, expected_output)
        shutil.rmtree(TMP_DIR)
        
    def test__get_relevant_venues(self):
        items_by_id = dict()
        item_1 = {'venue': 'Venue [id:a id:b id:c]', 'volume': '1', 'issue': 'a', 'type': 'journal article'}
        item_2 = {'venue': 'Venue [id:a id:d]', 'volume': '2', 'issue': 'b', 'type': 'journal article'}
        item_3 = {'venue': 'Venue [id:e id:d]', 'volume': '3', 'issue': 'c', 'type': 'journal article'}
        item_4 = {'venue': 'Venue [id:e id:f issn:0000-0000]', 'volume': '', 'issue': 'd', 'type': 'journal article'}
        item_5 = {'venue': 'Venue [id:f]', 'volume': '', 'issue': 'e', 'type': 'journal article'}
        item_6 = {'id': 'isbn:9789089646491', 'title': 'Transit Migration in Europe', 'venue': '', 'volume': '', 'issue': '', 'type': 'book'}
        item_7 = {'id': 'isbn:9789089646491', 'title': 'Transit Migration in Europe', 'venue': 'An Introduction to Immigrant Incorporation Studies [isbn:9789089646484]', 'volume': '', 'issue': '', 'type': 'book'}
        items = [item_1, item_2, item_3, item_4, item_5, item_6, item_7]
        _get_relevant_venues(data= items, items_by_id=items_by_id)
        expected_output = {
            'id:a': {'others': {'id:c', 'id:d', 'id:b'}, 'name': 'Venue', 'type': 'journal', 'volume': {'1': {'a'}, '2': {'b'}}, 'issue': set()}, 
            'id:b': {'others': {'id:c', 'id:a'}, 'name': 'Venue', 'type': 'journal', 'volume': {'1': {'a'}}, 'issue': set()}, 
            'id:c': {'others': {'id:a', 'id:b'}, 'name': 'Venue', 'type': 'journal', 'volume': {'1': {'a'}}, 'issue': set()}, 
            'id:d': {'others': {'id:a', 'id:e'}, 'name': 'Venue', 'type': 'journal', 'volume': {'2': {'b'}, '3': {'c'}}, 'issue': set()}, 
            'id:e': {'others': {'id:f', 'id:d'}, 'name': 'Venue', 'type': 'journal', 'volume': {'3': {'c'}}, 'issue': {'d'}}, 
            'id:f': {'others': {'id:e'}, 'name': 'Venue', 'type': 'journal', 'volume': dict(), 'issue': {'d', 'e'}},
            'isbn:9789089646491': {'others': set(), 'name': 'Transit Migration in Europe', 'type': 'book', 'volume': dict(), 'issue': set()}, 
            'isbn:9789089646484': {'others': set(), 'name': 'An Introduction to Immigrant Incorporation Studies', 'type': 'book series', 'volume': dict(), 'issue': set()}}
        self.assertEqual(items_by_id, expected_output)

    def test__get_resp_agents(self):
        items_by_id = dict()
        item_1 = {'author': 'Massari, Arcangelo [orcid:0000-0002-8420-0696]', 'editor': ''}
        item_2 = {'author': '', 'editor': 'Massari, A. [orcid:0000-0002-8420-0696 viaf:1]'}
        item_3 = {'author': 'Massari, A [viaf:1]', 'editor': ''}
        item_4 = {'author': 'Peroni, Silvio [orcid:0000-0003-0530-4305]', 'editor': ''}
        items = [item_1, item_2, item_3, item_4]
        _get_resp_agents(data= items, items_by_id=items_by_id)
        expected_output = {
            'orcid:0000-0002-8420-0696': {'others': {'viaf:1'}, 'name': 'Massari, Arcangelo', 'type': 'author'}, 
            'viaf:1': {'others': {'orcid:0000-0002-8420-0696'}, 'name': 'Massari, A.', 'type': 'author'}, 
            'orcid:0000-0003-0530-4305': {'others': set(), 'name': 'Peroni, Silvio', 'type': 'author'}}
        self.assertEqual(items_by_id, expected_output)

    def test__do_collective_merge(self):
        items = {
            'id:a': {'others': {'id:c', 'id:d', 'id:b'}, 'name': 'Venue', 'type': 'journal', 'volume': {'1': {'a'}, '2': {'b'}}, 'issue': set()}, 
            'id:b': {'others': {'id:c', 'id:a'}, 'name': 'Venue', 'type': 'journal', 'volume': {'1': {'a'}}, 'issue': set()}, 
            'id:c': {'others': {'id:a', 'id:b'}, 'name': 'Venue', 'type': 'journal', 'volume': {'1': {'a'}}, 'issue': set()}, 
            'id:d': {'others': {'id:a', 'id:e'}, 'name': 'Venue', 'type': 'journal', 'volume': {'2': {'c'}, '3': {'c'}}, 'issue': set()}, 
            'id:e': {'others': {'id:f', 'id:d'}, 'name': 'Venue', 'type': 'journal', 'volume': {'3': {'c'}}, 'issue': {'d'}}, 
            'id:f': {'others': {'id:e'}, 'name': 'Venue', 'type': 'journal', 'volume': dict(), 'issue': {'vol. 17, n° 2', 'e'}}}
        output = _do_collective_merge(items)
        vi_number = 0
        for _, data in output.items():
            for _, issues in data['volume'].items():
                if issues:
                    vi_number += len(issues)
                elif not issues:
                    vi_number += 1
            vi_number += len(data['issue'])
        expected_output = {'id:a': {'name': 'Venue', 'type': 'journal', 'others': {'id:c', 'id:f', 'id:e', 'id:b', 'id:d'}, 'volume': {'1': {'a'}, '2': {'b', 'c'}, '3': {'c'}}, 'issue': {'vol. 17, n° 2', 'e', 'd'}}}
        self.assertEqual(output, expected_output)
    
    def test__find_multi_pub_venues(self):
        multi_pub_venues = dict()
        pub_by_venue = dict()
        venues_by_id = dict()
        data = [
            {'id': 'doi:10.1001/.391', 'title': 'Treatment of Excessive Anticoagulation With Phytonadione (Vitamin K): A Meta-analysis', 'author': 'DeZee, K. J.', 'venue': 'Archives of Internal Medicine [issn:0003-9926]', 'volume': '166', 'issue': '4', 'pub_date': '2006-2-27', 'type': 'journal article', 'page': '391-397', 'editor': '', 'publisher': 'American Medical Association (AMA) [crossref:10]'},
            {'id': 'doi:10.1001/.405', 'title': "Neutropenia in Human Immunodeficiency Virus Infection: Data From the Women's Interagency HIV Study", 'author': 'Levine, A. M.', 'venue': 'Archives of Internal Medicine [issn:0003-9926 issn:0003-987X]', 'volume': '', 'issue': '', 'pub_date': '', 'type': '', 'page': '', 'editor': '', 'publisher': 'Wiley [crossref:311]'},
            {'id': 'doi:10.1001/archderm.107.4.628b', 'title': 'Carcinoma of mammary crease ""simulating basal cell epithelioma', 'author': '', 'venue': 'Chemischer Informationsdienst [issn:0009-2975]', 'volume': '', 'issue': '', 'pub_date': '', 'type': '', 'page': '', 'editor': '', 'publisher': 'Wiley [crossref:311]'},
            {'id': 'issn:0003-9926 issn:0013-9351', 'title': 'Archives of Internal Medicine', 'author': '', 'venue': '', 'volume': '', 'issue': '', 'pub_date': '', 'type': 'journal', 'page': '', 'editor': '', 'publisher': ''}
        ]
        _get_relevant_venues(data=data, items_by_id=venues_by_id)
        _find_multi_pub_venues(data, pub_by_venue, multi_pub_venues, venues_by_id)
        output = (pub_by_venue, multi_pub_venues)
        expected_output = (
            {'issn:0003-9926': {'crossref:10', 'crossref:311'}, 'issn:0009-2975': {'crossref:311'}},
            {
                'issn:0003-9926': {'others': {'issn:0003-987X', 'issn:0013-9351'}, 'name': 'Archives of Internal Medicine', 'type': 'journal', 'volume': {'166': {'4'}}, 'issue': set()}, 
                'issn:0003-987X': {'others': {'issn:0003-9926'}, 'name': 'Archives of Internal Medicine', 'type': '', 'volume': {}, 'issue': set()}, 
                'issn:0013-9351': {'others': {'issn:0003-9926'}, 'name': 'Archives of Internal Medicine', 'type': 'journal', 'volume': {}, 'issue': set()}}
        )
        self.assertEqual(output, expected_output)


if __name__ == '__main__':
    unittest.main()