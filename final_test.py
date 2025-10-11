#!/usr/bin/env python3
"""
最終統合テストスクリプト - 全機能の動作確認
"""

import os
import sys
import time
sys.path.append('.')

from utils import detect_employee_query, query_employee_data

def print_section(title):
    """セクションタイトルを表示"""
    print("\n" + "="*80)
    print(f"🚀 {title}")
    print("="*80)

def print_subsection(title):
    """サブセクションタイトルを表示"""
    print("\n" + "-"*60)
    print(f"📋 {title}")
    print("-"*60)

def test_environment():
    """環境確認テスト"""
    print_section("環境確認テスト")
    
    # 必要なファイルの存在確認
    files_to_check = [
        './main.py',
        './utils.py', 
        './components.py',
        './constants.py',
        './initialize.py',
        './data/社員について/社員名簿.csv',
        './data/MTG議事録/議事録ルール.txt'
    ]
    
    print("📁 ファイル存在確認:")
    all_files_exist = True
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        if not exists:
            all_files_exist = False
    
    # ライブラリインポート確認
    print("\n📦 ライブラリインポート確認:")
    libraries = [
        ('streamlit', 'st'),
        ('langchain', 'langchain'),
        ('pandas', 'pd'),
        ('langchain_experimental', 'langchain_experimental')
    ]
    
    for lib_name, import_name in libraries:
        try:
            exec(f"import {import_name}")
            print(f"  ✅ {lib_name}")
        except ImportError as e:
            print(f"  ❌ {lib_name} - {e}")
            all_files_exist = False
    
    return all_files_exist

def test_employee_queries():
    """従業員検索機能テスト"""
    print_section("従業員検索機能テスト")
    
    test_queries = [
        {
            "query": "人事部に所属している従業員情報を一覧化して",
            "expected_employees": 9,
            "description": "人事部全員の検索"
        },
        {
            "query": "営業部のマネージャーは誰ですか",
            "expected_employees": 4,
            "description": "営業部マネージャーの検索"
        },
        {
            "query": "IT部の社員は何人いますか？",
            "expected_employees": 11,
            "description": "IT部社員数の確認"
        },
        {
            "query": "経理部のスタッフを教えて",
            "expected_employees": 6,
            "description": "経理部全員の検索"
        },
        {
            "query": "総務部の従業員一覧を表示して",
            "expected_employees": 3,
            "description": "総務部全員の検索"
        }
    ]
    
    success_count = 0
    for i, test_case in enumerate(test_queries, 1):
        print_subsection(f"テスト {i}: {test_case['description']}")
        print(f"クエリ: '{test_case['query']}'")
        
        try:
            # クエリ判定テスト
            is_employee_query = detect_employee_query(test_case['query'])
            print(f"従業員クエリ判定: {'✅' if is_employee_query else '❌'} {is_employee_query}")
            
            if is_employee_query:
                # 実際のクエリ実行
                result = query_employee_data(test_case['query'])
                answer = result.get('answer', '')
                
                # 結果確認
                if "検索結果:" in answer and "名の従業員が見つかりました" in answer:
                    print("✅ 検索実行成功")
                    # 表形式が含まれているか確認
                    if "|" in answer and "社員ID" in answer:
                        print("✅ 表形式表示成功")
                        success_count += 1
                    else:
                        print("❌ 表形式表示失敗")
                else:
                    print("❌ 検索実行失敗")
            else:
                print("❌ クエリ判定失敗")
                
        except Exception as e:
            print(f"❌ エラー: {e}")
        
        time.sleep(0.5)  # レート制限回避
    
    print(f"\n🎯 従業員検索テスト結果: {success_count}/{len(test_queries)} 成功")
    return success_count == len(test_queries)

def test_non_employee_queries():
    """非従業員クエリテスト"""
    print_section("非従業員クエリ判定テスト")
    
    non_employee_queries = [
        "今日の天気はどうですか？",
        "会社の売上について教えて",
        "新商品の開発状況は？",
        "来月の予算計画について",
        "システムの不具合報告"
    ]
    
    success_count = 0
    for i, query in enumerate(non_employee_queries, 1):
        print(f"\nテスト {i}: '{query}'")
        is_employee_query = detect_employee_query(query)
        if not is_employee_query:
            print("✅ 正しく非従業員クエリと判定")
            success_count += 1
        else:
            print("❌ 誤って従業員クエリと判定")
    
    print(f"\n🎯 非従業員クエリテスト結果: {success_count}/{len(non_employee_queries)} 成功")
    return success_count == len(non_employee_queries)

def test_file_structure():
    """データファイル構造テスト"""
    print_section("データファイル構造テスト")
    
    data_dir = "./data"
    if not os.path.exists(data_dir):
        print("❌ dataディレクトリが見つかりません")
        return False
    
    expected_structure = {
        "社員について": ["社員名簿.csv"],
        "MTG議事録": ["議事録ルール.txt"],
        "会社について": [],
        "サービスについて": [],
        "顧客について": []
    }
    
    success = True
    for folder, expected_files in expected_structure.items():
        folder_path = os.path.join(data_dir, folder)
        if os.path.exists(folder_path):
            print(f"✅ {folder}/ ディレクトリ存在")
            for file_name in expected_files:
                file_path = os.path.join(folder_path, file_name)
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"  ✅ {file_name} ({file_size} bytes)")
                else:
                    print(f"  ❌ {file_name} 見つからない")
                    success = False
        else:
            print(f"❌ {folder}/ ディレクトリが見つかりません")
            success = False
    
    return success

def main():
    """メインテスト実行"""
    print("🔥 最終統合テスト開始 🔥")
    print("="*80)
    
    # テスト実行
    results = {
        "環境確認": test_environment(),
        "従業員検索": test_employee_queries(),
        "非従業員判定": test_non_employee_queries(),
        "ファイル構造": test_file_structure()
    }
    
    # 結果サマリー
    print_section("最終テスト結果")
    
    passed_tests = 0
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n🎯 総合成功率: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("\n🎉 全テスト成功！アプリケーションは本番環境での利用準備が整いました！")
    elif success_rate >= 80:
        print("\n👍 大部分のテストが成功！軽微な修正で本番利用可能です。")
    else:
        print("\n⚠️ 重要な問題が検出されました。修正が必要です。")
    
    # Streamlitアプリの案内
    print_section("Streamlitアプリケーション")
    print("🌐 Streamlitアプリは以下のURLで動作中です:")
    print("   Local URL: http://localhost:8501")
    print("   Network URL: http://192.168.10.105:8501")
    print("\n📝 推奨テストクエリ:")
    print("   1. 「人事部に所属している従業員情報を一覧化して」")
    print("   2. 「営業部のマネージャーは誰ですか」")
    print("   3. 「IT部の社員は何人いますか？」")
    print("   4. 「議事録のルールを教えて」")

if __name__ == "__main__":
    main()