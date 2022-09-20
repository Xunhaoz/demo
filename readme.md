# demo

## requirement
```shell
pip install flask
pip install pandas
pip install tqdm
pip install PyPortfolioOpt
pip install yfinance
pip install scikit-learn
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
