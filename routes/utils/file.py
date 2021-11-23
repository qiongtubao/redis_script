import json
import io

from routes.utils import endcoder
class File(object):
    def __init__(self, path):
        self.path = path 
    def write_json(self, data, mode='w+', encoding = 'utf-8'):
        return self.write_str(json.dumps(data), mode, encoding)
    def write_str(self, data, mode='w+', encoding='utf-8'):
        try:
            fp = io.open(self.path, mode, encoding=encoding);
            fp.write(data.decode(encoding))
            fp.close()
            return True;
        except Exception as e:
            print("write file error: %s" % e)
            return False;
    def read_str(self, mode='r',encoding='utf-8'):
        try:
            fp = io.open(self.path, mode, encoding=encoding);
            str = fp.read()
            fp.close()
            return str
        except Exception as e:
            print("read file error: %s" % e)
            exit(0)