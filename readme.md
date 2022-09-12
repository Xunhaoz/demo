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

```docker
sudo docker image build -t demo_web .
sudo docker run -p 5000:5000 --name demo_web demo_web
```