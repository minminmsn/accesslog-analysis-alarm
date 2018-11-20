#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import datetime
import time
import urllib
import urllib2
from elasticsearch import Elasticsearch
from elasticsearch import helpers

#索引名字
index_name = "filebeat-ngx1-135-*"

#实例化Elasticsearch类，并设置超时间为180秒，默认是10秒的，如果数据量很大，时间设置更长一些
es = Elasticsearch(['192.188.2.213','192.188.2.214'],timeout=180)


#DSL（领域特定语言）查询语法，查询最近1分钟该URL出现次数统计，排序TOP10
data_getip = {
  "aggs": {
    "counts": {
      "terms": {
        "field": "url.raw",
        "size": 10
      }
    }
  },
 "query": {
    "bool": {
      "must": [
        {
          "query_string": {
            "query": "http_host.raw:\"www.minminmsn.com\""
          }
        },
        {
          "range": {
            "@timestamp": {
              "gte": "now-5m/m",
              "lte": "now"
            }
          }
        }
      ],
      "must_not": [{"regexp": {"clientRealIp.raw": "(172.*|192.*)" }}]
    }
  }
}

#按照DSL（特定领域语言）语法查询获取数据
def get_original_data():
    try:
        #根据上面条件搜索数据
        res = es.search(
            index=index_name,
            size=0,
            body=data_getip
        )
        return res

    except:
        print "get original data failure"

def Writelog(f_url,f_count):
	datetime_now=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        fp = open('baa_denyurl.log', 'a')
	fp.write(str(datetime_now) + " " + str(f_url) + " " + str(f_count) + "\n")
	fp.close()


def get_blockurl_data():
    try:
        #列表形式显示结果
        res = get_original_data()
        res_list = res.get('aggregations').get('counts').get('buckets')
        #print res_list
	urlstr=""
	result_array=[]
	f = open("whitelist.txt")
	line = f.read()
	print line
	for x in res_list:
		if x["doc_count"]>20000 and (x['key'] not in line):
			urlstr+=x['key']+","
			Writelog(x['key'],x["doc_count"])			
	if len(urlstr)>0:
		urlstr=urlstr[:-1]
	#print urlstr
	return urlstr
    except Exception,e:
        print "get blockip data failure"
	return "None"

def add_domain():
    try:
	urls=get_blockurl_data()
	#print urls
        headers = {'host':'api.minminmsn.com'}
	block_data = {'url':urls,'type':'0'}
	data=urllib.urlencode(block_data)
        requrl = "http://api.minminmsn.com/ipops/blockurl.php"
     	req = urllib2.Request(requrl, data)
        response = urllib2.urlopen(req)

        res = response.read()
    
    except Exception, e:
	print repr(e)
	print (e.code)
       
if __name__ == "__main__":
    #get_blockurl_data()
    add_domain()
