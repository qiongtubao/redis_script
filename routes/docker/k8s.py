
import json
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
    def __init__(self, env, groupName, groupId, dockerNum):
        self.env = env
        self.groupName = groupName
        self.groupId = groupId
        self.dockerNum = dockerNum

class K8s(object):
    def __init__(self, env):
        self.env = env
    def get_docker_info(self, host, port=6379):
        print(self.env, host ,port)
        res = requests.get('http://cd.release.ctripcorp.com/api/v2/redisservice/isdocker?ip=%s&port=%d' % (host, port))
        res.encoding = 'utf-8';
        payload = res.json()["content"];
        print('get_docker_info: %s' % payload)
        if payload != '':
            return Info(payload["env"], payload["dockerGroupName"], payload["groupId"], payload["dockerGroupNumber"])
        else:
            return None
    def del_docker(self, info):
        print("del_docker groupId:%s dockerGroupName:%s, env:%s stsNum:%d" % (info.groupId, info.groupName, info.env, info.dockerNum))
        res = requests.post('http://cd.release.ctripcorp.com/api/v2/redisservice/fxdelete', headers=headers, json={
            "groupId": info.groupId,
            "dockerGroupName": info.groupName,
            "env": info.env,
            "stsNum": info.dockerNum
        })
        result = res.json()
        print("del_docker: %s" % result)
        return result["issuccess"]
    def query_all_docker(self, info):
        res = requests.post('http://cd.release.ctripcorp.com/api/v2/redisservice/fxgetstatus', headers=headers, json={
            "groupId": info.groupId,
            "dockerGroupName": info.groupName,
            "env": info.env
        })
        ips = []
        content = res.json()["content"]
        print("query_all_docker: %s" % content)
        for c in content:
            ips.append(c["server"])
        return ips
    