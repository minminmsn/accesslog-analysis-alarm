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
index_name = "filebeat-nginxlog-*"

#实例化Elasticsearch类，并设置超时间为180秒，默认是10秒的，如果数据量很大，时间设置更长一些
es = Elasticsearch(['192.188.2.213','192.188.2.214'],timeout=180)


#DSL（领域特定语言）查询语法，查询最近1分钟该URL出现次数统计，排序TOP10
data_getip = {
  "aggs": {
    "counts": {
      "terms": {
        "field": "clientRealIp.raw",
        "size": 100
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
              "gte": "now-1m/m",
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


def get_blockip_data():
    try:
        #列表形式显示结果
        res = get_original_data()
        res_list = res.get('aggregations').get('counts').get('buckets')
        #print res_list
	ipstr=""
	for x in res_list:
		if x["doc_count"]>500:
			ipstr+=x['key']+","
	if len(ipstr)>0:
		ipstr=ipstr[:-1]
	#print ipstr
	return ipstr
        #判断ip是否属于白名单，白名单应该剔除
        
        #最后需要备份ipstr列表

    except:
        print "get blockip data failure"


def add_blockip_domain():
    try:
        #列表形式显示结果
        res_ip = get_blockip_data()
        #res_ip="'" + res_ip + "'"
        print res_ip
        
        #add blockip 
        headers = {'Host':'api.minminmsn.com','Referer': 'http://api.minminmsn.com/'}
        blockip_data = {'token':'6e5ff3f200eab5594d3452b69596dc40','domainname':'www.minminmsn.com','ip': res_ip,'type':'1'}
        print blockip_data
	data = urllib.urlencode(blockip_data)   
  
  
        requrl = "http://api.minminmsn.com/ipops/blockip.php"
        #requrl = "http://www.baidu.com"
	req = urllib2.Request(requrl, data, headers)
	#req = urllib2.Request(requrl)

        response = urllib2.urlopen(req)
        #res = response.read()
        #print res
    except Exception, e:
	print e.code
	#print repr(e)
        #print "add blockip to domain failure"



if __name__ == "__main__":
    add_blockip_domain()
