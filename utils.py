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
# 真のRAG統合関数
############################################################

def create_csv_documents():
    """CSVデータをRAG用のドキュメント形式に変換"""
    from langchain.schema import Document
    
    try:
        csv_path = "./data/社員について/社員名簿.csv"
        if not os.path.exists(csv_path):
            return []
        
        df = pd.read_csv(csv_path, encoding='utf-8')
        documents = []
        
        # 各従業員をドキュメント化
        for index, row in df.iterrows():
            content = f"""従業員情報:
氏名: {row['氏名（フルネーム）']}
部署: {row['部署']}
役職: {row['役職']}
従業員区分: {row['従業員区分']}
スキルセット: {row['スキルセット']}
保有資格: {row['保有資格']}
年齢: {row['年齢']}歳
入社日: {row['入社日']}"""
            
            # メタデータに部署情報などを含める
            metadata = {
                "source": "社員名簿.csv",
                "type": "employee_data",
                "department": row['部署'],
                "name": row['氏名（フルネーム）'],
                "role": row['役職']
            }
            
            documents.append(Document(page_content=content, metadata=metadata))
        
        # 部署別サマリーも作成
        for dept in df['部署'].unique():
            dept_df = df[df['部署'] == dept]
            summary_content = f"""{dept}の概要:
所属人数: {len(dept_df)}名
主な役職: {', '.join(dept_df['役職'].unique())}
従業員区分: {', '.join(dept_df['従業員区分'].unique())}
            # 代表的なスキル: {', '.join(list(set([skill for skills in dept_df['スキルセット'].dropna().str.split(', ') for skill in skills]))[:10])}"""
            
            metadata = {
                "source": f"{dept}_概要",
                "type": "department_summary", 
                "department": dept
            }
            
            documents.append(Document(page_content=summary_content, metadata=metadata))
        
        return documents
        
    except Exception as e:
        print(f"CSV文書化エラー: {e}")
        return []

def format_search_results(retrieved_docs, query):
    """検索結果を動的にフォーマット - ファイルパスとページ数を含む表示"""
    if not retrieved_docs:
        return "関連する情報が見つかりませんでした。"
    
    # 従業員データが含まれているかチェック
    employee_docs = [doc for doc in retrieved_docs if doc.metadata.get("type") == "employee_data"]
    dept_summary_docs = [doc for doc in retrieved_docs if doc.metadata.get("type") == "department_summary"]
    other_docs = [doc for doc in retrieved_docs if doc.metadata.get("type") not in ["employee_data", "department_summary"]]
    
    result = ""
    
    # 従業員データがある場合はテーブル形式で表示
    if employee_docs:
        result += "**関連する従業員情報:**\n\n"
        
        # 簡潔なテーブル形式
        table_data = []
        for doc in employee_docs[:10]:  # 最大10件
            lines = doc.page_content.split('\n')
            name = lines[1].replace('氏名: ', '') if len(lines) > 1 else "不明"
            dept = lines[2].replace('部署: ', '') if len(lines) > 2 else "不明"
            role = lines[3].replace('役職: ', '') if len(lines) > 3 else "不明"
            table_data.append(f"| {name} | {dept} | {role} |")
        
        if table_data:
            result += "| 氏名 | 部署 | 役職 |\n|------|------|------|\n"
            result += "\n".join(table_data) + "\n\n"
        
        # 従業員データのソース表示
        result += "**データソース:**\n"
        result += f"📊 data/社員について/社員名簿.csv\n\n"
    
    # 部署概要がある場合
    if dept_summary_docs:
        result += "**部署概要:**\n\n"
        for doc in dept_summary_docs:
            result += doc.page_content + "\n\n"
    
    # 他の文書ファイル情報 - ファイルパスとページ数を表示
    if other_docs:
        result += "**入力内容に関する情報は、以下のファイルに含まれている可能性があります:**\n\n"
        
        # 重複チェック用
        displayed_sources = set()
        
        for doc in other_docs[:5]:  # 最大5件
            source = doc.metadata.get('source', '不明なソース')
            page = doc.metadata.get('page')
            
            # 重複を避ける
            source_key = f"{source}_{page}" if page else source
            if source_key in displayed_sources:
                continue
            displayed_sources.add(source_key)
            
            # ファイルパス表示
            if source.endswith('.pdf') and page:
                file_display = f"📄 {source} (ページNo.{page})"
            else:
                file_display = f"📄 {source}"
            
            result += f"{file_display}\n"
        
        result += "\n**その他、ファイルありかの候補を提示します:**\n\n"
    
    return result

# 従来の個別従業員検索関数は削除
# 全てRAGで統一処理するため不要

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

