"""
テスト用の軽量初期化処理
"""

from __future__ import annotations

import os
import logging
from uuid import uuid4
import streamlit as st
from dotenv import load_dotenv
import constants as ct

# 「.env」ファイルで定義した環境変数の読み込み
load_dotenv()

def initialize_minimal():
    """
    最小限の初期化処理（テスト用）
    """
    print("🔧 最小限の初期化処理を開始...")
    
    # セッション状態の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_history = []
    
    # セッションID生成
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid4().hex
    
    # ダミーのretrieverを設定（実際の検索機能は無効）
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
        
    print("✅ 最小限の初期化処理完了")