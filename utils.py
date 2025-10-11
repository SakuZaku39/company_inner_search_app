"""
このファイルは、画面表示以外の様々な関数定義のファイルです。
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
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_experimental.agents import create_pandas_dataframe_agent
import constants as ct
from typing import Optional  # 修正点: PDF参照表示の共通関数化のためのtype hint追加


############################################################
# 設定関連
############################################################
# 「.env」ファイルで定義した環境変数の読み込み
load_dotenv()


############################################################
# 関数定義
############################################################

def get_source_icon(source):
    """
    メッセージと一緒に表示するアイコンの種類を取得

    Args:
        source: 参照元のありか

    Returns:
        メッセージと一緒に表示するアイコンの種類
    """
    # 参照元がWebページの場合とファイルの場合で、取得するアイコンの種類を変える
    if source.startswith("http"):
        icon = ct.LINK_SOURCE_ICON
    else:
        icon = ct.DOC_SOURCE_ICON
    
    return icon


def format_pdf_reference(file_path: str, page_number: Optional[int] = None) -> str:
    """
    PDF参照表示の共通関数（修正点: PDFファイルのページ番号付き表示を統一化）
    
    Args:
        file_path: ファイルパス
        page_number: ページ番号（オプション）
    
    Returns:
        フォーマットされた参照文字列
        
    Examples:
        >>> format_pdf_reference("data/document.pdf", 23)
        "data/document.pdf (ページNo.23)"
        
        >>> format_pdf_reference("data/document.pdf", None)
        "data/document.pdf"
        
        >>> format_pdf_reference("data/document.docx", 5)
        "data/document.docx"
    """
    # 修正点: PDFファイルかつページ番号が存在する場合、(ページNo.XX)形式で表示
    if file_path.lower().endswith('.pdf') and page_number is not None:
        return f"{file_path} (ページNo.{page_number})"
    return file_path


def build_error_message(message):
    """
    エラーメッセージと管理者問い合わせテンプレートの連結

    Args:
        message: 画面上に表示するエラーメッセージ

    Returns:
        エラーメッセージと管理者問い合わせテンプレートの連結テキスト
    """
    return "\n".join([message, ct.COMMON_ERROR_MESSAGE])


def detect_employee_query(chat_message):
    """
    従業員情報に関するクエリかどうかを判定
    
    Args:
        chat_message: ユーザー入力値
    
    Returns:
        bool: 従業員情報クエリの場合True
    """
    employee_keywords = [
        "従業員", "社員", "スタッフ", "人事部", "営業部", "IT部", "経理部", "総務部", "マーケティング部",
        "一覧", "リスト", "名簿", "所属", "部署", "役職", "マネージャー", "主任", "アシスタント"
    ]
    
    return any(keyword in chat_message for keyword in employee_keywords)


def query_employee_data(chat_message):
    """
    従業員データに対する自然言語クエリを実行
    
    Args:
        chat_message: ユーザー入力値
    
    Returns:
        dict: クエリ結果とメタデータ
    """
    csv_file_path = './data/社員について/社員名簿.csv'
    
    if not os.path.exists(csv_file_path):
        return {
            "answer": "社員名簿ファイルが見つかりません。管理者にお問い合わせください。",
            "context": [],
            "source_documents": []
        }
    
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(csv_file_path, encoding='utf-8')
        
        # 部署名の検出と直接フィルタリング
        answer = ""
        filtered_df = None
        
        # 特定の部署名での絞り込みを確認
        departments = ["人事部", "営業部", "IT部", "経理部", "総務部", "マーケティング部"]
        for dept in departments:
            if dept in chat_message:
                filtered_df = df[df['部署'] == dept]
                break
        
        # 役職での絞り込み
        positions = ["マネージャー", "主任", "アシスタント", "スタッフ", "インターン"]
        department_filtered_df = filtered_df  # 部署フィルタ結果を保存
        
        if filtered_df is not None:
            for pos in positions:
                if pos in chat_message:
                    role_filtered_df = filtered_df[filtered_df['役職'] == pos]
                    if len(role_filtered_df) > 0:
                        filtered_df = role_filtered_df
                    else:
                        # 該当する役職がない場合は、その旨を明記して部署全体を表示
                        answer = f"## 検索結果: 「{pos}」の役職は{filtered_df.iloc[0]['部署']}に存在しません\n\n"
                        answer += f"代わりに、{filtered_df.iloc[0]['部署']}の全従業員({len(filtered_df)}名)を表示します:\n\n"
                        
                        # 部署の役職分布を表示
                        role_counts = filtered_df['役職'].value_counts()
                        answer += "**役職分布:**\n"
                        for role, count in role_counts.items():
                            answer += f"- {role}: {count}名\n"
                        answer += "\n"
                        
                        # 表形式で全従業員を表示
                        display_columns = ['社員ID', '氏名（フルネーム）', '性別', '年齢', '従業員区分', '部署', '役職', '入社日']
                        display_df = filtered_df[display_columns]
                        answer += display_df.to_markdown(index=False)
                        
                        return {
                            "answer": answer,
                            "context": [],
                            "source_documents": [
                                type('MockDoc', (), {
                                    'page_content': f'社員データベース検索結果（役職「{pos}」が存在しないため部署全体を表示）',
                                    'metadata': {'source': csv_file_path}
                                })()
                            ]
                        }
                    break
        
        # 結果が見つかった場合
        if filtered_df is not None and len(filtered_df) > 0:
            # 表形式での表示
            answer = f"## 検索結果: {len(filtered_df)}名の従業員が見つかりました\n\n"
            
            # 主要なカラムのみを表示
            display_columns = ['社員ID', '氏名（フルネーム）', '性別', '年齢', '従業員区分', '部署', '役職', '入社日']
            display_df = filtered_df[display_columns]
            
            # markdown表形式で表示
            answer += display_df.to_markdown(index=False)
            
            # 追加情報（スキルセットなど）が必要な場合
            if "スキル" in chat_message or "資格" in chat_message:
                answer += "\n\n### 詳細情報（スキルセット・資格）\n"
                for idx, row in filtered_df.iterrows():
                    answer += f"\n**{row['氏名（フルネーム）']}**\n"
                    answer += f"- スキルセット: {row['スキルセット']}\n"
                    answer += f"- 保有資格: {row['保有資格']}\n"
        
        else:
            # DataFrame Agentによる高度な検索
            try:
                # LLMオブジェクトを作成
                llm = ChatOpenAI(model_name=ct.MODEL, temperature=ct.TEMPERATURE)
                
                # Pandas DataFrame Agentを作成
                agent = create_pandas_dataframe_agent(
                    llm,
                    df,
                    verbose=False,
                    allow_dangerous_code=True,
                    return_intermediate_steps=False
                )
                
                # エージェント用のプロンプトを構築
                enhanced_prompt = f"""
