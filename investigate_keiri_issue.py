#!/usr/bin/env python3
"""
経理部検索失敗の原因調査スクリプト
"""

import pandas as pd
import sys
sys.path.append('.')

from utils import detect_employee_query, query_employee_data

def investigate_accounting_department():
    """経理部のデータ詳細調査"""
    print("=" * 80)
    print("🔍 経理部検索失敗の原因調査")
    print("=" * 80)
    
    # CSVファイルを読み込み
    csv_file_path = './data/社員について/社員名簿.csv'
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    
    # 経理部の従業員を抽出
    keiri_employees = df[df['部署'] == '経理部']
    print(f"\n📊 経理部の従業員数: {len(keiri_employees)}名")
    
    # 役職の分布を確認
    positions = keiri_employees['役職'].value_counts()
    print(f"\n👔 経理部の役職分布:")
    for position, count in positions.items():
        print(f"  - {position}: {count}名")
    
    print(f"\n📋 経理部従業員詳細一覧:")
    for idx, row in keiri_employees.iterrows():
        print(f"  社員ID: {row['社員ID']} | 氏名: {row['氏名（フルネーム）']} | 役職: {row['役職']} | 従業員区分: {row['従業員区分']}")
    
    return keiri_employees

def test_search_queries():
    """様々な検索クエリをテスト"""
    print("\n" + "=" * 80)
    print("🧪 検索クエリテスト")
    print("=" * 80)
    
    test_queries = [
        "経理部のスタッフを教えて",
        "経理部の従業員を教えて", 
        "経理部の社員一覧",
        "経理部のアシスタントは誰ですか",
        "経理部の主任を教えて",
        "経理部のマネージャーは誰ですか"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 テスト {i}: '{query}'")
        print("-" * 60)
        
        # クエリ判定
        is_employee_query = detect_employee_query(query)
        print(f"従業員クエリ判定: {'✅' if is_employee_query else '❌'} {is_employee_query}")
        
        if is_employee_query:
            try:
                # 検索実行
                result = query_employee_data(query)
                answer = result.get('answer', '')
                
                # 結果の分析
                if "検索結果:" in answer and "名の従業員が見つかりました" in answer:
                    # 従業員数を抽出
                    import re
                    match = re.search(r'検索結果: (\d+)名の従業員', answer)
                    if match:
                        found_count = int(match.group(1))
                        print(f"✅ 検索成功: {found_count}名見つかりました")
                        
                        # 表形式が含まれているか確認
                        if "|" in answer and "社員ID" in answer:
                            print("✅ 表形式表示成功")
                        else:
                            print("❌ 表形式表示失敗")
                    else:
                        print("❌ 結果数の解析失敗")
                else:
                    print("❌ 検索失敗")
                    print(f"実際の回答: {answer[:200]}...")
                    
            except Exception as e:
                print(f"❌ エラー: {e}")
        else:
            print("❌ クエリ判定失敗")

def analyze_search_logic():
    """検索ロジックの分析"""
    print("\n" + "=" * 80)
    print("🔬 検索ロジック分析")
    print("=" * 80)
    
    # CSVファイルを読み込み
    csv_file_path = './data/社員について/社員名簿.csv'
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    
    # 問題のクエリ
    query = "経理部のスタッフを教えて"
    print(f"問題のクエリ: '{query}'")
    
    # 部署フィルタリング
    departments = ["人事部", "営業部", "IT部", "経理部", "総務部", "マーケティング部"]
    filtered_df = None
    
    for dept in departments:
        if dept in query:
            filtered_df = df[df['部署'] == dept]
            print(f"✅ 部署フィルタ適用: {dept} ({len(filtered_df)}名)")
            break
    
    if filtered_df is not None:
        # 役職フィルタリング
        positions = ["マネージャー", "主任", "アシスタント", "スタッフ", "インターン"]
        original_count = len(filtered_df)
        
        for pos in positions:
            if pos in query:
                filtered_df = filtered_df[filtered_df['役職'] == pos]
                print(f"🔍 役職フィルタ適用: {pos}")
                print(f"  フィルタ前: {original_count}名 → フィルタ後: {len(filtered_df)}名")
                break
        
        if len(filtered_df) == 0:
            print("❌ 役職フィルタ適用後、該当者なし")
            print("💡 経理部の実際の役職:")
            keiri_employees = df[df['部署'] == '経理部']
            for position in keiri_employees['役職'].unique():
                count = len(keiri_employees[keiri_employees['役職'] == position])
                print(f"    - {position}: {count}名")

def main():
    print("🚨 経理部スタッフ検索失敗の原因調査開始")
    
    # 1. 経理部データの詳細調査
    keiri_employees = investigate_accounting_department()
    
    # 2. 様々な検索クエリのテスト
    test_search_queries()
    
    # 3. 検索ロジックの詳細分析
    analyze_search_logic()
    
    print("\n" + "=" * 80)
    print("🎯 調査結果まとめ")
    print("=" * 80)
    print("原因調査が完了しました。上記の結果を基に問題を特定してください。")

if __name__ == "__main__":
    main()