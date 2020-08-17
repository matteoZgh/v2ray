# -*- coding:utf-8 -*-

import sys
import subprocess
import pickle
from sub2conf import Sub2Conf
from time import sleep

path = "/etc/v2ray/current"


class V2rayL(object):
    def __init__(self):
        
        try:
            with open(path, "rb") as f:
                self.current, self.url = pickle.load(f)
        except:
            self.current = "未连接VPN"
            self.url = None

        self.subs = Sub2Conf(subs_url=self.url)


    def help(self):
        print("\r------------------------------------------")
        print("连接：con")
        print("断开：dcon")
        print("配置：cfg")
        print("订阅：sub")
        print("状态：sta")
        print("节点：node")
        print("帮助：help")
        print("\r------------------------------------------")

    
    def nodes(self):
        tmp = dict()
        num = 1
        for k, v in self.subs.conf.items():
            tmp[num] = k
            num +=1
        return tmp, num

    def print_nodes(self):
        print("{:^5}\t\t{:<20}".format("序号", "地区"))
        tmp = self.nodes()[0]
        for k, v in tmp.items():
            print("{:^5}\t\t{:<20}".format(k, v))

        
    def run(self, choice):
        if choice == "con":
            self.connect(sys.argv[2])
        elif choice == "dcon":
            self.disconnect()
        elif choice == "cfg":
            self.cgeconf(sys.argv[2])
        elif choice == "sub":
            self.subscribe(sys.argv[2])
        elif choice == "sta":
            self.status()
        elif choice == "node":
            self.print_nodes()
        elif choice == "help":
            self.help()
        else:
            print("argument error")


    def cgeconf(self, choice):
        if choice == "add":
            self.addconf(sys.argv[3])
        elif choice == "del":
            self.delconf(sys.argv[3])
        else:
            print("argument error")
    

    def subscribe(self, choice):
        self.update(choice)


    def status(self):
        print("\r------------------------------------------")
        print("当前状态: {}".format(self.current))
        print("订阅地址：{}".format(self.url if self.url else "无"))
        print("\r------------------------------------------")


    def connect(self, choice):
        t = self.subs.conf.items()
        if not t:
            print("无可连接的VPN，请输入订阅地址更新")
        else:
            tmp, num = self.nodes()
            if choice in [str(i) for i in range(num)]:
                self.subs.setconf(tmp[int(choice)])
                try:
                    print("\r正在连接")
                    output = subprocess.getoutput(["sudo systemctl status v2ray.service"])
                    if "Active: active" in output:
                        subprocess.call(["sudo systemctl restart v2ray.service"], shell=True)
                    else:
                        subprocess.call(["sudo systemctl start v2ray.service"], shell=True)
                except:
                    print("连接失败，请尝试更新订阅后再次连接")
                else:   
                    sleep(2)
                    print("成功连接到VPN：{}".format(tmp[int(choice)]))
                    self.current = tmp[int(choice)]
                    with open(path, "wb") as jf:
                        pickle.dump((self.current, self.url), jf)

            else:
                print("argument error")


    def disconnect(self):
        try:
            output = subprocess.getoutput(["sudo systemctl status v2ray.service"])
            if "Active: active" in output:
                print("\r正在断开连接")
                subprocess.call(["sudo systemctl stop v2ray.service"], shell=True)
                sleep(2)
                print("VPN连接已断开")
                self.current = "未连接至VPN"
                with open(path, "wb") as jf:
                        pickle.dump((self.current, self.url), jf)
                
            else:
                print("服务未开启，无需断开连接")
        except Exception as e:
            print(e)
            print("服务出错，请稍后再试")


    def update(self, url):
        print("\r正在更新订阅地址")
        self.subs = Sub2Conf(subs_url=url)
        self.subs.update()
        print("订阅地址更新完成，VPN已更新")
        with open(path, "wb") as jf:
            pickle.dump((self.current, url), jf)


    def addconf(self, url):
        print("\r正在添加配置")
        self.subs = Sub2Conf(conf_url=url)
        self.subs.add_conf_by_uri()
        print("配置添加成功，VPN已更新")

        
    def delconf(self, choice):
        t = self.subs.conf.items()
        if not t:
            print("当前无可连接VPN.")
        else:
            tmp, num = self.nodes()
            if choice in [str(i) for i in range(num)]:
                self.subs.delconf(tmp[int(choice)])
                print("成功删除配置：{}".format(tmp[int(choice)]))
            else:
                print("argument error")


if __name__ == '__main__':
    v = V2rayL()
    v.run(sys.argv[1])
