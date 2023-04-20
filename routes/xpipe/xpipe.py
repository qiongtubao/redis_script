import logging
import requests

class Xpipe(object):
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
    def get_clusters(self, type=None):
        res = requests.get(self.url + '/console/clusters/all', headers=self.headers)
        res.encoding = 'utf-8';
        logging.info("[get_clusters] allcluster result: %s" %  res.json())
        clusters = res.json()
        result = []
        for cluster in clusters:
            if type != None:
                if cluster['clusterType'].lower() == type.lower() :
                    result.append(cluster['clusterName'])
            else:
                result.append(cluster['clusterName'])
        return result
            