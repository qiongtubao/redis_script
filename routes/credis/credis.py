
from json import encoder
import requests
import json

dba_token = "31f0deadf2bf9942gydd3agh5gfs3ju"

class Credis(object):
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def get_cluster_info(self, cluster_name):
        print(self.url, cluster_name)
        res = requests.get(self.url + '/opsapi/GetOpsClusterV2?clusterName=' + cluster_name)
        res.encoding = 'utf-8';
        return res.json()
    def close_credis_monitor(self, cluster_name, time):
        res = requests.post(self.url + '/opsapi/cluster/monitor/'+ cluster_name +'/stop/' + time)
        res.encoding = 'utf-8';
        return res.json()
    def start_credis_monitor(self, cluster_name):
        res = requests.post(self.url + '/opsapi/cluster/monitor/'+ cluster_name +'/start')
        res.encoding = 'utf-8';
        return res.json()
        
    def del_instance(self, id):
        res = requests.post(self.url + '/redisapi/InstanceDelete', json={
            'ID': id,
            'Token': dba_token
        });
        res.encoding = 'utf-8';
        return res.json()
    def del_cluster(self, id):
        res = requests.post(self.url + "/redisapi/ClusterDelete", json={
            'ID': id,
            'Token': dba_token
        })
        res.encoding = 'utf-8';
        return res.json()