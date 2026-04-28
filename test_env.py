import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 检查环境变量
print("=== 环境变量检查 ===")
print(f"QWEN_API_KEY: {os.getenv('QWEN_API_KEY')[:10]}..." if os.getenv('QWEN_API_KEY') else "QWEN_API_KEY: 未设置")
print(f"QWEN_MODEL: {os.getenv('QWEN_MODEL')}")
print(f"QWEN_API_BASE: {os.getenv('QWEN_API_BASE')}")

# 检查 .env 文件是否存在
print("\n=== .env 文件检查 ===")
if os.path.exists('.env'):
    print(".env 文件存在")
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
        print("文件内容:")
        print(content)
else:
    print(".env 文件不存在")
