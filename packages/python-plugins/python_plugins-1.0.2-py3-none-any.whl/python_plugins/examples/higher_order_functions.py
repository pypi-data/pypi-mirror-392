from functools import reduce
import time

# lambda parameters: expression
print("Higher-Order Functions in Python")

lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

print("lst=",lst)

print("map(function, iterable, *iterables) -> iterable")
print(lst_2:=list(map(lambda i: i**2, lst)))

print("[i**2 for i in lst] -> iterable")
print([i**2 for i in lst])

print("map(lambda x, y: x + y, lst, lst_2) -> iterable")
lst_3 = list(map(lambda x, y: x + y, lst, lst_2))
print(lst_3)

print("filter(function, iterable) -> iterable")
print("filter(lambda x: x % 2 == 0, lst) -> iterable")
result = list(filter(lambda x: x % 2 == 0, lst))

print(result)
print("[item for item in lst if item % 2 == 0] -> iterable")
print([item for item in lst if item % 2 == 0])

# reduce() - 累积函数
print("reduce(function, iterable[, initializer])")
print("reduce(lambda x, y: x + y, lst) -> value")
result = reduce(lambda x, y: x + y, lst)

print(result)

print("计算乘积")
numbers = [1, 2, 3, 4, 5]
product = reduce(lambda x, y: x * y, numbers)
print(product)  # 120

print("找出最大值")
max_number = reduce(lambda x, y: x if x > y else y, numbers)
print(max_number)  # 5

print("字符串连接")
words = ['Hello', 'World', 'Python']
sentence = reduce(lambda x, y: x + ' ' + y, words)
print(sentence)  # 'Hello World Python'


# zip(*iterables)
# sorted() - 排序函数
# sorted(iterable, key=None, reverse=False)
# 自定义排序
students = [
    {'name': 'Alice', 'grade': 85},
    {'name': 'Bob', 'grade': 92},
    {'name': 'Charlie', 'grade': 78}
]

# 按成绩排序
sorted_by_grade = sorted(students, key=lambda x: x['grade'])
print(sorted_by_grade)
# [{'name': 'Charlie', 'grade': 78}, {'name': 'Alice', 'grade': 85}, {'name': 'Bob', 'grade': 92}]

# 按名字长度排序
words = ['python', 'java', 'c', 'javascript', 'go']
sorted_by_length = sorted(words, key=len)
print(sorted_by_length)  # ['c', 'go', 'java', 'python', 'javascript']

# 装饰器 - 经典的高阶函数应用
def timer(func):
    """计算函数执行时间的装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 执行时间: {end_time - start_time:.4f}秒")
        return result
    return wrapper

# 使用装饰器
@timer
def slow_function():
    """模拟耗时操作"""
    time.sleep(1)
    return "完成"

# 测试
result = slow_function()
print(result)

# 接受函数作为参数

def apply_operation(numbers, operation):
    """
    对数字列表应用操作
    
    Args:
        numbers: 数字列表
        operation: 操作函数
    """
    return [operation(x) for x in numbers]

# 使用示例
numbers = [1, 2, 3, 4, 5]

# 平方
squared = apply_operation(numbers, lambda x: x**2)
print(f"平方: {squared}")

# 加倍
doubled = apply_operation(numbers, lambda x: x * 2)
print(f"加倍: {doubled}")

# 使用命名函数
def increment(x):
    return x + 1

incremented = apply_operation(numbers, increment)
print(f"加一: {incremented}")

# 返回函数作为结果

def create_multiplier(factor):
    """
    创建乘法器函数
    
    Args:
        factor: 乘数因子
    Returns:
        乘法函数
    """
    def multiplier(x):
        return x * factor
    return multiplier

# 使用示例
double = create_multiplier(2)
triple = create_multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15

# 在列表中使用
numbers = [1, 2, 3, 4, 5]
doubled_numbers = list(map(double, numbers))
print(doubled_numbers)  # [2, 4, 6, 8, 10]

# 函数组合

def compose(*functions):
    """
    函数组合：compose(f, g, h)(x) = f(g(h(x)))
    """
    def composed(x):
        result = x
        for func in reversed(functions):
            result = func(result)
        return result
    return composed

# 使用示例
def add_one(x):
    return x + 1

def multiply_by_two(x):
    return x * 2

def square(x):
    return x ** 2

# 组合函数：square(multiply_by_two(add_one(x)))
complex_operation = compose(square, multiply_by_two, add_one)

result = complex_operation(3)  # ((3 + 1) * 2) ** 2 = 64
print(result)  # 64

# 偏函数（Partial Functions）

from functools import partial

# 创建偏函数
def power(base, exponent):
    return base ** exponent

# 创建平方函数
square = partial(power, exponent=2)
# 创建立方函数
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(3))    # 27

# 在 map 中使用
numbers = [1, 2, 3, 4, 5]
squares = list(map(square, numbers))
print(squares)  # [1, 4, 9, 16, 25]

