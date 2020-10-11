"""
封装cookie购物车字典数据的加解密(编解码)
"""
import pickle,base64

class CookieSecret(object):

    # 1、加密(编码)
    @staticmethod
    def dumps(data):
        """
        功能：把购物车字典数据 ----> pickle编码  ----> base64编码 --> 字符串
        :param data: 购物车字典数据 {1: {"count":5, "selected":True}}
        :return: 加密后的存入cookie的字符串数据
        """
        # 1、pickle编码
        data_bytes = pickle.dumps(data)
        # 2、base64编码
        base64_bytes = base64.b64encode(data_bytes) # 返回字节
        # 3、返回字符串
        return base64_bytes.decode()


    # 2、解密(解码)
    @staticmethod
    def loads(data):
        """
        功能：字符串 --> base64解码 --> pickle解码 --> 购物车字典
        :param data: 购物车cookie中的字节数据 b"gAN9cQBLAX1xAShYCAAAAHNlbGVjdGVkcQKIWAUAAABjb3VudHEDSwV1cy4="
        :return: 返回购物车字典
        """
        # 1、base64解码
        base64_bytes = base64.b64decode(data)
        # 2、pickle解码
        cart_dict = pickle.loads(base64_bytes)
        # 3、返回字典
        return cart_dict



if __name__ == '__main__':
    # 编写当前模块的测试案例
    cookie_cart = {
        1: {
            "count": 5,
            "selected": True
        },
        2: {
            "count": 15,
            "selected": False
        }
    }
    # 加密
    cart_str = CookieSecret.dumps(cookie_cart)
    print("cart_str: ", cart_str)
    # 解密
    cart_dict = CookieSecret.loads(cart_str.encode())
    print("cart_dict: ", cart_dict)
