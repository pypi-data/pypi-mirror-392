#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级模糊补全示例
演示 prompt_toolkit 的强大自动补全功能，包括：
- 模糊匹配
- 多级补全
- 动态补全
- 自定义补全器
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter, WordCompleter
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.formatted_text import HTML
from typing import Iterable, List, Dict, Any
import re


class AliCloudResourceCompleter(Completer):
    """阿里云资源自定义补全器"""
    
    def __init__(self):
        # 模拟阿里云资源数据
        self.resources = {
            'ecs': {
                'instances': ['i-bp1234567890', 'i-bp0987654321', 'i-bp1111222233'],
                'images': ['centos_7_9_x64', 'ubuntu_20_04_x64', 'windows_2019_datacenter'],
                'security-groups': ['sg-bp1234567890', 'sg-bp0987654321'],
                'regions': ['cn-hangzhou', 'cn-beijing', 'cn-shanghai', 'cn-shenzhen']
            },
            'rds': {
                'instances': ['rm-bp1234567890', 'rm-bp0987654321'],
                'databases': ['mysql', 'postgresql', 'sqlserver'],
                'versions': ['8.0', '5.7', '13.0', '2019']
            },
            'vpc': {
                'vpcs': ['vpc-bp1234567890', 'vpc-bp0987654321'],
                'subnets': ['vsw-bp1234567890', 'vsw-bp0987654321'],
                'routes': ['rtb-bp1234567890', 'rtb-bp0987654321']
            },
            'slb': {
                'instances': ['lb-bp1234567890', 'lb-bp0987654321'],
                'listeners': ['tcp_80', 'https_443', 'http_8080']
            }
        }
    
    def get_completions(self, document, complete_event):
        """获取补全建议"""
        text = document.text_before_cursor
        words = text.split()
        
        if not words:
            # 如果没有输入，显示所有服务
            for service in self.resources.keys():
                yield Completion(
                    service,
                    display=HTML(f'<b>{service}</b> - 阿里云{service.upper()}服务')
                )
        elif len(words) == 1:
            # 第一个词：服务名补全
            service_input = words[0].lower()
            for service in self.resources.keys():
                if self._fuzzy_match(service_input, service):
                    yield Completion(
                        service,
                        start_position=-len(service_input),
                        display=HTML(f'<b>{service}</b> - 阿里云{service.upper()}服务')
                    )
        elif len(words) == 2:
            # 第二个词：资源类型补全
            service = words[0].lower()
            resource_input = words[1].lower()
            
            if service in self.resources:
                for resource_type in self.resources[service].keys():
                    if self._fuzzy_match(resource_input, resource_type):
                        yield Completion(
                            resource_type,
                            start_position=-len(resource_input),
                            display=HTML(f'<ansicyan>{resource_type}</ansicyan> - {service}资源类型')
                        )
        elif len(words) >= 3:
            # 第三个词及以后：具体资源补全
            service = words[0].lower()
            resource_type = words[1].lower()
            resource_input = words[2].lower()
            
            if service in self.resources and resource_type in self.resources[service]:
                resources = self.resources[service][resource_type]
                for resource in resources:
                    if self._fuzzy_match(resource_input, resource):
                        yield Completion(
                            resource,
                            start_position=-len(resource_input),
                            display=HTML(f'<ansigreen>{resource}</ansigreen>')
                        )
    
    def _fuzzy_match(self, input_text: str, target: str) -> bool:
        """模糊匹配算法"""
        if not input_text:
            return True
        
        # 简单的模糊匹配：检查输入的字符是否按顺序出现在目标字符串中
        input_chars = list(input_text.lower())
        target_chars = list(target.lower())
        
        i = 0
        for char in target_chars:
            if i < len(input_chars) and char == input_chars[i]:
                i += 1
        
        return i == len(input_chars)


class CommandCompleter(Completer):
    """命令补全器"""
    
    def __init__(self):
        self.commands = {
            'list': '列出资源',
            'create': '创建资源',
            'delete': '删除资源',
            'update': '更新资源',
            'describe': '描述资源详情',
            'start': '启动资源',
            'stop': '停止资源',
            'restart': '重启资源',
            'backup': '备份资源',
            'restore': '恢复资源'
        }
    
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lower()
        
        for command, description in self.commands.items():
            if command.startswith(text):
                yield Completion(
                    command,
                    start_position=-len(text),
                    display=HTML(f'<b>{command}</b> - {description}')
                )


def demo_basic_fuzzy_completion():
    """基础模糊补全演示"""
    print("\n=== 基础模糊补全演示 ===")
    print("输入编程语言名称（支持模糊匹配）:")
    
    languages = [
        'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 
        'Rust', 'Swift', 'Kotlin', 'PHP', 'Ruby', 'Scala', 'Haskell'
    ]
    
    completer = FuzzyCompleter(WordCompleter(languages))
    
    try:
        result = prompt(
            '选择编程语言: ',
            completer=completer,
            complete_style=CompleteStyle.MULTI_COLUMN
        )
        print(f"你选择了: {result}")
    except KeyboardInterrupt:
        print("\n操作已取消")


