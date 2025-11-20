#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
questionary 高级自动补全功能演示
实现智能补全、模糊搜索和动态选项功能
"""

import questionary
from questionary import Choice
from typing import List, Dict, Any
import re


class AdvancedCompleter:
    """高级自动补全器"""
    
    def __init__(self):
        # 阿里云服务列表
        self.services = [
            "ECS - 弹性计算服务",
            "RDS - 关系型数据库",
            "OSS - 对象存储服务", 
            "VPC - 专有网络",
            "SLB - 负载均衡",
            "CDN - 内容分发网络",
            "Redis - 云数据库Redis版",
            "MongoDB - 云数据库MongoDB版",
            "ACK - 容器服务Kubernetes版",
            "FC - 函数计算",
            "MQ - 消息队列",
            "ES - Elasticsearch",
        ]
        
        # 区域列表
        self.regions = [
            "cn-hangzhou - 华东1(杭州)",
            "cn-shanghai - 华东2(上海)", 
            "cn-beijing - 华北2(北京)",
            "cn-shenzhen - 华南1(深圳)",
            "cn-qingdao - 华北1(青岛)",
            "cn-zhangjiakou - 华北3(张家口)",
            "cn-huhehaote - 华北5(呼和浩特)",
            "us-west-1 - 美国西部1(硅谷)",
            "us-east-1 - 美国东部1(弗吉尼亚)",
            "ap-southeast-1 - 亚太东南1(新加坡)",
        ]

    def fuzzy_search(self, query: str, options: List[str]) -> List[str]:
        """模糊搜索功能"""
        if not query:
            return options
            
        # 转换为小写进行匹配
        query_lower = query.lower()
        matches = []
        
        for option in options:
            option_lower = option.lower()
            # 检查是否包含查询字符串
            if query_lower in option_lower:
                matches.append(option)
            # 检查首字母匹配
            elif any(word.startswith(query_lower) for word in option_lower.split()):
                matches.append(option)
                
        return matches

    def create_dynamic_choices(self, options: List[str], query: str = "") -> List[Choice]:
        """创建动态选择项"""
        filtered_options = self.fuzzy_search(query, options)
        choices = []
        
        for option in filtered_options[:10]:  # 限制显示数量
            # 高亮匹配部分
            display_text = option
            if query and query.lower() in option.lower():
                # 简单高亮显示
                display_text = option.replace(
                    query, f"[{query}]"
                ).replace(
                    query.lower(), f"[{query.lower()}]"
                ).replace(
                    query.upper(), f"[{query.upper()}]"
                )
            
            choices.append(Choice(
                title=display_text,
                value=option
            ))
            
        return choices

    def service_selector(self) -> str:
        """服务选择器"""
        return questionary.autocomplete( "请选择阿里云服务:", choices=self.services,
            meta_information={
                service.split(" - ")[0]: service.split(" - ")[1] 
                for service in self.services
            }
        ).ask()

    def region_selector(self) -> str:
        """区域选择器"""
        return questionary.autocomplete(
            "请选择区域:",
            choices=self.regions,
            meta_information={
                region.split(" - ")[0]: region.split(" - ")[1]
                for region in self.regions
            }
        ).ask()

    def advanced_search_demo(self):
        """高级搜索演示"""
        print("🚀 questionary 高级自动补全演示")
        print("=" * 50)
        
        # 服务选择
        selected_service = self.service_selector()
        if selected_service:
            print(f"✅ 已选择服务: {selected_service}")
        
        # 区域选择  
        selected_region = self.region_selector()
        if selected_region:
            print(f"✅ 已选择区域: {selected_region}")
            
        # 多选演示
        selected_features = questionary.checkbox(
            "请选择需要的功能特性:",
            choices=[
                Choice("自动扩缩容", checked=True),
                Choice("监控告警"),
                Choice("备份恢复"),
                Choice("安全加固"),
                Choice("性能优化"),
                Choice("成本优化"),
            ]
        ).ask()
        
        if selected_features:
            print(f"✅ 已选择功能: {', '.join(selected_features)}")
            
        return {
            "service": selected_service,
            "region": selected_region, 
            "features": selected_features
        }


def main():
    """主函数"""
    completer = AdvancedCompleter()
    
    try:
        result = completer.advanced_search_demo()
        
        print("\n" + "=" * 50)
        print("📋 配置摘要:")
        print(f"服务: {result.get('service', '未选择')}")
        print(f"区域: {result.get('region', '未选择')}")
        print(f"功能: {', '.join(result.get('features', []))}")
        
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()