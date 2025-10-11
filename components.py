"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

from __future__ import annotations

############################################################
# ライブラリの読み込み
############################################################
import streamlit as st
import utils
import constants as ct


############################################################
# 関数定義
############################################################

def display_sidebar_navigation():
    """
    サイドバーにナビゲーション要素を表示（修正点: UI構成の分離）
    """
    with st.sidebar:
        # アプリタイトル
        #st.markdown(f"## {ct.APP_NAME}")
        #st.markdown("---")
        
        # 利用目的の選択
        st.markdown("### 利用目的")
        st.session_state.mode = st.radio(
            label="利用目的",
            options=[ct.ANSWER_MODE_1, ct.ANSWER_MODE_2],
            help="用途に応じて適切なモードを選択してください",
            label_visibility="collapsed"
        )
        
        # 選択されたモードの説明
        st.markdown("---")
        # 「社内文書検索」の機能説明
        st.markdown("**【「社内文書検索」を選択した場合】**")
        # 「st.info()」を使うと青枠で表示される
        st.info("入力内容と関連性が高い社内文書のありかを検索できます。")
        # 「st.code()」を使うとコードブロックの装飾で表示される
        # 「wrap_lines=True」で折り返し設定、「language=None」で非装飾とする
        st.code("【入力例】\n社員の育成方針に関するMTGの議事録", wrap_lines=True, language=None)

        # 「社内問い合わせ」の機能説明
        st.markdown("**【「社内問い合わせ」を選択した場合】**")
        st.info("質問・要望に対して、社内文書の情報をもとに回答を得られます。")
        st.code("【入力例】\n人事部に所属している従業員情報を一覧化して", wrap_lines=True, language=None)


def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f"## {ct.APP_NAME}")


def display_select_mode():
    """
    回答モードのラジオボタンを表示
    """
    # 回答モードを選択する用のラジオボタンを表示（マジックナンバー対策: カラム比率を定数化）
    col1, col2 = st.columns([ct.UI_COLUMN_RATIO_MAIN, ct.UI_COLUMN_RATIO_SPACER])
    with col1:
        # 「label_visibility="collapsed"」とすることで、ラジオボタンを非表示にする
        st.session_state.mode = st.radio(
            label="",
            options=[ct.ANSWER_MODE_1, ct.ANSWER_MODE_2],
            label_visibility="collapsed"
        )


def display_initial_ai_message():
    """
    メインバーでのAIメッセージの初期表示（修正点: すべての目的に対応した説明を常に表示）
    """
    # アプリ名を表示
    st.markdown(f"## {ct.APP_NAME}")
    
    # チャットメッセージ
    with st.chat_message("assistant"):
        # 挨拶メッセージ
        st.success("こんにちは。私は社内文書の情報をもとに回答する生成AIチャットボットです。サイドバーで利用目的を選択し、画面下部のチャット欄からメッセージを送信してください。")
        
        # 注意事項
        st.warning("⚠️ 具体的に入力した方が期待通りの回答を得やすいです。")


def display_conversation_log():
    """
    会話ログの一覧表示（エラー耐性強化版 + RAGファイル表示対応）
    """
    # 会話ログのループ処理
    for message in st.session_state.messages:
        try:
            # 「message」辞書の中の「role」キーには「user」か「assistant」が入っている
            with st.chat_message(message["role"]):

                # ユーザー入力値の場合、そのままテキストを表示するだけ
                if message["role"] == "user":
                    st.markdown(message["content"])
                
                # LLMからの回答の場合（安全な表示）
                else:
                    # 新しい軽量版レスポンス形式に対応
                    content = message.get("content", {})
                    
                    # シンプルな文字列レスポンスの場合
                    if isinstance(content, str):
                        st.markdown(content)
                    # 辞書形式のレスポンスの場合（RAG対応）
                    elif isinstance(content, dict):
                        if "answer" in content:
                            st.markdown(content["answer"])
                            
                            # 社内文書検索モードの場合、ファイル情報を表示
                            if "context" in content and content["context"]:
                                display_file_sources(content["context"])
                        else:
                            st.markdown(str(content))
                    else:
                        st.markdown("回答を表示できませんでした。")
        except Exception as display_error:
            # 表示エラーが発生した場合のフォールバック
            st.error(f"⚠️ メッセージの表示中にエラーが発生しました: {str(display_error)}")


