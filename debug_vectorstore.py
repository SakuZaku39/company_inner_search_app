"""
ベクターストアのデバッグ用スクリプト
RAGが正しく動作しているかを確認する
"""

import os
import constants as ct
from initialize import recursive_file_check

def debug_vectorstore():
    """
    ベクターストア構築対象ファイルを確認
    """
    print("=== ベクターストア構築対象ファイル確認 ===")
    
    # 修正点: サポートされている拡張子を確認
    print(f"サポート拡張子: {list(ct.SUPPORTED_EXTENSIONS.keys())}")
    
    # 修正点: データフォルダ内のファイルを確認
    data_path = ct.RAG_TOP_FOLDER_PATH
    print(f"\nデータフォルダ: {data_path}")
    
    all_files = []
    supported_files = []
    
    # 修正点: ファイル一覧を取得して分類
    for root, dirs, filenames in os.walk(data_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            all_files.append(file_path)
            
            # 拡張子をチェック
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension in ct.SUPPORTED_EXTENSIONS:
                supported_files.append(file_path)
    
    print(f"\n全ファイル数: {len(all_files)}")
    print(f"サポート対象ファイル数: {len(supported_files)}")
    
    # 修正点: .txtファイルを特に確認
    txt_files = [f for f in supported_files if f.endswith('.txt')]
    print(f"\n.txtファイル数: {len(txt_files)}")
    
    if txt_files:
        print("=== .txtファイル一覧 ===")
        for txt_file in txt_files:
            print(f"  - {txt_file}")
            
            # 修正点: ファイル内容の一部を表示
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()[:200]  # 最初の200文字
                    print(f"    内容抜粋: {content[:100]}...")
            except Exception as e:
                print(f"    読み込みエラー: {e}")
    
    # 修正点: 議事録関連ファイルを特に確認
    print("\n=== 議事録関連ファイル ===")
    for file_path in supported_files:
        if "議事録" in file_path or "MTG" in file_path:
            print(f"  - {file_path}")

if __name__ == "__main__":
    debug_vectorstore()