#!/usr/bin/env python3
"""
COMMON_ERROR_MESSAGE表示問題の調査スクリプト
"""

import sys
sys.path.append('.')

from utils import get_llm_response, detect_employee_query, query_employee_data
import traceback

def test_employee_query_with_debug():
    """従業員クエリのデバッグテスト"""
    print("🔍 COMMON_ERROR_MESSAGE問題の調査")
    print("=" * 80)
    
    test_queries = [
        "人事部に所属している従業員情報を一覧化して",
        "経理部のスタッフを教えて",
        "営業部のマネージャーは誰ですか"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 テスト {i}: '{query}'")
        print("-" * 60)
        
        try:
            print("🔍 ステップ1: クエリ判定")
            is_employee_query = detect_employee_query(query)
            print(f"  従業員クエリ判定: {is_employee_query}")
            
            if is_employee_query:
                print("🔍 ステップ2: 従業員データクエリ")
                try:
                    result = query_employee_data(query)
                    answer = result.get('answer', '')
                    print(f"  クエリ実行成功: 回答長 {len(answer)} 文字")
                    
                    # エラーメッセージが含まれているかチェック
                    if "エラーが発生しました" in answer:
                        print("  ❌ 従業員データ検索でエラー発生")
                        print(f"  エラー内容: {answer}")
                    else:
                        print("  ✅ 従業員データ検索成功")
                        
                except Exception as e:
                    print(f"  ❌ 従業員データクエリで例外: {e}")
                    print(f"  スタックトレース: {traceback.format_exc()}")
            
            print("🔍 ステップ3: LLM レスポンス取得")
            try:
                llm_response = get_llm_response(query)
                answer = llm_response.get('answer', '')
                print(f"  LLMレスポンス成功: 回答長 {len(answer)} 文字")
                
                # 管理者問い合わせメッセージが含まれているかチェック
                if "管理者にお問い合わせください" in answer:
                    print("  ❌ 管理者問い合わせメッセージが含まれています")
                    print(f"  回答内容: {answer}")
                else:
                    print("  ✅ 正常な回答")
                    
            except Exception as e:
                print(f"  ❌ LLMレスポンス取得で例外: {e}")
                print(f"  スタックトレース: {traceback.format_exc()}")
                
        except Exception as e:
            print(f"❌ 全体テストで例外: {e}")
            print(f"スタックトレース: {traceback.format_exc()}")

def test_pandas_agent_issues():
    """Pandas Agentの問題を特定"""
    print("\n" + "=" * 80)
    print("🔍 Pandas Agent 問題の調査")
    print("=" * 80)
    
    try:
        import pandas as pd
        from langchain_experimental.agents import create_pandas_dataframe_agent
        from langchain_openai import ChatOpenAI
        import constants as ct
        
        # CSVファイルを読み込み
        csv_file_path = './data/社員について/社員名簿.csv'
        df = pd.read_csv(csv_file_path, encoding='utf-8')
        print(f"✅ CSV読み込み成功: {len(df)} 行")
        
        # LLMオブジェクトを作成
        llm = ChatOpenAI(model_name=ct.MODEL, temperature=ct.TEMPERATURE)
        print("✅ LLMオブジェクト作成成功")
        
        # Pandas DataFrame Agentを作成
        agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=False,
            allow_dangerous_code=True,
            return_intermediate_steps=False
        )
        print("✅ Pandas DataFrame Agent作成成功")
        
        # 簡単なクエリでテスト
        test_prompt = "このデータフレームには何行のデータがありますか？"
        response = agent.invoke(test_prompt)
        print(f"✅ Agent実行成功: {response.get('output', 'No output')}")
        
    except Exception as e:
        print(f"❌ Pandas Agent テストで例外: {e}")
        print(f"スタックトレース: {traceback.format_exc()}")

def main():
    print("🚨 COMMON_ERROR_MESSAGE問題の詳細調査開始")
    
    # 1. 従業員クエリのデバッグテスト
    test_employee_query_with_debug()
    
    # 2. Pandas Agentの問題調査
    test_pandas_agent_issues()
    
    print("\n" + "=" * 80)
    print("🎯 調査結果")
    print("=" * 80)
    print("上記の結果から、COMMON_ERROR_MESSAGEが表示される原因を特定してください。")

if __name__ == "__main__":
    main()