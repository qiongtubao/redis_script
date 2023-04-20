#coding=utf-8
import json
import os
import sys
import threading
import time
from config import Config, Env
import logging
import time
import routes

from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler



def init_logging(level=logging.DEBUG):
    #创建一个logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Log等级总开关
    # 创建一个handler，用于写入日志文件
    rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
    log_path = os.getcwd() + '/Logs/'
    log_name = log_path + rq + '.log'
    logfile = log_name
    fh = logging.FileHandler(logfile, mode='w')
    fh.setLevel(level)  # 输出到file的log等级的开关
    
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

def help():
    print("python main.py {env} {command} {argv...}")
    print("     env: %s" % (Env.__members__.keys()))
    api = routes.Api("", {},"UAT")
    commands = [];
    for name in [name for name in dir(api) if not name.startswith('_')]:
        if str(type(getattr(api,name))) == "<type 'instancemethod'>":
            commands.append(name)
    print("     command:  %s" % commands)

if __name__ == '__main__':
    init_logging()
    logging.info("run command: %s" % sys.argv)

    if len(sys.argv) <= 1: 
        exit(0)
    if sys.argv[1] == "help":
        help()
        exit(0)
    elif Env.__members__.get(sys.argv[1]) == None:
        print("env params error " + sys.argv[1])
        help()
        exit(0)

    config = Config(Env.__members__.get(sys.argv[1]))
    api = routes.Api(config.get_credis_console_url(), config.get_credis_headers(), config.get_xpipe_url(), config.get_xpipe_headers(), config.get_k8s_env())
    eval('api.'+sys.argv[2])(sys.argv[3:])
    
    