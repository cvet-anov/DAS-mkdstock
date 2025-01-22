from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

class DataService:
    def __init__(self):
        self.df = None
        self.load_data()

    def load_data(self):
        try:
            possible_locations = [
                '/app/data/mse_data.csv',
                './data/mse_data.csv',
                '../data/mse_data.csv',
                '../../data/mse_data.csv'
            ]

            for location in possible_locations:
                if os.path.exists(location):
                    self.df = pd.read_csv(location)
                    self.df['Date'] = pd.to_datetime(self.df['Date'])
                    self.df = self.df.sort_values('Date', ascending=False)
                    return
        except Exception as e:
            self.df = pd.DataFrame()

data_service = DataService()

@app.route('/api/health')
def health_check():
    if data_service.df is None or data_service.df.empty:
        return jsonify({'status': 'unhealthy', 'message': 'No data loaded'}), 500
    return jsonify({'status': 'healthy', 'rows': len(data_service.df)})

@app.route('/api/companies')
def get_companies():
    if data_service.df is None or data_service.df.empty:
        return jsonify({'error': 'No data available'}), 404
    companies = data_service.df['Company'].unique().tolist()
    return jsonify({'companies': companies})

@app.route('/api/company/<company>')
def get_company_data(company):
    if data_service.df is None or data_service.df.empty:
        return jsonify({'error': 'No data available'}), 404

    company_df = data_service.df[data_service.df['Company'] == company].copy()
    if company_df.empty:
        return jsonify({'error': f'No data found for company {company}'}), 404

    result = []
    for _, row in company_df.iterrows():
        result.append({
            'Date': row['Date'].strftime('%Y-%m-%d'),
            'Last_Price': float(row['Last_Price']),
            'Change_Pct': float(row['Change_Pct']),
            'Volume': float(row['Volume']),
            'High': float(row['High']),
            'Low': float(row['Low'])
        })

    return jsonify({'history': result})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port)