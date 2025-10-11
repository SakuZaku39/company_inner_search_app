"""
Streamlit Cloud 超安定版初期化
ベクトルストアを使わない軽量実装
"""

from __future__ import annotations

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from uuid import uuid4
import streamlit as st
import constants as ct
from dotenv import load_dotenv

# 「.env」ファイルで定義した環境変数の読み込み
load_dotenv()

def initialize():
    """
    画面読み込み時に実行する初期化処理（超軽量版）
    """
    initialize_session_state()
    initialize_session_id()
    initialize_logger()
    # ベクトルストアは初期化しない（エラー回避）
    st.session_state.retriever = None


def initialize_logger():
    """
    ログ出力の設定（簡素版）
    """
    try:
        os.makedirs(ct.LOG_DIR_PATH, exist_ok=True)
        logger = logging.getLogger(ct.LOGGER_NAME)
        
        if logger.hasHandlers():
            return

        log_handler = TimedRotatingFileHandler(
            os.path.join(ct.LOG_DIR_PATH, ct.LOG_FILE),
            when="D",
            encoding="utf8"
        )
        
        formatter = logging.Formatter(
            f"[%(levelname)s] %(asctime)s session_id={st.session_state.session_id}: %(message)s"
        )
        
        log_handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(log_handler)
        
    except Exception:
        # ログ初期化に失敗してもアプリは動作させる
        pass


def initialize_session_id():
    """
    セッションIDの作成
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid4().hex


def initialize_session_state():
    """
    初期化データの用意
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_history = []


def initialize_retriever():
    """
    RAG統合版リトリーバー初期化（CSV統合）
    """
    try:
        # CSVデータをドキュメント化
        from utils import create_csv_documents
        csv_docs = create_csv_documents()
        
        if csv_docs:
            # 簡易RAG: CSVドキュメントのみでベクトルストア作成
            from langchain_openai import OpenAIEmbeddings
            from langchain.vectorstores import FAISS
            
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_documents(csv_docs, embeddings)
            return vectorstore.as_retriever(search_kwargs={"k": 5})
        else:
            return None
            
    except Exception as e:
        # 初期化失敗時はNoneを返す
        print(f"RAG初期化失敗: {e}")
        return None