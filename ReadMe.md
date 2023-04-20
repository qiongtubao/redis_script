### 功能
#### 删除集群功能
##### 删除本机房缓存
1. 关闭credis监控 (python main.py uat close_credis_monitor test_localcache_swap_crdt 100)
2. 删除所有redis实例上的哨兵 (python main.py uat remove_redis_sentinel 10.22.175.103 6379)
3. 删除credis中的实例  (del_instance)
4. 释放docker  (http://conf.ctripcorp.com/pages/viewpage.action?pageId=356198263)
5. 删除集群  (del_cluster)