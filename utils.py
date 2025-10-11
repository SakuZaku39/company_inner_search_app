"""
Streamlit Cloud用の軽量版 utils.py
langchain_experimental を使わずに従業員検索を実装
"""

from __future__ import annotations

############################################################
# ライブラリの読み込み
############################################################
import os
import pandas as pd
import re
from dotenv import load_dotenv
import streamlit as st
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
import constants as ct
from typing import Optional
from tabulate import tabulate

############################################################
# 設定関連
############################################################
# 「.env」ファイルで定義した環境変数の読み込み
load_dotenv()

############################################################
# 従業員検索関数（軽量版）
############################################################

def detect_employee_query(query: str) -> bool:
    """従業員データに関するクエリかどうかを判定（厳密版）"""
    
    # 文書検索を明確に示すキーワード（従業員情報検索と区別）
    document_keywords = [
        "議事録", "MTG", "会議", "ミーティング", "資料", "文書", "ファイル",
        "方針", "政策", "戦略", "計画", "プロジェクト", "取り組み"
    ]
    
    # 明確な文書検索キーワードがある場合は従業員検索ではない
    if any(keyword in query for keyword in document_keywords):
        return False
    
    # 「について」や「に関する」があっても、従業員情報を求める文脈なら従業員検索
    # 例: "人事部について教えて" → 文書検索、"人事部の従業員について一覧化" → 従業員検索
    contextual_keywords = ["について", "に関する", "関連", "情報", "内容", "詳細", "説明"]
    
    # 従業員関連のキーワードと文脈キーワードの組み合わせをチェック
    employee_terms = ["従業員", "社員", "スタッフ", "名簿", "一覧"]
    has_employee_context = any(emp_term in query for emp_term in employee_terms)
    has_contextual_keyword = any(keyword in query for keyword in contextual_keywords)
    
    # 従業員関連の文脈がない場合のみ、文脈キーワードで文書検索と判定
    if has_contextual_keyword and not has_employee_context:
        return False
    
    # 従業員情報を明確に求めるキーワード（より厳密に）
    employee_direct_keywords = [
        "従業員一覧", "社員一覧", "スタッフ一覧", "人事部一覧", "営業部一覧", 
        "開発部一覧", "経理部一覧", "マーケティング部一覧",
        "従業員名簿", "社員名簿", "名簿",
        "人数", "何人", "何名"
    ]
    
    # 従業員情報 + 動作の組み合わせ（一覧化、表示、抽出など）  
    employee_action_patterns = [
        "従業員.*一覧", "社員.*一覧", "スタッフ.*一覧",
        "従業員.*表示", "社員.*表示", "スタッフ.*表示",
        "従業員.*抽出", "社員.*抽出", "スタッフ.*抽出",
        "従業員情報.*一覧化", "社員情報.*一覧化", "スタッフ情報.*一覧化",
        "人事部.*従業員", "営業部.*従業員", "開発部.*従業員", "経理部.*従業員", "マーケティング部.*従業員",
        "人事部.*社員", "営業部.*社員", "開発部.*社員", "経理部.*社員", "マーケティング部.*社員",
        ".*部.*所属.*従業員", ".*部.*所属.*社員", ".*部.*所属.*スタッフ",
        ".*従業員情報.*一覧", ".*社員情報.*一覧", ".*スタッフ情報.*一覧"
    ]
    
    # 明確な従業員検索キーワードがあるかチェック
    has_direct_keyword = any(keyword in query for keyword in employee_direct_keywords)
    
    # 従業員と動作の組み合わせパターンがあるかチェック
    import re
    has_employee_action = any(re.search(pattern, query) for pattern in employee_action_patterns)
    
    return has_direct_keyword or has_employee_action

def simple_employee_search(query: str) -> dict:
    """シンプルな従業員検索（Pandas Agentを使わない版）"""
    try:
        # CSVファイルの読み込み
        csv_path = "./data/社員について/社員名簿.csv"
        if not os.path.exists(csv_path):
            return {
                "answer": "従業員データファイルが見つかりません。",
                "success": False
            }
        
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # クエリから部署を抽出
        departments = ["人事部", "営業部", "開発部", "経理部", "マーケティング部"]
        found_dept = None
        for dept in departments:
            if dept.replace("部", "") in query or dept in query:
                found_dept = dept
                break
        
        # 役職を抽出
        positions = ["部長", "課長", "主任", "マネージャー", "リーダー", "チーフ", "スタッフ"]
        found_position = None
        for pos in positions:
            if pos in query:
                found_position = pos
                break
        
        # データフィルタリング
        filtered_df = df.copy()
        
        if found_dept:
            filtered_df = filtered_df[filtered_df['部署'] == found_dept]
        
        if found_position:
            if found_position == "スタッフ":
                # スタッフの場合は管理職以外
                management_positions = ["部長", "課長", "主任", "マネージャー", "リーダー", "チーフ"]
                filtered_df = filtered_df[~filtered_df['役職'].isin(management_positions)]
            else:
                filtered_df = filtered_df[filtered_df['役職'] == found_position]
        
        if filtered_df.empty:
            # 該当データがない場合のフォールバック
            if found_dept:
                dept_df = df[df['部署'] == found_dept]
                if not dept_df.empty:
                    table = tabulate(dept_df, headers='keys', tablefmt='pipe', showindex=False)
                    return {
                        "answer": f"**{found_dept}の従業員一覧**\n\n{table}\n\n※ 特定の役職が見つからなかったため、部署全体の情報を表示しています。",
                        "success": True
                    }
            
            return {
                "answer": "該当する従業員が見つかりませんでした。検索条件を変更してお試しください。",
                "success": False
            }
        
        # 結果をテーブル形式で整形
        table = tabulate(filtered_df, headers='keys', tablefmt='pipe', showindex=False)
        
        result_text = f"**検索結果: {len(filtered_df)}件**\n\n{table}"
        
        if found_dept:
            result_text += f"\n\n📊 **{found_dept}** の検索結果"
        if found_position:
            result_text += f"\n🏷️ **{found_position}** で絞り込み"
            
        return {
            "answer": result_text,
            "success": True
        }
        
    except Exception as e:
        return {
            "answer": f"従業員検索でエラーが発生しました: {str(e)}",
            "success": False
        }

