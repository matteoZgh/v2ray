# -*- coding:utf-8 -*-

import base64
import json
import pickle
import requests
from config import conf_template as conf

path = "/etc/v2ray/data"


class Sub2Conf(object):
    def __init__(self, subs_url=None, conf_url=None):
        # 订阅原始数据
        self.origin = []
        
        self.subs_url = subs_url
        self.conf_url = conf_url

        # 解析后配置
        try:
            with open(path, "rb") as f:
                self.saved_conf = pickle.load(f)
        except:
            self.saved_conf = {
                "local": {},
                "subs": {}
            }
        
        '''
        self.conf结构
        {
            "地区"： "配置"
        }

        配置为解析得到的内容 + 协议
        '''
        self.conf = dict(self.saved_conf['local'], **self.saved_conf['subs'])


    def b642conf(self, prot, tp, b64str):
        if prot == "vmess":
            nodes = base64.b64decode(b64str + "==").decode()
            ret = json.loads(nodes)
            region = ret['ps']

        elif prot == "ss":
            string = b64str.split("#")
            cf = string[0].split("@")
            if len(cf) == 1:
                tmp = base64.b64decode(cf[0] + "==").decode()  # aes-256-cfb:541603466@142.93.50.78:9898
            else:
                tmp = base64.b64decode(cf[0] + "==").decode()+"@"+cf[1]
            ret = {
                "method": tmp.split(":")[0],
                "port": tmp.split(":")[2],
                "password": tmp.split(":")[1].split("@")[0],
                "add": tmp.split(":")[1].split("@")[1],
            }
            region = string[1]

        ret["prot"] = prot
        self.saved_conf[["local", "subs"][tp]][region] = ret


    def setconf(self, region):
        use_conf = self.conf[region]
        if use_conf['prot'] == "vmess":
            conf['outbounds'][0]["protocol"] = "vmess"
            conf['outbounds'][0]["settings"]["vnext"] = list()
            conf['outbounds'][0]["settings"]["vnext"].append({
                "address": use_conf["add"],
                "port": int(use_conf["port"]),
                "users": [
                  {
                    "id": use_conf["id"],
                    "alterId": use_conf["aid"]
                  }
                ] 
            })

            conf['outbounds'][0]["streamSettings"] = {
                "network": use_conf["net"],
                "wsSettings":{
                  "path": use_conf["path"],
                  "headers": {
                    "Host": use_conf['host']
                  }
                }
            }

        elif use_conf['prot'] == "ss":
            conf['outbounds'][0]["protocol"] = "shadowsocks"
            conf['outbounds'][0]["settings"]["servers"] = list()
            conf['outbounds'][0]["settings"]["servers"].append({
                "address": use_conf["add"],
                "port": int(use_conf["port"]),
                "password": use_conf["password"],
                "ota": False,
                "method": use_conf["method"]
            })
            conf['outbounds'][0]["streamSettings"] = {
                "network": "tcp"
            }

        
        with open("/etc/v2ray/config.json", "w") as f:
            f.write(json.dumps(conf, indent=4))

    
    def delconf(self, region):
        self.conf.pop(region)
        try:
            self.saved_conf['local'].pop(region)
        except:
            self.saved_conf['subs'].pop(region)

        with open(path, "wb") as jf:
            pickle.dump(self.saved_conf, jf)
    

    def update(self):
        """
        更新订阅
        """
        try:
            ret = requests.get(self.subs_url, headers={'user-agent': 'v2rayL/1.0'})
            if ret.status_code != 200:
                return 
            all_subs = base64.b64decode(ret.text + "==").decode().strip().split("\n")
        except Exception as e:
            raise "wrong"

        for sub in all_subs:
            self.origin.append(sub.split("://"))

        self.saved_conf["subs"] = {}

        for ori in self.origin:
            if ori[0] == "vmess":
                self.b642conf("vmess", 1, ori[1])
            elif ori[0] == "ss":
                self.b642conf("ss", 1, ori[1])

        self.conf = dict(self.saved_conf['local'], **self.saved_conf['subs'])

        with open(path, "wb") as jf:
            pickle.dump(self.saved_conf, jf)


    def add_conf_by_uri(self):
        """
        通过分享的连接添加配置
        """
        try:
            op = self.conf_url.split("://")
            if op[0] == "vmess":
                self.b642conf("vmess", 0, op[1])
            elif op[0] == "ss":
                self.b642conf("ss", 0, op[1])
        except:
            raise "wrong"

        self.conf = dict(self.saved_conf['local'], **self.saved_conf['subs'])

        with open(path, "wb") as jf:
            pickle.dump(self.saved_conf, jf)
