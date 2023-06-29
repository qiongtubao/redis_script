import logging
import requests
import json

class Xpipe(object):
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
    def get_clusters(self, type=None):
        res = requests.get(self.url + '/console/clusters/all', headers=self.headers)
        res.encoding = 'utf-8';
        logging.info("[get_clusters] allcluster result: %s" %  res.json())
        clusters = res.json()
        result = []
        for cluster in clusters:
            if type != None:
                if cluster['clusterType'].lower() == type.lower() :
                    result.append(cluster['clusterName'])
            else:
                result.append(cluster['clusterName'])
        return result
    def get_shard_redis_info(self, cluster, idc, group):
        payload = {}
        res = requests.get(self.url + "/console/clusters/" + cluster + "/dcs/" + idc + "/shards/" + group, headers=self.headers, data=payload)
        logging.info("[get_shard_redis_info] result: %s" %  res.json())
        return res.json()
    def update_shard_redis_info(self, cluster, idc, group, redisinfo):
        res = requests.post(self.url + "/console/clusters/" + cluster + "/dcs/" + idc + "/shards/" + group, headers=self.headers, data=json.dumps(redisinfo))
        logging.info("[update_shard_redis_info] result: %s" %  res.text)
        return res.text      