def display_file_sources(context_docs):
    """
    RAGコンテキストからファイルソースを表示（🔧 緊急修正版）
    """
    if not context_docs:
        return
    
    # 区切り線の表示
    st.divider()
    
    # メインファイル表示（最も関連性の高いファイル）
    main_doc = context_docs[0] if context_docs else None
    if main_doc:
        st.markdown("**入力内容に関する情報は、以下のファイルに含まれている可能性があります。**")
        
        source = main_doc.metadata.get('source', '不明なソース')
        page = main_doc.metadata.get('page')
        icon = utils.get_source_icon(source)
        
        if source.endswith('.pdf') and page:
            file_display = f"{source} (ページNo.{page})"
        else:
            file_display = source
            
        st.success(file_display, icon=icon)

    # 🔧 緊急修正: sub_files を確実に初期化
    sub_files = []
    displayed_sources = set()
    
    # サブファイル処理
    try:
        for doc in context_docs[1:]:  # メインファイル以外
            if doc.metadata.get("type") in ["employee_data", "department_summary"]:
                continue
                
            source = doc.metadata.get('source', '不明なソース')
            page = doc.metadata.get('page')
            
            # 重複チェック
            source_key = f"{source}_{page}" if page else source
            if source_key in displayed_sources:
                continue
            displayed_sources.add(source_key)
            
            if source.endswith('.pdf') and page:
                file_display = f"{source} (ページNo.{page})"
            else:
                file_display = source
                
            sub_files.append({"display": file_display, "source": source})
    except Exception as e:
        print(f"サブファイル処理エラー: {e}")
        sub_files = []

    # サブファイル表示
    if sub_files:
        st.markdown("**その他、ファイルありかの候補を提示します。**")
        for file_info in sub_files[:3]:  # 最大3件
            icon = utils.get_source_icon(file_info["source"])
            st.info(file_info["display"], icon=icon)

def display_conversation_log_legacy():
    """
    従来の会話ログ表示（複雑なRAG対応版）- 現在は使用しない
    """
    # 会話ログのループ処理
    for message in st.session_state.messages:
        # 「message」辞書の中の「role」キーには「user」か「assistant」が入っている
        with st.chat_message(message["role"]):

            # ユーザー入力値の場合、そのままテキストを表示するだけ
            if message["role"] == "user":
                st.markdown(message["content"])
            
            # LLMからの回答の場合
            else:
                # 「社内文書検索」の場合、テキストの種類に応じて表示形式を分岐処理
                if message["content"]["mode"] == ct.ANSWER_MODE_1:
                    
                    # ファイルのありかの情報が取得できた場合（通常時）の表示処理
                    if not "no_file_path_flg" in message["content"]:
                        # ==========================================
                        # ユーザー入力値と最も関連性が高いメインドキュメントのありかを表示
                        # ==========================================
                        # 補足文の表示
                        st.markdown(message["content"]["main_message"])

                        # 参照元のありかに応じて、適したアイコンを取得
                        icon = utils.get_source_icon(message['content']['main_file_path'])
                        # 修正点: 共通関数を使用してPDF参照表示を統一化
                        page_number = message["content"].get("main_page_number")
                        formatted_reference = utils.format_pdf_reference(message['content']['main_file_path'], page_number)
                        st.success(formatted_reference, icon=icon)
                        
                        # ==========================================
                        # ユーザー入力値と関連性が高いサブドキュメントのありかを表示
                        # ==========================================
                        if "sub_message" in message["content"]:
                            # 補足メッセージの表示
                            st.markdown(message["content"]["sub_message"])

                            # サブドキュメントのありかを一覧表示
                            for sub_choice in message["content"]["sub_choices"]:
                                # 参照元のありかに応じて、適したアイコンを取得
                                icon = utils.get_source_icon(sub_choice['source'])
                                # 修正点: 共通関数を使用してPDF参照表示を統一化
                                page_number = sub_choice.get("page_number")
                                formatted_reference = utils.format_pdf_reference(sub_choice['source'], page_number)
                                st.info(formatted_reference, icon=icon)
                    # ファイルのありかの情報が取得できなかった場合、LLMからの回答のみ表示
                    else:
                        st.markdown(message["content"]["answer"])
                
                # 「社内問い合わせ」の場合の表示処理
                else:
                    # LLMからの回答を表示
                    st.markdown(message["content"]["answer"])

                    # 参照元のありかを一覧表示
                    if "file_info_list" in message["content"]:
                        # 区切り線の表示
                        st.divider()
                        # 「情報源」の文字を太字で表示
                        st.markdown(f"##### {message['content']['message']}")
                        # ドキュメントのありかを一覧表示
                        for file_info in message["content"]["file_info_list"]:
                            # 参照元のありかに応じて、適したアイコンを取得
                            icon = utils.get_source_icon(file_info)
                            st.info(file_info, icon=icon)


