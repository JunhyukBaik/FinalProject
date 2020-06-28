#!/usr/bin/python
from elasticsearch import Elasticsearch, NotFoundError


es = Elasticsearch()


if __name__=="__main__":
    ipAddress='127.0.0.1'
    es = Elasticsearch([{'es_host':ipAddress, 'es_port':'9200'}], timeout=30)

    elasticSettings = { 
        'settings': {
            'index.mapping.total_fields.limit':20000
        }
    }

    try:
        es.search(index='website')
        es.indices.delete(index='website')
    except NotFoundError:
        pass
        
    es.indices.create(index='website', body=elasticSettings)

def web_count():
    elasticWebsiteCount = es.count(index='website', doc_type='urldata')['count']
    print(elasticWebsiteCount)


def mathcing_with_web():
    nowWeb='https://apache.org/'
    doc = es.search(body={"query":{"match":{"URL.keyword":nowWeb}}}, index='website', doc_type='urldata')['hits']['total']['value']
    print('\n\n', doc)


def file_input_test():
    import Multi_website_Crawler
    URL_list = Multi_website_Crawler.multi_URL_analyze("URL_test.txt")

    print("Total URLs = ", len(URL_list))
    for dic in URL_list:
        print(dic, '\n\n')
