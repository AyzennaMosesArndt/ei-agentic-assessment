"""Setup Test - prüft ob alle Dependencies funktionieren"""
import sys
from dotenv import load_dotenv
import os

def test_setup():
    print("🔍 Testing Setup...\n")
    
    # 1. Python Version
    py_version = sys.version.split()[0]
    print(f"✅ Python Version: {py_version}")
    assert py_version >= "3.11", "Python 3.11+ required!"
    
    # 2. Imports
    try:
        import chainlit
        print(f"✅ Chainlit: {chainlit.__version__}")
    except ImportError:
        print("❌ Chainlit nicht installiert!")
        return False
    
    try:
        import langgraph
        print(f"✅ LangGraph: installed")
    except ImportError:
        print("❌ LangGraph nicht installiert!")
        return False
    
    try:
        from langchain_openai import ChatOpenAI
        print("✅ LangChain OpenAI: imported")
    except ImportError:
        print("❌ LangChain OpenAI nicht installiert!")
        return False
    
    # 3. .env laden
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY nicht in .env gefunden!")
        return False
    
    if api_key.startswith("sk-"):
        print(f"✅ API Key gefunden (starts with sk-...)")
    else:
        print("⚠️  API Key Format sieht komisch aus!")
    
    # 4. OpenAI Connection Test
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Setup OK!'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI API Test: {result}")
        
    except Exception as e:
        print(f"❌ OpenAI API Fehler: {e}")
        return False
    
    print("\n🎉 SETUP KOMPLETT! Bereit für Agent-Development.")
    return True

if __name__ == "__main__":
    test_setup()