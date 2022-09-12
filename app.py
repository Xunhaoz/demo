from flask import Flask, render_template, redirect, url_for, request, jsonify
import json
import modules.finance as finance

app = Flask(__name__)


def cal_risk_free(form):
    risk_free = [0.02, ]

    with open('static/src/risk_free_weight.json') as f:
        weight_dict = json.load(f)

    for key, value in list(form.lists()):
        for v in value:
            risk_free.append(weight_dict[key][v])

    return sum(risk_free) / float(len(risk_free))


@app.route('/')
def estimation_page():
    return render_template('estimation.html')


@app.route('/result_page', methods=['post'])
def result_page():
    risk_free = cal_risk_free(request.form)
    cal_result = finance.for_demo(risk_free)

    risk_free = int(risk_free * 10000) / 100
    stock_names = ['Risk Free', ]
    stock_weights = [risk_free, ]
    for k, i in cal_result['clean_weight'].items():
        stock_names.append(k)
        stock_weights.append(int(i * (100 - risk_free) * 100) / 100)

    for k, i in cal_result['performance'].items():
        cal_result['performance'][k] = int(i * 10000) / 100

    return render_template('index.html', stock_names=stock_names, stock_weights=stock_weights,
                           performance=cal_result['performance'], pct_change=cal_result['pct_change'],
                           pct_period=cal_result['pct_period'])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
