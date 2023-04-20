
import json
import logging
import requests


domain = "http://cd.release.ctripcorp.com"
headers = {
    "X-SERVICE-TOKEN": "f38af46bc18a2f9a1f0a4469df0dd0184f058198fe95f46d24b6f6d2ae7cc9a2",
    "Content-Type": "application/json"
}

class Info(object):
    groupName = ""
    dockerNum = 2
    env = "UAT"
    groupId = ""
    clusterName = ""
    info = {}
    def __init__(self, env, groupName, groupId, dockerNum, info):
        self.env = env
        self.groupName = groupName
        self.groupId = groupId
        self.dockerNum = dockerNum
        self.info = info


class K8s(object):
    def __init__(self, env):
        self.env = env
    def get_docker_info(self, host, port=6379, groupId=0):
        res = requests.get('http://cd.release.ctripcorp.com/api/v2/redisservice/isdocker?ip=%s&port=%d' % (host, port))
        res.encoding = 'utf-8';
        result = res.json()
        payload = result["content"];
        logging.info('[get_docker_info] host: %s, port: %d , result: %s' % (host,port,result))
        if payload != '':
            return Info(payload["env"], payload["dockerGroupName"], groupId, payload["dockerGroupNumber"], payload)
        else:
            return None
    def get_docker_info_by_groupname(self, info):
        res = requests.post('http://cd.release.ctripcorp.com/api/v2/redisservice/fxgetstatus', headers=headers, json={
            "groupId": info["groupId"],
            "dockerGroupName": info["groupName"],
            "env": info["env"]
        })
        result = res.json()
        logging.info("get_docker_info_by_groupname groupId:%s ,dockerGroupName:%s, env: %s, result:%s" % (info["groupId"], info["groupName"],info["env"],result))
        if result["issuccess"]:
            return result["content"]
        else:
            return None

    def del_docker(self, info):
        res = requests.post('http://cd.release.ctripcorp.com/api/v2/redisservice/fxdelete', headers=headers, json={
            "groupId": info.groupId,
            "dockerGroupName": info.groupName,
            "env": info.env,
            "stsNum": info.dockerNum
        })
        result = res.json()
        logging.info("del_docker groupId:%s ,dockerGroupName:%s, env:%s, stsNum:%d, result:%s" % (info.groupId, info.groupName, info.env, info.dockerNum, result))
        return result["issuccess"]
    def query_all_docker(self, info):
        res = requests.post('http://cd.release.ctripcorp.com/api/v2/redisservice/fxgetstatus', headers=headers, json={
            "groupId": info.groupId,
            "dockerGroupName": info.groupName,
            "env": info.env
        })
        result = res.json();
        logging.info("[query_all_docker]: groupId:%s, groupName:%s, env:%s, result:%s" % (info.groupId, info.groupName, info.env, result))
        ips = []
        content = result["content"]
        for c in content:
            ips.append({
                "host":c["server"],
                "port":int(c["port"])
            })
        return ips
    def create_docker(self, info):
        info["env"] = self.env;
        res = requests.post("http://cd.release.ctripcorp.com/api/v2/redisservice/fxcreate", headers=headers, json=info);
        res.encoding = 'utf-8';
        result = res.json();
        logging.info("[create_docker]: info:%s result:%s" % (info, result))
        if result["issuccess"]:
            return result["content"]

    def env_2_idc(self, env):
        #"UAT" => NTGXY
        #"NTGXH" => "NTGXH"
        if env == "UAT":
            return "NTGXY";
        else:
            return env
    
    