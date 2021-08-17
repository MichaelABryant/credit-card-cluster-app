from flask import Flask, render_template, request
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)
scaler_purchases = pickle.load(open('scaler_purchases.pkl', 'rb'))
scaler_cash = pickle.load(open('scaler_cash.pkl', 'rb'))
purchases_model = pickle.load(open('random_forest_model.pkl', 'rb'))
cash_model = pickle.load(open('knn_model.pkl', 'rb'))
@app.route('/',methods=['GET'])


def Home():
    return render_template('index.html')

@app.route("/predict", methods=['POST'])

def predict():
    
    if request.method == 'POST':
                
        purchases = float(request.form['purchases'])
        purchases_trx = float(request.form['purchases_trx'])
        oneoff_purchases = float(request.form['oneoff'])
        installments_purchases = float(request.form['installments'])
        
        avg_price_per_trx = purchases/purchases_trx
        
        balance = float(request.form['balance'])
        cash_advance = float(request.form['cash'])
        cash_advance_trx = float(request.form['cash_trx'])
        
        avg_cash_advance_per_trx = cash_advance/cash_advance_trx
        
        inputs_purchases = pd.DataFrame([avg_price_per_trx, oneoff_purchases,
                               installments_purchases]).T
        
        inputs_cash = pd.DataFrame([balance, avg_cash_advance_per_trx]).T
        
        inputs_scaled_purchases = scaler_purchases.transform(inputs_purchases)
        
        inputs_scaled_cash = scaler_cash.transform(inputs_cash)
        
        prediction_purchases = purchases_model.predict(inputs_scaled_purchases)
        
        prediction_cash = cash_model.predict(inputs_scaled_cash)
        
        i = int(np.where(prediction_purchases==1)[1])

        j = int(np.where(prediction_cash==1)[1])
        
        purchases_output = ['less than or equal to $500',
                            '$800 to $3,000',
                            'less than or equal to $500 and in installments',
                            'less than or equal to $400 and in installments']
        
        cash_output = ['less than or equal to $1,000 (specifically for financial hardship)',
                       'less than or equal to $2,000',
                       '$4,000 to $10,000',
                       'less than or equal to $4000']
        
        if purchases < oneoff_purchases + installments_purchases:
            output = 'Error: the sum of max amount purchases and installment purchases must be less than or equal to the total purchase amount.'
        else:
            output = 'Advertise items for {} and loans of {}'.format(purchases_output[i],cash_output[j])
        
        return render_template('index.html', prediction_text = "{}".format(output))
                        
    else:
        
        return render_template('index.html')

if __name__=="__main__":
    
    app.run(debug=True)