def display_search_llm_response(llm_response):
    """
    「社内文書検索」モードにおけるLLMレスポンスを表示

    Args:
        llm_response: LLMからの回答

    Returns:
        LLMからの回答を画面表示用に整形した辞書データ
    """
    # LLMからのレスポンスに参照元情報が入っており、かつ「該当資料なし」が回答として返された場合
    if llm_response["context"] and llm_response["answer"] != ct.NO_DOC_MATCH_ANSWER:

        # ==========================================
        # ユーザー入力値と最も関連性が高いメインドキュメントのありかを表示
        # ==========================================
        # LLMからのレスポンス（辞書）の「context」属性の最初（最も関連性が高い）ドキュメント情報を取得（マジックナンバー対策: インデックスを定数化）
        main_file_path = llm_response["context"][ct.MAIN_DOCUMENT_INDEX].metadata["source"]

        # 補足メッセージの表示
        main_message = "入力内容に関する情報は、以下のファイルに含まれている可能性があります。"
        st.markdown(main_message)
        
        # 参照元のありかに応じて、適したアイコンを取得
        icon = utils.get_source_icon(main_file_path)
        # 修正点: 共通関数を使用してPDF参照表示を統一化
        main_page_number = llm_response["context"][ct.MAIN_DOCUMENT_INDEX].metadata.get("page")
        formatted_main_reference = utils.format_pdf_reference(main_file_path, main_page_number)
        st.success(formatted_main_reference, icon=icon)

        # ==========================================
        # ユーザー入力値と関連性が高いサブドキュメントのありかを表示
        # ==========================================
        # メインドキュメント以外で、関連性が高いサブドキュメントを格納する用のリストを用意
        sub_choices = []
        # 重複チェック用のリストを用意
        duplicate_check_list = []

        # ドキュメントが2件以上検索できた場合（サブドキュメントが存在する場合）のみ、サブドキュメントのありかを一覧表示
        # 「context」内のリストの2番目以降をスライスで参照（マジックナンバー対策: 開始インデックスを定数化）
        for document in llm_response["context"][ct.SUB_DOCUMENTS_START_INDEX:]:
            # ドキュメントのファイルパスを取得
            sub_file_path = document.metadata["source"]

            # メインドキュメントのファイルパスと重複している場合、処理をスキップ（表示しない）
            if sub_file_path == main_file_path:
                continue
            
            # 同じファイル内の異なる箇所を参照した場合、2件目以降のファイルパスに重複が発生する可能性があるため、重複を除去
            if sub_file_path in duplicate_check_list:
                continue

            # 重複チェック用のリストにファイルパスを順次追加
            duplicate_check_list.append(sub_file_path)
            
            # ページ番号が取得できない場合のための分岐処理
            if "page" in document.metadata:
                # ページ番号を取得
                sub_page_number = document.metadata["page"]
                # 「サブドキュメントのファイルパス」と「ページ番号」の辞書を作成
                sub_choice = {"source": sub_file_path, "page_number": sub_page_number}
            else:
                # 「サブドキュメントのファイルパス」の辞書を作成
                sub_choice = {"source": sub_file_path}
            
            # 後ほど一覧表示するため、サブドキュメントに関する情報を順次リストに追加
            sub_choices.append(sub_choice)
        
        # サブドキュメントが存在する場合のみの処理
        if sub_choices:
            # 補足メッセージの表示
            sub_message = "その他、ファイルありかの候補を提示します。"
            st.markdown(sub_message)

            # サブドキュメントに対してのループ処理
            for sub_choice in sub_choices:
                # 参照元のありかに応じて、適したアイコンを取得
                icon = utils.get_source_icon(sub_choice['source'])
                # 修正点: 共通関数を使用してPDF参照表示を統一化
                page_number = sub_choice.get("page_number")
                formatted_sub_reference = utils.format_pdf_reference(sub_choice['source'], page_number)
                st.info(formatted_sub_reference, icon=icon)
        
        # 表示用の会話ログに格納するためのデータを用意
        # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
        # - 「main_message」: メインドキュメントの補足メッセージ
        # - 「main_file_path」: メインドキュメントのファイルパス
        # - 「main_page_number」: メインドキュメントのページ番号
        # - 「sub_message」: サブドキュメントの補足メッセージ
        # - 「sub_choices」: サブドキュメントの情報リスト
        content = {}
        content["mode"] = ct.ANSWER_MODE_1
        content["main_message"] = main_message
        content["main_file_path"] = main_file_path
        # メインドキュメントのページ番号は、取得できた場合にのみ追加（マジックナンバー対策: インデックスを定数化）
        if "page" in llm_response["context"][ct.MAIN_DOCUMENT_INDEX].metadata:
            content["main_page_number"] = main_page_number
        # サブドキュメントの情報は、取得できた場合にのみ追加
        if sub_choices:
            content["sub_message"] = sub_message
            content["sub_choices"] = sub_choices
    
    # LLMからのレスポンスに、ユーザー入力値と関連性の高いドキュメント情報が入って「いない」場合
    else:
        # 関連ドキュメントが取得できなかった場合のメッセージ表示
        st.markdown(ct.NO_DOC_MATCH_MESSAGE)

        # 表示用の会話ログに格納するためのデータを用意
        # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
        # - 「answer」: LLMからの回答
        # - 「no_file_path_flg」: ファイルパスが取得できなかったことを示すフラグ（画面を再描画時の分岐に使用）
        content = {}
        content["mode"] = ct.ANSWER_MODE_1
        content["answer"] = ct.NO_DOC_MATCH_MESSAGE
        content["no_file_path_flg"] = True
    
    return content


