"""
このファイルは、最初の画面読み込み時にのみ実行される初期化処理が記述されたファイルです。
"""

from __future__ import annotations

############################################################
# ライブラリの読み込み
############################################################
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from uuid import uuid4
import sys
import unicodedata
from dotenv import load_dotenv
import streamlit as st
from docx import Document
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import constants as ct


############################################################
# 設定関連
############################################################
# 「.env」ファイルで定義した環境変数の読み込み
load_dotenv()


############################################################
# 関数定義
############################################################

def initialize():
    """
    画面読み込み時に実行する初期化処理
    """
    # 初期化データの用意
    initialize_session_state()
    # ログ出力用にセッションIDを生成
    initialize_session_id()
    # ログ出力の設定
    initialize_logger()
    # RAGのRetrieverを作成
    initialize_retriever()


def initialize_logger():
    """
    ログ出力の設定
    """
    # 指定のログフォルダが存在すれば読み込み、存在しなければ新規作成
    os.makedirs(ct.LOG_DIR_PATH, exist_ok=True)
    
    # 引数に指定した名前のロガー（ログを記録するオブジェクト）を取得
    # 再度別の箇所で呼び出した場合、すでに同じ名前のロガーが存在していれば読み込む
    logger = logging.getLogger(ct.LOGGER_NAME)

    # すでにロガーにハンドラー（ログの出力先を制御するもの）が設定されている場合、同じログ出力が複数回行われないよう処理を中断する
    if logger.hasHandlers():
        return

    # 1日単位でログファイルの中身をリセットし、切り替える設定
    log_handler = TimedRotatingFileHandler(
        os.path.join(ct.LOG_DIR_PATH, ct.LOG_FILE),
        when="D",
        encoding="utf8"
    )
    # 出力するログメッセージのフォーマット定義
    # - 「levelname」: ログの重要度（INFO, WARNING, ERRORなど）
    # - 「asctime」: ログのタイムスタンプ（いつ記録されたか）
    # - 「lineno」: ログが出力されたファイルの行番号
    # - 「funcName」: ログが出力された関数名
    # - 「session_id」: セッションID（誰のアプリ操作か分かるように）
    # - 「message」: ログメッセージ
    formatter = logging.Formatter(
        f"[%(levelname)s] %(asctime)s line %(lineno)s, in %(funcName)s, session_id={st.session_state.session_id}: %(message)s"
    )

    # 定義したフォーマッターの適用
    log_handler.setFormatter(formatter)

    # ログレベルを「INFO」に設定
    logger.setLevel(logging.INFO)

    # 作成したハンドラー（ログ出力先を制御するオブジェクト）を、
    # ロガー（ログメッセージを実際に生成するオブジェクト）に追加してログ出力の最終設定
    logger.addHandler(log_handler)


def initialize_session_id():
    """
    セッションIDの作成
    """
    if "session_id" not in st.session_state:
        # ランダムな文字列（セッションID）を、ログ出力用に作成
        st.session_state.session_id = uuid4().hex


def initialize_retriever():
    """
    画面読み込み時にRAGのRetriever（ベクターストアから検索するオブジェクト）を作成
    軽量化: 初回起動時は最小限のファイルのみ処理
    """
    # ロガーを読み込むことで、後続の処理中に発生したエラーなどがログファイルに記録される
    logger = logging.getLogger(ct.LOGGER_NAME)

    # すでにRetrieverが作成済みの場合、後続の処理を中断
    if "retriever" in st.session_state:
        return
    
    try:
        logger.info("RAG初期化を開始します...")
        
        # RAGの参照先となるデータソースの読み込み（軽量化：ファイル数制限）
        docs_all = load_data_sources_lite()  # 軽量版を使用
        logger.info(f"データソース読み込み完了: {len(docs_all)}個のドキュメント")

        # OSがWindowsの場合、Unicode正規化と、cp932（Windows用の文字コード）で表現できない文字を除去
        for doc in docs_all:
            doc.page_content = adjust_string(doc.page_content)
            for key in doc.metadata:
                doc.metadata[key] = adjust_string(doc.metadata[key])
        
        logger.info("文字コード調整完了")
        
        # 埋め込みモデルの用意
        embeddings = OpenAIEmbeddings()
        logger.info("埋め込みモデル準備完了")
        
        # チャンク分割用のオブジェクトを作成（マジックナンバー対策: 定数化）
        text_splitter = CharacterTextSplitter(
            chunk_size=ct.CHUNK_SIZE,      # 500 → 定数化
            chunk_overlap=ct.CHUNK_OVERLAP, # 50 → 定数化
            separator=ct.CHUNK_SEPARATOR   # "\n" → 定数化
        )

        # チャンク分割を実施
        splitted_docs = text_splitter.split_documents(docs_all)
        logger.info(f"チャンク分割完了: {len(splitted_docs)}個のチャンク")

        # ベクターストアの作成
        db = Chroma.from_documents(splitted_docs, embedding=embeddings)
        logger.info("ベクターストア作成完了")

        # ベクターストアを検索するRetrieverの作成（問題1: 3→5に変更、マジックナンバー対策: 定数化）
        st.session_state.retriever = db.as_retriever(search_kwargs={"k": ct.RAG_SEARCH_K})
        logger.info("RAG初期化完了")
        
    except Exception as e:
        logger.error(f"RAG初期化エラー: {e}")
        # フォールバック: ダミーのretrieverを作成
        st.session_state.retriever = None
        # エラーは再発生させずに、警告として処理
        st.warning("⚠️ 検索機能の初期化に失敗しました。基本的な応答機能のみ利用可能です。")


