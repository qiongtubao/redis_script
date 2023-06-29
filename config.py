
# coding=utf-8
from enum import Enum

class Env(Enum):
    uat = 1
    pro = 2

class Config(object):
    def __init__(self, env):
        self.env = env 
    def get_credis_console_url(self):
        if self.env == Env.pro:
            return "http://credis.arch.ctripcorp.com"
        else:
            return "http://credis.arch.uat.qa.nt.ctripcorp.com" 

    def get_credis_headers(self):
        return {
            'Cookie': '_RGUID=5e928a78-5ed6-4366-adeb-94e0d1f57c32; _RSG=cDarUXdYIw5omNzH3EbhtA; _RDG=2831d23fadaa1329433d977457c812b215; _ga=GA1.2.822149363.1610712338; nfes_isSupportWebP=1; principal=38022ad20b093c42a324fe12a26cc542-6e9c0d0d-9b8f-4123-b6cb-459156ba7f6d; _gid=GA1.2.1887155528.1618193245; Union=OUID=&AllianceID=66672&SID=1693366&SourceID=&AppID=&OpenID=&exmktID=&createtime=1618468221&Expires=1619073021082; _bfa=1.1610680322996.40fkyv.1.1618393133974.1618468221420.204.531.0; _RF1=114.80.11.230; JSESSIONID=778EE5A7EBAFAD91A1DA060650365E21'
        }
    def get_xpipe_url(self):
        if self.env == Env.pro:
            return "http://xpipe.ctripcorp.com"
        else:
            return "http://xpipe.fx.uat.tripqate.com"
    def get_xpipe_headers(self):
        result = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'http://xpipe.fx.uat.tripqate.com/',
            'Referer': 'http://xpipe.fx.uat.tripqate.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json;charset=UTF-8'
        }
        if self.env == Env.pro:
            result['Cookie'] = "_ga=GA1.2.479410682.1603190665; _RSG=wYa_E9NJCF0wh9EOJY1hfB; _RDG=286c8cf8a7ba3b229f2a17e693c1df54dd; _RGUID=03cc4d72-4efe-48ba-ba6b-0624d8389afa; nfes_isSupportWebP=1; _bfaStatusPVSend=1; _bfa=1.1603187049696.49ag06.1.1639135325751.1639139649859.827.1995.10650046130; _RF1=117.131.104.30; _bfaStatus=success; PRO_cas_principal=PRO-67642e7a686f75-MTY0ODU1NDgzMTUzNA-c371a98b2a644c958f4c69ffc2190c1d; PRO_principal=c97f9e69d4a3b65ff032d82959ee3cee-21c0779b-460f-4502-ac57-9cd089e712b4; offlineTicket=_D1C12CED08662CF525F2B46E4E763791D95BFA2C7578253C7414F1971EB1E9B0; PRO_CCST_SECRET_ADFC=PRO-67642e7a686f75-20afd02be46b4c7887c0a7262c1cbe69"
        else:
            result['Cookie'] = "Servers_Eid=S79608; UAT_cas_principal=UAT-67642e7a686f75-MTY4NjY0MzI1MDE1Mw-45a8836b9202458284bb2b85fb05b08d; FAT_cas_principal=FAT-67642e7a686f75-MTY4NjY0MzExMzIxMg-e64458eea2f54184a0447a6e96ccef04";
        return result
    def get_k8s_env(self):
        if self.env == Env.pro:
            return "PROD";
        else:
            return "UAT"