def demo_alicloud_resource_completion():
    """阿里云资源补全演示"""
    print("\n=== 阿里云资源补全演示 ===")
    print("输入: <服务名> <资源类型> <资源ID>")
    print("例如: ecs instances i-bp")
    print("支持的服务: ecs, rds, vpc, slb")
    
    completer = AliCloudResourceCompleter()
       
    try:
        result = prompt( '阿里云资源: ',completer=completer,complete_style=CompleteStyle.MULTI_COLUMN
        )
        print(f"你输入了: {result}")
    except KeyboardInterrupt:
        print("\n操作已取消")


def demo_command_completion():
    """命令补全演示"""
    print("\n=== 命令补全演示 ===")
    print("输入操作命令:")
    
    completer = CommandCompleter()
    
    try:
        result = prompt(
            '命令: ',
            completer=completer,
            complete_style=CompleteStyle.READLINE_LIKE
        )
        print(f"你选择的命令: {result}")
    except KeyboardInterrupt:
        print("\n操作已取消")


def demo_nested_completion():
    """嵌套补全演示"""
    print("\n=== 嵌套补全演示 ===")
    print("多级文件路径补全:")
    
    # 模拟文件系统结构
    file_structure = [
        '/home/user/documents/project1/src/main.py',
        '/home/user/documents/project1/src/utils.py',
        '/home/user/documents/project1/tests/test_main.py',
        '/home/user/documents/project2/app.py',
        '/home/user/documents/project2/config.json',
        '/var/log/system.log',
        '/var/log/application.log',
        '/etc/nginx/nginx.conf',
        '/etc/ssh/sshd_config'
    ]
    
    completer = FuzzyCompleter(WordCompleter(file_structure))
    
    try:
        result = prompt(
            '文件路径: ',
            completer=completer,
            complete_style=CompleteStyle.MULTI_COLUMN
        )
        print(f"你选择的路径: {result}")
    except KeyboardInterrupt:
        print("\n操作已取消")


class DynamicCompleter(Completer):
    """动态补全器 - 根据上下文动态生成补全选项"""
    
    def __init__(self):
        self.context_data = {}
    
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        
        # 根据输入内容动态生成补全
        if text.startswith('config.'):
            # 配置项补全
            config_options = [
                'database.host', 'database.port', 'database.username',
                'redis.host', 'redis.port', 'redis.password',
                'logging.level', 'logging.file', 'logging.format'
            ]
            
            prefix = text[7:]  # 去掉 'config.'
            for option in config_options:
                if option.startswith(prefix):
                    yield Completion(
                        option,
                        start_position=-len(prefix),
                        display=HTML(f'<ansiblue>config.{option}</ansiblue>')
                    )
        
        elif text.startswith('env.'):
            # 环境变量补全
            env_vars = [
                'PATH', 'HOME', 'USER', 'SHELL', 'LANG',
                'PYTHONPATH', 'JAVA_HOME', 'NODE_ENV'
            ]
            
            prefix = text[4:]  # 去掉 'env.'
            for var in env_vars:
                if var.lower().startswith(prefix.lower()):
                    yield Completion(
                        var,
                        start_position=-len(prefix),
                        display=HTML(f'<ansigreen>env.{var}</ansigreen>')
                    )


def demo_dynamic_completion():
    """动态补全演示"""
    print("\n=== 动态补全演示 ===")
    print("尝试输入 'config.' 或 'env.' 查看动态补全:")
    
    completer = DynamicCompleter()
    
    try:
        result = prompt('动态补全: ', completer=completer, complete_style=CompleteStyle.MULTI_COLUMN
        )
        print(f"你输入了: {result}")
    except KeyboardInterrupt:
        print("\n操作已取消")


def main():
    """主函数 - 运行所有演示"""
    print("🚀 Prompt Toolkit 高级模糊补全演示")
    print("=" * 50)
    
    demos = [
        ("1", "基础模糊补全", demo_basic_fuzzy_completion),
        ("2", "阿里云资源补全", demo_alicloud_resource_completion),
        ("3", "命令补全", demo_command_completion),
        ("4", "嵌套路径补全", demo_nested_completion),
        ("5", "动态补全", demo_dynamic_completion),
        ("0", "运行所有演示", None)
    ]
    
    while True:
        print("\n请选择演示:")
        for code, name, _ in demos:
            print(f"  {code}. {name}")
        print("  q. 退出")
        
        try:
            choice = input("\n你的选择: ").strip().lower()
            
            if choice == 'q':
                print("再见! 👋")
                break
            elif choice == '0':
                # 运行所有演示
                for _, _, demo_func in demos[:-1]:  # 排除 "运行所有演示" 选项
                    if demo_func:
                        demo_func()
            else:
                # 运行特定演示
                for code, _, demo_func in demos:
                    if choice == code and demo_func:
                        demo_func()
                        break
                else:
                    print("❌ 无效选择，请重试")
        
        except KeyboardInterrupt:
            print("\n\n再见! 👋")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()