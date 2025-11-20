#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prompt_toolkit 包功能演示
展示各种命令行 prompt 形式，重点展示自动补全功能
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, PathCompleter, FuzzyCompleter
from prompt_toolkit.shortcuts import confirm, radiolist_dialog, checkboxlist_dialog
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
import os


class NumberValidator(Validator):
    """数字验证器"""
    def validate(self, document):
        text = document.text
        if text and not text.isdigit():
            i = 0
            for i, c in enumerate(text):
                if not c.isdigit():
                    break
            raise ValidationError(message='请输入数字', cursor_position=i)


def demo_basic_prompt():
    """基础 prompt 演示"""
    print("\n=== 基础 Prompt 演示 ===")
    
    # 简单输入
    name = prompt('请输入您的姓名: ')
    print(f'您好, {name}!')
    
    # 带默认值的输入
    age = prompt('请输入您的年龄: ', default='25')
    print(f'您的年龄是: {age}')
    
    # 密码输入
    password = prompt('请输入密码: ', is_password=True)
    print('密码已设置')


def demo_completion():
    """自动补全演示"""
    print("\n=== 自动补全演示 ===")
    
    # 单词补全
    animals = ['cat', 'dog', 'elephant', 'fish', 'giraffe', 'horse']
    animal_completer = WordCompleter(animals)
    
    animal = prompt('选择一个动物 (输入首字母按Tab补全): ', completer=animal_completer)
    print(f'您选择了: {animal}')
    
    # 路径补全
    print('\n--- 路径补全 ---')
    path = prompt('输入文件路径 (按Tab补全): ', completer=PathCompleter())
    print(f'您输入的路径: {path}')
    
    # 模糊补全
    print('\n--- 模糊补全 ---')
    commands = ['list-files', 'create-directory', 'delete-file', 
               'copy-file', 'move-file', 'search-content']
    fuzzy_completer = FuzzyCompleter(WordCompleter(commands))
    
    command = prompt('输入命令 (支持模糊匹配): ', completer=fuzzy_completer)
    print(f'您选择的命令: {command}')


def demo_validation():
    """输入验证演示"""
    print("\n=== 输入验证演示 ===")
    
    # 数字验证
    number = prompt('请输入一个数字: ',validator=NumberValidator(),validate_while_typing=True)
    print(f'您输入的数字: {number}')


def demo_history_and_suggestions():
    """历史记录和自动建议演示"""
    print("\n=== 历史记录和自动建议演示 ===")
    
    # 创建历史记录
    history = InMemoryHistory()
    history.append_string('git status')
    history.append_string('git add .')
    history.append_string('git commit -m "update"')
    history.append_string('git push origin main')
    
    # 带历史记录和自动建议的输入
    command = prompt('输入Git命令 (↑↓浏览历史，自动建议): ',history=history,auto_suggest=AutoSuggestFromHistory())
    print(f'执行命令: {command}')


def demo_styled_prompt():
    """样式化 prompt 演示"""
    print("\n=== 样式化 Prompt 演示 ===")
    
    # 定义样式
    style = Style.from_dict({
        'prompt': '#ff0066 bold',
        'input': '#44ff00 bold',
    })
    
    # HTML 格式的提示文本
    message = HTML('<prompt>请输入您的</prompt> <b>用户名</b>: ')
    
    username = prompt(message, style=style)
    print(f'用户名: {username}')


def demo_confirmation():
    """确认对话框演示"""
    print("\n=== 确认对话框演示 ===")
    
    # 简单确认
    result = confirm('您确定要继续吗?')
    print(f'确认结果: {result}')
    
    # 带默认值的确认
    result = confirm('是否保存文件?')
    print(f'保存结果: {result}')


def demo_selection_dialogs():
    """选择对话框演示"""
    print("\n=== 选择对话框演示 ===")
    
    # 单选对话框
    print('--- 单选对话框 ---')
    options = [
        ('red', '红色'),
        ('green', '绿色'),
        ('blue', '蓝色'),
        ('yellow', '黄色')
    ]
    
    color = radiolist_dialog(
        title="颜色选择",
        text="请选择您喜欢的颜色:",
        values=options
    ).run()
    
    if color:
        print(f'您选择的颜色: {color}')
    
    # 多选对话框
    print('\n--- 多选对话框 ---')
    features = [
        ('auto_complete', '自动补全'),
        ('syntax_highlight', '语法高亮'),
        ('line_numbers', '行号显示'),
        ('word_wrap', '自动换行')
    ]
    
    selected = checkboxlist_dialog(
        title="功能选择",
        text="请选择需要的功能:",
        values=features
    ).run()
    
    if selected:
        print(f'您选择的功能: {selected}')


def demo_advanced_completion():
    """高级自动补全演示"""
    print("\n=== 高级自动补全演示 ===")
    
    # 嵌套补全 - 阿里云服务
    aliyun_services = {
        'ecs': ['实例管理', '镜像管理', '安全组', '密钥对'],
        'vpc': ['专有网络', '交换机', '路由表', 'NAT网关'],
        'rds': ['实例管理', '数据库管理', '备份恢复', '监控报警'],
        'oss': ['存储桶', '对象管理', '权限控制', '生命周期']
    }
    
    # 创建服务补全器
    service_completer = WordCompleter(list(aliyun_services.keys()))
    
    service = prompt('选择阿里云服务 (ecs/vpc/rds/oss): ', completer=service_completer)
    
    if service in aliyun_services:
        # 根据选择的服务创建功能补全器
        feature_completer = WordCompleter(aliyun_services[service])
        feature = prompt(f'选择 {service} 功能: ', completer=feature_completer)
        print(f'您选择了 {service} 的 {feature} 功能')


def main():
    """主函数 - 运行所有演示"""
    print("🚀 prompt_toolkit 功能演示")
    print("=" * 50)
    
    try:
        # 基础功能演示
        demo_basic_prompt()
        
        # 自动补全演示
        demo_completion()
        
        # 输入验证演示
        demo_validation()
        
        # 历史记录和建议演示
        demo_history_and_suggestions()
        
        # 样式化演示
        demo_styled_prompt()
        
        # 确认对话框演示
        demo_confirmation()
        
        # 选择对话框演示
        demo_selection_dialogs()
        
        # 高级补全演示
        demo_advanced_completion()
        
        print("\n✅ 所有演示完成!")
        
    except KeyboardInterrupt:
        print("\n\n👋 演示已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


if __name__ == '__main__':
    main()