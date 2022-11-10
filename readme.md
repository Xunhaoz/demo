# demo

## requirement
```shell
pip install flask
pip install pandas
pip install tqdm
pip install PyPortfolioOpt
pip install yfinance
pip install matplotlib
pip install scikit-learn
pip install yfinance
```

## run

### docker
```shell
sudo docker image build -t demo_web .
sudo docker run -p 5000:5000 --name demo demo_web
```

### terminal
```shell
python3 -m venv env
source env/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

# merge from another code 

## project structure

```shell
├── venv # python 虛擬環境
├── app.py # 程式進入點
├── readme.md # 使用手冊
├── database
│   └── finance_feature.db # 資料庫
├── module
│   ├── __init__.py
│   ├── get_stock.py # FindMind API 下載股票
│   ├── kmeans_allocation.py # Kmeans 分群
│   ├── stocks_features.py # 計算基礎股票指標
│   └── store_feature_sqlite.py # 與 finance_feature.db 互動 (新增資料)
└── statics
    ├── stocks # 所有被篩選過的股票 datafram 都在這裡
    └── all_stock.csv # 台灣所有沒有被篩選過的股票代號
```

## get_stock.py
1. 比對 all_stock.csv 檔案中與 statics/stocks 現有檔案差異，並下載尚未存在的股票歷史資訊。

> 現有下載支股票為篩選過之股票<br>
> 剔除資料為空的 CSV 檔

## store_feature_sqlite.py
1. 建立資料庫
2. 計算每檔平均、變異數、峰度、偏度
3. 存入資料庫

## kmeans_allocation.py
1. 資料標準化
2. 資料降維
3. KMeans 群分類
4. 出圖
5. 計算 sortino_ratio
6. 存入資料庫

### stocks_features.py
1. 供期他腳本調用