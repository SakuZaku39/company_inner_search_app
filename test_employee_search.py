#!/usr/bin/env python3
"""
従業員検索機能のテストスクリプト
"""

import os
import sys
sys.path.append('.')

from utils import detect_employee_query, query_employee_data

def test_employee_detection():
    """従業員クエリ検出のテスト"""
    print("=" * 60)
    print("従業員クエリ検出テスト")
    print("=" * 60)
    
    test_queries = [
        "人事部に所属している従業員情報を一覧化して",
        "営業部のマネージャーは誰ですか",
        "社員の一覧を教えて",
        "天気はどうですか？",  # 非従業員クエリ
        "会社の売上について教えて",  # 非従業員クエリ
        "IT部のスタッフのスキルセットを知りたい"
    ]
    
    for query in test_queries:
        is_employee_query = detect_employee_query(query)
        print(f"クエリ: '{query}'")
        print(f"従業員クエリ判定: {is_employee_query}")
        print("-" * 40)

def test_employee_query():
    """従業員データクエリのテスト"""
    print("\n" + "=" * 60)
    print("従業員データクエリテスト")
    print("=" * 60)
    
    test_queries = [
        "人事部に所属している従業員情報を一覧化して",
        "営業部のマネージャーを教えて",
        "IT部の社員は何人いますか？"
    ]
    
    for query in test_queries:
        print(f"\nクエリ: '{query}'")
        print("-" * 40)
        
        try:
            result = query_employee_data(query)
            answer = result.get('answer', 'No answer')
            
            # 回答の長さを制限して表示
            if len(answer) > 500:
                print(f"回答（抜粋）: {answer[:500]}... [省略]")
            else:
                print(f"回答: {answer}")
                
        except Exception as e:
            print(f"エラー: {e}")
        
        print("-" * 40)

def main():
    print("従業員検索機能テストスクリプト")
    
    # 環境確認
    csv_file = './data/社員について/社員名簿.csv'
    if not os.path.exists(csv_file):
        print(f"CSVファイルが見つかりません: {csv_file}")
        return
    
    # テスト実行
    test_employee_detection()
    test_employee_query()
    
    print("\n" + "=" * 60)
    print("テスト完了")

if __name__ == "__main__":
    main()