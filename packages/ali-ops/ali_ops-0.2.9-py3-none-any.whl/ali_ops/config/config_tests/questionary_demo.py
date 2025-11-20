#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
questionary 库全面演示
展示所有问答组件，重点演示自动补全功能
"""

import questionary
from questionary import Style


def demo_autocomplete():
    """演示自动补全功能"""
    print("\n=== 自动补全演示 ===")
    
    # 基础自动补全
    regions = [
        "cn-hangzhou", "cn-shanghai", "cn-qingdao", "cn-beijing",
        "cn-zhangjiakou", "cn-huhehaote", "cn-shenzhen", "cn-guangzhou",
        "us-west-1", "us-east-1", "ap-southeast-1", "eu-central-1"
    ]
    
    region = questionary.autocomplete(
        "选择阿里云地域:",
        choices=regions,
        meta_information={
            "cn-hangzhou": "华东1（杭州）",
            "cn-shanghai": "华东2（上海）",
            "cn-beijing": "华北2（北京）",
            "us-west-1": "美国西部1（硅谷）"
        }
    ).ask()
    
    print(f"选择的地域: {region}")
    
    # 高级自动补全 - 支持模糊匹配
    services = [
        "ECS - 云服务器",
        "RDS - 云数据库",
        "OSS - 对象存储",
        "VPC - 专有网络",
        "SLB - 负载均衡",
        "CDN - 内容分发网络",
        "Redis - 云数据库Redis版"
    ]
    
    service = questionary.autocomplete(
        "选择阿里云服务:",
        choices=services,
        match_middle=True,  # 支持中间匹配
        ignore_case=True    # 忽略大小写
    ).ask()
    
    print(f"选择的服务: {service}")


def demo_select():
    """演示选择组件"""
    print("\n=== 选择组件演示 ===")
    
    # 单选
    instance_type = questionary.select(
        "选择实例规格:",
        choices=[
            "ecs.t5-lc1m1.small",
            "ecs.t5-lc1m2.small", 
            "ecs.t5-lc1m4.large",
            "ecs.c5.large",
            "ecs.g5.large"
        ]
    ).ask()
    
    print(f"选择的实例规格: {instance_type}")
    
    # 多选
    features = questionary.checkbox(
        "选择需要的功能:",
        choices=[
            questionary.Choice("自动备份", checked=True),
            questionary.Choice("监控告警"),
            questionary.Choice("弹性伸缩"),
            questionary.Choice("负载均衡"),
            questionary.Choice("CDN加速")
        ]
    ).ask()
    
    print(f"选择的功能: {features}")


def demo_input():
    """演示输入组件"""
    print("\n=== 输入组件演示 ===")
    
    # 文本输入
    project_name = questionary.text(
        "项目名称:",
        default="ali-ops-demo"
    ).ask()
    
    # 密码输入
    password = questionary.password("输入密码:").ask()
    
    # 数字输入
    instance_count = questionary.text(
        "实例数量:",
        validate=lambda x: x.isdigit() and int(x) > 0,
        default="1"
    ).ask()
    
    print(f"项目名称: {project_name}")
    print(f"密码长度: {len(password) if password else 0}")
    print(f"实例数量: {instance_count}")


def demo_confirm():
    """演示确认组件"""
    print("\n=== 确认组件演示 ===")
    
    # 简单确认
    confirm_create = questionary.confirm(
        "确认创建资源?",
        default=True
    ).ask()
    
    print(f"确认创建: {confirm_create}")
    
    if confirm_create:
        # 危险操作确认
        confirm_delete = questionary.confirm(
            "⚠️  这是危险操作，确认删除所有数据?",
            default=False
        ).ask()
        
        print(f"确认删除: {confirm_delete}")


def demo_path():
    """演示路径选择"""
    print("\n=== 路径选择演示 ===")
    
    # 文件路径
    config_path = questionary.path(
        "选择配置文件路径:",
        default="./config.json"
    ).ask()
    
    print(f"配置文件路径: {config_path}")


def demo_rawselect():
    """演示原始选择（数字键选择）"""
    print("\n=== 原始选择演示 ===")
    
    action = questionary.rawselect(
        "选择操作:",
        choices=[
            "创建实例",
            "删除实例", 
            "重启实例",
            "查看状态"
        ]
    ).ask()
    
    print(f"选择的操作: {action}")


def demo_custom_style():
    """演示自定义样式"""
    print("\n=== 自定义样式演示 ===")
    
    custom_style = Style([
        ('qmark', 'fg:#ff0066 bold'),       # 问号
        ('question', 'bold'),                # 问题文本
        ('answer', 'fg:#44ff00 bold'),       # 答案
        ('pointer', 'fg:#ff0066 bold'),      # 指针
        ('highlighted', 'fg:#ff0066 bold'),  # 高亮
        ('selected', 'fg:#cc5454'),          # 选中
        ('separator', 'fg:#cc5454'),         # 分隔符
        ('instruction', ''),                 # 指令
        ('text', ''),                        # 文本
        ('disabled', 'fg:#858585 italic')    # 禁用
    ])
    
    styled_choice = questionary.select(
        "选择主题颜色:",
        choices=["蓝色", "绿色", "红色", "紫色"],
        style=custom_style
    ).ask()
    
    print(f"选择的主题: {styled_choice}")


def demo_advanced_autocomplete():
    """演示高级自动补全功能"""
    print("\n=== 高级自动补全演示 ===")
    
    # autocomplete 只支持字符串列表，不支持 Choice 对象
    # 使用简单的字符串列表进行自动补全
    regions = [
        "华东1（杭州） - cn-hangzhou",
        "华东2（上海） - cn-shanghai", 
        "华北2（北京） - cn-beijing",
        "华南1（深圳） - cn-shenzhen",
        "美国西部1 - us-west-1",
        "美国东部1 - us-east-1",
        "新加坡 - ap-southeast-1"
    ]
    
    region = questionary.autocomplete(
        "选择部署地域:",
        choices=regions,
        match_middle=True,
        ignore_case=True
    ).ask()
    
    print(f"选择的地域: {region}")
    
    # 演示另一种高级自动补全 - 实例规格
    instance_specs = [
        "ecs.t5-lc1m1.small - 1核1GB",
        "ecs.t5-lc1m2.small - 1核2GB",
        "ecs.t5-lc1m4.large - 1核4GB", 
        "ecs.c5.large - 2核4GB",
        "ecs.c5.xlarge - 4核8GB",
        "ecs.g5.large - 2核8GB",
        "ecs.g5.xlarge - 4核16GB",
        "ecs.r5.large - 2核16GB"
    ]
    
    spec = questionary.autocomplete(
        "选择实例规格 (支持模糊搜索):",
        choices=instance_specs,
        match_middle=True,
        ignore_case=True
    ).ask()
    
    print(f"选择的规格: {spec}")


def demo_grouped_select():
    """演示分组选择（select 支持分组，autocomplete 不支持）"""
    print("\n=== 分组选择演示 ===")
    
    # 使用 select 实现分组选择
    choices = [
        questionary.Separator("=== 国内地域 ==="),
        questionary.Choice("华东1（杭州）", value="cn-hangzhou"),
        questionary.Choice("华东2（上海）", value="cn-shanghai"),
        questionary.Choice("华北2（北京）", value="cn-beijing"),
        questionary.Choice("华南1（深圳）", value="cn-shenzhen"),
        questionary.Separator("=== 海外地域 ==="),
        questionary.Choice("美国西部1", value="us-west-1"),
        questionary.Choice("美国东部1", value="us-east-1"),
        questionary.Choice("新加坡", value="ap-southeast-1")
    ]
    
    region = questionary.select(
        "选择部署地域 (分组显示):",
        choices=choices
    ).ask()
    
    print(f"选择的地域值: {region}")


def main():
    """主函数 - 运行所有演示"""
    print("🚀 questionary 库全面功能演示")
    print("=" * 50)
    
    try:
        # 运行各个演示
        demo_autocomplete()
        demo_select() 
        demo_input()
        demo_confirm()
        demo_path()
        demo_rawselect()
        demo_custom_style()
        demo_advanced_autocomplete()
        demo_grouped_select()
        
        print("\n✅ 所有演示完成!")
        
    except KeyboardInterrupt:
        print("\n\n❌ 用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    main()