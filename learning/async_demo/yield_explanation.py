"""
yield 关键字详细解释
对比 yield 和 return 的区别
"""

import time

print("=" * 60)
print("1. 使用 return 的普通函数（不保持状态）")
print("=" * 60)

def normal_function_with_return():
    """使用 return 的普通函数"""
    print("🔵 函数开始执行")
    
    for i in range(3):
        print(f"🔵 处理数字 {i}")
        if i == 1:
            print("🔵 遇到 return，函数结束！")
            return i  # 函数彻底结束，状态丢失
        print(f"🔵 数字 {i} 处理完成")
    
    print("🔵 函数正常结束")
    return "完成"

# 测试普通函数
print("调用 normal_function_with_return():")
result = normal_function_with_return()
print(f"返回值: {result}")
print("再次调用同一个函数:")
result2 = normal_function_with_return()
print(f"返回值: {result2}")
print("注意：每次调用都从头开始！\n")

print("=" * 60)
print("2. 使用 yield 的生成器函数（保持状态）")
print("=" * 60)

def generator_function_with_yield():
    """使用 yield 的生成器函数"""
    print("🟢 生成器开始执行")
    
    for i in range(3):
        print(f"🟢 处理数字 {i}")
        print(f"🟢 准备 yield 数字 {i}")
        yield i  # 暂停并返回值，但保持函数状态！
        print(f"🟢 从 yield 恢复，继续处理数字 {i}")
    
    print("🟢 生成器正常结束")
    return "生成器完成"  # 这个 return 会触发 StopIteration 异常

# 测试生成器
print("创建生成器对象:")
gen = generator_function_with_yield()
print(f"生成器对象: {gen}")
print(f"类型: {type(gen)}")

print("\n手动调用 next() 来获取值:")
try:
    print("第一次调用 next():")
    value1 = next(gen)
    print(f"得到值: {value1}")
    
    print("\n第二次调用 next():")
    value2 = next(gen)
    print(f"得到值: {value2}")
    
    print("\n第三次调用 next():")
    value3 = next(gen)
    print(f"得到值: {value3}")
    
    print("\n第四次调用 next() (生成器已结束):")
    value4 = next(gen)
    print(f"得到值: {value4}")
    
except StopIteration as e:
    print(f"生成器结束，StopIteration 异常: {e.value}")

print("\n" + "=" * 60)
print("3. 详细状态保持演示")
print("=" * 60)

def stateful_generator():
    """演示状态保持的生成器"""
    print("🟡 生成器启动")
    
    # 局部变量
    counter = 0
    total = 0
    
    for i in range(5):
        counter += 1
        total += i
        print(f"🟡 局部变量 - counter: {counter}, total: {total}, i: {i}")
        
        # 在 yield 前后都有代码
        print(f"🟡 即将 yield 值 {i}")
        yield_value = f"第{counter}次: {i} (累计:{total})"
        yield yield_value
        print(f"🟡 yield 后恢复 - counter: {counter}, total: {total}")
    
    print("🟡 生成器结束")

print("使用 for 循环消费生成器:")
for value in stateful_generator():
    print(f"👉 收到: {value}")
    time.sleep(0.5)  # 模拟处理延迟

print("\n" + "=" * 60)
print("4. 如果不保持状态会怎样？")
print("=" * 60)

def simulated_no_state_function():
    """模拟如果不保持状态会怎样"""
    print("🔴 假设每次都重新开始...")
    
    # 如果不保持状态，每次调用都要从头开始
    for i in range(3):
        print(f"🔴 从头处理数字 {i}")
        return i  # 每次都只能返回第一个值

print("如果 yield 不保持状态（模拟）:")
print("第一次调用:", simulated_no_state_function())
print("第二次调用:", simulated_no_state_function())
print("第三次调用:", simulated_no_state_function())
print("结果：每次都只能得到 0，无法获取后续值！")

print("\n" + "=" * 60)
print("5. 生成器的内部状态查看")
print("=" * 60)

def debug_generator():
    """可以查看内部状态的生成器"""
    local_var = "我是局部变量"
    
    for i in range(3):
        print(f"🔍 yield 前 - i={i}, local_var={local_var}")
        yield i
        print(f"🔍 yield 后 - i={i}, local_var={local_var}")
        local_var += f" +{i}"

print("查看生成器内部状态:")
debug_gen = debug_generator()

print(f"生成器状态: {debug_gen.gi_frame}")  # 生成器帧对象
print(f"生成器运行状态: {debug_gen.gi_running}")

print("\n获取第一个值:")
val1 = next(debug_gen)
print(f"返回值: {val1}")

print(f"生成器状态: {debug_gen.gi_frame}")  
print(f"生成器运行状态: {debug_gen.gi_running}")

print("\n获取第二个值:")
val2 = next(debug_gen)
print(f"返回值: {val2}")

print("\n" + "=" * 60)
print("6. 总结")
print("=" * 60)

print("""
🎯 yield 的核心特性：

1. ✅ 暂停函数执行，返回值给调用者
2. ✅ 保持函数的所有状态（局部变量、执行位置）
3. ✅ 下次调用时从 yield 的下一行继续
4. ✅ 可以多次返回值，形成数据流

🚫 如果不保持状态：
1. ❌ 每次调用都从函数开头重新开始
2. ❌ 局部变量重新初始化
3. ❌ 无法实现迭代功能
4. ❌ 只能返回第一个值

💡 这就是为什么 yield 能够创建生成器，实现惰性求值和内存高效的数据流处理！
""") 