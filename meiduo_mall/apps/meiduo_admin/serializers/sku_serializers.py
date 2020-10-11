
from django.db import transaction
from rest_framework import serializers
from apps.goods.models import SKU,SKUSpecification,GoodsCategory,SPU,SPUSpecification,SpecificationOption
from celery_tasks.html.tasks import generate_static_sku_detail_html

class SpecOptSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = [
            'id',
            'value'
        ]

class SPUSpecModelSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    # 关联从表SpecficationOption多条数据
    options = SpecOptSimpleSerializer(many=True)

    class Meta:
        model = SPUSpecification
        fields = [
            'id',
            'name',
            'spu',
            'spu_id',
            'options'
        ]


class SPUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPU
        fields = [
            'id',
            'name'
        ]

class SKUCategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = [
            'id',
            'name'
        ]


class SKUSpecOptModelSerializer(serializers.ModelSerializer):
    # 因为这2个字段必须参与反序列化，所有我们只能手动映射覆盖原有的默认映射(默认只作用于序列化)
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        # 如果关联对象主键隐藏字段，我们在fields中显示声明，则会自动映射类型为ReadOnlyField —— 只读(只参与序列化)
        fields = [
            'spec_id',
            'option_id'
        ]

class SKUModelSerializer(serializers.ModelSerializer):
    # 三个隐藏字段：
    # 1、本表主键id，会自动映射
    # 2、外间关联对象的主键隐藏字段(如：spu_id), 不会自动映射
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()

    # 3、从表related_name指定的主表隐藏字段，不会自动映射
    # 表示当前SKU对象(主表)关联的"多个"SKUSpecification对象(从表)
    specs = SKUSpecOptModelSerializer(many=True)

    class Meta:
        model = SKU
        fields = "__all__"

    # 重写模型类序列化器的create方法的原因
    # 默认create方法，无法帮助我们插入中间表数据来记录新增sku商品的规格和选项信息
    def create(self, validated_data):
        #  [{spec_id: "4", option_id: 8}, {spec_id: "5", option_id: 11}]
        specs = validated_data.pop('specs')
        # 设计默认图片
        validated_data['default_image'] = 'group1/M00/00/02/CtM3BVrPB4GAWkTlAAGuN6wB9fU4220429'
        # TODO: 下面两步操作，是数据库两张表的插入动作，必须保证"事务"特性
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                # 1、新建sku模型类对象(主表)
                sku = SKU.objects.create(**validated_data)
                # 2、新建规格选项中间表数据，来记录新增sku的规格和选项信息
                for temp in specs:
                    # temp : {spec_id: "4", option_id: 8}
                    temp['sku_id'] = sku.id
                    SKUSpecification.objects.create(**temp)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('数据库新建失败！')

            transaction.savepoint_commit(save_id)

        # TODO: 使用异步任务方式，静态化生成当前新建sku商品的详情页
        generate_static_sku_detail_html.delay(sku.id)

        return sku

    # 默认update方法，无法完成中间表数据的更新
    def update(self, instance, validated_data):
        # [{spec_id: "1", option_id: 1}, {spec_id: "2", option_id: 4}, {spec_id: "3", option_id: 6}]
        specs = validated_data.pop('specs')

        # TODO: 两张表动作必须保证事务特性

        # 0、更新主表数据
        sku = super().update(instance, validated_data)
        # 1、删除原有中间表数据
        SKUSpecification.objects.filter(
            sku_id=sku.id
        ).delete()
        # 2、插入新的规格和选项中间表数据
        for temp in specs:
            # temp: {spec_id: "1", option_id: 1}
            temp['sku_id'] = sku.id
            SKUSpecification.objects.create(**temp)

        # TODO: 重新静态化生成新的详情页

        return sku




