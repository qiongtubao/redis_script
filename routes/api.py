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
			print("%s" % (self.k8s.get_docker_info(argv[0], 6379, argv[1])))
		else:
			print("function [k8s_find] argv error!!!!!")
			return 
	def k8s_del(self, argv):
		argc = len(argv)
		if argc >= 1:
			map = {}
			groupId = argv.pop(0);
			print("%s" % argv)
			while len(argv) != 0:
				info = self.k8s.get_docker_info(argv[0], 6379, groupId)
				ips = self.k8s.query_all_docker(info)
				num = 0
				# 默认传入的参数不重
				will_del = True
				for ip in ips:
					remove = False
					for i in range(len(argv)-1, -1, -1):
						if argv[i] == ip["host"] and ip["port"] == 6379:
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
					docker_info = self.k8s.get_docker_info(instance["IPAddress"], int(instance["Port"]), groupId )
					dockers = self.k8s.query_all_docker(docker_info)
					if len(dockers) == 0:
						print("query docker info %s %d %s %s" % (instance["IPAddress"], int(instance["Port"]), groupId, dockers))
						docker_info = self.k8s.get_docker_info(instance["IPAddress"], int(instance["Port"]), groupId - 10000000)
						dockers = self.k8s.query_all_docker(docker_info)
						if len(dockers) == 0:
							print("query docker info2 %s %d %s %s" % (instance["IPAddress"], int(instance["Port"]), groupId - 10000000, dockers))
							return
						redises.append({
							'host': instance["IPAddress"], 
							'port': int(instance["Port"]),
							'groupId': groupId - 10000000
						})
					else:
						redises.append({
							'host': instance["IPAddress"], 
							'port': int(instance["Port"]),
							'groupId': groupId - 10000000
						})

				for instance in instances:
					self.credis.del_instance(instance["ID"])
					
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
								time.sleep(5)
								if not self.k8s.del_docker(docker_info):
									logging.error("[del_docker] fail ")
				else:
					print("query docker info2 %s %d %s %s" % (redises[0]["host"], redises[0]["port"], redises[0]["groupId"], dockers))
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
	def peerof_no_one(self, argv):
		# config_set <cluster> 
		argc = len(argv)
		if  argc >= 2:
			info = self.credis.get_cluster_info(argv[0])
			i = 1;
			while i < argc:
				print("index : %d %s" % (i, argv[i]))
				groups = info["Groups"]
				for group in groups:
					instances = group["Instances"]
					groupId = group["ID"]
					print("groupId: %s" % (groupId))
					for instance in instances:
						if instance["ParentID"] == 0:
							print("instance: %s:%d ,id :%d" % (instance["IPAddress"], instance["Port"], instance["ID"]))
							redis = redis_tool.RedisSession(instance["IPAddress"], int(instance["Port"]))
							redis.peerof(argv[i], None, 0)
				i += 1
		else:
			print("function [peerof] argv error!!!!!")
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
					if redis_info["redises"] == None:
						redis_info["redises"] = []
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
					self.credis.add_instance({
						"GroupID": groupId,
						"IPAddress": new_master_host,
						"Port": new_master_port,
						"Env": idc,
						"ParentID": 0,#0 master 1 slave
						"Status": 1,
						"CanRead": True
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
						self.credis.add_instance({
							"GroupID": groupId,
							"IPAddress": docker_info_result[i]["server"],
							"Port": docker_info_result[i]["port"],
							"Env": idc,
							"ParentID": 1,
							"Status": 1,
							"CanRead": True
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
	def create_cluster(self, argv):
		#argv[0] clusterName
		#argv[1] tmp_name
		#argv[2] Contactor
		#argv[3] SubsystemName
		#argv[4] SubsystemID
		#argv[5] ProductID
		#argv[6] ProductName
		#argv[7] groupCount
		#argv[8] IDC
		#argv[9] flavor 4C16G
		#argv[10] Orgid
		#argv[11] dockerType v2
		#argv[12] Env (PROD|FAT|UAT)
		argc = len(argv)
		if argc >= 9:
			cluster_name = argv[0];
			if (argv[1] != "None"):
				tmp_cluster_name = cluster_name + "_" + argv[1];
			else:
				tmp_cluster_name = cluster_name;
			cluster_create_info = {}
			cluster_create_info["ID"] = 0;
			cluster_create_info["Name"] = tmp_cluster_name;
			cluster_create_info["Status"] = 1;
			cluster_create_info["Contactor"] = argv[2];
			cluster_create_info["Email"] = argv[2] + "@trip.com";
			cluster_create_info["CreateTime"] = None;
			cluster_create_info["UpdateTime"] = None;
			cluster_create_info["Remark"] = None;
			cluster_create_info["PoolID"] = 0;
			cluster_create_info["DBNumber"] = 0;
			cluster_create_info["UsingIDC"] = 1;
			
			cluster_create_info["SubsystemName"] = argv[3];
			cluster_create_info["SubsystemID"] = argv[4];
			cluster_create_info["PoolName"] = None;
			cluster_create_info["ProductID"] = int(argv[5]);
			cluster_create_info["ProductName"] = argv[6];
			cluster_create_info["MasterIDC"] = "";
			cluster_create_info["ClusterType"] = 4;
			cluster_create_info["FrozenStatus"] = 0;
			cluster_create_info["SwitchV3"] = 0;
			cluster_create_info["CreateStatus"] = 0;
			cluster_create_info["HashType"] = 0;
			cluster_create_info["Route"] = None;
			cluster_create_info["Importance"] = None;
			cluster_create_info["Creator"] = "admin";
			

			cluster_result = self.credis.create_cluster(cluster_create_info)
			if (cluster_result["Success"] == False) :
				print("create cluster fail %s "%(cluster_result))
				return
			cluster_id = cluster_result["Result"];
			# update clusterType (4)
			update_result = self.credis.update_cluster(cluster_create_info)
			if (cluster_result["Success"] == False) :
				print("update cluster fail %s "%(cluster_result))
				return
			idc = argv[8];
			for i in range(1, int(argv[7]) + 1):
				groupname = tmp_cluster_name + "_" + str(i);
				redis_info = self.xpipe.get_shard_redis_info(tmp_cluster_name,idc,groupname)
				if redis_info["redises"] == None:
					redis_info["redises"] = []
				group_info = {}
				group_info["ID"] = 0;
				group_info["PoolID"] = 0;
				group_info["Status"] = 0;
				group_info["Creator"] = "admin";
				group_info["CreateTime"] = None;
				group_info["UpdateTime"] = None;
				group_info["Remark"] = "";
				group_info["Name"] = groupname; 
				group_info["ClusterID"] = cluster_id;
				group_info["PoolName"] = None;
				group_info["Env"] = "";
				group_info["SubEnv"] = "";
				group_result = self.credis.cluster_add_group(group_info)
				if (group_result["Success"] == False) :
					print("group create fail! %s" %(group_info["Name"]));
					return
				group_id = group_result["Result"]
				docker_info = {}
				docker_info["type"] = argv[11];
				docker_info["clusterName"] = cluster_name;
				docker_info["orgId"] = argv[10];
				docker_info["groupId"] = group_id;
				docker_info["instanceType"] = "rediscrdt";
				docker_info["flavor"] = argv[9];
				docker_info["idc"] = argv[8];
				if docker_info["idc"] == "SIN-AWS" or docker_info["idc"] == "FRA-AWS":
					docker_info["arch"] = "arm64"
				docker_info["replicas"] = 2;
				docker_info["env"] = argv[12];
				docker_groupname = self.k8s.create_docker(docker_info);
				logging.info("docker groupname %s" % docker_groupname);
				try_num = 12 * 5;
				ginfo = {}
				ginfo["groupId"] = group_id;
				ginfo["groupName"] = docker_groupname;
				ginfo["env"] = docker_info["env"];
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
				# new_master.config_set("set", "maxmemory", master_maxmemory);
				redis_info['redises'].append({
					"redisPort": new_master_port,
					"master": True,
					"redisIp": new_master_host
				})
				self.credis.add_instance({
					"GroupID": group_id,
					"IPAddress": new_master_host,
					"Port": new_master_port,
					"Env": idc,
					"ParentID": 0,#0 master 1 slave
					"Status": 1,
					"CanRead": True
				})
				master_name_space = cluster_name + "_" + str(group_id);
				if master_name_space != None:
					new_master.config_set("crdt.set", "crdt-gid", master_name_space);
				for i in range(1, len(docker_info_result)):
					new_slave = redis_tool.RedisSession(docker_info_result[i]["server"], docker_info_result[i]["port"])
					# new_slave.config_set("set", "maxmemory", master_maxmemory);
					if master_name_space != None:
						new_slave.config_set("crdt.set", "crdt-gid", master_name_space);
					new_slave.slaveof(new_master_host, new_master_port)
					logging.info("new_slave[%s]: %s:%d slaveof %s:%d\n"%(docker_groupname, docker_info_result[i]["server"], docker_info_result[i]["port"], new_master_host, new_master_port))
					redis_info['redises'].append({
						"redisPort": int(docker_info_result[i]["port"]),
						"master": False,
						"redisIp": docker_info_result[i]["server"]
					})
					self.credis.add_instance({
						"GroupID": group_id,
						"IPAddress": docker_info_result[i]["server"],
						"Port": docker_info_result[i]["port"],
						"Env": idc,
						"ParentID": 1,
						"Status": 1,
						"CanRead": True
					})
				self.xpipe.update_shard_redis_info(tmp_cluster_name,idc,groupname, redis_info) 
				

		else:
			print("function [create_tmp_cluster] argv error!!!!!")
			return
		
	def cluster_is_use_command(self, argv):
		argc = len(argv)
		match_commands = ["zadd", "zincrby", "zrange", "zremrangebyscore","zrangebyscore","zrevrangebyscore"];
		if argc >= 1:
			info = self.credis.get_cluster_info(argv[0])
			if len(info["Groups"]) > 0:
				group = info["Groups"][0]
				instances = group["Instances"]
				for instance in instances:
					if instance["ParentID"] == 0: # is master
						master_redis = redis_tool.RedisSession(instance["IPAddress"], int(instance["Port"]))
						result = master_redis.info_commandstats();
						for command_stats in result:
							command = (command_stats[:8])
							for c in match_commands:
								if command == c:
									print("%s", argv[0]);
									break

			return                
		else:
			print("function [cluster_is_use_command] argv error!!!!!")
			return 
				
	def latte_create_same_machine_cluster(self, argv):
		# 0: cluster_name
		# 1: group_number
		# 2: idc
		# 3: ip
		# 4: start_port
		argc = len(argv)
		if argc >= 5:
			cluster_name = argv[0];
			cluster_create_info = {}
			cluster_create_info["ID"] = 0;
			cluster_create_info["Name"] = cluster_name;
			cluster_create_info["Status"] = 1;
			cluster_create_info["Contactor"] = "周国栋";
			cluster_create_info["Email"] = "gd.zhou@trip.com";
			cluster_create_info["CreateTime"] = None;
			cluster_create_info["UpdateTime"] = None;
			cluster_create_info["Remark"] = None;
			cluster_create_info["PoolID"] = 0;
			cluster_create_info["DBNumber"] = 0;
			cluster_create_info["UsingIDC"] = 1;
			
			cluster_create_info["SubsystemName"] = "03Service";
			cluster_create_info["SubsystemID"] = 189;
			cluster_create_info["PoolName"] = None;
			cluster_create_info["ProductID"] = 44;
			cluster_create_info["ProductName"] = "框架架构";
			cluster_create_info["MasterIDC"] = "";
			cluster_create_info["ClusterType"] = 0;
			cluster_create_info["FrozenStatus"] = 0;
			cluster_create_info["SwitchV3"] = 0;
			cluster_create_info["CreateStatus"] = 0;
			cluster_create_info["HashType"] = 0;
			cluster_create_info["Route"] = None;
			cluster_create_info["Importance"] = None;
			cluster_create_info["Creator"] = "admin";
			cluster_result = self.credis.create_cluster(cluster_create_info)
			if (cluster_result["Success"] == False) :
				print("create cluster fail %s "%(cluster_result))
				return
			cluster_id = cluster_result["Result"];
			idc = argv[2];
			for i in range(0, int(argv[1])):
				groupname = cluster_name + "_" + str(i + 1);
				group_info = {}
				group_info["ID"] = 0;
				group_info["PoolID"] = 0;
				group_info["Status"] = 0;
				group_info["Creator"] = "admin";
				group_info["CreateTime"] = None;
				group_info["UpdateTime"] = None;
				group_info["Remark"] = "";
				group_info["Name"] = groupname; 
				group_info["ClusterID"] = cluster_id;
				group_info["PoolName"] = None;
				group_info["Env"] = "";
				group_info["SubEnv"] = "";
				group_result = self.credis.cluster_add_group(group_info)
				if (group_result["Success"] == False) :
					print("group create fail! %s" %(group_info["Name"]));
					return
				group_id = group_result["Result"]
				self.credis.add_instance({
					"GroupID": group_id,
					"IPAddress": argv[3],
					"Port": int(argv[4]) + i,
					"Env": idc,
					"ParentID": 0,#0 master 1 slave
					"Status": 1,
					"CanRead": True
				})

		else:
			print("function [test_create_cluster] argv error!!!!!")
			return 
	def test(self, argv):
		for i in range(1, 3):
			print(i)
	def test_credis_add_redis(self, argv):
		info = self.credis.get_cluster_info(argv[0])
		groups = info["Groups"]
		for group in groups:
			groupId = group["ID"]
			self.credis.add_instance({
				"GroupID": groupId,
				"IPAddress": "127.1.1.1",
				"Port": 6380,
				"Env": "NTGXY",
				"ParentID": 0,
				"Status": 1,
				"CanRead": True
			})
			self.credis.add_instance({
				"GroupID": groupId,
				"IPAddress": "127.1.1.1",
				"Port": 6381,
				"Env": "NTGXY",
				"ParentID": 1,
				"Status": 1,
				"CanRead": True
			})
		
