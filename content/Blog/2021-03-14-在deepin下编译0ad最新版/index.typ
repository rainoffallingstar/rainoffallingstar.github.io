#import "../index.typ": template, tufted
#show: template.with(title: "在Deepin下编译0.A.D最新版").with(lang: "en")

== 在Deepin下编译0.A.D最新版

获取.sh文件 #link("0adsetup.sh")[0adsetup.sh 下载]

+ 获取源代码：git clone #link("https://gitlab.com/0ad/0ad.git")[https://gitlab.com/0ad/0ad.git   或在官网下载其源码包]

+ 安装依赖：
   
   ```bash
   sudo apt-get install build-essential cmake libboost-dev libboost-system-dev \
    libboost-filesystem-dev libcurl4-gnutls-dev libenet-dev libfmt-dev \
    libgloox-dev libicu-dev libminiupnpc-dev libnvtt-dev libogg-dev \
    libopenal-dev libpng-dev libsdl2-dev libsodium-dev libvorbis-dev \
    libxml2-dev python rustc subversion zlib1g-dev
   
   sudo apt install wx3.0-headers libwxbase3.0-dev libwxgtk3.0-gtk3-dev libwxbase3.0-0v5 libwxgtk3.0-gtk3-0v5
   ```

+ 编译：4G内存的建议在开机后ctrl+alt+f2进入tty模式下编译，4G以上内存的，当我没说～
   
   ```bash
   print("Entering ttf mode")
   sudo systemctl disable lightdm.service
   print("Now you are in ttf mode！")
   cd 0ad
   cd build/workspaces/
   ./update-workspaces.sh -j 
   cd gcc
   make -j
   print("#以下测试编译结果")
   cd ../../..
   binaries/system/test
   print("必要时请更改data/mods文件夹内内容，因为编译出的内容可能出现界面乱码复制win下同名文件夹替换即可。")
   print("run 'binaries/system/pyrogenesis' to enjoy your game!") 
   ```

+ 运行：binaries/system/pyrogenesis，将该文件发送到桌面快捷方式即可在桌面打开了
