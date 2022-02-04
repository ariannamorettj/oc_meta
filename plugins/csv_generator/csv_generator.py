import os
import re
import yaml
from meta.lib.master_of_regex import *
from meta.lib.finder import ResourceFinder
from meta.lib.file_manager import write_csv
from typing import Tuple
from tqdm import tqdm


class CSVGenerator:
    def __init__(self, config:str):
        with open(config, encoding='utf-8') as file:
            settings = yaml.full_load(file)
        triplestore_url = settings['triplestore_url']
        self.info_dir = settings['info_dir']
        self.base_iri = settings['base_iri'][:-1] if settings['base_iri'][-1] == '/' else settings['base_iri']
        self.supplier_prefix = settings['supplier_prefix']
        self.dir_split_number = settings['dir_split_number']
        self.output_csv_dir = os.path.join(settings['output_csv_dir'], str(self.supplier_prefix))
        self.items_per_file = settings['items_per_file']
        self.verbose = settings['verbose']
        self.forbidden_types = {'journal issue', 'journal volume', 'journal', 'book set', 'book series', 'book part', 'book section'}
        self.finder = ResourceFinder(triplestore_url, self.base_iri)        
    
    def generate_csv(self):
        counter = 1
        br_info_dir_path = os.path.join(self.info_dir, 'creator', f'info_file_br.txt')
        number_of_entities = self.read_number(br_info_dir_path)
        last_file, dir_number = self.skip_files()
        counter += last_file
        self.cur_output_dir = os.path.join(self.output_csv_dir, str(dir_number))
        if self.verbose:
            pbar = tqdm(total=number_of_entities)
            pbar.update(last_file)
        self.data = list()
        while counter <= number_of_entities:
            row = dict()
            metaid = self.supplier_prefix + str(counter)
            res = f'{self.base_iri}/br/{metaid}'
            res_exists_and_is_relevant = self.finder.check_type(res=res, forbidden_types=self.forbidden_types)
            if res_exists_and_is_relevant:
                br_info = self.finder.retrieve_br_info_from_meta(metaid)
                br_title_and_ids = self.finder.retrieve_br_from_meta(metaid)
                # Pub_date, Volume, Issue, Type
                row.update(br_info)
                # Id
                ids = [id[1] for id in br_title_and_ids[1]]
                row['id'] = f'meta:br/{metaid} ' + ' '.join(ids)
                # Title
                row['title'] = br_title_and_ids[0]
                # Authors and Editors
                row['author'] = self.get_resp_agents(metaid, 'author')
                row['editor'] = self.get_resp_agents(metaid, 'editor')
                # Page
                row['page'] = br_info['page'][1] if row['page'] else ''
                # Venue
                if br_info['venue']:
                    venue_metaid = re.search(ids_inside_square_brackets, br_info['venue']).group(1).replace('meta:br/', '')
                    venue_title_and_ids = self.finder.retrieve_br_from_meta(venue_metaid)
                    venue_title = venue_title_and_ids[0]
                    venue_ids = '[' + ' '.join([id[1] for id in venue_title_and_ids[1]]) + ']'
                    row['venue'] = venue_title + ' ' + venue_ids
                # Publisher
                row['publisher'] = self.finder.retrieve_publisher_from_br_metaid(metaid)
                row = {k:v if v else '' for k,v in row.items()}
                self.data.append(row)
            self.store_csv(counter)
            counter += 1
            if self.verbose:
                pbar.update()
        if self.verbose:
            pbar.close()
    
    def get_resp_agents(self, metaid:str, column:str) -> str:
        resp_agents = self.finder.retrieve_ra_sequence_from_br_meta(metaid, column)
        output = ''
        if resp_agents:
            full_resp_agents = list()
            for item in resp_agents:
                for _, resp_agent in item.items():
                    author_name = resp_agent[0]
                    ids = [f'meta:ra/{resp_agent[2]}']
                    ids.extend([id[1] for id in resp_agent[1]])
                    author_ids = '[' + ' '.join(ids) + ']'
                    full_resp_agent =  author_name + ' ' + author_ids
                    full_resp_agents.append(full_resp_agent)
            output = '; '.join(full_resp_agents)
        return output
    
    def store_csv(self, counter:int) -> None:
        if counter != 0 and counter % self.items_per_file == 0:
            if os.path.exists(self.cur_output_dir):
                if len(os.listdir(self.cur_output_dir)) % self.dir_split_number == 0:
                    cur_dir = str(int(counter - self.items_per_file + self.dir_split_number * self.items_per_file))
                    self.cur_output_dir = os.path.join(self.output_csv_dir, cur_dir)
            path = os.path.join(self.cur_output_dir, f'{counter}.csv')
            fieldnames = ['id', 'title', 'author', 'pub_date', 'venue', 'volume', 'issue', 'page', 'type', 'publisher', 'editor']
            write_csv(path=path, datalist=self.data, fieldnames=fieldnames, mode='w')
            self.data = list()
    
    def skip_files(self) -> Tuple[int, int]:
        last_file = 0
        dir_number = self.dir_split_number * self.items_per_file
        if os.path.exists(self.output_csv_dir):
            folders = os.listdir(self.output_csv_dir)
            if folders:
                last_folder = sorted(folders, key=lambda x: int(x))[-1]
                files = os.listdir(os.path.join(self.output_csv_dir, last_folder))
                if files:
                    last_file = sorted(files, key=lambda x: int(x.replace('.csv', '')))[-1]
                    last_file = int(last_file.replace('.csv', ''))
                    dir_number = dir_number * len(folders)
        return last_file, dir_number

    @staticmethod
    def read_number(file_path: str) -> Tuple[int, int]:
        with open(file_path, "rb") as f:
            number = int(f.readlines()[0].decode('ascii').strip())
            return number