あなたは社員データベースの専門家です。以下のデータフレームには社員情報が含まれています。
データフレームのカラムは以下の通りです：
{list(df.columns)}

ユーザーの質問: {chat_message}

以下の点に注意して回答してください：
1. 可能な限り具体的で詳細な回答を提供する
2. 該当する社員がいる場合は、名前、部署、役職などの主要情報を含める
3. 一覧表示の場合は、見やすい形式で整理して表示する
4. 該当するデータがない場合は、その旨を明確に伝える
5. 日本語で自然な文章で回答する

回答は必ず日本語で行い、データに基づいた正確な情報のみを提供してください。
"""
                
                # エージェントにクエリを実行
                response = agent.invoke(enhanced_prompt)
                answer = response.get('output', '申し訳ございませんが、回答を生成できませんでした。')
                
            except Exception as agent_error:
                answer = f"高度な検索でエラーが発生しました: {str(agent_error)}\n\n基本的な検索を実行します。"
                # 基本的な検索にフォールバック
                if "一覧" in chat_message or "リスト" in chat_message:
                    answer += f"\n\n## 全従業員一覧（{len(df)}名）\n\n"
                    display_columns = ['社員ID', '氏名（フルネーム）', '部署', '役職']
                    answer += df[display_columns].to_markdown(index=False)
        
        return {
            "answer": answer,
            "context": [],
            "source_documents": [
                type('MockDoc', (), {
                    'page_content': f'社員データベース検索結果（社員名簿.csv）',
                    'metadata': {'source': csv_file_path}
                })()
            ]
        }
        
    except Exception as e:
        return {
            "answer": f"従業員データの検索中にエラーが発生しました: {str(e)}",
            "context": [],
            "source_documents": []
        }


def get_llm_response(chat_message):
    """
    LLMからの回答取得

    Args:
        chat_message: ユーザー入力値

    Returns:
        LLMからの回答
    """
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
            # セッション状態が利用できない場合は無視（デバッグ時など）
            pass
        return employee_response
    
    # 通常のRAG処理
    # LLMのオブジェクトを用意
    llm = ChatOpenAI(model_name=ct.MODEL, temperature=ct.TEMPERATURE)

    # 会話履歴なしでもLLMに理解してもらえる、独立した入力テキストを取得するためのプロンプトテンプレートを作成
    question_generator_template = ct.SYSTEM_PROMPT_CREATE_INDEPENDENT_TEXT
    question_generator_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", question_generator_template),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    # モードによってLLMから回答を取得する用のプロンプトを変更
    try:
        current_mode = st.session_state.mode if hasattr(st, 'session_state') and hasattr(st.session_state, 'mode') else ct.ANSWER_MODE_2
    except Exception:
        current_mode = ct.ANSWER_MODE_2  # デフォルトは「社内問い合わせ」モード
    
    if current_mode == ct.ANSWER_MODE_1:
        # モードが「社内文書検索」の場合のプロンプト
        question_answer_template = ct.SYSTEM_PROMPT_DOC_SEARCH
    else:
        # モードが「社内問い合わせ」の場合のプロンプト
        question_answer_template = ct.SYSTEM_PROMPT_INQUIRY
    # LLMから回答を取得する用のプロンプトテンプレートを作成
    question_answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", question_answer_template),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    # 会話履歴なしでもLLMに理解してもらえる、独立した入力テキストを取得するためのRetrieverを作成
    try:
        retriever = st.session_state.retriever if hasattr(st, 'session_state') and hasattr(st.session_state, 'retriever') else None
    except Exception:
        retriever = None
    
    if retriever is None:
        # リトリーバーが利用できない場合は初期化を試行
        from initialize import initialize_retriever
        retriever = initialize_retriever()
    
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, question_generator_prompt
    )

    # LLMから回答を取得する用のChainを作成
    question_answer_chain = create_stuff_documents_chain(llm, question_answer_prompt)
    # 「RAG x 会話履歴の記憶機能」を実現するためのChainを作成
    chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # チャット履歴を取得（セッション状態が利用可能な場合）
    try:
        chat_history = st.session_state.chat_history if hasattr(st, 'session_state') and hasattr(st.session_state, 'chat_history') else []
    except Exception:
        chat_history = []
    
    # LLMへのリクエストとレスポンス取得
    llm_response = chain.invoke({"input": chat_message, "chat_history": chat_history})
    
    # LLMレスポンスを会話履歴に追加（セッション状態が利用可能な場合のみ）
    try:
        if hasattr(st, 'session_state') and hasattr(st.session_state, 'chat_history'):
            st.session_state.chat_history.extend([HumanMessage(content=chat_message), llm_response["answer"]])
    except Exception:
        # セッション状態が利用できない場合は無視（デバッグ時など）
        pass

    return llm_response