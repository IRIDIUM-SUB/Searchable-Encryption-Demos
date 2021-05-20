# README

## Description

一个基于模糊提取器和PEKSBoneh2004的公钥可搜索加密系统。

## Deploy

### Environment

Ubuntu+Python3

### Fuzzy Extractor

Ref:[fuzzy-extractor · PyPI](https://pypi.org/project/fuzzy-extractor/)

安装Openssl：

```bash
sudo apt-get install libssl-dev
```

安装:

```bash
pip install fuzzy-extractor
```

### Charm

Official Website: [Charm-Crypto Project](http://charm-crypto.io/)

Official GitHub: [JHUISI/charm: Charm: A Framework for Rapidly Prototyping Cryptosystems (github.com)](https://github.com/JHUISI/charm)

Clone到源代码所在的同级目录:

```bash
git clone https://github.com/JHUISI/charm.git
```

安装GMP库:

```bash
apt-get install  libgmp3-dev
sudo apt-get install m4
cd gmp-6.2.1
./configure #不要加prefix用g++！！！！
make
make check
sudo make install
```

安装PBC库:

参考[Linux环境下PBC库的安装_bubbleliar的博客-CSDN博客_pbc库安装](https://blog.csdn.net/bubbleliar/article/details/101548630)

```bash
cd /dir/to/pbc
./configure
make
make install

cd /etc/ld.so.conf.d
sudo vi libpbc.conf
>/usr/local/lib
sudo ldconfig
```

 安装charm

参考[charm-crypto安装_qq_34823530的博客-CSDN博客](https://blog.csdn.net/qq_34823530/article/details/96605662)

````bash
./configure.sh 
make 
sudo make install
````

## Run

```bash
python3 server.py
python3 local.py
```

## 原理

![image-20210520101835096](README.assets/image-20210520101835096.png)

## 操作

- 第一次运行先生成key,输入16个字母的指纹生成
- 之后运行选择恢复key,输入偏差不超过6的指纹
- 生成明文后加密上传,测试用每个文件5个词\*每个词5个字母
- 搜索关键词

## ISSUE

可搜索加密部分的生成密钥函数,Seed一定的情况下生成的安全参数并不相同...只能说原理是没问题的,如果要截图应付的话建议在同一次运行中完成全部流程

## Reference

[公钥可搜索加密及其python实现_因自私而无私-CSDN博客_公钥可搜索加密](https://blog.csdn.net/u014134327/article/details/103788783)

