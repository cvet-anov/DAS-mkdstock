from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)


def load_data():
    try:
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for mse_data.csv...")

        if not os.path.exists('mse_data.csv'):
            print("Error: mse_data.csv not found!")
            return pd.DataFrame()

        df = pd.read_csv('mse_data.csv')
        print(f"Successfully loaded data with shape: {df.shape}")

        df['Date'] = pd.to_datetime(df['Date'])

        df = df.sort_values('Date', ascending=False)

        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

@app.template_filter('format_number')
def format_number(value):
    return "{:,.0f}".format(value)


@app.route('/')
def home():
    df = load_data()
    if df.empty:
        return "Error: Could not load data. Please check if mse_data.csv exists and is properly formatted."

    companies = df['Company'].unique().tolist()[:9]  # Get first 9 companies for grid
    company_data = []
    total_volume = 0

    for company in companies:
        company_df = df[df['Company'] == company].iloc[0]
        total_volume += float(company_df['Volume'])
        company_data.append({
            'name': company,
            'last_price': float(company_df['Last_Price']),
            'change': float(company_df['Change_Pct']),
            'volume': float(company_df['Volume']),
            'date': company_df['Date'].strftime('%d.%m.%Y'),
            'high': float(company_df['High']),
            'low': float(company_df['Low'])
        })

    return render_template('index.html',
                           companies=company_data,
                           total_volume=total_volume)


@app.route('/company/<company>')
def company_detail(company):
    print(f"Loading data for company: {company}")
    df = load_data()

    if df.empty:
        return "Error: Could not load data"

    company_df = df[df['Company'] == company].copy()
    if company_df.empty:
        return f"No data found for company {company}"

    history = []
    for _, row in company_df.iterrows():
        history.append({
            'Date': row['Date'].strftime('%d.%m.%Y'),
            'Last_Price': float(row['Last_Price']),
            'Change_Pct': float(row['Change_Pct']),
            'Volume': float(row['Volume']),
            'High': float(row['High']),  
            'Low': float(row['Low'])
        })

    latest = history[0] if history else None

    return render_template('company.html',
                         company=company,
                         history=history,
                         latest=latest)


@app.route('/api/debug')
def debug_info():
    """Endpoint to check data loading and formatting"""
    df = load_data()
    if df.empty:
        return jsonify({
            "error": "No data loaded",
            "cwd": os.getcwd(),
            "files_in_directory": os.listdir()
        })

    return jsonify({
        "data_shape": df.shape,
        "columns": df.columns.tolist(),
        "sample_data": df.head(1).to_dict('records'),
        "companies": df['Company'].unique().tolist()[:5]
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)