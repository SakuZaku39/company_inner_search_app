"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

from __future__ import annotations

############################################################
# 1. ライブラリの読み込み
############################################################
# 「.env」ファイルから環境変数を読み込むための関数
from dotenv import load_dotenv
# ログ出力を行うためのモジュール
import logging
# streamlitアプリの表示を担当するモジュール
import streamlit as st
# （自作）画面表示以外の様々な関数が定義されているモジュール
import utils
# （自作）アプリ起動時に実行される初期化処理が記述された関数
from initialize_ultra_lite import initialize  # 超軽量版を使用
# （自作）画面表示系の関数が定義されているモジュール
import components as cn
# （自作）変数（定数）がまとめて定義・管理されているモジュール
import constants as ct


############################################################
# 2. 設定関連
############################################################
# ブラウザタブの表示文言を設定
st.set_page_config(
    page_title=ct.APP_NAME
)

# ログ出力を行うためのロガーの設定
logger = logging.getLogger(ct.LOGGER_NAME)


############################################################
# 3. 初期化処理
############################################################
try:
    # 初期化処理（「initialize.py」の「initialize」関数を実行）
    initialize()
except Exception as e:
    # 詳細なエラー情報を追加
    import traceback
    error_details = traceback.format_exc()
    # エラーログの出力
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}\n{error_details}")
    # 詳細エラーメッセージの画面表示（デバッグ用）
    st.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n\n**エラー詳細（デバッグ用）:**\n```\n{str(e)}\n```", icon=ct.ERROR_ICON)
    # 詳細なトレースバック情報も表示
    st.code(error_details, language="python")
    # 後続の処理を中断
    st.stop()

# アプリ起動時のログファイルへの出力
if not "initialized" in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)


############################################################
# 4. 初期表示
############################################################
# 修正点: サイドバーナビゲーション表示（UI構成の分離）
cn.display_sidebar_navigation()

# AIメッセージの初期表示（メインバー：チャットボット対話エリア）
cn.display_initial_ai_message()


############################################################
# 5. 会話ログの表示
############################################################
try:
    # 会話ログの表示
    cn.display_conversation_log()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    st.stop()


############################################################
# 6. チャット入力の受け付け
############################################################
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)


############################################################
# 7. チャット送信時の処理
############################################################
if chat_message:
    # ==========================================
    # 7-1. ユーザーメッセージの表示
    # ==========================================
    # ユーザーメッセージのログ出力
    logger.info({"message": chat_message, "application_mode": st.session_state.mode})

    # ユーザーメッセージを表示
    with st.chat_message("user"):
        st.markdown(chat_message)

    # ==========================================
    # 7-2. LLMからの回答取得
    # ==========================================
    # 「st.spinner」でグルグル回っている間、表示の不具合が発生しないよう空のエリアを表示
    res_box = st.empty()
    # LLMによる回答生成（回答生成が完了するまでグルグル回す）
    with st.spinner(ct.SPINNER_TEXT):
        try:
            # 画面読み込み時に作成したRetrieverを使い、Chainを実行
            llm_response = utils.get_llm_response(chat_message)
        except Exception as e:
            # エラーログの出力
            logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
            # エラーメッセージの画面表示
            st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            # 後続の処理を中断
            st.stop()
    
    # ==========================================
    # 7-3. LLMからの回答表示
    # ==========================================
    with st.chat_message("assistant"):
        try:
            # 軽量版レスポンス処理（RAGファイル表示対応）
            if isinstance(llm_response, dict) and "answer" in llm_response:
                # 新しい軽量版レスポンス形式
                st.markdown(llm_response["answer"])
                
                # 社内文書検索モードの場合、ファイル情報を表示
                if st.session_state.get("mode") == ct.ANSWER_MODE_1 and "context" in llm_response and llm_response["context"]:
                    cn.display_file_sources(llm_response["context"])
                
                content = llm_response  # 辞書全体を保存
            elif isinstance(llm_response, str):
                # 文字列レスポンス
                st.markdown(llm_response)
                content = llm_response
            else:
                # 不明な形式の場合
                error_msg = "⚠️ 回答表示に失敗しました。"
                st.error(error_msg)
                content = error_msg
            
            # AIメッセージのログ出力
            response_text = llm_response.get("answer", str(llm_response)) if isinstance(llm_response, dict) else str(llm_response)
            logger.info({"message": response_text, "application_mode": st.session_state.mode})
        except Exception as e:
            # エラーログの出力
            logger.error(f"{ct.DISP_ANSWER_ERROR_MESSAGE}\n{e}")
            # エラーメッセージの画面表示
            error_msg = f"⚠️ 回答表示に失敗しました。\n\nこのエラーが繰り返し発生する場合は、管理者にお問い合わせください。\n\n詳細: {str(e)}"
            st.error(error_msg, icon=ct.ERROR_ICON)
            content = error_msg

    # ==========================================
    # 7-4. 会話ログへの追加
    # ==========================================
    # 表示用の会話ログにユーザーメッセージを追加
    st.session_state.messages.append({"role": "user", "content": chat_message})
    # 表示用の会話ログにAIメッセージを追加
    st.session_state.messages.append({"role": "assistant", "content": content})