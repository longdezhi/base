
# 如果使用 redis 作为中间人 —— 任务队列(消息队列) -- 作用：暂存任务的地方！
# 需要这样配置:
broker_url='redis://192.168.203.153:6379/3'



# 如果使用别的作为中间人, 例如使用 rabbitmq
# 则 rabbitmq 配置如下:
# broker_url= 'amqp://用户名:密码@ip地址:5672'

# 例如:
# meihao: 在rabbitq中创建的用户名, 注意: 远端链接时不能使用guest账户.
# 123456: 在rabbitq中用户名对应的密码
# ip部分: 指的是当前rabbitq所在的电脑ip
# 5672: 是规定的端口号
# broker_url = 'amqp://meihao:123456@172.16.238.128:5672'