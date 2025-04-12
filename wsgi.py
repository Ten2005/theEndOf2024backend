import os
from main import app

# Railway環境用のエントリポイント
# Railwayは時々独自の方法でuvicornを起動することがあるため、
# このファイルを通じてアプリケーションを提供することで、
# 設定が一貫して適用されるようにする

# app変数を明示的にエクスポート
application = app 