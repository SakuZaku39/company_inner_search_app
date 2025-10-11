"""
Streamlit Cloud用の初期化ファイル（軽量版）
ベクトルストアなしでも動作する設定
"""

import os
import streamlit as st
from typing import Optional

def initialize_retriever_lightweight():
    """
    軽量版リトリーバー初期化
    ベクトルストアの問題を回避
    """
    try:
        # ダミーリトリーバーを返す（エラー回避）
        return None
    except Exception as e:
        st.error(f"リトリーバー初期化エラー: {e}")
        return None

def initialize_app_lightweight():
    """
    軽量版アプリ初期化
    """
    try:
        # セッション状態の初期化
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        if "mode" not in st.session_state:
            st.session_state.mode = "社内問い合わせ"
        
        if "retriever" not in st.session_state:
            st.session_state.retriever = initialize_retriever_lightweight()
        
        return True
    except Exception as e:
        st.error(f"アプリ初期化エラー: {e}")
        return False