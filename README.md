🏢 社内情報特化型生成AI検索アプリ
💡「社内情報、すべて自然言語で検索できる時代へ。」

   

📌 プロジェクト概要
社内情報特化型生成AI検索アプリは、企業内の文書・従業員情報を自然言語で検索・取得できるRAG（Retrieval-Augmented Generation）システムです。

🎯 解決する課題
- 情報の分散：文書・議事録・社員情報が各所に散在
- 検索の困難さ：キーワード検索では目的情報に辿り着けない
- 時間のロス：情報探索に多くの時間を消費
- アクセス性の低さ：非ITユーザーでも簡単に使える必要がある

🔥 生成AIの活用
- 自然言語理解：「人事部の管理職は誰？」などの曖昧な質問にも対応
- 文脈理解：関連情報を含めた包括的な回答生成
- インテリジェント回答：検索結果の要約・整理・提案

🚀 主な機能
📚 社内文書検索
- PDF・Word・CSV・TXT対応の統合検索
- ベクトル検索による意味的類似性の高精度検索
- 会話履歴を活用した文脈保持型対話

👥 従業員情報検索（自然言語 → CSV）
- 自然言語クエリでCSVデータをフィルタリング
- LangChain Pandas Agentによる条件検索・分析
- 該当データがない場合のフォールバック提案
- Markdown形式での表表示

🎨 ユーザーインターフェース
- Streamlitによる直感的なWeb UI
- モード切替（文書検索／社内問い合わせ）
- ストリーミング形式でのリアルタイム回答生成
- デスクトップ・タブレット・モバイル対応

🛠️ 技術スタック
🐍 Core Technologies
- Python 3.11+
- Streamlit 1.50.0
- LangChain 0.3.27
- OpenAI GPT-4o-mini

🧠 AI/ML Stack
- ChromaDB（ベクトルDB）
- OpenAI Embeddings（ベクトル化）
- LangChain Experimental（Pandas Agent）
- PyMuPDF（PDF処理）
- python-docx（Word処理）

📊 Data Processing
- Pandas（データ操作）
- Tabulate（表整形）
- python-dotenv（環境変数管理）

📦 インストール方法
1. リポジトリのクローン
git clone https://github.com/yourusername/company_inner_search_app.git
cd company_inner_search_app

2. 仮想環境の作成・アクティベート
# Windows
python -m venv env
.\env\Scripts\activate

# macOS/Linux
python -m venv env
source env/bin/activate

3. 依存関係のインストール
# Windows用
pip install -r requirements_windows.txt

# macOS用
pip install -r requirements_mac.txt


4. 環境変数の設定
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

▶️ 使用方法
✅ アプリケーションの起動
streamlit run main.py

ブラウザで http://localhost:8501 にアクセス

💬 使用例
📋 従業員情報検索
- 入力：「人事部に所属している従業員情報を一覧化して」
→ 表形式で人事部の社員一覧を表示
- 入力：「営業部のマネージャーは誰ですか？」
→ 営業部の管理職一覧を表示
📄 社内文書検索
- 入力：「MTGの議事録について教えて」
→ 関連議事録から要約情報を生成
- 入力：「新入社員研修について」
→ 研修関連文書の内容を統合して回答

📁 ディレクトリ構成
company_inner_search_app/
├── main.py                 # Streamlitアプリ本体
├── utils.py                # RAG・従業員検索ロジック
├── components.py           # UI部品
├── constants.py            # 設定定数
├── initialize.py           # 初期化処理
├── requirements_windows.txt
├── requirements_mac.txt
├── data/                   # 社内文書・社員情報
│   ├── MTG議事録/
│   ├── サービスについて/
│   ├── 社員について/
│   │   └── 社員名簿.csv
├── env/                    # 仮想環境
└── logs/                   # ログファイル

📸 デモ画面
🏠 メイン画面（Streamlit UI）

🔍 検索モード選択          
 ◉ 社内文書検索              
 ○ 社内問い合わせ         

💬 チャット入力エリア

🔧 設定・カスタマイズ
constants.py の主要設定例
MODEL = "gpt-4o-mini"
TEMPERATURE = 0.5

RAG_SEARCH_K = 5
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

SUPPORTED_EXTENSIONS = {
    ".pdf": PyMuPDFLoader,
    ".docx": Docx2txtLoader,
    ".csv": CSVLoader,
    ".txt": TextLoader
}

🤝 貢献方法
🐛 Issueの報告
- 再現手順・環境情報・期待動作 vs 実際の動作を記載

🔄 Pull Request
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature

📈 改訂履歴（Changelog）

## [v1.0.0] - 2025-10-11
### 🎉 初回リリース
- **RAGシステム基盤**: ChromaDB + OpenAI Embeddings による文書検索機能
- **従業員検索機能**: 自然言語でCSVデータを検索するPandas Agent統合
- **Streamlit UI**: 直感的なチャットインターフェース
- **多形式文書対応**: PDF, Word, CSV, TXT ファイルの統合検索
- **モード切替**: 社内文書検索 / 社内問い合わせ の2モード対応

### ✨ 主要機能
- 🔍 **ベクトル検索**: 意味的類似性による高精度検索
- 💬 **対話型UI**: 会話履歴を保持した連続対話
- 📊 **表形式表示**: 従業員検索結果のMarkdown表示
- 🛡️ **エラーハンドリング**: フォールバック処理による安定動作
- ⚙️ **カスタマイズ可能**: constants.py による設定管理

### 🔧 技術仕様
- **Python**: 3.11+
- **フレームワーク**: Streamlit 1.50.0
- **AI/ML**: LangChain 0.3.27, OpenAI GPT-4o-mini
- **データベース**: ChromaDB (ベクトルストア)
- **データ処理**: Pandas, LangChain Experimental

### 🐛 修正された問題
- **セッション状態エラー**: Streamlit外でのst.session_state参照エラーを修正
- **経理部検索問題**: 存在しない役職検索時のフォールバック処理を追加  
- **エラーメッセージ表示**: 正常動作時の不適切なエラーメッセージ表示を修正
- **CSV文字化け**: UTF-8エンコーディング対応による日本語文字化け解決

### 📋 テスト結果
- ✅ **従業員検索**: 5/5 テストケース成功
- ✅ **文書検索**: PDF, Word, TXT ファイル読み込み確認
- ✅ **UI動作**: Streamlit インターフェース正常動作確認
- ✅ **エラーハンドリング**: 異常系処理の安定動作確認

---