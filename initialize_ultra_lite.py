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
    画面読み込み時に実行する初期化処理（RAG対応版）
    """
    initialize_session_state()
    initialize_session_id()
    initialize_logger()
    # RAGリトリーバーを初期化
    if "retriever" not in st.session_state:
        st.session_state.retriever = initialize_retriever()


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
    RAG統合版リトリーバー初期化（CSV+ファイル統合）
    """
    try:
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        import os
        
        all_documents = []
        
        # 1. CSVデータをドキュメント化
        from utils import create_csv_documents
        csv_docs = create_csv_documents()
        if csv_docs:
            all_documents.extend(csv_docs)
            print(f"CSV文書を統合: {len(csv_docs)}件")
        
        # 2. 社内文書ファイルを読み込み
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=ct.CHUNK_SIZE,
            chunk_overlap=ct.CHUNK_OVERLAP,
            separators=[ct.CHUNK_SEPARATOR]
        )
        
        # サポートされているファイル形式を読み込み
        for root, dirs, files in os.walk(ct.RAG_TOP_FOLDER_PATH):
            for file in files:
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file)[1].lower()
                
                if file_extension in ct.SUPPORTED_EXTENSIONS:
                    try:
                        # ファイル読み込み
                        loader = ct.SUPPORTED_EXTENSIONS[file_extension](file_path)
                        documents = loader.load()
                        
                        # テキスト分割
                        chunks = text_splitter.split_documents(documents)
                        
                        # メタデータにファイルパスを設定
                        for chunk in chunks:
                            chunk.metadata["source"] = file_path.replace("\\", "/")
                        
                        all_documents.extend(chunks)
                        
                    except Exception as e:
                        print(f"ファイル読み込みエラー {file_path}: {e}")
        
        print(f"総文書数: {len(all_documents)}件")
        
        # 3. ベクトルストア作成
        if all_documents:
            from langchain_community.vectorstores import FAISS
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_documents(all_documents, embeddings)
            return vectorstore.as_retriever(search_kwargs={"k": ct.RAG_SEARCH_K})
        else:
            print("読み込める文書が見つかりませんでした")
            return None
            
    except Exception as e:
        # 初期化失敗時はNoneを返す
        print(f"RAG初期化失敗: {e}")
        import traceback
        print(traceback.format_exc())
        return None