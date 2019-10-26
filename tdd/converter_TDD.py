import unittest

from converter import *
import csv

def reset():
    with open("converter_counter/br.txt", 'w') as br:
        br.write('0')
    with open("converter_counter/id.txt", 'w') as br:
        br.write('0')
    with open("converter_counter/ra.txt", 'w') as br:
        br.write('0')

def datacollect():
    with open("new_test_data.csv", 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        data = [dict(x) for x in reader]

    return data

def prepare2test(data, testcase_csv):
    reset()

    conversion = Converter(data, 'http://127.0.0.1:9999/blazegraph/sparql').data

    with open(testcase_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        testcase = [dict(x) for x in reader]


    return conversion, testcase


class testcase_01 (unittest.TestCase):
    def test (self):
        # testcase1: 2 different issues of the same venue (no volume)
        data = datacollect()
        partial_data = list()
        partial_data.append(data[0])
        partial_data.append(data[5])
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_01_data.csv")
        self.assertEqual(conversion, testcase)


class testcase_02(unittest.TestCase):
    def test(self):
        # testcase2: 2 different volumes of the same venue (no issue)
        data = datacollect()
        partial_data = list()
        partial_data.append(data[1])
        partial_data.append(data[3])
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_02_data.csv")
        self.assertEqual(conversion, testcase)




class testcase_03(unittest.TestCase):
    def test(self):
        # testcase3: 2 different issues of the same volume
        data = datacollect()
        partial_data = list()
        partial_data.append(data[2])
        partial_data.append(data[4])
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_03_data.csv")
        self.assertEqual(conversion, testcase)





class testcase_04 (unittest.TestCase):
    def test (self):
        # testcase4: 2 new IDS and different date format (yyyy-mm and yyyy-mm-dd)
        data = datacollect()
        partial_data = list()
        partial_data.append(data[6])
        partial_data.append(data[7])
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_04_data.csv")
        self.assertEqual(conversion, testcase)




class testcase_05 (unittest.TestCase):
    def test (self):
        # testcase5: NO ID scenario
        data = datacollect()
        partial_data = list()
        partial_data.append(data[8])
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_05_data.csv")
        self.assertEqual(conversion, testcase)



class testcase_06 (unittest.TestCase):
    def test (self):
        # testcase6: ALL types test
        data = datacollect()
        partial_data = data[9:33]
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_06_data.csv")
        self.assertEqual(conversion, testcase)



'''
DEPRECATED
class testcase_07 (unittest.TestCase):
    def test (self):
        testcase7: archival document in an archival document set
        data = datacollect()
        partial_data = list()
        partial_data.append(data[33])
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_07_data.csv")
        self.assertEqual(conversion, testcase)
'''


class testcase_07 (unittest.TestCase):
    def test (self):
        # testcase7: all journal related types with an editor
        data = datacollect()
        partial_data = data[34:40]
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_07_data.csv")
        self.assertEqual(conversion, testcase)



class testcase_08 (unittest.TestCase):
    def test (self):
        # testcase8: all book related types with an editor
        data = datacollect()
        partial_data = data[40:43]
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_08_data.csv")
        self.assertEqual(conversion, testcase)


class testcase_09 (unittest.TestCase):
    def test (self):
        # testcase09: all proceeding related types with an editor
        data = datacollect()
        partial_data = data[43:45]
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_09_data.csv")
        self.assertEqual(conversion, testcase)

class testcase_10 (unittest.TestCase):
    def test (self):
        # testcase10: a book inside a book series and a book inside a book set
        data = datacollect()
        partial_data = data[45:49]
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_10_data.csv")
        self.assertEqual(conversion, testcase)


class testcase_11 (unittest.TestCase):
    def test (self):
        # testcase11: real time entity update
        data = datacollect()
        partial_data = data[49:52]
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_11_data.csv")
        self.assertEqual(conversion, testcase)

class testcase_12 (unittest.TestCase):
    def test (self):
        # testcase12: clean name, title, ids
        data = datacollect()
        partial_data = list()
        partial_data.append(data[52])
        conversion, testcase = prepare2test(partial_data, "testcases/testcase_data/testcase_12_data.csv")
        self.assertEqual(conversion, testcase)

'''
class testcase_13 (unittest.TestCase):
    #AD HOC TEST

    reset()
    # testcase13: ID_clean massive test
    def test1 (self):
        #meta specified [row-0] new id belonging to a wannabe [row-1] meta specified with an id related to wannabe [row-2]
        empty_val = {"author":"", "pub-date":"", "venue":"", "volume":"", "issue":"", "page":"", "type":"", "publisher":"", "editor":""}
        row_data = [{"id":"meta:br/1" , "title":""},{"id":"doi:20", "title": "title1"}, {"id":"meta:br/1 doi:20", "title": "title1"}]
        data = [{**d, **empty_val} for d in row_data]
        row_testcase = [{'id': 'doi:20 doi:1 doi:2 doi:40 meta:br/1', 'title': 'Title1'}, {'id': 'doi:20 doi:1 doi:2 doi:40 meta:br/1', 'title': 'Title1'}]
        testcase = [{**t, **empty_val} for t in row_testcase]
        conversion = Converter(data, 'http://127.0.0.1:9999/blazegraph/sparql').data

        self.assertEqual(conversion, testcase)
'''



def suite(testobj):
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(testobj))
    return test_suite


TestSuit=suite(testcase_13)

runner=unittest.TextTestRunner()
runner.run(TestSuit)