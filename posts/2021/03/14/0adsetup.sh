#!/bin/bash
echo "Downloading the source code from gitlab"
git clone [https://gitlab.com/0ad/0ad.git
echo "处理依赖中"
sudo apt-get install build-essential cmake libboost-dev libboost-system-dev \
 libboost-filesystem-dev libcurl4-gnutls-dev libenet-dev libfmt-dev \
 libgloox-dev libicu-dev libminiupnpc-dev libnvtt-dev libogg-dev \
 libopenal-dev libpng-dev libsdl2-dev libsodium-dev libvorbis-dev \
 libxml2-dev python rustc subversion zlib1g-dev \
 wx3.0-headers libwxbase3.0-dev libwxgtk3.0-gtk3-dev \
 libwxbase3.0-0v5 libwxgtk3.0-gtk3-0v5

echo "Entering ttf mode"
sudo systemctl disable lightdm.service
echo "Now you are in ttf mode！"
cd 0ad
cd build/workspaces/
./update-workspaces.sh -j 
cd gcc
make -j
echo "Now exit ttf mode"
sudo systemctl enable lightdm.service
echo "#以下测试编译结果"
cd ../../..
binaries/system/test
echo "必要时请更改data/mods文件夹内内容，因为编译出的内容可能出现界面乱码复制win下同名文件夹替换即可。"
echo "run 'binaries/system/pyrogenesis' to enjoy your game!"