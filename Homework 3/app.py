from flask import Flask, render_template, jsonify
import pandas as pd
import os
from flask import send_from_directory
from analysis.technical import TechnicalAnalysis

app = Flask(__name__)

def load_data():
    try:
        # Print current directory for debugging
        current_dir = os.getcwd()
        print(f"Current working directory: {current_dir}")

        # Try multiple possible locations for the CSV file
        possible_locations = [
            'mse_data.csv',  # Same directory
            '../Homework 1/mse_data.csv',  # HW1 directory
            os.path.join(current_dir, 'mse_data.csv'),  # Absolute path
            os.path.join(current_dir, '../Homework 1/mse_data.csv')  # Absolute path to HW1
        ]

        df = None
        used_path = None

        for file_path in possible_locations:
            print(f"Trying to load from: {file_path}")
            if os.path.exists(file_path):
                print(f"Found file at: {file_path}")
                df = pd.read_csv(file_path)
                used_path = file_path
                break

        if df is None:
            print("Error: mse_data.csv not found in any of these locations:")
            for loc in possible_locations:
                print(f"- {loc}")
            return pd.DataFrame()

        print(f"Successfully loaded data from {used_path} with shape: {df.shape}")

        # Data preprocessing
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date', ascending=False)

        # Verify data is loaded correctly
        print("Sample of loaded data:")
        print(df.head())

        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return pd.DataFrame()

@app.template_filter('format_number')
def format_number(value):
    return "{:,.0f}".format(value)

@app.route('/')
def home():
    df = load_data()
    if df.empty:
        return "Error: Could not load data. Please check if mse_data.csv exists and is properly formatted."

    companies = df['Company'].unique().tolist()[:9]
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

@app.route('/analysis/<company>')
def technical_analysis(company):
    df = load_data()
    if df.empty:
        return "Error: Could not load data"

    company_df = df[df['Company'] == company].copy()
    if company_df.empty:
        return f"No data found for company {company}"

    # Sort data by date
    company_df = company_df.sort_values('Date')

    # Calculate technical indicators
    analyzer = TechnicalAnalysis(company_df)
    analysis = analyzer.analyze_all_periods()

    # Prepare historical data for plotting
    history = []
    for _, row in company_df.iterrows():
        history.append({
            'Date': row['Date'].strftime('%Y-%m-%d'),
            'Last_Price': float(row['Last_Price']) if not pd.isna(row['Last_Price']) else None,
            'Volume': float(row['Volume']) if not pd.isna(row['Volume']) else 0,
            'High': float(row['High']) if not pd.isna(row['High']) else None,
            'Low': float(row['Low']) if not pd.isna(row['Low']) else None,
            'Change_Pct': float(row['Change_Pct']) if not pd.isna(row['Change_Pct']) else 0
        })

    return render_template('analysis.html',
                         company=company,
                         analysis=analysis,
                         history=history)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

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