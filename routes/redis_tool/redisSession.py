import redis
import time
import sentinel 
import json

class MonitorInfo(object):
    sentinels = [sentinel.Sentinel()]
    monitor_name = ""
    master_host = ""
    master_port = -1
    def resetSentinels(self, map):
        sentinels = []
        for k,v in map.items():
            sentinels.append(v)
        self.sentinels = sentinels




    


class RedisSession(object):
    def __init__(self, host, port):
        self.host = host 
        self.port = port
        print(host, port)
        try:
            self.client = redis.Redis(host, port)
        except Exception as e:
            print("connect redis error: %s" % e)
    def get_sentinels(self, wait_time=5):
        session = redis.StrictRedis(self.host, self.port, socket_timeout = 5)
        pubsub =session.pubsub()
        pubsub.subscribe("__sentinel__:hello")
        sentinels = {}
        monitor_name = None
        start_time = (int)(time.time())  
        master_host = None
        master_port = -1
        for item in pubsub.listen():
            if (int)(time.time()) - start_time > wait_time:
                break
            if item['type'] == 'message':
                sentinel_info = item['data']
                split = sentinel_info.split(",")
                
                sentinel_uri = split[0] + ":" + split[1]
                if sentinels.get(sentinel_uri) == None:
                    # sentinel = {"host": str(split[0]), "port": int(split[1])}
                    sentinels[sentinel_uri] = sentinel.Sentinel(split[0], int(split[1]))
                if monitor_name == None :
                    monitor_name = split[4] 
                elif monitor_name != None and monitor_name != split[4]:
                    print("monitor_name: %s != %s" % (monitor_name, split[4]))
                if master_host == None:
                    master_host = str(split[5])
                    master_port = int(split[6])
                elif master_host != None and (master_host != str(split[5]) or master_port != int(split[6])):
                    print("master_host: %s:%s != %s:%s" % (master_host, master_port, split[5], split[6]))
        monitor_info = MonitorInfo()
        monitor_info.resetSentinels(sentinels)
        monitor_info.master_host = master_host
        monitor_info.master_port = master_port
        monitor_info.monitor_name = monitor_name
        return monitor_info

        # return {"sentinels": sentinels, "monitor_name": monitor_name, "master": master}
