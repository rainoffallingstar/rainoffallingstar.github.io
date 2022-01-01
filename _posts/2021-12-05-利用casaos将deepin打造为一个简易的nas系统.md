---
layout: mypost
title: 利用casaos将deepin打造为一个简易的nas系统
categories: [教程]
---

## 利用casaos将deepin打造为一个简易的nas系统

### Casaos不是一个操作系统

它是一个基于docker的家庭云管理系统，简单地说就是用于docker可视化的。

> CasaOS is an open-source Home Cloud system based on the Docker ecosystem and designed for home scenarios. It is committed to building the world's most simple, easy-to-use, and elegant Home Cloud system.[github地址](https://github.com/IceWhaleTech/CasaOS)

### 测试出来的优缺点

#### 优点

1. 可视化管理，安装，启动，关闭docker容器，设置参数等，步骤简单，倾向于管理local。自带部分docker image是一键安装的。

2. 提供终端登录，命令行控制宿主机。

3. 在其中安装的docker应用提供统一的存储路径和映射。

#### 缺点：

1. 默认安装在系统盘，包括应用的用户data也会在系统盘，如果deepin全盘安装系统盘参数小的可能吃不消。

![截图_选择区域_20211205182745.png](01.png)

### 如何安装获得

1. 安装docker，参考[深度wiki](https://wiki.deepin.org/wiki/Docker)
2. 终端运行
   
   ```
   wget -qO- https://get.icewhale.io/casaos.sh | bash
   ```

> Notice：此脚本中安装包是在github中下载，建议根据[链接](https://get.icewhale.io/casaos.sh)下载casaos.sh后修改其第343行处链接为github镜像链接加速。我手动修改过的脚本[下载](https://gitee.com/rainoffallingstar/rapid-configs-for-my-manjaro/blob/master/casaos.sh)

3. 安装中可能会提示依赖问题（20.3中未提示有依赖问题），安装成功后即可在终端得到地址链接。一般为本机hostip号。

4. 在浏览器中访问上述地址，即可进入casaos，此时可根据需要安装与配置docker应用
   
   ![截图_选择区域_20211205182818.png](02.png)

> 默认支持一键安装应用如上图，不需手动配置，记住默认帐号密码即可。

![截图_选择区域_20211205182858.png](03.png)

> 手动安装配置页面如上，填写dockerimage的名称如###/&&&即可自动生成链接，填写webui处的端口以便于在casaos界面内跳转。其他各参数可参考网络上各配置命令行设置。
