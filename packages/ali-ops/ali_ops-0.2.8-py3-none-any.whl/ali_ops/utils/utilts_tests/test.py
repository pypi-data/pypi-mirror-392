from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import CompleteStyle


class CustomCompleter(Completer):
    def __init__(self, words):
        self.words = words

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        for word in self.words:
            if word.startswith(word_before_cursor):
                yield Completion(word, start_position=-len(word_before_cursor))


# 如何使用自动补全类
words = ['hello', 'world', 'python', 'programming', 'help']
completer = CustomCompleter(words)


# user_input = prompt('请输入: ', completer=completer, complete_style=CompleteStyle.READLINE_LIKE)
user_input = prompt('请输入: ', completer=completer, complete_style=CompleteStyle.MULTI_COLUMN)
print(f'您输入的是: {user_input}')
