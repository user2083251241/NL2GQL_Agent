"""
LLM模块测试脚本
用于验证LangChain LLM初始化和连接
"""
from modules.llm.client import create_llm, create_llm_with_retry, get_llm


def test_llm_basic():
    """测试基础LLM创建"""
    print("=" * 60)
    print("🧪 LLM模块测试 - 基础功能")
    print("=" * 60)
    
    try:
        print("\n1️⃣ 创建LLM实例...")
        llm = create_llm(temperature=0.7)
        print(f"✅ LLM实例创建成功: {llm.model_name}")
        
        return llm
    except Exception as e:
        print(f"❌ LLM创建失败: {e}")
        return None


def test_llm_connection(llm):
    """测试LLM连接和响应"""
    print("\n2️⃣ 测试LLM连接和响应...")
    
    try:
        # 简单测试问题
        response = llm.invoke("请用一句话介绍一下北京")
        print(f"✅ LLM响应成功:")
        print(f"   {response.content}")
        
        return True
    except Exception as e:
        print(f"❌ LLM响应失败: {e}")
        return False


def test_llm_with_retry():
    """测试带重试机制的LLM创建"""
    print("\n3️⃣ 测试带重试机制的LLM创建...")
    
    try:
        llm = create_llm_with_retry(max_retries=2)
        print(f"✅ 带重试的LLM创建成功")
        return True
    except Exception as e:
        print(f"❌ 带重试的LLM创建失败: {e}")
        return False


def test_llm_singleton():
    """测试LLM单例模式"""
    print("\n4️⃣ 测试LLM单例模式...")
    
    try:
        llm1 = get_llm()
        llm2 = get_llm()
        
        if llm1 is llm2:
            print("✅ 单例模式工作正常（两次获取是同一实例）")
            return True
        else:
            print("❌ 单例模式异常（两次获取不是同一实例）")
            return False
    except Exception as e:
        print(f"❌ 单例测试失败: {e}")
        return False


def test_custom_parameters():
    """测试自定义参数"""
    print("\n5️⃣ 测试自定义参数...")
    
    try:
        llm = create_llm(
            temperature=0.9,
            max_tokens=1000,
            verbose=False
        )
        print(f"✅ 自定义参数LLM创建成功")
        print(f"   Temperature: {llm.temperature}")
        print(f"   Max Tokens: {llm.max_tokens}")
        return True
    except Exception as e:
        print(f"❌ 自定义参数测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🚀 开始LLM模块完整测试")
    print("=" * 60 + "\n")
    
    # 测试1: 基础创建
    llm = test_llm_basic()
    
    if llm is None:
        print("\n⚠️ 基础创建失败，跳过后续测试")
        print("\n💡 提示: 请检查 .env 文件中的 OPENAI_API_KEY 是否正确配置")
        return
    
    # 测试2: 连接测试
    test_llm_connection(llm)
    
    # 测试3: 重试机制
    test_llm_with_retry()
    
    # 测试4: 单例模式
    test_llm_singleton()
    
    # 测试5: 自定义参数
    test_custom_parameters()
    
    print("\n" + "=" * 60)
    print("✅ LLM模块测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