def query_employee_data(query: str) -> dict:
    """従業員データクエリのメイン関数"""
    return simple_employee_search(query)

############################################################
# 既存の関数群（変更なし）
############################################################

def get_source_icon(source):
    """メッセージと一緒に表示するアイコンの種類を取得"""
    if source.startswith("http"):
        icon = ct.LINK_SOURCE_ICON
    else:
        icon = ct.DOC_SOURCE_ICON
    return icon

def build_error_message(error_message):
    """エラーメッセージを整形して返す"""
    return f"{ct.ERROR_ICON} **エラーが発生しました**\n\n{error_message}\n\n{ct.COMMON_ERROR_MESSAGE}"

def get_llm_response(chat_message):
    """LLMから回答を生成する"""
    try:
        # 従業員データに関するクエリかどうかを判定
        if detect_employee_query(chat_message):
            # 従業員データに対するクエリを実行
            employee_response = query_employee_data(chat_message)
            # 会話履歴に追加（Streamlitセッションが利用可能な場合のみ）
            try:
                if hasattr(st, 'session_state') and hasattr(st.session_state, 'chat_history'):
                    st.session_state.chat_history.extend([
                        HumanMessage(content=chat_message), 
                        employee_response["answer"]
                    ])
            except Exception:
                pass
            return employee_response
        
        # 軽量版LLM処理（RAG機能なし）
        try:
            llm = ChatOpenAI(model_name=ct.MODEL, temperature=ct.TEMPERATURE)

            # モードに応じたプロンプト選択
            try:
                current_mode = st.session_state.mode if hasattr(st, 'session_state') and hasattr(st.session_state, 'mode') else ct.ANSWER_MODE_2
            except Exception:
                current_mode = ct.ANSWER_MODE_2

            if current_mode == ct.ANSWER_MODE_1:
                system_prompt = ct.SYSTEM_PROMPT_DOC_SEARCH
            else:
                system_prompt = ct.SYSTEM_PROMPT_INQUIRY
            
            # LangChain互換のメッセージフォーマットを使用
            from langchain.schema import SystemMessage, HumanMessage as LCHumanMessage
            
            messages = [SystemMessage(content=system_prompt)]
            
            # 会話履歴を取得
            try:
                chat_history = st.session_state.chat_history if hasattr(st, 'session_state') and hasattr(st.session_state, 'chat_history') else []
            except Exception:
                chat_history = []

            # 過去の会話履歴を追加（最新の4つまで）
            if chat_history:
                for i, msg in enumerate(chat_history[-8:]):  # 最新8件（ユーザー4+アシスタント4）
                    if i % 2 == 0:  # 偶数番目はユーザーメッセージ
                        content = str(msg.content) if hasattr(msg, 'content') else str(msg)
                        messages.append(LCHumanMessage(content=content))
                    else:  # 奇数番目はアシスタントメッセージ
                        from langchain.schema import AIMessage
                        content = str(msg)
                        messages.append(AIMessage(content=content))
            
            # 現在のメッセージを追加
            messages.append(LCHumanMessage(content=chat_message))

            # LLM応答取得
            response = llm.invoke(messages)

            # LLMレスポンスを会話履歴に追加
            try:
                if hasattr(st, 'session_state') and hasattr(st.session_state, 'chat_history'):
                    st.session_state.chat_history.extend([HumanMessage(content=chat_message), response.content])
            except Exception:
                pass

            return {
                "answer": response.content,
                "context": []
            }
            
        except Exception as llm_error:
            # LLM処理でエラーが発生した場合の詳細エラーハンドリング
            error_details = str(llm_error)
            
            # よくあるエラーの場合は、より具体的な対処法を提示
            if "rate limit" in error_details.lower():
                fallback_message = "⚠️ OpenAI APIの利用制限に達しました。しばらく時間をおいてから再度お試しください。"
            elif "authentication" in error_details.lower() or "api key" in error_details.lower():
                fallback_message = "⚠️ OpenAI APIキーの認証に失敗しました。管理者にお問い合わせください。"
            elif "connection" in error_details.lower() or "network" in error_details.lower():
                fallback_message = "⚠️ ネットワーク接続に問題があります。インターネット接続を確認してください。"
            else:
                fallback_message = f"⚠️ AI応答の生成中にエラーが発生しました。\n\n詳細: {error_details}\n\n従業員情報の検索は引き続き利用可能です。"
            
            return {
                "answer": fallback_message,
                "context": []
            }

    except Exception as e:
        error_message = f"LLM応答生成中にエラーが発生しました: {str(e)}"
        return {"answer": build_error_message(error_message)}