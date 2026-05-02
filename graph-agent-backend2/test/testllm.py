from modules.llm.client import create_llm, create_llm_with_retry, get_llm

def test_llm_basic():
    
    try:
        llm = create_llm(temperature=0.7)
        
        return llm
    except Exception as e:
        print(f"❌ LLM创建失败: {e}")
        return None

def test_llm_connection(llm):
    
    try:
        response = llm.invoke("100字介绍一下大连理工大学软件学院")
        print(f"   {response.content}")
        
        return True
    except Exception as e:
        print(f"❌ LLM响应失败: {e}")
        return False


def test_llm_with_retry():
    
    try:
        llm = create_llm_with_retry(max_retries=2)
        print(f"✅ 带重试的LLM创建成功")
        return True
    except Exception as e:
        print(f"❌ 带重试的LLM创建失败: {e}")
        return False


def test_llm_singleton():

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
    
    llm = test_llm_basic()
    
    if llm is None:
        print("\n⚠️ 基础创建失败，跳过后续测试")
        print("\n💡 提示: 请检查 .env 文件中的 OPENAI_API_KEY 是否正确配置")
        return
    
    test_llm_connection(llm)


if __name__ == "__main__":
    main()
