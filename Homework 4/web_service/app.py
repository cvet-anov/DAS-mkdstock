from flask import Flask, render_template, jsonify, url_for
import requests
import os

app = Flask(__name__)

DATA_SERVICE_URL = os.environ.get('DATA_SERVICE_URL', 'http://localhost:5002')
ANALYSIS_SERVICE_URL = os.environ.get('ANALYSIS_SERVICE_URL', 'http://localhost:5003')

def get_analysis_data(company):
    try:
        response = requests.get(f'{ANALYSIS_SERVICE_URL}/api/analysis/{company}')
        if response.status_code == 200:
            return response.json()
        return {
            'daily': {
                'sma20': None, 'ema20': None, 'rsi': None,
                'macd': None, 'signal': None, 'histogram': None,
                'bollinger': {}
            }
        }
    except Exception:
        return {
            'daily': {
                'sma20': None, 'ema20': None, 'rsi': None,
                'macd': None, 'signal': None, 'histogram': None,
                'bollinger': {}
            }
        }

@app.route('/')
def home():
    try:
        response = requests.get(f'{DATA_SERVICE_URL}/api/companies')
        if response.status_code != 200:
            return render_template('error.html', message="Cannot load companies"), 500

        companies = response.json()['companies']
        company_data = []

        for company in companies[:9]:
            company_response = requests.get(f'{DATA_SERVICE_URL}/api/company/{company}')
            if company_response.status_code == 200:
                data = company_response.json()['history'][0]
                company_data.append({
                    'name': company,
                    'last_price': data['Last_Price'],
                    'change': data['Change_Pct'],
                    'volume': data['Volume'],
                    'date': data['Date'],
                    'high': data['High'],
                    'low': data['Low']
                })

        return render_template('index.html',
                             companies=company_data,
                             total_volume=sum(c['volume'] for c in company_data))

    except Exception:
        return render_template('error.html',
                             message="An error occurred. Please try again."), 500

@app.route('/company/<company>')
def company_detail(company):
    try:
        response = requests.get(f'{DATA_SERVICE_URL}/api/company/{company}')
        if response.status_code != 200:
            return render_template('error.html',
                                 message=f"Cannot find data for {company}"), response.status_code

        data = response.json()
        latest = data['history'][0] if data['history'] else None
        analysis = get_analysis_data(company)

        return render_template('company.html',
                             company=company,
                             history=data['history'],
                             latest=latest,
                             analysis=analysis)

    except Exception:
        return render_template('error.html',
                             message="An error occurred. Please try again."), 500

@app.route('/analysis/<company>')
def analysis(company):
    try:
        response = requests.get(f'{DATA_SERVICE_URL}/api/company/{company}')
        if response.status_code != 200:
            return render_template('error.html',
                                 message=f"Cannot find data for {company}"), response.status_code

        data = response.json()
        analysis = get_analysis_data(company)

        return render_template('analysis.html',
                             company=company,
                             history=data['history'],
                             analysis=analysis)

    except Exception:
        return render_template('error.html',
                             message="An error occurred. Please try again."), 500

@app.template_filter('format_number')
def format_number(value):
    return "{:,.0f}".format(value)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))
    app.run(host='0.0.0.0', port=port)