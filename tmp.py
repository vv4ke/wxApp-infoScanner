def contains_any(string, substrings):
    return any(substring in string for substring in substrings)

# 示例
my_string = "This is a sample text with some words."
my_list = ["sample", "words", "absent"]

result = contains_any(my_string, my_list)
print(result)  # 输出: True
