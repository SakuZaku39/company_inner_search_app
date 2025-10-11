#!/usr/bin/env python3
"""
ベクトルストアの検証ツール
"""

import os
import sys
from pathlib import Path
import constants as ct
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

def check_csv_loading():
    """CSVファイルがLangChainで正しく読み込まれるかテスト"""
    print("="*60)
    print("CSVファイルのLangChain読み込みテスト")
    print("="*60)
    
    csv_file_path = './data/社員について/社員名簿.csv'
    
    if not os.path.exists(csv_file_path):
        print(f"CSVファイルが見つかりません: {csv_file_path}")
        return None
    
    try:
        # CSVLoaderでファイルを読み込み
        loader = CSVLoader(file_path=csv_file_path, encoding='utf-8')
        documents = loader.load()
        
        print(f"読み込み成功: {len(documents)} ドキュメント")
        
        # 人事部関連のドキュメントを確認
        hr_docs = []
        for doc in documents:
            if "人事部" in doc.page_content:
                hr_docs.append(doc)
        
        print(f"人事部関連ドキュメント: {len(hr_docs)}個")
        
        # 最初の人事部ドキュメントの内容を表示
        if hr_docs:
            print("\n=== 最初の人事部ドキュメント ===")
            print(f"内容: {hr_docs[0].page_content}")
            print(f"メタデータ: {hr_docs[0].metadata}")
        
        return documents
        
    except Exception as e:
        print(f"CSVLoader読み込みエラー: {e}")
        return None

def check_vector_store_creation():
    """ベクトルストアの作成をテスト"""
    print("\n" + "="*60)
    print("ベクトルストア作成テスト")
    print("="*60)
    
    try:
        # CSVファイルを読み込み
        documents = check_csv_loading()
        if not documents:
            return None
        
        # テキスト分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=ct.CHUNK_SIZE,
            chunk_overlap=ct.CHUNK_OVERLAP
        )
        
        texts = text_splitter.split_documents(documents)
        print(f"テキスト分割結果: {len(texts)} チャンク")
        
        # エンベディング生成
        embeddings = OpenAIEmbeddings()
        
        # ベクトルストア作成
        vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory="./test_chroma_db"
        )
        
        print("ベクトルストア作成成功")
        
        # 人事部関連の検索テスト
        search_queries = ["人事部", "斉藤 舞", "人事部 従業員"]
        
        for query in search_queries:
            print(f"\n検索クエリ: '{query}'")
            results = vectorstore.similarity_search(query, k=3)
            print(f"検索結果数: {len(results)}")
            
            for i, doc in enumerate(results):
                content_preview = doc.page_content[:150].replace('\n', ' ')
                print(f"  結果 {i+1}: {content_preview}...")
        
        return vectorstore
        
    except Exception as e:
        print(f"ベクトルストア作成エラー: {e}")
        return None

def check_data_directory():
    """dataディレクトリの構造を確認"""
    print("\n" + "="*60)
    print("dataディレクトリ構造確認")
    print("="*60)
    
    data_dir = Path('./data')
    if not data_dir.exists():
        print("dataディレクトリが見つかりません")
        return
    
    for root, dirs, files in os.walk(data_dir):
        level = root.replace(str(data_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            print(f"{subindent}{file} ({file_size} bytes)")

def main():
    print("ベクトルストア検証ツール")
    print("="*60)
    
    # 1. データディレクトリ構造確認
    check_data_directory()
    
    # 2. CSV読み込みテスト
    check_csv_loading()
    
    # 3. ベクトルストア作成テスト
    vectorstore = check_vector_store_creation()
    
    print("\n" + "="*60)
    print("検証完了")

if __name__ == "__main__":
    main()