# new terminal
# cd spider/downloads
# python .\mongo_import.py -c movies -i "E:\VS_Code\ZHAW\Model_Deployment\HikePlanner\model\imdb_scraper\imdb_scraper\spiders\movies.jl" -u "mongodb+srv://werleja1:Md1794682350.@mdmwerleja1.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
import argparse
import json
from pymongo import MongoClient
from concurrent.futures import ProcessPoolExecutor

def to_document(item):
    try:
        doc = {
            "Title": item["Title"],
            "Boxoffice in Million": item["Boxoffice in Million"],
            "Runtime in Minutes": item["Runtime in Minutes"],
            "Original Language": item["Original Language"],
            "Director": item["Director"],
            "release_month": item["release_month"],
            "rating": item["rating"],
        }
        return doc
    except Exception as e:
        print(f"Could not process item: {item}, Error: {e}")
        return None

class JsonLinesImporter:

    def __init__(self, file, mongo_uri, batch_size=30, db='movies', collection='movies'):
        self.file = file
        self.batch_size = batch_size
        self.client = MongoClient(mongo_uri)
        self.db = db
        self.collection = collection

    def read_lines(self):
        with open(self.file, encoding='UTF-8') as f:
            batch = []
            for line in f:
                batch.append(json.loads(line))
                if len(batch) == self.batch_size:
                    yield batch
                    batch.clear()
            if batch:
                yield batch

    def save_to_mongodb(self):
        db = self.client[self.db]
        collection = db[self.collection]
        for idx, batch in enumerate(self.read_lines()):
            print("Inserting batch", idx)
            prepared_batch = [doc for doc in map(to_document, batch) if doc is not None]
            if prepared_batch:
                collection.insert_many(prepared_batch)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--uri', required=True, help="mongodb uri with username/password")
    parser.add_argument('-i', '--input', required=True, help="input file in JSON Lines format")
    parser.add_argument('-c', '--collection', required=True, help="name of the mongodb collection where the data should be stored")
    args = parser.parse_args()
    importer = JsonLinesImporter(args.input, collection=args.collection, mongo_uri=args.uri)
    importer.save_to_mongodb()
