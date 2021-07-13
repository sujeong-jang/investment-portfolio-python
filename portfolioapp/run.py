import json
import joblib
import numpy as np
import datetime
import sqlalchemy as sa
import cx_Oracle

from flask import Flask, render_template, session, request, redirect, url_for

app = Flask(__name__)
oracle_engine = sa.create_engine('oracle://ft:1234@localhost:1522/xe')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/survey", methods=['POST', 'GET'])
def get_survey():
    if request.method == 'POST':
        # 국내 ETF / 국내/외 ETF is_oversea = request.form['oversea']

        gender = request.form['gender']
        age = request.form['age']
        income = request.form['income']
        knowledge = request.form['knowledge']
        exp = request.form['exp']
        risk = request.form['risk']
        term = request.form['term']
        s1 = request.form['s1']
        s2 = request.form['s2']
        s3 = request.form['s3']
        s4 = request.form['s4']
        s5 = request.form['s5']

        i_list = [gender, age, income, knowledge, exp, risk, term, s1, s2, s3, s4, s5]
        i_list = list(map(int, i_list)) # str -> int
        score = sum(i_list)
        i_list.append(score)
        data = np.array(i_list).reshape(1, -1)

        clf = joblib.load('./models/rf_model.pkl')
        type_num = clf.predict(data)

        if type_num == 0:
            invest_type = "안정추구형"
        elif type_num == 1:
            invest_type = "안정형"
        elif type_num == 2:
            invest_type = "적극투자형"
        elif type_num == 3:
            invest_type = "공격투자형"
        else:
            invest_type = "위험중립형"

    return render_template('result.html', KEY_INVEST_TYPE=invest_type)

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')

if __name__ == '__main__':
    app.run(debug=True)
