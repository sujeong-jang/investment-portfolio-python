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
def survey():
    if request.method == 'GET':
        return render_template('survey.html')

    if request.method == 'POST':
        is_oversea = request.form['oversea']

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

    return render_template('result.html', KEY_INVEST_TYPE=invest_type, IS_OVERSEA=is_oversea)

@app.route("/portfolio", methods=['POST', 'GET'])
def portfolio():
    if request.method == 'POST':
        money = request.form['money']
        type = request.form['type']
        risk_no = request.form['risk_no']
        is_oversea = request.form['oversea']

        db = ""


        if is_oversea == '0': # 해외 ETF
            db = "ETF_US"
        else: # 국내 ETF
            db = "ETF_KR"

        print(db)

        with oracle_engine.connect() as conn:
            try:
                sql = "select * from " +  db + " where invest_type=:1"
                results = conn.execute(sql, (type)).fetchall()

                name_list = [] # 상품명
                risk_list = [] # 위험등급
                weight_list = [] # 가중치
                returns_1y = [] # 1년 수익률
                returns_3y = [] # 3년 수익률
                returns_5y = [] # 5년 수익률

                for etf in results:
                    name_list.append(etf[0])
                    risk_list.append(etf[2])
                    weight_list.append(etf[3])
                    returns_1y.append(etf[4])
                    returns_3y.append(etf[5])
                    returns_5y.append(etf[6])

            except Exception as e:
                print(e)
                return render_template('error.html')

        # 투자 등급 카운팅 (파이차트에 비중 나타내기 위해 사용)
        count_list = [0,0,0]

        for risk_type in risk_list:
            if risk_type == '위험':
                count_list[0] += 1
            elif risk_type == '중립':
                count_list[1] += 1
            else:
                count_list[2] += 1

        return render_template('portfolio.html', KEY_INVEST_TYPE=type, KEY_NAME_LIST=name_list, KEY_RISK_LIST=risk_list, KEY_WEIGHT_LIST=weight_list, KEY_COUNT_LIST=count_list, KEY_RETURN_1Y=returns_1y, KEY_RETURN_3Y=returns_3y, KEY_RETURN_5Y=returns_5y)

if __name__ == '__main__':
    app.run(debug=True)
