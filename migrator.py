from graphlib import *
import re

class Migrator():
    def __init__(self, data, txtindex):
        self.url = "https://w3id.org/OC/meta/"

        self.setgraph = GraphSet(self.url, "", "counter/")

        self.index = dict()
        self.index['crossref'] = dict()
        self.index["doi"] = dict()
        self.index["issn"] = dict()
        self.index["isbn"] = dict()
        self.index["orcid"] = dict()
        self.index["pmid"] = dict()
        self.index['pmcid'] = dict()
        self.index['url'] = dict()
        self.index['viaf'] = dict()
        self.index['wikidata'] = dict()



        with open(txtindex) as file:
            id_index = file.read().splitlines()
            for line in id_index:
                values = line.split(" , ")

                if 'crossref' in line:
                    id = values[0].replace('crossref:', '')
                    self.index['crossref'][id] = values[1]

                elif "doi" in line:
                    id = values[0].replace('doi:', '')
                    self.index['doi'][id] = values[1]

                elif "issn" in line:
                    id = values[0].replace('issn:', '')
                    self.index['issn'][id] = values[1]

                elif "isbn" in line:
                    id = values[0].replace('isbn:', '')
                    self.index['isbn'][id] = values[1]

                elif "orcid" in line:
                    id = values[0].replace('orcid:', '')
                    self.index['orcid'][id] = values[1]

                elif "pmid" in line:
                    id = values[0].replace('pmid:', '')
                    self.index['pmid'][id] = values[1]

                elif "pmcid" in line:
                    id = values[0].replace('pmcid:', '')
                    self.index['pmcid'][id] = values[1]

                elif "url" in line:
                    id = values[0].replace('url:', '')
                    self.index['url'][id] = values[1]

                elif "viaf" in line:
                    id = values[0].replace('viaf:', '')
                    self.index['viaf'][id] = values[1]

                elif "wikidata" in line:
                    id = values[0].replace('wikidata:', '')
                    self.index['wikidata'][id] = values[1]


        for row in data:
            ids = row['id']
            title = row['title']
            authors = row['author']
            pub_date = row['pub_date']
            venue = row['venue']
            vol = row['volume']
            issue = row['issue']
            page = row['page']
            type = row['type']
            publisher = row['publisher']

            self.id_job(ids)
            self.title_job(title)
            self.author_job(authors)
            self.pub_date_job(pub_date)
            self.venue_job(venue, vol, issue)
            self.page_job(page)
            self.type_job(type)
            self.publisher_job(publisher)

        self.final_graph = Graph()
        for g in self.setgraph.graphs():
            self.final_graph += g



    def id_job (self, ids):
        idslist = re.split(r'\s*;\s*', ids)

        #publication id
        for id in idslist:
            if "meta:" in id:
                id = id.replace("meta:", "")
                url = URIRef(self.url + id)
                self.br_graph = self.setgraph.add_br("agent", source_agent=None, source=None, res=url, wanted_type = True)

        for id in idslist:
            self.id_creator(self.br_graph, id)

    def title_job (self, title):
        self.br_graph.create_title(title)


    def author_job (self, authors):
        authorslist = re.split(r'\s*;\s*(?=[^]]*(?:\[|$))', authors)

        aut_role_list = list()
        for aut in authorslist:
            aut_id = re.search(r'\[\s*(.*?)\s*\]', aut).group(1)
            aut_id_list = re.split(r'\s*;\s*', aut_id)

            for id in aut_id_list:
                if "meta:" in id:
                    id = id.replace("meta:", "")
                    url = URIRef(self.url + id)
                    pub_aut = self.setgraph.add_ra("agent", source_agent=None, source=None, res=url, wanted_type = True)
                    author_name = re.search(r'(.*?)\s*\[.*?\]', aut).group(1)
                    author_name_splitted = re.split(r'\s*,\s*', author_name)
                    firstName = author_name_splitted[1]
                    lastName = author_name_splitted[0]
                    pub_aut.create_given_name(firstName)
                    pub_aut.create_family_name(lastName)

        # lists of authors' IDs
            for id in aut_id_list:
                self.id_creator(pub_aut, id)

        # authorRole
            pub_aut_role = self.setgraph.add_ar("agent", source_agent=None, source=None, res=None, wanted_label = False)
            pub_aut_role.create_author(self.br_graph)
            pub_aut.has_role(pub_aut_role)
            aut_role_list.append(pub_aut_role)
            if len(aut_role_list) > 1:
                pub_aut_role.follows(aut_role_list[aut_role_list.index(pub_aut_role)-1])

    def pub_date_job (self, pub_date):
        if pub_date:
            datelist = list()
            datesplit = pub_date.split("-")
            if datesplit:
                for x in datesplit:
                    datelist.append(int(x))
            else:
                datelist.append(int(pub_date))
            self.br_graph.create_pub_date(datelist)

    def venue_job (self, venue, vol, issue):

        if venue:
            venue_id = re.search(r'\[\s*(.*?)\s*\]', venue).group(1)
            venue_id_list = re.split(r'\s*;\s*', venue_id)

            for id in venue_id_list:
                if "meta:" in id:
                    id = id.replace("meta:", "")
                    url = URIRef(self.url + id)
                    venue_title = re.search(r'(.*?)\s*\[.*?\]', venue).group(1)
                    venue_graph = self.setgraph.add_br("agent", source_agent=None, source=None, res=url, wanted_type = True)
                    venue_graph.create_title(venue_title)

            for id in venue_id_list:
                self.id_creator(venue_graph, id)

        if vol:
            vol_id = re.search(r'\[\s*(.*?)\s*\]', vol).group(1)
            vol_id_list = re.split(r'\s*;\s*', vol_id)

            for id in vol_id_list:
                if "meta:" in id:
                    id = id.replace("meta:", "")
                    url = URIRef(self.url + id)
                    vol_graph = self.setgraph.add_br("agent", source_agent=None, source=None, res=url, wanted_type = True)
                    vol_title = re.search(r'(.*?)\s*\[.*?\]', vol).group(1)
                    vol_graph.create_volume()
                    vol_graph.create_number(vol_title)


        if issue:
            issue_id = re.search(r'\[\s*(.*?)\s*\]', issue).group(1)
            issue_id_list = re.split(r'\s*;\s*', issue_id)

            for id in issue_id_list:
                if "meta:" in id:
                    id = id.replace("meta:", "")
                    url = URIRef(self.url + id)
                    issue_graph = self.setgraph.add_br("agent", source_agent=None, source=None, res=url, wanted_type = True)
                    issue_title = re.search(r'(.*?)\s*\[.*?\]', issue).group(1)
                    issue_graph.create_issue()
                    issue_graph.create_number(issue_title)

        if venue and vol and issue:
            issue_graph.has_part(self.br_graph)
            vol_graph.has_part(issue_graph)
            venue_graph.has_part(vol_graph)
        elif venue and not vol and issue:
            issue_graph.has_part(self.br_graph)
            venue_graph.has_part(issue_graph)
        elif venue and vol and not issue:
            vol_graph.has_part(self.br_graph)
            venue_graph.has_part(vol_graph)
        elif not venue and vol and issue:
            issue_graph.has_part(self.br_graph)
            vol_graph.has_part(issue_graph)
        elif venue and not vol and not issue:
            venue_graph.has_part(self.br_graph)
        elif not venue and vol and not issue:
            vol_graph.has_part(self.br_graph)
        elif not venue and not vol and issue:
            issue_graph.has_part(self.br_graph)


    def page_job (self, page):
        if page:
            form = self.setgraph.add_re("agent", source_agent=None, source=None, res=None, wanted_label=False)
            pages = page.split("-")
            form.create_starting_page(pages[0])
            form.create_ending_page(pages[1])
            self.br_graph.has_format(form)


    def type_job (self, type):
        if type == "academic proceedings":
            self.br_graph.create_proceedings()
        elif type == "book":
            self.br_graph.create_book()
        elif type == "book chapter":
            self.br_graph.create_book_chapter()
        elif type == "book series":
            self.br_graph.create_book_series()
        elif type == "book set":
            self.br_graph.create_book_set()
        elif type == "data file":
            self.br_graph.create_dataset()
        elif type == "journal":
            self.br_graph.create_journal()
        elif type == "journal article":
            self.br_graph.create_journal_article()
        elif type == "journal issue":
            self.br_graph.create_journal_issue()
        elif type == "journal volume":
            self.br_graph.create_journal_volume()
        elif type == "proceedings paper":
            self.br_graph.create_proceedings_article()
        elif type == "reference book":
            self.br_graph.create_reference_book()
        elif type == "reference entry":
            self.br_graph.create_reference_entry()
        elif type == "journal article":
            self.br_graph.create_journal_article()
        elif type == "report document":
            self.br_graph.create_report()
        elif type == "specification document":
            self.br_graph.create_standard()
        elif type == "thesis":
            self.br_graph.create_dissertation()



    def publisher_job (self, publisher):

        publ_id = re.search(r'\[\s*(.*?)\s*\]', publisher).group(1)
        publ_id_list = re.split(r'\s*;\s*', publ_id)

        for id in publ_id_list:
            if "meta:" in id:
                id = id.replace("meta:", "")
                url = URIRef(self.url + id)
                publ_name = re.search(r'(.*?)\s*\[.*?\]', publisher).group(1)
                publ = self.setgraph.add_ra("agent", source_agent=None, source=None, res=url, wanted_type = True)
                publ.create_name(publ_name)

        for id in publ_id_list:
            self.id_creator(publ, id)

        # authorRole
        publ_role = self.setgraph.add_ar("agent", source_agent=None, source=None, res=None, wanted_label=False)
        publ_role.create_publisher(self.br_graph)
        publ.has_role(publ_role)



    def id_creator (self,graph, id):

        new_id = None

        if 'crossref' in id:
            id = id.replace('crossref:', '')
            res = self.index['crossref'][id]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id("agent", source_agent=None, source=None, res=url, wanted_type = True)
            new_id.create_crossref(id)

        elif "doi:" in id:
            id = id.replace("doi:", "")
            res = self.index['doi'][id]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id("agent", source_agent=None, source=None, res=url, wanted_type = True)
            new_id.create_doi(id)

        elif "issn" in id:
            id = id.replace("issn:", "")
            res = self.index['issn'][id]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id("agent", source_agent=None, source=None, res=url, wanted_type = True)
            new_id.create_issn(id)

        elif "isbn" in id:
            id = id.replace("isbn:", "")
            res = self.index['isbn'][id]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id("agent", source_agent=None, source=None, res=url, wanted_type = True)
            new_id.create_isbn(id)

        elif "orcid" in id:
            id = id.replace("orcid:", "")
            res = self.index['orcid'][id]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id("agent", source_agent=None, source=None, res=url, wanted_type = True)
            new_id.create_orcid(id)

        elif "pmid:" in id:
            id = id.replace("pmid:", "")
            res = self.index['pmid'][id]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id("agent", source_agent=None, source=None, res=url, wanted_type=True)
            new_id.create_pmid(id)

        elif "pmcid:" in id:
            id = id.replace("pmcid:", "")
            res = self.index['pmcid'][id]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id("agent", source_agent=None, source=None, res=url, wanted_type=True)
            new_id.create_pmcid(id)

        elif "url:" in id:
            id = id.replace("url:", "")
            res = self.index['url'][id]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id("agent", source_agent=None, source=None, res=url, wanted_type=True)
            new_id.create_url(id)

        elif "viaf" in id:
            id = id.replace("viaf:", "")
            res = self.index['viaf'][id]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id("agent", source_agent=None, source=None, res=url, wanted_type=True)
            new_id.create_viaf(id)

        elif "wikidata" in id:
            id = id.replace("wikidata:", "")
            res = self.index['wikidata'][id]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id("agent", source_agent=None, source=None, res=url, wanted_type=True)
            new_id.create_wikidata(id)

        if new_id:
            graph.has_id(new_id)