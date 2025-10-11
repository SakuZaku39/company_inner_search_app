#!/usr/bin/env python3
"""
人事部従業員情報の確認（簡易版）
"""

import pandas as pd
import os

def check_csv_file():
    """CSVファイルの直接読み込みと人事部従業員の抽出"""
    csv_file_path = './data/社員について/社員名簿.csv'
    print(f"CSVファイルパス: {csv_file_path}")
    print(f"ファイル存在確認: {os.path.exists(csv_file_path)}")
    
    if not os.path.exists(csv_file_path):
        print("CSVファイルが見つかりません。")
        return None
    
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(csv_file_path, encoding='utf-8')
        print(f"CSV読み込み成功: {len(df)} 行, {len(df.columns)} 列")
        print(f"カラム名: {list(df.columns)}")
        
        # 人事部の従業員を抽出
        hr_employees = df[df['部署'] == '人事部']
        print(f"\n人事部の従業員数: {len(hr_employees)}")
        
        if len(hr_employees) > 0:
            print("\n=== 人事部の従業員一覧 ===")
            for idx, row in hr_employees.iterrows():
                print(f"社員ID: {row['社員ID']}")
                print(f"氏名: {row['氏名（フルネーム）']}")
                print(f"性別: {row['性別']}")
                print(f"年齢: {row['年齢']}")
                print(f"従業員区分: {row['従業員区分']}")
                print(f"役職: {row['役職']}")
                print(f"入社日: {row['入社日']}")
                print(f"スキルセット: {row['スキルセット']}")
                print("-" * 50)
        else:
            print("人事部の従業員が見つかりませんでした。")
            
        # 部署の一覧を確認
        departments = df['部署'].unique()
        print(f"\n全部署一覧 ({len(departments)}個):")
        for dept in sorted(departments):
            count = len(df[df['部署'] == dept])
            print(f"  - {dept}: {count}名")
            
        return hr_employees
        
    except Exception as e:
        print(f"CSV読み込みエラー: {e}")
        return None

def main():
    print("社員名簿.csv の人事部従業員確認ツール")
    print("="*60)
    
    # CSVファイルの直接確認
    hr_employees = check_csv_file()
    
    print("\n" + "="*60)
    print("確認完了")

if __name__ == "__main__":
    main()