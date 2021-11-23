import json
import redis
class Sentinel(object):
    def __init__(self, host="", port=-1) :
        self.host = host 
        self.port = port
    def monitor(self, monitor_name, master_host, master_port, quorum):
        client = redis.Redis(self.host, self.port)
        try:
            client.sentinel_monitor(monitor_name, master_host, master_port, quorum)
            print("%s:%d sentinel monitor success %s %s:%d %d" % (self.host, self.port, monitor_name, master_host, master_port, quorum))
            return True
        except Exception as e:
            print("%s:%d sentinel monitor fail %s %s:%d %d" % (self.host, self.port, monitor_name, master_host, master_port, quorum))
            print("sentinel monitor error: %s" % e);
            return False

    def remove(self, monitor_name):
        client = redis.Redis(self.host, self.port)
        try:
            result = client.sentinel_remove(monitor_name)
            print("%s:%d remove sentinel success %s" %(self.host, self.port, monitor_name))
            return True
        except Exception as e:
            print("%s:%d remove sentinel fail %s" %(self.host, self.port, monitor_name) )
            print("remove sentinel error: %s" % e);
            return False
        

    