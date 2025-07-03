"""
FastAPI Demo API 测试脚本
演示如何调用FastAPI接口
"""

import json
import time
import requests

# API基础URL
BASE_URL = "http://localhost:8000"

def test_api():
    """测试所有API接口"""
    print("🧪 开始测试FastAPI图书管理系统API...")
    print("=" * 50)
    
    # 1. 测试首页
    print("1️⃣ 测试首页接口")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ 状态码: {response.status_code}")
        print(f"📝 响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n" + "-" * 30 + "\n")
    
    # 2. 测试健康检查
    print("2️⃣ 测试健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ 状态码: {response.status_code}")
        print(f"📝 响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n" + "-" * 30 + "\n")
    
    # 3. 测试获取所有图书
    print("3️⃣ 测试获取所有图书")
    try:
        response = requests.get(f"{BASE_URL}/books")
        books = response.json()
        print(f"✅ 状态码: {response.status_code}")
        print(f"📚 找到 {len(books)} 本图书:")
        for book in books:
            print(f"   - {book['title']} by {book['author']} (¥{book['price']})")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n" + "-" * 30 + "\n")
    
    # 4. 测试创建新图书
    print("4️⃣ 测试创建新图书")
    new_book = {
        "title": "FastAPI实战指南",
        "author": "张三",
        "price": 99.9,
        "category": "编程",
        "description": "一本详细的FastAPI实战教程"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/books",
            json=new_book,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ 状态码: {response.status_code}")
        created_book = response.json()
        book_id = created_book['id']
        print(f"📖 创建成功! 图书ID: {book_id}")
        print(f"📝 图书信息: {created_book['title']} - ¥{created_book['price']}")
    except Exception as e:
        print(f"❌ 错误: {e}")
        book_id = None
    
    print("\n" + "-" * 30 + "\n")
    
    # 5. 测试根据ID获取图书
    if book_id:
        print("5️⃣ 测试根据ID获取图书")
        try:
            response = requests.get(f"{BASE_URL}/books/{book_id}")
            print(f"✅ 状态码: {response.status_code}")
            book = response.json()
            print(f"📖 找到图书: {book['title']}")
            print(f"📝 详细信息: {json.dumps(book, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n" + "-" * 30 + "\n")
    
    # 6. 测试搜索图书
    print("6️⃣ 测试搜索图书")
    try:
        response = requests.get(f"{BASE_URL}/books/search/?q=Python")
        print(f"✅ 状态码: {response.status_code}")
        books = response.json()
        print(f"🔍 搜索'Python'找到 {len(books)} 本图书:")
        for book in books:
            print(f"   - {book['title']} by {book['author']}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n" + "-" * 30 + "\n")
    
    # 7. 测试分类筛选
    print("7️⃣ 测试分类筛选")
    try:
        response = requests.get(f"{BASE_URL}/books?category=编程&limit=5")
        print(f"✅ 状态码: {response.status_code}")
        books = response.json()
        print(f"📂 '编程'分类下有 {len(books)} 本图书:")
        for book in books:
            print(f"   - {book['title']} ({book['category']})")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n" + "-" * 30 + "\n")
    
    # 8. 测试统计信息
    print("8️⃣ 测试统计信息")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print(f"✅ 状态码: {response.status_code}")
        stats = response.json()
        print(f"📊 图书统计:")
        print(f"   - 总图书数: {stats['total_books']}")
        print(f"   - 总价值: ¥{stats['total_value']}")
        print(f"   - 平均价格: ¥{stats['average_price']}")
        print(f"   - 分类统计: {json.dumps(stats['categories'], ensure_ascii=False, indent=4)}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n" + "-" * 30 + "\n")
    
    # 9. 测试更新图书
    if book_id:
        print("9️⃣ 测试更新图书")
        update_data = {
            "price": 88.8,
            "description": "更新后的FastAPI实战指南，价格更优惠！"
        }
        try:
            response = requests.put(
                f"{BASE_URL}/books/{book_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"✅ 状态码: {response.status_code}")
            updated_book = response.json()
            print(f"📝 更新成功! 新价格: ¥{updated_book['price']}")
            print(f"📄 新描述: {updated_book['description']}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n" + "-" * 30 + "\n")
    
    # 10. 测试异常处理
    print("🔟 测试异常处理")
    try:
        response = requests.get(f"{BASE_URL}/books/error-demo?error_type=not_found")
        print(f"⚠️  状态码: {response.status_code}")
        print(f"📝 错误信息: {response.json()}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n" + "-" * 30 + "\n")
    
    # 11. 测试删除图书
    if book_id:
        print("1️⃣1️⃣ 测试删除图书")
        try:
            response = requests.delete(f"{BASE_URL}/books/{book_id}")
            print(f"✅ 状态码: {response.status_code}")
            result = response.json()
            print(f"🗑️ 删除结果: {result['message']}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API测试完成！")
    print("📖 想查看完整的API文档，请访问: http://localhost:8000/docs")

if __name__ == "__main__":
    # 等待服务器启动
    print("⏳ 等待FastAPI服务器启动...")
    time.sleep(3)
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器已就绪！")
            test_api()
        else:
            print("❌ 服务器状态异常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器。请确保FastAPI服务器正在运行:")
        print("   python -m fastapi dev simple_main.py")
    except Exception as e:
        print(f"❌ 连接错误: {e}") 