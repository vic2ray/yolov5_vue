FROM python:3.8.5
# 更新，安装nginx
RUN apt update && apt install -y nginx && apt install libgl1-mesa-glx -y && apt install vim -y
RUN pip install --upgrade pip
# 设置目录
WORKDIR /train
# 复制文件
ADD . /train
RUN chmod +x startup.sh
# 安装依赖
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple
# 启动
EXPOSE 80
CMD ["./startup.sh"]