import joblib
import numpy as np

def get_type():
    clf = joblib.load('./models/rf_model.pkl')

    survey = [0, 1, 2, 0, 2, 1, 2, 3, 3, 3, 1, 3]
    score = sum(survey)
    survey.append(score)
    data = np.array(survey).reshape(1, -1)
    data
    i_type = clf.predict(data)

    if i_type == 0:
        print("안정추구형")
    elif i_type == 1:
        print("안정형")
    elif i_type == 2:
        print("적극투자형")
    elif i_type == 3:
        print("공격투자형")
    else:
        print(위험투자형)

get_type()