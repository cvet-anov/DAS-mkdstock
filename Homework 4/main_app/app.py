from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

DATA_SERVICE_URL = os.environ.get('DATA_SERVICE_URL', 'http://localhost:5001')
ANALYSIS_SERVICE_URL = os.environ.get('ANALYSIS_SERVICE_URL', 'http://localhost:5002')


@app.route('/')
def home():
    try:
        # Get companies from data service
        response = requests.get(f'{DATA_SERVICE_URL}/api/companies')
        if response.status_code != 200:
            return "Error: Could not load companies"

        companies = response.json()['companies']
        company_data = []

        for company in companies[:9]:
            # Get company details
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

    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/company/<company>')
def company_detail(company):
    try:
        # Get company data
        response = requests.get(f'{DATA_SERVICE_URL}/api/company/{company}')
        if response.status_code != 200:
            return f"Error: Could not load data for {company}"

        # Get analysis
        analysis_response = requests.get(f'{ANALYSIS_SERVICE_URL}/api/analysis/{company}')
        analysis = analysis_response.json() if analysis_response.status_code == 200 else {}

        return render_template('company.html',
                               company=company,
                               history=response.json()['history'],
                               analysis=analysis)

    except Exception as e:
        return f"Error: {str(e)}"


@app.template_filter('format_number')
def format_number(value):
    return "{:,.0f}".format(value)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
