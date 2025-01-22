from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import requests
import os
from strategies import AnalysisFactory

app = Flask(__name__)
CORS(app)

DATA_SERVICE_URL = os.environ.get('DATA_SERVICE_URL', 'http://localhost:5002')


@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy'})


@app.route('/api/analysis/<company>')
def analyze_company(company):
    try:
        response = requests.get(f'{DATA_SERVICE_URL}/api/company/{company}', timeout=10)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch company data'}), 404

        data = response.json()
        if not data.get('history'):
            return jsonify({'error': 'No historical data available'}), 404

        df = pd.DataFrame(data['history'])
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        numeric_columns = ['Last_Price', 'Change_Pct', 'Volume', 'High', 'Low']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        factory = AnalysisFactory()
        strategies = ['sma', 'rsi', 'macd', 'bollinger']
        daily_analysis = {}

        for strategy_name in strategies:
            try:
                strategy = factory.create_strategy(strategy_name)
                result = strategy.analyze(df)

                if strategy_name == 'sma':
                    daily_analysis.update({
                        'sma20': result.get('sma', {}).get('sma20'),
                        'ema20': result.get('sma', {}).get('ema20')
                    })
                elif strategy_name == 'rsi':
                    daily_analysis['rsi'] = result.get('rsi', {}).get('rsi')
                elif strategy_name == 'macd':
                    macd_data = result.get('macd', {})
                    daily_analysis.update({
                        'macd': macd_data.get('macd'),
                        'signal': macd_data.get('signal'),
                        'histogram': macd_data.get('histogram')
                    })
                elif strategy_name == 'bollinger':
                    daily_analysis['bollinger'] = result.get('bollinger', {})

            except Exception:
                continue

        return jsonify({'daily': daily_analysis})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port)