def format_pdf_reference(file_path, page_number=None):
    """PDFファイルのページ数を含む参照形式を生成"""
    if file_path.endswith('.pdf') and page_number:
        return f"{file_path} (ページNo.{page_number})"
    else:
        return file_path

def build_error_message(error_message):
    """エラーメッセージを整形して返す"""
    return f"{ct.ERROR_ICON} **エラーが発生しました**\n\n{error_message}\n\n{ct.COMMON_ERROR_MESSAGE}"

def get_llm_response(chat_message):
    """LLMから回答を生成する（真のRAGアプローチ）"""
    try:
        # 統一RAGアプローチ: 全てのクエリを同じ方法で処理
        # キーワード判定は廃止し、RAGの自然な検索に任せる
        
        # 真のRAG処理: 全データを統合検索
        llm = ChatOpenAI(model_name=ct.MODEL, temperature=ct.TEMPERATURE)
        
        # RAGリトリーバーの取得（緊急修正: フォールバック強化）
        retriever = None
        try:
            # Streamlit環境での取得を試行
            if hasattr(st, 'session_state') and hasattr(st.session_state, 'retriever'):
                retriever = st.session_state.retriever
            
            # retrieverがNoneの場合、緊急初期化を試行
            if retriever is None:
                print("⚠️ retriever が None です。緊急初期化を試行...")
                from initialize_ultra_lite import initialize_retriever
                retriever = initialize_retriever()
                
                # 初期化成功時はsession_stateに保存
                if retriever and hasattr(st, 'session_state'):
                    st.session_state.retriever = retriever
                    print("✅ retriever 緊急初期化成功")
                    
        except Exception as e:
            print(f"Retriever取得エラー: {e}")
            retriever = None
        
        if retriever is None:
            # リトリーバーが利用できない場合のフォールバック
            try:
                chat_history = st.session_state.chat_history if hasattr(st, 'session_state') and hasattr(st.session_state, 'chat_history') else []
            except Exception:
                chat_history = []
            
            messages = [
                SystemMessage(content="あなたは社内情報に詳しいアシスタントです。質問に丁寧に回答してください。"),
                HumanMessage(content=chat_message)
            ]
            
            response = llm.invoke(messages)
            
            try:
                if hasattr(st, 'session_state') and hasattr(st.session_state, 'chat_history'):
                    st.session_state.chat_history.extend([HumanMessage(content=chat_message), response.content])
            except Exception:
                pass
            
            return {
                "answer": response.content + "\n\n⚠️ **緊急モード**: 文書検索機能が一時的に利用できません。管理者に連絡してください。",
                "context": []
            }
        
        # RAG検索実行
        try:
            retrieved_docs = retriever.invoke(chat_message)
            
            # 結果の動的フォーマット
            formatted_results = format_search_results(retrieved_docs, chat_message)
            
            # LLMによる統合回答生成
            context_text = "\n\n".join([doc.page_content for doc in retrieved_docs[:5]])  # 上位5件
            
            system_prompt = """あなたは社内情報検索アシスタントです。
提供された情報を基に、ユーザーの質問に正確で有用な回答を提供してください。
従業員情報がある場合は表形式で整理し、文書情報がある場合は要点をまとめてください。"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"質問: {chat_message}\n\n検索結果:\n{context_text}\n\n上記の情報を基に回答してください。")
            ]
            
            response = llm.invoke(messages)
            
            # 会話履歴に追加
            try:
                if hasattr(st, 'session_state') and hasattr(st.session_state, 'chat_history'):
                    st.session_state.chat_history.extend([HumanMessage(content=chat_message), response.content])
            except Exception:
                pass
            
            return {
                "answer": response.content,
                "context": retrieved_docs,
                "mode": ct.ANSWER_MODE_1 if hasattr(st, 'session_state') and st.session_state.get("mode") == ct.ANSWER_MODE_1 else ct.ANSWER_MODE_2
            }
            
        except Exception as rag_error:
            # RAG処理エラーの場合のフォールバック
            fallback_message = f"⚠️ 検索処理中にエラーが発生しました: {str(rag_error)}\n\n基本的な応答機能で対応します。"
            
            messages = [
                SystemMessage(content="あなたは社内情報アシスタントです。"),
                HumanMessage(content=chat_message)
            ]
            
            try:
                response = llm.invoke(messages)
                return {
                    "answer": response.content + f"\n\n{fallback_message}",
                    "context": []
                }
            except Exception:
                return {
                    "answer": fallback_message,
                    "context": []
                }

    except Exception as e:
        error_message = f"LLM応答生成中にエラーが発生しました: {str(e)}"
        return {"answer": build_error_message(error_message)}