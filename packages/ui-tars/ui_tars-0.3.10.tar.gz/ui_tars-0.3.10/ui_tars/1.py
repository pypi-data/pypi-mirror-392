def add_backslash_before_newline(s):
    result = []
    for i in range(len(s)):
        if s[i] == '\n':
            # 如果当前字符是 '\n'，并且前一个字符不是 '\'
            if i == 0 or s[i - 1] != '\\':
                result.append('\\')  # 在 '\n' 前添加 '\'
        result.append(s[i])
    return ''.join(result)

# 测试
input_string = "Hello\nWorld\nThis is a test\\\nAnother line\n"
output_string = add_backslash_before_newline(input_string)
print("输入字符串:")
print(repr(input_string))
print("输出字符串:")
print(repr(output_string))