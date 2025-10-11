"""
LangChainの動作確認テスト
Python 3.11とfrom __future__ import annotationsを使用
"""

from __future__ import annotations

try:
    from langchain_openai import ChatOpenAI
    print("✅ langchain-openai import successful")
    
    from langchain.chains.combine_documents import create_stuff_documents_chain
    print("✅ create_stuff_documents_chain import successful")
    
    from langchain.chains import create_history_aware_retriever, create_retrieval_chain
    print("✅ chains import successful")
    
    print("🎉 All LangChain imports successful!")
    print("Python environment is working correctly.")
    
except Exception as e:
    print(f"❌ Error importing LangChain: {e}")
    import sys
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")