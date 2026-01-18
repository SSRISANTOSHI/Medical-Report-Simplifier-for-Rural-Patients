<<<<<<< HEAD
# Medical Report Simplifier for Rural Patients

An AI-powered system that converts complex medical lab reports into simple, patient-friendly explanations using OCR and Large Language Models.

## Features

- 📄 Upload PDF or image files of medical reports
- 🔍 Extract text using OCR (Tesseract)
- 🤖 AI-powered explanations using OpenAI GPT
- 📊 Parse and identify lab values
- 💡 Provide lifestyle suggestions
- 🏥 Patient-friendly interface

## Setup Instructions

### MySQL Database Setup

1. Install MySQL server:
   - **macOS**: `brew install mysql`
   - **Ubuntu**: `sudo apt-get install mysql-server`
   - **Windows**: Download from https://dev.mysql.com/downloads/mysql/

2. Start MySQL service:
   ```bash
   # macOS
   brew services start mysql
   
   # Ubuntu
   sudo systemctl start mysql
   ```

3. Create database and tables:
   ```bash
   cd backend
   python setup_database.py
   ```

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR:
- **macOS**: `brew install tesseract`
- **Ubuntu**: `sudo apt-get install tesseract-ocr`
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki

5. Create environment file and configure database:
```bash
cp .env.example .env
```

6. Edit `.env` file with your credentials:
```
OPENAI_API_KEY=your_actual_api_key_here
MYSQL_HOST=localhost
MYSQL_DATABASE=medical_reports
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
```

7. Setup database:
```bash
python setup_database.py
```

8. Run the Flask server:
```bash
python app.py
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

## Usage

1. Start both backend (port 5000) and frontend (port 3000)
2. Open http://localhost:3000 in your browser
3. Upload a medical report (PDF or image)
4. Get simplified explanations and lifestyle tips

## Technology Stack

- **Frontend**: React.js, CSS3
- **Backend**: Python Flask
- **OCR**: Tesseract OCR
- **AI**: OpenAI GPT-3.5-turbo
- **Image Processing**: PIL, pdf2image

## Important Notes

⚠️ This tool is for educational purposes only. Always consult healthcare professionals for medical advice.

## Project Structure

```
Medical Report Simplifier for Rural Patients/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.js
    │   ├── App.css
    │   └── ...
    └── package.json
```
=======
# Medical-Report-Simplifier-for-Rural-Patients
>>>>>>> 04c02b430b15bd38eef80a6f6fc78db9a34d8cb3