def display_contact_llm_response(llm_response):
    """
    「社内問い合わせ」モードにおけるLLMレスポンスを表示

    Args:
        llm_response: LLMからの回答

    Returns:
        LLMからの回答を画面表示用に整形した辞書データ
    """
    # LLMからの回答を表示
    st.markdown(llm_response["answer"])

    # ユーザーの質問・要望に適切な回答を行うための情報が、社内文書のデータベースに存在しなかった場合
    if llm_response["answer"] != ct.INQUIRY_NO_MATCH_ANSWER:
        # 区切り線を表示
        st.divider()

        # 補足メッセージを表示
        info_message = "情報源"
        # st.markdown(f"##### {info_message}")

        # 参照元のファイルパスの一覧を格納するためのリストを用意
        file_path_list = []
        file_info_list = []

        # LLMが回答生成の参照元として使ったドキュメントの一覧が「context」内のリストの中に入っているため、ループ処理
        for document in llm_response["context"]:
            # ファイルパスを取得
            file_path = document.metadata["source"]
            # ファイルパスの重複は除去
            if file_path in file_path_list:
                continue

            # 修正点: 共通関数を使用してPDF参照表示を統一化
            page_number = document.metadata.get("page")
            file_info = utils.format_pdf_reference(file_path, page_number)

            # 参照元のありかに応じて、適したアイコンを取得
            icon = utils.get_source_icon(file_path)
            # ファイル情報を表示
            st.info(file_info, icon=icon)

            # 重複チェック用に、ファイルパスをリストに順次追加
            file_path_list.append(file_path)
            # ファイル情報をリストに順次追加
            file_info_list.append(file_info)

    # 表示用の会話ログに格納するためのデータを用意
    # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
    # - 「answer」: LLMからの回答
    # - 「message」: 補足メッセージ
    # - 「file_path_list」: ファイルパスの一覧リスト
    content = {}
    content["mode"] = ct.ANSWER_MODE_2
    content["answer"] = llm_response["answer"]
    # 参照元のドキュメントが取得できた場合のみ
    if llm_response["answer"] != ct.INQUIRY_NO_MATCH_ANSWER:
        content["message"] = info_message
        content["file_info_list"] = file_info_list

    return content