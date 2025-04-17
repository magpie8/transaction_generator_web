from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session  # Added session here
import csv
import os
import random
from datetime import datetime, date
import calendar
from typing import Dict, List
from io import StringIO
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_product_prices(csv_path: str) -> Dict[str, float]:
    product_prices = {}
    
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        if not all(field in reader.fieldnames for field in ['ProductID', 'Price']):
            raise ValueError("CSV must contain 'ProductID' and 'Price' columns.")
            
        for row in reader:
            if not row['ProductID'] or not row['Price']:
                continue
            product_prices[row['ProductID']] = float(row['Price'])
    
    if not product_prices:
        raise ValueError("No valid product prices found in CSV.")
    
    return product_prices

def generate_random_units_per_month(min_units: float = 1.0, max_units: float = 25.0, precision: int = 1) -> Dict[str, float]:
    units_per_month = {}
    for month in range(1, 13):
        month_abbr = calendar.month_abbr[month].lower()
        units = round(random.uniform(min_units, max_units), precision)
        units_per_month[month_abbr] = units
    return units_per_month

def generate_data(
    num_records: int,
    year: int,
    month: int,
    units_max: int,
    product_ids: List[str],
    total_products: int,
    product_prices: Dict[str, float],
    supplier_id: str
) -> List[Dict]:
    data = []
    branches = [
        'ABG', 'ALB', 'AUK', 'BAL', 'BLM', 'BAY', 'BRN', 'BRI',
        'BUN', 'CAM', 'CBR', 'CAN', 'CHT', 'CHR', 'COB', 'COF',
        'DAR', 'DUB', 'ESS', 'FRK', 'GEE', 'GLF', 'GLC', 'HAM',
        'HOB', 'HOR', 'INV', 'JOO', 'KEW', 'LAU', 'LOG', 'MAN',
        'MAI', 'MRO', 'MEL', 'NPL', 'NCL', 'NOR', 'NSH', 'ORA',
        'PER', 'PAK', 'PAD', 'QUE', 'ROC', 'SRH', 'SUN', 'TAM',
        'TOW', 'WAG', 'WAR', 'WEL', 'WER', 'WOL', 'YAR', 'YEO'
    ]

    num_days_in_month = calendar.monthrange(year, month)[1]
    
    for i in range(num_records):
        day_offset = i % num_days_in_month
        transaction_date = date(year, month, day_offset + 1)
        
        supplier = supplier_id
        branch = random.choice(branches)
        invoice_status = 'Paid'

        product_id = product_ids[i % total_products]
        transaction_type = 'Purchase'
        units = random.randint(1, units_max)
        price_per_unit = product_prices[product_id]
        value = round(units * price_per_unit, 3)
        currency = 'AUD'
        external_ref = ''
        interface_date = ''

        month_str = f"{month:02d}"
        primary_key = f"{supplier_id}-PRI-{month_str}-{year}-{i + 1}"
        agreement_id = ''
        advised_earnings = ''
        order_reference = ''
        delivery_reference = ''
        invoice_reference = f"{supplier_id}-INV-{month_str}-{year}-{i + 1}"

        data.append({
            'Date': transaction_date.strftime('%d/%m/%Y'),
            'Supplier': supplier,
            'Branch': branch,
            'Invoice status': invoice_status,
            'Product': product_id,
            'Transaction Type': transaction_type,
            'Units': units,
            'Value': value,
            'Currency': currency,
            'External Reference': external_ref,
            'Interface Date': interface_date,
            'Primary Key': primary_key,
            'Agreement ID': agreement_id,
            'Advised Earnings': advised_earnings,
            'Order Reference': order_reference,
            'Delivery Reference': delivery_reference,
            'Invoice Reference': invoice_reference
        })
    
    return data

def generate_transaction_data(supplier_id, year, price_file):
    try:
        product_prices = load_product_prices(price_file)
    except (ValueError, FileNotFoundError) as error:
        raise Exception(f"Error loading product prices: {error}")

    product_ids = list(product_prices.keys())
    total_products = len(product_ids)
    num_records_per_month = total_products

    units_per_month = generate_random_units_per_month()
    consolidated_data = []

    output = StringIO()
    csv_writer = csv.DictWriter(output, fieldnames=[
        'Date', 'Supplier', 'Branch', 'Invoice status', 'Product',
        'Transaction Type', 'Units', 'Value', 'Currency',
        'External Reference', 'Interface Date', 'Primary Key',
        'Agreement ID', 'Advised Earnings', 'Order Reference',
        'Delivery Reference', 'Invoice Reference'
    ])
    csv_writer.writeheader()

    for month in range(1, 13):
        month_name_abbr = calendar.month_abbr[month].lower()
        units_max = int(units_per_month.get(month_name_abbr, 6))

        sample_data = generate_data(
            num_records_per_month,
            year,
            month,
            units_max,
            product_ids,
            total_products,
            product_prices,
            supplier_id
        )

        consolidated_data.extend(sample_data)
        csv_writer.writerows(sample_data)

    output.seek(0)
    return output.getvalue(), units_per_month, total_products

@app.template_filter('capitalize')
def capitalize_filter(s):
    return s.capitalize()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                supplier_id = request.form.get('supplier_id', 'S012')
                year = int(request.form.get('year', 2024))
                
                # Save uploaded file temporarily
                filename = secure_filename(file.filename)
                temp_dir = tempfile.mkdtemp()
                filepath = os.path.join(temp_dir, filename)
                file.save(filepath)
                
                # Generate transaction data
                csv_data, units_per_month, total_products = generate_transaction_data(
                    supplier_id, year, filepath
                )
                
                # Clean up
                os.remove(filepath)
                os.rmdir(temp_dir)
                
                # Save CSV to temp file
                temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
                temp_csv.write(csv_data.encode('utf-8'))
                temp_csv.close()
                
                # Store info in session
                session['csv_path'] = temp_csv.name
                session['stats'] = {
                    'supplier_id': supplier_id,
                    'year': year,
                    'total_products': total_products,
                    'units_per_month': units_per_month
                }
                
                return redirect(url_for('download'))
            
            except Exception as e:
                flash(str(e))
                return redirect(request.url)
    
    return render_template('index.html')

@app.route('/download')
def download():
    if 'csv_path' not in session:
        flash('No generated file found')
        return redirect(url_for('index'))
    
    stats = session.get('stats', {})
    return render_template('download.html', stats=stats)

@app.route('/download-csv')
def download_csv():
    if 'csv_path' not in session:
        flash('No generated file found')
        return redirect(url_for('index'))
    
    csv_path = session['csv_path']
    
    def cleanup():
        if os.path.exists(csv_path):
            os.remove(csv_path)
        session.pop('csv_path', None)
        session.pop('stats', None)
    
    response = send_file(
        csv_path,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"transactions_{session['stats']['supplier_id']}_{session['stats']['year']}.csv"
    )
    response.call_on_close(cleanup)
    return response

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)