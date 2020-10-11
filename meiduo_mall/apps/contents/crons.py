
from django.template import loader
from apps.goods.models import GoodsCategory,GoodsChannel,GoodsChannelGroup
from apps.contents.models import Content,ContentCategory
import os
from django.conf import settings

def generate_static_index_html():
    """
    功能：渲染完整的首页文件index.html
    :return:
    """
    # ============1、构建模版参数categories=========
    categories = {} # # 商品分类频道

    # 按照组id排序，再按照sequence排序
    channels = GoodsChannel.objects.order_by(
        'group_id',
        'sequence'
    )

    # 遍历每一个频道。把频道插入以"组id"为键的键值对中
    for channel in channels:
        # 当前组不存在的时候(第一次构建)
        if channel.group_id not in categories:
            # categories[1] = {}
            categories[channel.group_id] = {
                'channels': [], # 一级分类信息
                'sub_cats': [] # 二级分类
            }
        # 一级分类
        cat1 = channel.category
        categories[channel.group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })

        # 二级分类
        cat2s = cat1.subs.all()
        for cat2 in cat2s:
            # cat2：每一个二级分类对象

            # 当前二级分类关联的三级分类
            cat3s_list = []
            cat3s = cat2.subs.all()
            for cat3 in cat3s:
                # cat3：当前二级分类关联的每一个三级分类对象
                cat3s_list.append({
                    'id': cat3.id,
                    'name': cat3.name
                })

            categories[channel.group_id]['sub_cats'].append({
                'id': cat2.id,
                'name': cat2.name,
                'sub_cats': cat3s_list # 三级分类
            })


    # ============2、模版参数contents=========
    contents = {}
    # 所有广告分类
    content_cats = ContentCategory.objects.all()
    for content_cat in content_cats:
        # content_cat: 每一个分类如：轮播图
        # 当前广告分类关联的所有广告加入列表中
        # contents['index_lbt'] = [<美图M8s>, <黑色星期五>...]
        contents[content_cat.key] = Content.objects.filter(
            category=content_cat,
            status=True # 正在展示的广告
        ).order_by('sequence')

    # ============3、模版渲染=========
    # 首页模版文件
    template = loader.get_template('index.html')

    # 模版参数(动态数据)
    context = {
        'categories': categories, # 填充商品分类频道
        'contents': contents # 填充广告数据
    }

    # 渲染完整的页面数据
    page = template.render(context)

    file_path = os.path.join(
        settings.STATIC_FILE_PATH,
        'index.html'
    )
    # 把完整的页面数据，写入静态html文件中
    with open(file_path, 'w') as f:
        f.write(page)



def static_demo():
    """
    案例函数，讲解django页面渲染接口
    :return:
    """
    # 1、get_template函数用来获取一个模版
    template = loader.get_template('demo.html') # 返回值为一个模版对象

    # 2、通过模版对象里面的render函数实现模版渲染
    # django模版参数可以传递"python"基础类型：int,str,[]..., 也可以传递django的模型类对象
    context = {
        'name': 'weiwei',
        'age': 18,
        'favors': ['足球', '篮球', '羽毛球'],
        'sku_image': SKUImage.objects.get(pk=4)
    }
    page = template.render(context)

    with open('demo.html', 'w') as f:
        f.write(page)
