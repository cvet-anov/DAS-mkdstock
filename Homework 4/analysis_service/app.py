from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import requests
import os
from strategies import AnalysisFactory

app = Flask(__name__)
CORS(app)

DATA_SERVICE_URL = os.environ.get('DATA_SERVICE_URL', 'http://localhost:5001')


@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy'})


@app.route('/api/analysis/<company>')
def analyze_company(company):
    try:
        # Get data from data service
        response = requests.get(f'{DATA_SERVICE_URL}/api/company/{company}')
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch company data'}), 404

        data = response.json()
        df = pd.DataFrame(data['history'])
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        # Create analysis strategies
        factory = AnalysisFactory()
        strategies = ['sma', 'rsi', 'macd', 'bollinger']

        # Perform analysis
        analysis = {}
        for strategy_name in strategies:
            strategy = factory.create_strategy(strategy_name)
            analysis[strategy_name] = strategy.analyze(df)

        return jsonify(analysis)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port)