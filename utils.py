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
from langchain.schema import HumanMessage
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
    """従業員データに関するクエリかどうかを判定"""
    employee_keywords = [
        "従業員", "社員", "スタッフ", "人事", "営業", "開発", "経理", "マーケティング",
        "部長", "課長", "主任", "マネージャー", "リーダー", "チーフ",
        "人数", "一覧", "名前", "氏名", "職位", "役職", "部署"
    ]
    return any(keyword in query for keyword in employee_keywords)

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
        llm = ChatOpenAI(model_name=ct.MODEL, temperature=ct.TEMPERATURE)

        # シンプルなプロンプト構築
        system_prompt = ct.SYSTEM_PROMPT_INQUIRY
        
        try:
            chat_history = st.session_state.chat_history if hasattr(st, 'session_state') and hasattr(st.session_state, 'chat_history') else []
        except Exception:
            chat_history = []

        # 会話履歴を含めたメッセージ構築
        messages = [{"role": "system", "content": system_prompt}]
        
        # 過去の会話履歴を追加（最新の5つまで）
        if chat_history:
            for i, msg in enumerate(chat_history[-10:]):  # 最新10件
                if i % 2 == 0:  # 偶数番目はユーザーメッセージ
                    messages.append({"role": "user", "content": str(msg.content) if hasattr(msg, 'content') else str(msg)})
                else:  # 奇数番目はアシスタントメッセージ
                    messages.append({"role": "assistant", "content": str(msg)})
        
        # 現在のメッセージを追加
        messages.append({"role": "user", "content": chat_message})

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

    except Exception as e:
        error_message = f"LLM応答生成中にエラーが発生しました: {str(e)}"
        return {"answer": build_error_message(error_message)}