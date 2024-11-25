# line-liff-backend
## 仮想環境を作成
cd lineapp
python -m venv venv

## 仮想環境有効化
cd lineapp
.\venv\Scripts\activate

## ライブラリ有効化
pip install -r requirements.txt


## set environment
## Windows
set PAYPAY_API_KEY="a_ymQWcSdv1W_c9FJ"
set PAYPAY_API_SECRET="+lNPeY1CPk83Ag7OsryLwQfBNCWzgPkZvO86Mi5Mf5k="
set PAYPAY_CLIENT_ID="a_ymQWcSdv1W"
set PAYPAY_MERCHANT_ID="838282367342632960"
set APP_HOST_NAME="https://liff.line.me/2006421613-ZrV2NXK1"
set PAYPAY_IP_WHITELIST="13.112.237.64,52.199.148.9,54.199.212.149,13.208.106.122,13.208.115.200,13.208.152.196"
## Mac OS
export PAYPAY_API_KEY="a_ymQWcSdv1W_c9FJ"
export PAYPAY_API_SECRET="+lNPeY1CPk83Ag7OsryLwQfBNCWzgPkZvO86Mi5Mf5k="
export PAYPAY_CLIENT_ID="a_ymQWcSdv1W"
export PAYPAY_MERCHANT_ID="838282367342632960"
export APP_HOST_NAME="https://liff.line.me/2006421613-ZrV2NXK1"
export PAYPAY_IP_WHITELIST="13.112.237.64,52.199.148.9,54.199.212.149,13.208.106.122,13.208.115.200,13.208.152.196"


## start
python manage.py runserver