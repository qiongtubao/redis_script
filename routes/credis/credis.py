# coding=utf-8
from json import encoder
import logging
import requests
import json

dba_token = "31f0deadf2bf9942gydd3agh5gfs3ju"

class Credis(object):
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def get_cluster_info(self, cluster_name):
        res = requests.get(self.url + '/opsapi/GetOpsClusterV2?clusterName=' + cluster_name)
        res.encoding = 'utf-8';
        logging.info("[get_cluster_info] cluster:%s result: %s" % (cluster_name, res.json()))
        return res.json()
    def close_credis_monitor(self, cluster_name, time):
        logging.info("[close_credis_monitor] cluster:%s close_time: %d" %(cluster_name, time))
        res = requests.post(self.url + '/opsapi/cluster/monitor/'+ cluster_name +'/stop/' + str(time))
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
        result = res.json()
        logging.info("[del_instance] id: %d, result:%s" %(id, result))
        return result
    def del_cluster(self, id):
        res = requests.post(self.url + "/redisapi/ClusterDelete", json={
            'ID': id,
            'Token': dba_token
        })
        res.encoding = 'utf-8';
        result = res.json()
        logging.info("[del_cluster] id: %d, result:%s" %(id, result))
        return result
    def add_instance(self, info):
        info["Token"] = dba_token;
        
        res = requests.post(self.url + '/redisapi/InstanceUpdate', json=info);
        res.encoding = 'utf-8';
        logging.info("[add_instance] %s, result:%s" %(info, res.text))
        result = res.json()
        return result
    def create_cluster(self, info):
        ##
        # {
        #     "ID":0,
        #     "Name":"credis-api-test",
        #     "Status":1,
        #     "SubsystemName":"03Service",
        #     "SubsystemID":189,
        #     "Contactor":"周国栋",
        #     "Email":"gd.zhou@trip.com",
        #     "Creator":"gd.zhou",
        #     "CreateTime":null,
        #     "UpdateTime":null,
        #     "Remark":null,
        #     "PoolID":0,
        #     "DBNumber":0,
        #     "Token":"31f0deadf2bf9942gydd3agh5gfs3ju",
        #     "UsingIDC":0,
        #     "PoolName":null,
        #     "ProductID":44,
        #     "ProductName":"框架架构",
        #     "MasterIDC":"",
        #     "ClusterType":0,
        #     "FrozenStatus":0,
        #     "SwitchV3":0,
        #     "CreateStatus":0,
        #     "HashType":0,
        #     "Route":null,
        #     "Importance":null
        # }
        ##
        info["Token"] = dba_token;
        res = requests.post(self.url + '/redisapi/ClusterUpdate', json=info);
        res.encoding = 'utf-8';
        logging.info('[create_cluster] %s, result:%s' %(info, res.text));
        result = res.json()
        ##
        # {
        #     "Success": true,
        #     "Result": 25487
        # }
        ##
        return result
    def update_cluster(self, info):
        ##
        # {
        #     "ID":0,
        #     "Name":"credis-api-test",
        #     "Status":1,
        #     "SubsystemName":"03Service",
        #     "SubsystemID":189,
        #     "Contactor":"周国栋",
        #     "Email":"gd.zhou@trip.com",
        #     "Creator":"gd.zhou",
        #     "CreateTime":null,
        #     "UpdateTime":null,
        #     "Remark":null,
        #     "PoolID":0,
        #     "DBNumber":0,
        #     "Token":"31f0deadf2bf9942gydd3agh5gfs3ju",
        #     "UsingIDC":1,
        #     "PoolName":null,
        #     "ProductID":44,
        #     "ProductName":"框架架构",
        #     "MasterIDC":"",
        #     "ClusterType":4,
        #     "FrozenStatus":0,
        #     "SwitchV3":0,
        #     "CreateStatus":0,
        #     "HashType":0,
        #     "Route":null,
        #     "Importance":null
        # }
        ##
        info["Token"] = dba_token;
        res = requests.post(self.url + '/redisapi/ClusterUpdateByName', json=info);
        res.encoding = 'utf-8';
        logging.info('[create_cluster] %s, result:%s' %(info, res.text));
        result = res.json()
        ##
        # {
        #     "Message": "修改成功",
        #     "Success": true
        # }
        ##
        return result
    def cluster_add_group(self, info):
        ##
        # {
        #     "ID":0,
        #     "PoolID":0,
        #     "Status":0,
        #     "Creator":"",
        #     "CreateTime":null,
        #     "UpdateTime":null,
        #     "Remark":"",
        #     "Name":"group1_2",
        #     "ClusterID":2503,
        #     "PoolName":null,
        #     "Env":"",
        #     "SubEnv":"",
        #     "Token":"31f0deadf2bf9942gydd3agh5gfs3ju"
        # }
        ##
        info["Token"] = dba_token;
        res = requests.post(self.url + '/redisapi/GroupUpdate', json=info);
        res.encoding = 'utf-8';
        logging.info('[cluster_add_group] %s, result:%s' %(info, res.text));
        result = res.json()
        ##
        # {
        #     "GroupName": "gd-credis-api-test_2",
        #     "Success": true,
        #     "Result": 1000131500
        # }
        ##
        return result