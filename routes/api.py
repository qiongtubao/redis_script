# coding=utf-8
import logging
import credis
from routes.docker import k8s
import xpipe
import redis_tool
from routes.redis_tool.redisSession import MonitorInfo
from routes.redis_tool.sentinel import Sentinel
import utils
import json
import math
import docker
import time

class Api(object): 
    def __init__(self, credis_url, credis_headers, xpipe_url, xpipe_headers, k8s_env):
        self.credis = credis.Credis(credis_url, credis_headers)
        self.k8s = docker.K8s(k8s_env)
        self.xpipe = xpipe.Xpipe(xpipe_url, xpipe_headers)
    
    def get_cluster_info(self, argv):
        argc = len(argv)
        if argc >= 1:
            info =  self.credis.get_cluster_info(argv[0])
            if argc >= 2:
                file = utils.File(argv[1])
                file.write_json(info)
            print(info)
            return info
        else:
            print("function [get_cluster] loss argv!!!!!");
            return
    # close_credis_monitor {cluster_name} {close_time}
    def close_credis_monitor(self, argv):
        argc = len(argv)
        if  argc == 1:
            self.credis.close_credis_monitor(argv[0])
        elif argc == 2:
            self.credis.close_credis_monitor(argv[0], argv[1])
        else :
            print("function [close_credis_monitor] argv error!!!!!")
            return 
    def start_credis_monitor(self, argv):
        argc = len(argv)
        if  argc == 1:
            self.credis.start_credis_monitor(argv[0])
        else:
            print("function [start_credis_monitor] argv error!!!!!")
            return 
    # get_redis_sentinel {host} {port} {save_file}
    def get_redis_sentinel(self, argv):
        argc = len(argv)
        if  argc >= 2:
            redis = redis_tool.RedisSession(argv[0], int(argv[1]))
            result = redis.get_sentinels()
            if argc == 3:
                file = utils.File(argv[2])
                file.write_str(utils.endcoder.json_serialize(result))
            print(utils.endcoder.json_serialize(result))
        else:
            print("function [start_credis_monitor] argv error!!!!!")
            return 
    def remove_redis_sentinel(self, argv):
        argc = len(argv)
        if  argc >= 2:
            redis = redis_tool.RedisSession(argv[0], int(argv[1]))
            result = redis.get_sentinels()
            for sentinel in result.sentinels:
                if sentinel.remove(result.monitor_name) == False:
                    return
            print("remove sentinels success")
        else:
            print("function [remove_redis_sentinel] argv error!!!!!")
            return 
    def remove_slave(self, argv):
        argc = len(argv)
        if  argc >= 4:
            redis = redis_tool.RedisSession(argv[0], int(argv[1]))
            result = redis.get_sentinels()
            for sentinel in result.sentinels:
                if sentinel.remove(result.monitor_name) == False:
                    return
            print("remove sentinels success")
            slave = redis_tool.RedisSession(argv[2], int(argv[3]))
            print("slaveof no one result %s" %(slave.slaveof("no", "one")))
        else:
            print("function [remove_redis_sentinel] argv error!!!!!")
            return
    def restore_redis_sentinel(self, argv):
        argc = len(argv)
        if  argc >= 1:
            file = utils.File(argv[0])
            monitor_info =  MonitorInfo()
            utils.endcoder.json_deserialize(file.read_str(),monitor_info)
            monitor_len = len(monitor_info.sentinels)
            for sentinel in monitor_info.sentinels:
                if sentinel.monitor(monitor_info.monitor_name, monitor_info.master_host, monitor_info.master_port, int(math.ceil(monitor_len/2.0))) == False:
                    return
        else:
            print("function [restore_sentinel] argv error!!!!!")
            return 
    def k8s_find(self, argv):
        argc = len(argv)
        if  argc >= 2:
            print(self.k8s.get_docker_info(argv[0], argv[1]))
        else:
            print("function [k8s_find] argv error!!!!!")
            return 
    def k8s_del(self, argv):
        argc = len(argv)
        if argc >= 1:
            map = {}
            while len(argv) != 0:
                info = self.k8s.get_docker_info(argv[0])
                ips = self.k8s.query_all_docker(info)
                num = 0
                # 默认传入的参数不重
                will_del = True
                for ip in ips:
                    remove = False
                    for i in range(len(argv)-1, -1, -1):
                        if argv[i] == ip:
                            argv.pop(i)
                            remove = True
                            break
                    if remove == False:
                        print("not find redis %s" % ip);
                        will_del = False
                        break
                
                if will_del:
                    self.k8s.del_docker(info)   
        else:
            print("function [restore_sentinel] argv error!!!!!")
            return
    def del_cluster(self, argv):
        argc = len(argv)
        if  argc >= 1:
            info = self.credis.get_cluster_info(argv[0])
            # cluster.json
            file = utils.File(argv[0] + ".json")
            file.write_json(info)
            groups = info["Groups"]
            if len(groups) > 0:
                self.credis.close_credis_monitor(argv[0], 10)
            redises = []
            for group in groups:
                instances = group["Instances"]
                groupId = group["ID"]
                print("groupId: %s" % (groupId))
                for instance in instances:
                    print("instance: %s:%d ,id :%d" %(instance["IPAddress"], instance["Port"], instance["ID"]))
                    redis = redis_tool.RedisSession(instance["IPAddress"], int(instance["Port"]))
                    result = redis.get_sentinels()
                    if result != None:
                        for sentinel in result.sentinels:
                            sentinel.remove(result.monitor_name)
                        print("remove %s:%d sentinels success" % (instance["IPAddress"], instance["Port"]))
                    self.credis.del_instance(instance["ID"])
                    redises.append({
                        'host': instance["IPAddress"], 
                        'port': int(instance["Port"]),
                        'groupId': groupId
                    })
            logging.info("del all redis: %s" % (redises))
            docker_info = {}
            while len(redises) != 0:
                docker_info = self.k8s.get_docker_info(redises[0]["host"], redises[0]["port"], redises[0]["groupId"] )
                dockers = self.k8s.query_all_docker(docker_info)
                if len(dockers) != 0:
                    # 默认传入的参数不重
                    will_del = True
                    for docker in dockers:
                        remove = False
                        for i in range(len(redises)-1, -1, -1):
                            if redises[i]["host"] == docker["host"] and redises[i]["port"] == docker["port"]:
                                redises.pop(i)
                                remove = True
                                break
                        if remove == False:
                            logging.error("not find redis %s:%d" % (docker["host"], docker["port"]));
                            will_del = False
                            break
                    
                    if will_del:
                        logging.info("[will del_docker] groupName:%s, groupId: %s, env: %s, dockerNum: %d " % (docker_info.groupName, docker_info.groupId, docker_info.env, docker_info.dockerNum));
                        
                        if not self.k8s.del_docker(docker_info):
                            time.sleep(5)
                            if not self.k8s.del_docker(docker_info):
                            	logging.warn("[del_docker] error, start try del with groupId - 10000000")
                            	docker_info["groupId"] = docker_info["groupId"] - 10000000
                            	if not self.k8s.del_docker(docker_info):
                                    logging.warn("[del_docker] fail")
            self.credis.del_cluster(info["ID"])

        else:
            print("function [del_cluster] argv error!!!!!")
            return
    def config_set(self, argv):
        # config_set <cluster> 
        argc = len(argv)
        if  argc >= 1:
            info = self.credis.get_cluster_info(argv[0])
            i = 1;
            action = "set"
            while i < argc:
                if argv[i] == "crdt.set":
                    action = "crdt.set"
                    i+=1
                    continue
                elif argv[i] == "set":
                    action = "set"
                    i+=1
                else:
                    print("index : %d %s" % (i, argv[i]))
                    groups = info["Groups"]
                    for group in groups:
                        instances = group["Instances"]
                        groupId = group["ID"]
                        print("groupId: %s" % (groupId))
                        for instance in instances:
                            print("instance: %s:%d ,id :%d" %(instance["IPAddress"], instance["Port"], instance["ID"]))
                            redis = redis_tool.RedisSession(instance["IPAddress"], int(instance["Port"]))
                            redis.config_set(action, argv[i], argv[i+1])
                    i += 2
        else:
            print("function [config_set] argv error!!!!!")
            return
    def cluster_dbsize(self, argv):
        argc = len(argv)
        if  argc >= 1:
            info = self.credis.get_cluster_info(argv[0])
            groups = info["Groups"]
            size = 0;
            for group in groups:
                instances = group["Instances"]
                groupId = group["ID"]
                print("groupId: %s" % (groupId))
                redis = redis_tool.RedisSession(instances[0]["IPAddress"], int(instances[0]["Port"]))
                redis_size = redis.dbsize();
                size += redis_size
                print("instance: %s:%d ,id :%d ,dbsize %d" %(instances[0]["IPAddress"], instances[0]["Port"], instances[0]["ID"], redis_size))
            print("cluster %s dbsize %d" %(argv[0], size))
        else:
            print("function [cluster_dbsize] argv error!!!!!")
            return
    def query_cluster_use_commands(self, argv):
        argc = len(argv)
        all = {}
        if argc >= 1:
            info = self.credis.get_cluster_info(argv[0])
            groups = info["Groups"]
            size = 0;
            for group in groups:
                instances = group["Instances"]
                groupId = group["ID"]
                print("groupId: %s" % (groupId))
                for instance in instances:
                    redis = redis_tool.RedisSession(instance["IPAddress"], int(instances[0]["Port"]))
                    result = redis.info_commandstats();
                    for command_stats in result:
                        all[command_stats[8:]] = 1
            print("cluster all used commans:")
            print(all)
        else:
            print("function [query_cluster_use_commands] argv error!!!!!")
            return
    def get_clusters_use_commands(self, argv):
        argc = len(argv)
        if argc >= 1:
            # type 
            clusters = self.xpipe.get_clusters(argv[0])
            for cluster in clusters:
                print("cluster: %s" % cluster)
                all = {}
                info = self.credis.get_cluster_info(cluster)
                groups = info["Groups"]
                for group in groups:
                    instances = group["Instances"]
                    groupId = group["ID"]
                    print("groupId: %s" % (groupId))
                    for instance in instances:
                        redis = redis_tool.RedisSession(instance["IPAddress"], int(instances[0]["Port"]))
                        try:
                            result = redis.info_commandstats();
                            for command_stats in result:
                                all[command_stats[8:]] = 1
                        except Exception as error:
                            print("info_commandstats error: %s", error)
                print("cluster %s used commands: %s" % (cluster, all))
        else:
            print("function [get_clusters_use_commands] argv error!!!!!")
            return
    def add_idc_redis(self, argv):
        argc = len(argv)
        # clustername IDC redisnum groupname
        if argc >= 3:
            cluster_name = argv[0]
            groupname = argv[0]
            if argc >= 4: 
                groupname = argv[3]
            info = self.credis.get_cluster_info(argv[0])
            idc = argv[1]
            orgId = info["ProductID"]
            groups = info["Groups"]
            i = 0
            for group in groups:
                i = i + 1
                groupId = group["ID"]
                info = {}
                if len(group["Instances"]) > 0: 
                    redis_info = self.xpipe.get_shard_redis_info(cluster_name,idc,groupname + "_" + str(i))
                    instance = group["Instances"][0]
                    master_redis = redis_tool.RedisSession(instance["IPAddress"], int(instance["Port"]))
                    docker_info = self.k8s.get_docker_info(instance["IPAddress"], int(instance["Port"]), groupId)
                    master_maxmemory = master_redis.config_get("get","maxmemory");
                    master_name_space = None;
                    if docker_info.info["instanceType"] == "rediscrdt":
                        master_name_space = master_redis.config_get("crdt.get", "crdt-gid").split(" ")[0];
                    info["type"] = docker_info.info["label"];
                    info["clusterName"] = docker_info.info["clusterName"];
                    info["orgId"] = docker_info.info["orgId"];
                    info["groupId"] = groupId;
                    info["instanceType"] = docker_info.info["instanceType"];
                    info["flavor"] = docker_info.info["flavor"];
                    info["idc"] = idc;
                    info["replicas"] = int(argv[2]);
                    info["env"] = docker_info.info["env"];
                    if idc == "SIN-AWS" or idc == "FRA-AWS":
                        info["arch"] = "arm64"
                    docker_groupname = self.k8s.create_docker(info);
                    logging.info("docker groupname %s" % docker_groupname);
                    try_num = 12 * 5;
                    ginfo = {}
                    ginfo["groupId"] = groupId;
                    ginfo["groupName"] = docker_groupname;
                    ginfo["env"] = docker_info.info["env"];
                    while try_num > 0:
                        docker_info_result = self.k8s.get_docker_info_by_groupname(ginfo)
                        if docker_info_result != None and docker_info_result[0]["server"] != None and docker_info_result[0]["server"] != "":
                            print(docker_info_result[0]["server"])
                            break
                        else:
                            try_num -= 1
                            if try_num == 0:
                                print("wait create docker fail %s "%(docker_groupname))
                                logging.error("wait create docker fail %s"%(docker_groupname))
                                return
                            time.sleep(5)
                    
                    new_master = redis_tool.RedisSession(docker_info_result[0]["server"], docker_info_result[0]["port"])
                    new_master_host = docker_info_result[0]["server"]
                    new_master_port = int(docker_info_result[0]["port"])
                    new_master.config_set("set", "maxmemory", master_maxmemory);
                    redis_info['redises'].append({
                        "redisPort": new_master_port,
                        "master": True,
                        "redisIp": new_master_host
                    })
                    if master_name_space != None:
                        new_master.config_set("crdt.set", "crdt-gid", master_name_space);
                    for i in range(1, len(docker_info_result)):
                        new_slave = redis_tool.RedisSession(docker_info_result[i]["server"], docker_info_result[i]["port"])
                        new_slave.config_set("set", "maxmemory", master_maxmemory);
                        if master_name_space != None:
                            new_slave.config_set("crdt.set", "crdt-gid", master_name_space);
                        new_slave.slaveof(new_master_host, new_master_port)
                        logging.info("new_slave[%s]: %s:%d slaveof %s:%d\n"%(docker_groupname, docker_info_result[i]["server"], docker_info_result[i]["port"], new_master_host, new_master_port))
                        redis_info['redises'].append({
                            "redisPort": int(docker_info_result[i]["port"]),
                            "master": False,
                            "redisIp": docker_info_result[i]["server"]
                        })
                    self.xpipe.update_shard_redis_info(cluster_name,idc,groupname + "_" + str(i), redis_info) 
        else:
            print("function [cluster_add_slave] argv error!!!!!")
            return
    def cluster_add_slave(self, argv):
        argc = len(argv)
        if argc >= 1:
            info = self.credis.get_cluster_info(argv[0])
            orgId = info["ProductID"]
            groups = info["Groups"]
            for group in groups:
                instances = group["Instances"]
                groupId = group["ID"]
                for instance in instances:
                    if instance["ParentID"] == 0: # is master
                        master_redis = redis_tool.RedisSession(instance["IPAddress"], int(instance["Port"]))
                        docker_info = self.k8s.get_docker_info(instance["IPAddress"], int(instance["Port"]), groupId)
                        master_maxmemory = master_redis.config_get("get","maxmemory");
                        master_name_space = None;
                        if docker_info.info["instanceType"] == "rediscrdt":
                            master_name_space = master_redis.config_get("crdt.get", "crdt-gid").split(" ")[0];
                        info = {}
                        info["type"] = docker_info.info["label"];
                        info["clusterName"] = docker_info.info["clusterName"];
                        info["orgId"] = docker_info.info["orgId"];
                        info["groupId"] = groupId;
                        info["instanceType"] = docker_info.info["instanceType"];
                        info["flavor"] = docker_info.info["flavor"];
                        info["idc"] = docker_info.info["idc"];
                        info["replicas"] = 1;
                        info["env"] = docker_info.info["env"];
                        docker_groupname = self.k8s.create_docker(info);
                        try_num = 12 * 5;
                        ginfo = {}
                        ginfo["groupId"] = groupId;
                        ginfo["groupName"] = docker_groupname;
                        ginfo["env"] = docker_info.info["env"];
                        while try_num > 0:
                            docker_info_result = self.k8s.get_docker_info_by_groupname(ginfo)
                            
                            if docker_info_result != None and docker_info_result[0]["server"] != None and docker_info_result[0]["server"] != "":
                                print(docker_info_result[0]["server"])
                                break
                            else:
                                try_num -= 1
                                if try_num == 0:
                                    print("wait create docker fail %s "%(docker_groupname))
                                    logging.error("wait create docker fail %s"%(docker_groupname))
                                    return
                                time.sleep(5)
                        new_redis = redis_tool.RedisSession(docker_info_result[0]["server"], docker_info_result[0]["port"])
                        new_redis.config_set("set", "maxmemory", master_maxmemory);
                        if master_name_space != None:
                            new_redis.config_set("crdt.set", "crdt-gid", master_name_space);
                        #new_redis.slaveof(instance["IPAddress"], int(instance["Port"]))
                        print("new_redis[%s]: %s:%d slaveof %s:%d\n"%(docker_groupname, docker_info_result[0]["server"], docker_info_result[0]["port"], instance["IPAddress"], int(instance["Port"])))
                        
        else:
            print("function [cluster_add_slave] argv error!!!!!")
            return
            

                
    def test(self, argv):
        for i in range(1, 3):
            print(i)
        
