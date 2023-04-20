
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
    def get_k8s_env(self):
        if self.env == Env.pro:
            return "PROD";
        else:
            return "UAT"