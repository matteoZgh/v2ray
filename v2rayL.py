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
                self.current, self.url, self.auto = pickle.load(f)
        except:
            self.current = "未连接VPN"
            self.url = None
            self.auto = False

        self.subs = Sub2Conf(subs_url=self.url)

        if self.auto:
            try:
                self.subs.update()
            except:
                print("自动更新失败:地址错误或不存在，请更换订阅地址。")
                self.update()

        print("\r------------------------------------------")
        print("当前状态:{}".format(self.current))
        print("自动更新:{}".format("开启" if self.auto else "关闭"))
        print("订阅地址:{}".format(self.url if self.url else "无"))
        print("\r------------------------------------------")

        
    def run(self):
        print("1. 连接VPN 2. 断开VPN 3. 配置\n4. 订阅 5. 查看当前状态 0. 退出")
        choice = input("请输入 >> ")

        if choice == "1":
            self.connect()
        elif choice == "2":
            self.disconnect()
        elif choice == "3":
            self.cgeconf()
        elif choice == "4":
            self.subscribe()
        elif choice == "5":
            self.status()

        elif choice == "0":
            exit()
        else:
            print("请输入正确的选项...........")
            self.run()


    def cgeconf(self):
        print("\r------------------------------------------")
        print("1. 添加配置 2. 删除配置 0. 返回主菜单")
        choice = input("请输入 >> ")
        if choice == "1":
            self.addconf()

        elif choice == "2":
            self.delconf()

        elif choice == "0":
            self.run()

        else:
            print("请输入正确的选项...........")
            self.run()
    

    def subscribe(self):
        print("\r------------------------------------------")
        print("1. 开启自动更新订阅 2. 关闭自动更新订阅\n3. 修改订阅地址 0. 返回主菜单")
        choice = input("请输入 >> ")
        if choice == "1":
            with open(path, "wb") as jf:
                self.auto = True
                pickle.dump((self.current, self.url, self.auto), jf)
            print("已开启自动更新订阅，下次进入生效")
            print("\r------------------------------------------")
            self.run()

        elif choice == "2":
            with open(path, "wb") as jf:
                self.auto = False
                pickle.dump((self.current, self.url, self.auto), jf)
            print("已关闭自动更新订阅，下次进入生效")
            print("\r------------------------------------------")
            self.run()

        elif choice == "3":
            self.update()

        elif choice == "0":
            self.run()
        else:
            print("请输入正确的选项...........")
            self.run()

    def status(self):
        print("\r------------------------------------------")
        print("当前状态: {}".format(self.current))
        print("自动更新: {}".format("开启" if self.auto else "关闭"))
        print("订阅地址：{}".format(self.url if self.url else "无"))
        print("\r------------------------------------------")
        self.run()


    def connect(self):
        print("\r------------------------------------------")
        t = self.subs.conf.items()
        if not t:
            print("无可连接的VPN，请输入订阅地址更新")
            print("\r------------------------------------------")
            self.run()
        else:
            print("{:^5}\t\t{:<10}\t{:<20}".format("序号", "协议","地区"))
            tmp = dict()
            num = 1
            for k, v in self.subs.conf.items():
                print("{:^5}\t\t{:<10}\t{:<20}".format(num, v["prot"], k))
                tmp[num] = k
                num +=1

            print("{:^5}\t\t{:<10}".format(0, "返回主菜单"))
            choice = input("请输入 >> ")

            if choice == "0":
                self.run()
            elif choice in [str(i) for i in range(num)]:
                self.subs.setconf(tmp[int(choice)])
                try:
                    print("\r正在连接................")
                    output = subprocess.getoutput(["sudo systemctl status v2ray.service"])
                    if "Active: active" in output:
                        subprocess.call(["sudo systemctl restart v2ray.service"], shell=True)
                    else:
                        subprocess.call(["sudo systemctl start v2ray.service"], shell=True)
                except:
                    print("连接失败，请尝试更新订阅后再次连接......")
                    self.run()
                else:   
                    sleep(2)
                    print("成功连接到VPN：{}".format(tmp[int(choice)]))
                    print("\r------------------------------------------")
                    self.current = tmp[int(choice)]
                    with open("./current", "wb") as jf:
                        pickle.dump((self.current, self.url, self.auto), jf)

            else:
                print("\r------------------------------------------")
                print("请输入正确的选项...........")
                self.connect()


    def disconnect(self):
        try:
            output = subprocess.getoutput(["sudo systemctl status v2ray.service"])
            if "Active: active" in output:
                print("\r正在断开连接...............................")
                subprocess.call(["sudo systemctl stop v2ray.service"], shell=True)
                sleep(2)
                print("VPN连接已断开...............................")
                print("\r------------------------------------------")
                self.current = "未连接至VPN"
                with open(path, "wb") as jf:
                        pickle.dump((self.current, self.url, self.auto), jf)
                
            else:
                print("\r------------------------------------------")
                print("服务未开启，无需断开连接................")
                print("\r------------------------------------------")
                self.run()
        except Exception as e:
            print("\r------------------------------------------")
            print(e)
            print("服务出错，请稍后再试.................")
            print("\r------------------------------------------")


    def update(self):
        print("\r------------------------------------------")
        url = input("输入 0 返回主菜单\n请输入地址>> ")
        if url == "0":
            self.run()
        else:
            print("\r正在更新订阅地址............................")
            self.subs = Sub2Conf(subs_url=url)
            self.subs.update()
            print("订阅地址更新完成，VPN已更新.....")
            print("\r------------------------------------------")
            with open(path, "wb") as jf:
                pickle.dump((self.current, url, self.auto), jf)
            self.run()


    def addconf(self):
        print("\r------------------------------------------")
        url = input("请输入配置信息链接, 0返回主菜单\n(目前支持 vmess://和ss://)>>> ")
        if url == "0":
            self.run()
        else:
            print("\r正在添加配置...................")
            self.subs = Sub2Conf(conf_url=url)
            self.subs.add_conf_by_uri()
            print("配置添加成功，VPN已更新.....")
            self.run()

    
    def delconf(self):
        print("\r------------------------------------------")
        t = self.subs.conf.items()
        if not t:
            print("当前无可连接VPN.")
            print("\r------------------------------------------")
            self.run()
        else:
            print("{:^5}\t\t{:<10}\t{:<20}".format("序号", "协议","地区"))
            tmp = dict()
            num = 1
            for k, v in self.subs.conf.items():
                print("{:^5}\t\t{:<10}\t{:<20}".format(num, v["prot"], k))
                tmp[num] = k
                num +=1

            print("{:^5}\t\t{:<10}".format(0, "返回主菜单"))
            choice = input("请输入需要删除的序号 >> ")

            if choice == "0":
                self.run()

            elif choice in [str(i) for i in range(num)]:
                self.subs.delconf(tmp[int(choice)])
                print("成功删除配置：{}".format(tmp[int(choice)]))
                print("\r------------------------------------------")
                self.run()

            else:
                print("\r------------------------------------------")
                print("请输入正确的选项...........")
                self.delconf()


if __name__ == '__main__':
    v = V2rayL()
    v.run()
