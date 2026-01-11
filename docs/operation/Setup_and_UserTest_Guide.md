---
title: Setup and User Test Guide
project: gov-llm-e2e-testkit
category: operation
audience:
  - developer
  - tester
scope:
  - initial_setup
  - user_test
  - f10-a
assumptions:
  - fresh_clone
  - new_machine
  - no_env_file
status: draft
last_updated: 2026-01-09
related:
  - README.md
  - docs/design/Design_Submit_Blue_Semantics_v0.1.md
  - docs/design/core/Design_ChatSelectPage_v0.1.md
notes:
  - This document is normative for local setup and user test execution.
  - README acts as an entry point only.
---

# 開発環境セットアップガイド

本プロジェクトを初めてクローンした開発者向けに、テスト実行までの初期セットアップ手順をまとめます。Python仮想環境の構築から依存パッケージのインストール、環境変数ファイル（.env）の準備までを以下に説明します。

## 前提条件と推奨環境

- **OS**: Windows 10/11 (PowerShell またはコマンドプロンプトが使用可能であることを推奨)  
  ※ Linux や macOS でもPython/Playwrightが動作する環境であれば実行可能ですが、本手順書では主に Windows 環境を想定しています。

- **Python**: 3.10 以上がインストール済みであること[\[1\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/README.md#L82-L89)。

- **その他**: インターネット接続環境（後述のPlaywrightブラウザのインストールに使用）。プロキシ環境下では追加設定が必要な場合があります。

## Python仮想環境の準備 (推奨)

他のプロジェクトとの依存関係の衝突を防ぐため、Pythonの仮想環境（venv）の使用を推奨します。※必須ではありませんが、環境をクリーンに保つため推奨されています。

1. **仮想環境の作成**: リポジトリのルートディレクトリで以下を実行します。

- python \-m venv .venv

- これにより、.venv フォルダに仮想環境が作成されます。

1. **仮想環境の有効化**:

2. **PowerShell（Windows）**:

- .\\.venv\\Scripts\\Activate.ps1

1. **コマンドプロンプト（Windows）**:

- .\\.venv\\Scripts\\activate.bat

1. **Git Bash / Unix系シェル**:

- source .venv/bin/activate

- コマンド実行後、シェルの先頭に (.venv) と表示されていれば仮想環境が有効になっています。

## 依存パッケージの一括インストール

仮想環境を有効にしたら、本プロジェクトが必要とするPythonパッケージをインストールします。リポジトリルートに依存関係一覧の requirements.txt がある場合、以下のコマンド一発でインストール可能です[\[2\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.github/workflows/e2e.yml#L50-L52):

pip install \-r requirements.txt

上記コマンドにより、次の主要パッケージがインストールされます:

- **Playwright** (ブラウザ操作用)[\[3\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L18-L21)

- **pytest および pytest-asyncio** (テストフレームワーク、非同期サポート)[\[4\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L45-L53)

- **pytest-playwright** (Playwright用のpytestプラグイン)[\[5\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L48-L52)

- **python-dotenv** (.envファイルの読み込み)[\[6\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L11-L19)

- **PyYAML** (YAMLファイルの読み込み)[\[7\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L14-L17)

- **python-frontmatter** (マークダウンのFront Matter処理)[\[8\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L20-L23)

※ requirements.txt が提供されていない場合は、代わりに上記のパッケージを個別にインストールしてください（pyproject.tomlに記載の依存パッケージに従うか、pip install playwright pytest pytest-asyncio python-dotenv pyyaml python-frontmatter などを実行）。開発用途でソースコードを直接参照する場合は、pip install \-e . により本パッケージを編集可能モードでインストールしておくと、src/ 配下のモジュールをPythonから直接読み込めるようになります。

### Playwrightブラウザのインストール

Playwright利用のため、ブラウザ実行環境をセットアップします。依存パッケージのインストール後、下記コマンドを実行して必要なブラウザをダウンロードしてください[\[2\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.github/workflows/e2e.yml#L50-L52):

python \-m playwright install \--with-deps

上記により、Playwrightが使用するブラウザ（Chromium など）が自動的にダウンロードされます（Linuxの場合は \--with-deps オプションにより必要なシステム依存もインストールされます）。完了後、npx playwright install と同等の環境が整います。

## 環境変数ファイル (.env) の準備

本プロジェクトでは、接続先URLや認証情報などの**機密情報**を .env ファイルに定義します。まずリポジトリ直下にあるサンプルファイルをコピーして、自分用の .env ファイルを作成してください。

- インターネット環境でテストする場合:  
  リポジトリ直下の **.env.internet.sample** をコピーして **.env.internet** というファイルを作成します[\[9\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.sample#L4-L9)。

- cp .env.internet.sample .env.internet

- 次に、.env.internet ファイル内の各変数を設定します。特に以下の項目を**テスト用アカウントの情報**で埋めてください（本番用アカウントは使用しないでください[\[10\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.sample#L12-L15)）:

- QOMMONS\_URL (接続先サービスのURL。インターネット側の場合、デフォルトで <https://qommons.ai> が指定されています[\[11\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.internet.sample#L18-L26))

- QOMMONS\_USERNAME / QOMMONS\_PASSWORD (テスト用ユーザーのログイン認証情報)[\[12\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.internet.sample#L20-L26)

- LGWAN 閉域環境でテストする場合:  
  リポジトリ直下の **.env.sample** をコピーして **.env.lgwan** というファイルを作成します[\[13\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.sample#L30-L38)。

- cp .env.sample .env.lgwan

- .env.lgwan 内の QOMMONS\_LGWAN\_URL, QOMMONS\_LGWAN\_USERNAME, QOMMONS\_LGWAN\_PASSWORD に、閉域環境で使用する接続先と認証情報を設定してください[\[13\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.sample#L30-L38)。インターネット非接続環境でのテストの場合はこちらを使用します。

- **PROFILEの設定**: 上記で作成した .env.internet または .env.lgwan に、使用するプロファイル名を示す PROFILE 変数を追加することを推奨します。例えばインターネット環境用設定であれば .env.internet の先頭行に以下を追記してください[\[14\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.github/workflows/e2e.yml#L60-L65):

- PROFILE=internet

- LGWAN環境用なら PROFILE=lgwan とします。これにより、実行時に正しい環境プロファイルが選択されます（env\_loader.pyが .env および .env.\<profile\> の両方を読み込み、該当プロファイルの設定を適用します）。

最後に、**現在有効な設定を .env ファイルとして適用**します。本プロジェクトでは **.env** という名前のファイルのみが実行時に読み込まれる設計です[\[15\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/README.md#L278-L286)。そのため、上で作成した .env.\<profile\> ファイルを **.env** にコピーする必要があります（環境切替ツールを使う場合は自動で行えます）。

- **手動で適用する場合**: 単純に .env.internet または .env.lgwan を .env にリネームまたはコピーしてください。例えばインターネット環境なら:

- cp .env.internet .env

- として .env を作成します。

- **スクリプトで適用する場合**: scripts/switch\_env.py を利用すると、既存の .env を上書きしつつ安全に切替ができます[\[16\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/scripts/switch_env.py#L34-L43)[\[17\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/scripts/switch_env.py#L53-L62)。例えばインターネット環境・Markdownナレッジ用のプロファイル名を internet\_markdown として .env.internet\_markdown を用意した場合、以下のように実行します:

- python scripts/switch\_env.py internet\_markdown \--force

- （※ .env がすでに存在する場合、\--force オプションがないとエラーで停止します[\[18\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/scripts/switch_env.py#L59-L67)。上書きする際は十分注意してください。）

.env ファイルの準備ができたら、**機密情報の管理に十分注意**してください。[\[10\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.sample#L12-L15)に示すとおり、本番アカウント情報は絶対に書かないようにし、また .env および .env.\* ファイルはGit追跡対象外になっているとはいえ、誤ってコミットしないよう注意しましょう。

これで、テストを実行するための環境構築は完了です。次は実際のユーザーテスト（カスタム質問セットを用いたE2Eテスト）の手順を説明します。

# ユーザーテスト実行ガイド

カスタム質問セットを用いて、実際にE2Eテストを実行する手順を示します。ここでは、data/customized\_question\_sets/\<ORDINANCE\_ID\>/customized\_question\_set.json に用意した質問セットを入力として、ブラウザ経由でLLMサービスに質問を投げ、回答素材を収集する一連の流れを紹介します。

**前提:** 上記「セットアップガイド」の手順に従い、必要な依存関係がインストール済みで .env の設定が完了していることを確認してください。また、質問を投げる対象となる**条例データ**（例規HTMLなど）は事前に入手済みであり、テスト実行時に参照可能な状態にしておきます（条例データ自体は本リポジトリには含まれません[\[19\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/README.md#L130-L139)。ファイルパスを後ほど対話的に指定します）。

## 1\. カスタム質問セットの配置

テスト対象とする**カスタム質問セットJSON**を所定のディレクトリに配置します。各条例IDごとにフォルダを作成し、その中に customized\_question\_set.json ファイルを置いてください[\[20\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L35-L44)[\[21\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L42-L49)。ディレクトリ構造の例:

data/  
└─ customized\_question\_sets/  
    ├─ k518RG00000022/  
    │   └─ customized\_question\_set.json  
    ├─ k518RG00000059/  
    │   └─ customized\_question\_set.json  
    └─ （以下略）

- フォルダ名は**条例ID**とし、その配下にファイル名 **customized\_question\_set.json** を置きます。複数の条例に対する質問セットを用意する場合は、上記のように条例IDごとにディレクトリを作成します。

- data/customized\_question\_sets/ 以下は**Gitで管理しない**ディレクトリです[\[22\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L194-L198)。このディレクトリ配下のJSONファイルは機密情報または大容量データとなる可能性があり、成果物と同様にコミット対象外です。誤ってGit管理下に置かないようご注意ください。

## 2\. 実行前の設定確認

テストを実行する前に、以下を確認・設定してください。

- **.envのプロファイル**: 使用する環境に合わせて適切な.envが適用されていることを再確認します（インターネット環境なら .env にQOMMONS\_URL等が設定済み、LGWANならLGWAN側のURL等）。必要に応じて前述の switch\_env スクリプトや手動コピーで .env を切り替えてください[\[15\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/README.md#L278-L286)。

- **ランID (run\_id) の決定**: 今回のテスト実行に一意なIDを付けます。run\_id は出力を保存するフォルダ名に使われ、過去の実行結果と混同しないようにするため**毎回異なる名前**を付けてください[\[23\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L14-L21)。推奨形式は **YYYYMMDD\_HHMM\_\<ラベル\>** です[\[24\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L16-L21)（例: 20260107\_0910\_test1）。過去に使用した run\_id を**再利用しない**でください[\[25\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L20-L23)。迷った場合は日時を更新して新しいIDにします。

- **OUTPUT\_ROOT 環境変数の設定**: 決定した run\_id を使い、結果出力先となる環境変数 OUTPUT\_ROOT を設定します（必須）。これを設定しないとスクリプトは実行されません[\[26\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L24-L29)。シェル種別ごとの設定例:

\# PowerShell の場合  
$env:OUTPUT\_ROOT="out/20260107\_0910\_test1"

\# Git Bash / Linux / macOS の場合  
export OUTPUT\_ROOT=out/20260107\_0910\_test1

上記のように設定した後、echo $OUTPUT\_ROOT や $Env:OUTPUT\_ROOT コマンドで正しく環境変数がセットされたことを確認してください[\[27\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L17-L25)。なお、OUTPUT\_ROOT には相対パス・絶対パスいずれも指定できますが、既定ではリポジトリ直下の out/ ディレクトリ配下に生成されることを想定しています。指定したパスにフォルダが存在しない場合はスクリプト実行時に自動作成されます。

## 3\. 単一条例でのスモークテスト実行

まずは**スモークテスト**として、1つの条例に対して質問セットを実行し、環境が正しく動作することを確認します。これはOOM（メモリ不足）を回避し、想定外の問題を早期に検知するための重要なステップです[\[28\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L102-L108)。

1. **スクリプトの起動**: リポジトリのルートディレクトリで次のコマンドを実行します。

- python scripts/run\_question\_set.py

- ※ カレントディレクトリはプロジェクトルートにしてください（scripts/run\_question\_set.py が参照するモジュールを正しく読み込むため）。初回実行時はPlaywrightがブラウザを起動します。ファイアウォールの警告が出た場合は通信を許可してください。

1. **対話形式での入力**: スクリプトを起動すると、対話的に実行モードを選択するプロンプトが表示されます。まずは「**単一条例（1 ordinance）を処理**」するオプションを選択してください[\[29\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L110-L118)。続いて対象の条例IDを尋ねられますので、用意したカスタム質問セットの条例ID（フォルダ名）を入力します（例: k518RG00000022 など）。入力後、テストが開始します。

2. **テスト実行と進行確認**: スクリプトはブラウザを自動操作し、指定した条例に対する質問セットを順に実行します。各質問送信ごとにコンソールログが出力されるので確認してください。**質問文の先頭に条例IDが付加されていること**に着目してください[\[30\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L116-L123)（例: 質問文が （条例ID：k518RG00000022）この条例の目的は何ですか？ のように自動で補われて送信されます）。このプレフィックスは後でログや出力を整理する上で重要です。もし質問送信時に条例IDの前置が付与されていない場合は異常動作の可能性があるため、その時点でテストを中止し、コンソールログを保存して開発者に相談してください[\[31\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L120-L124)。正常に進行している場合、そのまま全質問が送信され、LLMからの応答取得と結果ファイル保存まで自動で行われます。

3. **単一条例実行の完了**: スクリプトが指定した質問セットの処理を終えると、自動的にブラウザが閉じ、プログラムが終了します。コンソール上にエラーが出力されず終了ステータス0で終わればスモークテスト成功です。

## 4\. スモークテスト結果の確認

単一条例のテスト実行後、出力ディレクトリに成果物が生成されていることを確認します。OUTPUT\_ROOT で指定したパス（例: out/20260107\_0910\_test1/）以下にファイルが作られているはずです。ディレクトリ構造の最小例[\[32\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L137-L145):

out/20260107\_0910\_test1/  
├─ answer/  
│   └─ k518RG00000022/              \<- 条例IDごとのフォルダ  
│       └─ Q1234567890/            \<- 質問セット内の各質問（question\_fs\_id）ごとのフォルダ  
│           └─ answer.md           \<- 回答素材（Markdown形式）  
├─ execution\_meta.yaml             \<- 実行メタ情報（実行日時や設定を記録）  
├─ manifest.yaml                   \<- 質問と出力ファイルの対応関係を記録  
└─ README.md                       \<- 実行内容のサマリ（任意で実装側が出力する説明）

上記のように、**各質問に対する回答内容**が Markdownファイル（answer.md）として保存され、その他に実行全体のメタデータが YAML 形式で出力されます。特に次の点を確認してください:

- answer.md ファイルに、質問に対応する回答が含まれていること（Markdown形式で「\#\# Question」「\#\# Answer (Extracted)」などのセクションがあります）。

- execution\_meta.yaml に今回の run\_id や実行日時 (executed\_at)、使用したプロファイル情報が正しく記録されていること[\[33\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L150-L159)（evaluation\_performed: false は評価を行っていないことを示すフラグで、デフォルトはfalseのはずです）。

- manifest.yaml に全回答ファイルへのパスと質問ID対応が網羅されていること[\[34\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L159-L163)（スモークテストでは1条例分のみのはずです）。

問題なく出力が得られていれば、初期セットアップと単一条例での動作確認は成功です。

## 5\. 複数条例でのテスト本番実行

単一条例のスモークテストに問題がなければ、次に**複数条例をまとめて処理する本番実行**を行います。基本的な手順はスモークテスト時と同じですが、対象を増やすため注意点があります。

1. **新しい run\_id の設定**: スモークテスト時に使用した run\_id と出力ディレクトリをそのまま使い回さないでください。同じフォルダに出力を上書きすると記録が混在して再現性が損なわれます。必ず**新しい run\_id を決め、OUTPUT\_ROOT を更新**してください[\[35\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L20-L28)。例えば先ほど 20260107\_0910\_test1 を使ったなら、次は 20260107\_0930\_test\_all のように時刻やラベルを変えて設定します。環境変数の更新方法は前述と同様です。

2. **スクリプトの再実行**: 再度

- python scripts/run\_question\_set.py

- を実行します。今度は対話オプションで「**全条例を処理（all ordinances）**」もしくは複数選択肢がある場合は**複数条例をまとめて処理**するオプションを選びます[\[36\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L169-L177)。前者を選ぶと data/customized\_question\_sets/ 配下の全ての条例ディレクトリが対象となり、後者の場合は対話的に実行する条例IDを選択できる場合があります。必要に応じて使い分けてください。

1. **実行のモニタリング**: 単一実行時と同様、コンソールログに進行状況が表示されます。質問ごとにブラウザ操作と応答取得が行われるため、対象条例・質問数が多い場合は実行に時間がかかります。**途中で明らかな異常（例: ログイン失敗やタイムアウトの繰り返し）が発生した場合**は、一旦プロセスを終了してください。その際、それまでに生成された out/\<run\_id\>/answer/ 配下のファイルは残りますので、続行はせず原因を調査します（ログイン情報の誤りやネットワーク切断などが主な原因です）。

2. **OOM対策と分割実行**: 全条例を一度に実行する場合、ブラウザメモリの消費や動作の重さに注意してください。条例数や質問数が多いとブラウザやPythonプロセスがメモリ不足（OOM）に陥る可能性があります。そのため、**本番実行も二段階に分けることを推奨**します[\[37\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L176-L179)。例えば「まず2～3条例だけ実行して様子を見る → 問題なければ残りを実行」といった形です。一度に全てを処理するのではなく、適度に区切ることで安定性が向上します。また、実行中にブラウザが極端に重くなったり応答が返らなくなった場合も、**無理に続行せずプロセスを終了し、新しい run\_id を割り当てて再開**してください[\[38\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L176-L180)。再開時には、**既に出力済みの条例は除外**し、未処理の条例のみを選択するようにします[\[39\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L42-L46)。途中で中断した run\_id は今後使わず、必ず新しいIDで再開することで、どのランでどの条例を処理したか明確に記録されます[\[40\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L38-L46)。

3. **実行完了の確認**: 全指定条例の処理が完了したら、スモークテスト時と同様に out/\<run\_id\>/ 配下に成果物が揃っているか確認します。複数条例分の回答が含まれるため、answer/ 配下には複数の条例IDフォルダができているはずです。それぞれのフォルダ内に質問IDごとのサブフォルダと answer.md が存在することをチェックしてください。**完了の目安**としては、対象としたすべての条例について回答Markdown (answer.md) が生成され、ルート直下に manifest.yaml と execution\_meta.yaml および README.md が揃っていれば成功です[\[41\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L202-L210)。特に execution\_meta.yaml 内の evaluation\_performed が false となっており、run\_id フィールドがフォルダ名と一致していることも確認ポイントです[\[42\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L50-L59)。万一ファイルが欠けている場合や明らかな不整合がある場合は、途中で実行が失敗している可能性があります。その際はログやエラーメッセージを確認し、不足分の条例を別の run\_id で再実行するか、原因を取り除いてから再度実施してください。

4. **実行結果の活用**: 生成された answer.md 群と manifest.yaml は、この後の評価工程やレビューで使用する一次情報となります。これらのファイルはあくまで観測ログであり、本リポジトリ内では回答内容の良否評価は行いません。別途評価プロジェクトで活用するため、**出力を改変せず保管**してください（再現性確保のため、一度得られた結果の上書き・手動編集は厳禁です）。

## 6\. トラブルシューティングと補足情報

テスト実行中に問題が発生した場合の基本的な対処法をまとめます。

- **MissingSecretError が発生する**: 実行開始直後に Missing required environment variable 'XXX' for profile 'YYY'... というエラーが出た場合、.env（および .env.\<profile\>）に必要な環境変数が設定されていません[\[43\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.github/workflows/e2e.yml#L54-L62)。エラーメッセージ中に不足している変数名が明示されますので、.env ファイルを開き該当のキーに値をセットしてください。特に QOMMONS\_URL や QOMMONS\_USERNAME/PASSWORD、PROFILE の設定漏れに注意してください。

- **Playwright のブラウザ起動エラー**: python \-m playwright install を実行していない場合、テスト実行時にブラウザが見つからずエラーになることがあります。その場合は改めて依存関係のインストール手順に戻り、Playwrightのセットアップを実施してください。ブラウザ起動に関連するエラー（タイムアウト等）が出た場合、ネットワーク接続や認証情報も確認してください。環境によってはヘッドレスモード（デフォルト）ではなく実ブラウザ画面を表示する設定が役立つこともありますが、本ツールでは原則自動モードで動作する設計です。

- **ログの保存**: 大量の質問を投げる実行ではコンソールのログも重要な情報源です。エラー発生時には、直近のログメッセージ50行程度を含めて記録し、可能であれば out/\<run\_id\>/ フォルダごと保存しておきます[\[44\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L211-L219)。問題の再現手順（使用したコマンドオプションや対象条例など）と併せて報告することで、原因究明がスムーズになります。

- **pytest 知識について**: 本プロジェクトは内部的にpytestフレームワークを使用していますが、カスタム質問セットを用いたテスト実行においては run\_question\_set.py 等のスクリプトを直接実行することで目的を達成できます。したがって、pytest自体の詳しい使い方を知らなくても上記手順で十分テストを回せます。もし開発者として個別のテストケース（tests/ 配下）を実行したい場合は別途pytestコマンドを利用できますが、通常の評価業務の範囲では必要ありません。

最後に、実行後に生成された**入力データ（質問セット）や出力結果**は機密性の高い情報を含む可能性があります。前述のとおり、それらはGit管理から除外し、適切に保管してください[\[22\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L194-L198)。以上で、新規クローン直後からカスタム質問セットを用いたユーザーテスト実行までの手順説明は終わりです。セットアップおよび実行手順に沿って作業することで、環境構築の不備によるトラブルを減らし、確実にテストを再現できるようになります。技術的な問題や不明点が残る場合は、プロジェクト内の関連ドキュメントや担当者への問い合わせも併せて活用してください。

---

[\[1\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/README.md#L82-L89) [\[15\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/README.md#L278-L286) [\[19\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/README.md#L130-L139) README.md

[https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/README.md](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/README.md)

[\[2\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.github/workflows/e2e.yml#L50-L52) [\[14\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.github/workflows/e2e.yml#L60-L65) [\[43\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.github/workflows/e2e.yml#L54-L62) e2e.yml

[https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.github/workflows/e2e.yml](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.github/workflows/e2e.yml)

[\[3\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L18-L21) [\[4\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L45-L53) [\[5\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L48-L52) [\[6\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L11-L19) [\[7\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L14-L17) [\[8\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml#L20-L23) pyproject.toml

[https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/pyproject.toml)

[\[9\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.sample#L4-L9) [\[10\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.sample#L12-L15) [\[13\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.sample#L30-L38) .env.sample

[https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.sample](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.sample)

[\[11\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.internet.sample#L18-L26) [\[12\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.internet.sample#L20-L26) .env.internet.sample

[https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.internet.sample](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/.env.internet.sample)

[\[16\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/scripts/switch_env.py#L34-L43) [\[17\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/scripts/switch_env.py#L53-L62) [\[18\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/scripts/switch_env.py#L59-L67) switch\_env.py

[https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/scripts/switch\_env.py](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/scripts/switch_env.py)

[\[20\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L35-L44) [\[21\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L42-L49) [\[22\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L194-L198) [\[23\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L14-L21) [\[24\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L16-L21) [\[25\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L20-L23) [\[26\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L24-L29) [\[27\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L17-L25) [\[28\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L102-L108) [\[29\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L110-L118) [\[30\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L116-L123) [\[31\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L120-L124) [\[32\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L137-L145) [\[33\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L150-L159) [\[34\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L159-L163) [\[35\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L20-L28) [\[36\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L169-L177) [\[37\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L176-L179) [\[38\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L176-L180) [\[39\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L42-L46) [\[40\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L38-L46) [\[41\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L202-L210) [\[42\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L50-L59) [\[44\]](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md#L211-L219) customized\_question\_set.json\_to\_answer.md

[https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized\_question\_set.json\_to\_answer.md](https://github.com/oimus1976/gov-llm-e2e-testkit/blob/cdfdf2a4b8c628aceecffa80680528495dde6a45/docs/operation/customized_question_set.json_to_answer.md)
