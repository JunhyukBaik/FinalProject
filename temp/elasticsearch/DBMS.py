from elasticsearch import Elasticsearch
from elasticsearch import helpers

def make_index(es, index_name):
    if es.indices.exists(index = index_name):
        es.indices.delete(index = index_name)
    
    print(es.indices.create(index = index_name))



def insertData():
    es = Elasticsearch('127.0.0.1:9200')   
    index_name = "Crawling_list"
    make_index(es, index_name)

    doc = {
            "name" : project_name,
            "word_num" : number of word,
            "time" : spent time
            }
    
    es.index(index = "Crawling_list", doc_type = "_doc", body=doc)
    es.indices.refresh(index = index_name)



def searchDB():
    es = Elasticsearch('127.0.0.1:5050')

    index = index_for_search
    body = {
            "query": {
                "match_all": {}
                }
            }

    result =  es.search(index = index, body = body)

