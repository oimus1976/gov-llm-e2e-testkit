@echo off
REM =====================================================
REM F4 HTML profile execution (TEMPLATE)
REM -----------------------------------------------------
REM This is a template file.
REM DO NOT put real credentials in this file.
REM Copy this file to run_f4_html.local.bat for actual use.
REM =====================================================

REM --- 認証情報（ここに直接書かない） ---
REM Set these values in *.local.bat
set QOMMONS_USERNAME=
set QOMMONS_PASSWORD=

REM --- 実行プロファイル（記録用メタデータ） ---
set F4_PROFILE=html

REM --- 仮想環境（プロジェクト標準） ---
call .venv\Scripts\activate

REM --- pytest 実行（Python 実体を固定） ---
python -m pytest tests\f4 ^
  --profile=%F4_PROFILE% ^
  -v

REM --- 後始末（環境汚染防止） ---
set QOMMONS_USERNAME=
set QOMMONS_PASSWORD=
set F4_PROFILE=

pause
