# coding=utf-8
import credis
import redis_tool
from routes.redis_tool.redisSession import MonitorInfo
from routes.redis_tool.sentinel import Sentinel
import utils
import json
import math
import docker

class Api(object): 
    def __init__(self, url, headers, k8s_env):
        self.credis=credis.Credis(url, headers)
        self.k8s = docker.K8s(k8s_env)
    
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
        if  argc >= 1:
            print(self.k8s.get_docker_info(argv[0]))
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



