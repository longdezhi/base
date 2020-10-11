 # 基础镜像
FROM ubuntu:18.04

# 制定作者
MAINTAINER longdezhi

# 安装nginx
# RUN apt-get install nginx -y

# RUN apt-get install python3-pip -y

COPY 8000.conf /etc/nginx/conf.d/
COPY 8080.conf /etc/nginx/conf.d/
COPY 8081.conf /etc/nginx/conf.d/


ADD front_end_pc.tar.gz /data/
ADD meiduo_mall.tar.gz /data/
ADD meiduo_mall_admin.tar.gz /data/

# WORKDIR /data/meiduo_mall/
# RUN pip3 install -r requirements.txt

EXPOSE 8000 8080 8081

COPY command.sh /data/
WORKDIR /data/
ENTRYPOINT ["/bin/bash","command.sh"]
