"""
初期化処理のデバッグ用スクリプト
"""

from __future__ import annotations

import os
import sys
import traceback
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def debug_initialization():
    """初期化処理のデバッグ"""
    
    print("🔍 初期化処理のデバッグを開始します...")
    
    # 1. 環境変数の確認
    print("\n1. 環境変数の確認:")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✅ OPENAI_API_KEY: 設定済み (先頭10文字: {openai_key[:10]}...)")
    else:
        print("❌ OPENAI_API_KEY: 設定されていません")
    
    # 2. dataフォルダの確認
    print("\n2. dataフォルダの確認:")
    data_path = "./data"
    if os.path.exists(data_path):
        print(f"✅ dataフォルダ: 存在します ({data_path})")
        try:
            files = []
            for root, dirs, filenames in os.walk(data_path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            print(f"📁 ファイル数: {len(files)}個")
            for file in files[:5]:  # 最初の5個だけ表示
                print(f"  - {file}")
            if len(files) > 5:
                print(f"  ... 他 {len(files) - 5}個")
        except Exception as e:
            print(f"❌ ファイル一覧取得エラー: {e}")
    else:
        print(f"❌ dataフォルダ: 存在しません ({data_path})")
    
    # 3. ライブラリのインポート確認
    print("\n3. 必要ライブラリの確認:")
    try:
        from langchain_openai import OpenAIEmbeddings
        print("✅ OpenAIEmbeddings: インポート成功")
    except Exception as e:
        print(f"❌ OpenAIEmbeddings: インポートエラー - {e}")
        return
    
    try:
        from langchain_community.vectorstores import Chroma
        print("✅ Chroma: インポート成功")
    except Exception as e:
        print(f"❌ Chroma: インポートエラー - {e}")
        return
    
    # 4. OpenAI接続テスト
    print("\n4. OpenAI接続テスト:")
    try:
        embeddings = OpenAIEmbeddings()
        test_result = embeddings.embed_query("テスト")
        print(f"✅ OpenAI接続: 成功 (埋め込み次元: {len(test_result)})")
    except Exception as e:
        print(f"❌ OpenAI接続エラー: {e}")
        print("詳細:")
        traceback.print_exc()
        return
    
    print("\n🎉 初期化処理の前提条件がすべて満たされています！")

if __name__ == "__main__":
    debug_initialization()