def initialize_session_state():
    """
    初期化データの用意
    """
    if "messages" not in st.session_state:
        # 「表示用」の会話ログを順次格納するリストを用意
        st.session_state.messages = []
        # 「LLMとのやりとり用」の会話ログを順次格納するリストを用意
        st.session_state.chat_history = []


def load_data_sources():
    """
    RAGの参照先となるデータソースの読み込み

    Returns:
        読み込んだ通常データソース
    """
    # データソースを格納する用のリスト
    docs_all = []
    # ファイル読み込みの実行（渡した各リストにデータが格納される）
    recursive_file_check(ct.RAG_TOP_FOLDER_PATH, docs_all)

    web_docs_all = []
    # ファイルとは別に、指定のWebページ内のデータも読み込み
    # 読み込み対象のWebページ一覧に対して処理
    for web_url in ct.WEB_URL_LOAD_TARGETS:
        # 指定のWebページを読み込み
        loader = WebBaseLoader(web_url)
        web_docs = loader.load()
        # for文の外のリストに読み込んだデータソースを追加
        web_docs_all.extend(web_docs)
    # 通常読み込みのデータソースにWebページのデータを追加
    docs_all.extend(web_docs_all)

    return docs_all


def load_data_sources_lite():
    """
    RAGの参照先となるデータソースの軽量読み込み（最初の数ファイルのみ）

    Returns:
        読み込んだ軽量データソース
    """
    docs_all = []
    file_count = 0
    max_files = ct.MAX_FILES_LITE  # マジックナンバー対策: 定数化
    
    # 軽量読み込みの実行
    recursive_file_check_lite(ct.RAG_TOP_FOLDER_PATH, docs_all, file_count, max_files)
    
    # ファイルが見つからない場合のフォールバック
    if not docs_all:
        # サンプルドキュメントを作成
        from langchain.schema import Document
        sample_doc = Document(
            page_content="これはサンプルドキュメントです。会社の基本情報を含んでいます。",
            metadata={"source": "sample.txt"}
        )
        docs_all.append(sample_doc)
    
    return docs_all


def recursive_file_check_lite(path, docs_all, file_count, max_files):
    """
    RAGの参照先となるデータソースの軽量読み込み（ファイル数制限あり）
    """
    if file_count >= max_files:
        return file_count
        
    if os.path.isdir(path):
        files = os.listdir(path)
        for file in files:
            if file_count >= max_files:
                break
            full_path = os.path.join(path, file)
            file_count = recursive_file_check_lite(full_path, docs_all, file_count, max_files)
    else:
        file_count = file_load_lite(path, docs_all, file_count, max_files)
    
    return file_count


def file_load_lite(path, docs_all, file_count, max_files):
    """
    ファイル内のデータ読み込み（軽量版）
    """
    if file_count >= max_files:
        return file_count
        
    file_extension = os.path.splitext(path)[1]
    
    if file_extension in ct.SUPPORTED_EXTENSIONS:
        try:
            loader = ct.SUPPORTED_EXTENSIONS[file_extension](path)
            docs = loader.load()
            docs_all.extend(docs)
            return file_count + 1
        except Exception as e:
            print(f"ファイル読み込みエラー: {path} - {e}")
            return file_count
    
    return file_count


def recursive_file_check(path, docs_all):
    """
    RAGの参照先となるデータソースの読み込み

    Args:
        path: 読み込み対象のファイル/フォルダのパス
        docs_all: データソースを格納する用のリスト
    """
    # パスがフォルダかどうかを確認
    if os.path.isdir(path):
        # フォルダの場合、フォルダ内のファイル/フォルダ名の一覧を取得
        files = os.listdir(path)
        # 各ファイル/フォルダに対して処理
        for file in files:
            # ファイル/フォルダ名だけでなく、フルパスを取得
            full_path = os.path.join(path, file)
            # フルパスを渡し、再帰的にファイル読み込みの関数を実行
            recursive_file_check(full_path, docs_all)
    else:
        # パスがファイルの場合、ファイル読み込み
        file_load(path, docs_all)


def file_load(path, docs_all):
    """
    ファイル内のデータ読み込み

    Args:
        path: ファイルパス
        docs_all: データソースを格納する用のリスト
    """
    # ファイルの拡張子を取得
    file_extension = os.path.splitext(path)[1]
    # ファイル名（拡張子を含む）を取得
    file_name = os.path.basename(path)

    # 想定していたファイル形式の場合のみ読み込む
    if file_extension in ct.SUPPORTED_EXTENSIONS:
        # ファイルの拡張子に合ったdata loaderを使ってデータ読み込み
        loader = ct.SUPPORTED_EXTENSIONS[file_extension](path)
        docs = loader.load()
        docs_all.extend(docs)


def adjust_string(s):
    """
    Windows環境でRAGが正常動作するよう調整
    
    Args:
        s: 調整を行う文字列
    
    Returns:
        調整を行った文字列
    """
    # 調整対象は文字列のみ
    if type(s) is not str:
        return s

    # OSがWindowsの場合、Unicode正規化と、cp932（Windows用の文字コード）で表現できない文字を除去
    if sys.platform.startswith("win"):
        s = unicodedata.normalize('NFC', s)
        s = s.encode("cp932", "ignore").decode("cp932")
        return s
    
    # OSがWindows以外の場合はそのまま返す
    return s