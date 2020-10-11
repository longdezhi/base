"""
自定义Django的数据库读写路由
"""

class MasterSlaveDBRouter(object):

    def db_for_read(self, model, **hints):
        # 返回slave配置 --> 指向从mysql
        return 'slave'

    def db_for_write(self, model, **hints):
        # 返回default配置 --> 指向主mysql
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """是否运行关联操作"""
        return True