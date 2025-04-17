# Transaction Generator Web

A simple web application for generating synthetic transaction data using a user-friendly interface. This tool is ideal for testing financial platforms, building demo environments, or populating databases with mock transactions.

## 🚀 Features

- Generate realistic financial transactions on demand
- Customize transaction types, dates, and amounts
- Export transactions as JSON or CSV
- Minimal and responsive web UI built with Dash
- Ideal for fintech demos, testing, or education

## 🛠️ Tech Stack

- Python 3.9+
- [Dash](https://dash.plotly.com/) for the web UI
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)
- Pandas for data processing
- dotenv for environment management

## 🧑‍💻 Getting Started

### 1. Clone the Repository

git clone https://github.com/magpie8/transaction_generator_web.git
cd transaction_generator_web

### 2. Create and Activate a Virtual Environment
bash
Copy
Edit
python3 -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate

### 3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt

### 4. Run the Application
bash
Copy
Edit
python app.py
Then visit http://localhost:8050 in your browser.

📁 Project Structure
bash
Copy
Edit
transaction_generator_web/
├── app.py                 # Main Dash app
├── assets/                # Custom stylesheets (optional)
├── data/                  # Output or input data files (optional)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
📦 Output Formats
CSV: Flat structured data for spreadsheets or data ingestion

JSON: Easy to parse for APIs or client-side processing

✍️ Customization
You can modify the following in app.py to suit your needs:

Transaction templates (merchant names, categories, descriptions)

Currency, amount ranges

Export format logic

🤝 Contributing
Contributions are welcome! To contribute:

Fork this repository

Create a new branch (git checkout -b feature/your-feature)

Commit your changes (git commit -am 'Add a new feature')

Push to the branch (git push origin feature/your-feature)

Create a pull request

📄 License
This project is licensed under the MIT License.
