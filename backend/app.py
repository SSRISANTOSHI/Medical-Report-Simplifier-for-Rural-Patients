from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import pdf2image
import os
import tempfile
import re
from openai import OpenAI
import json
from rag_system import MedicalRAGSystem
from database import MySQLDatabase
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize RAG system and database
rag_system = MedicalRAGSystem()
db = MySQLDatabase()

class MedicalReportProcessor:
    def __init__(self):
        self.medical_knowledge = {
            "hemoglobin": {"normal_range": "12-16 g/dL", "description": "Carries oxygen in blood"},
            "glucose": {"normal_range": "70-100 mg/dL", "description": "Blood sugar level"},
            "cholesterol": {"normal_range": "<200 mg/dL", "description": "Fat in blood"},
            "blood_pressure": {"normal_range": "120/80 mmHg", "description": "Heart pumping pressure"},
            "creatinine": {"normal_range": "0.6-1.2 mg/dL", "description": "Kidney function marker"}
        }
    
    def extract_text_from_image(self, image_path):
        """Extract text from image using OCR"""
        try:
            image = Image.open(image_path)
            # Enhance image for better OCR
            image = image.convert('RGB')
            text = pytesseract.image_to_string(image, config='--psm 6')
            return text
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using OCR"""
        try:
            pages = pdf2image.convert_from_path(pdf_path, dpi=300)
            text = ""
            for page in pages:
                # Enhance image for better OCR
                page = page.convert('RGB')
                text += pytesseract.image_to_string(page, config='--psm 6') + "\n"
            return text
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"
    
    def parse_lab_values(self, text):
        """Parse lab values from extracted text"""
        values = {}
        
        # Enhanced patterns for lab values and medical conditions
        patterns = {
            'hemoglobin': r'(?:hemoglobin|hb|hgb).*?(\d+\.?\d*)',
            'glucose': r'(?:glucose|sugar|fbs).*?(\d+\.?\d*)',
            'cholesterol': r'(?:cholesterol|chol).*?(\d+\.?\d*)',
            'creatinine': r'(?:creatinine|creat).*?(\d+\.?\d*)',
            'white_blood_cells': r'(?:wbc|white.*?blood.*?cells?).*?(\d+\.?\d*)',
            'platelets': r'(?:platelets?|plt).*?(\d+\.?\d*)',
            'blood_pressure': r'(?:bp|blood.*?pressure).*?(\d+)/(\d+)',
            'hypertension': r'hypertension',
            'chest_pain': r'chest.*?pain',
            'palpitations': r'palpitations',
            'shortness_of_breath': r'shortness.*?breath'
        }
        
        for test, pattern in patterns.items():
            if test == 'blood_pressure':
                match = re.search(pattern, text.lower())
                if match:
                    values[test] = f"{match.group(1)}/{match.group(2)}"
            elif test in ['hypertension', 'chest_pain', 'palpitations', 'shortness_of_breath']:
                match = re.search(pattern, text.lower())
                if match:
                    values[test] = "present"
            else:
                match = re.search(pattern, text.lower())
                if match:
                    values[test] = float(match.group(1))
        
        return values
    
    def generate_explanation_with_rag(self, lab_values, extracted_text):
        """Generate explanation using RAG system"""
        try:
            if rag_system:
                rag_context = rag_system.generate_rag_context(lab_values, extracted_text)
                context_str = "\n".join([f"- {item['test']}: {item['description']}. Normal: {item['normal_range']}. Tips: {item['lifestyle_tips']}" for item in rag_context])
            else:
                context_str = "Basic medical knowledge available."
            
            prompt = f"""
            You are a medical assistant helping rural patients understand their lab reports.
            
            MEDICAL CONTEXT FROM KNOWLEDGE BASE:
            {context_str}
            
            PATIENT'S LAB VALUES: {json.dumps(lab_values)}
            REPORT TEXT: {extracted_text[:800]}
            
            Provide a simple explanation using the medical context above:
            1. Explain each test in simple terms
            2. Compare values to normal ranges
            3. Provide lifestyle suggestions (NO diagnosis/medication)
            4. Use simple language for rural patients
            5. Assess overall risk level as "Low", "Medium", or "High" based on the values.
            
            Return JSON: {{"summary": "", "test_explanations": {{}}, "lifestyle_tips": [], "when_to_see_doctor": "", "risk_level": "Low/Medium/High"}}
            """
            
            if client:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                return json.loads(response.choices[0].message.content)
            else:
                return self._fallback_explanation(lab_values)
                
        except Exception as e:
            return self._fallback_explanation(lab_values)
    
    def _fallback_explanation(self, lab_values):
        # Enhanced fallback for medical conditions
        risk_level = "Low"
        if 'hypertension' in lab_values:
            summary = "Medical report shows hypertension (high blood pressure) and related symptoms."
            tips = [
                "Reduce salt intake in your diet",
                "Exercise regularly as advised by your doctor", 
                "Take prescribed blood pressure medication",
                "Monitor your blood pressure regularly"
            ]
            risk_level = "High"
        elif any(condition in lab_values for condition in ['chest_pain', 'palpitations', 'shortness_of_breath']):
            summary = "Medical report shows cardiovascular symptoms that need attention."
            tips = [
                "Avoid strenuous activities until cleared by doctor",
                "Eat heart-healthy foods",
                "Stay hydrated and get adequate rest"
            ]
            risk_level = "Medium"
        else:
            summary = f"Found {len(lab_values)} medical findings in your report."
            tips = ["Maintain a healthy diet", "Exercise regularly", "Stay hydrated"]
            if len(lab_values) > 3:
                risk_level = "Medium"
            
        return {
            "summary": summary,
            "test_explanations": {test: f"Your report shows {test.replace('_', ' ')}: {value}" for test, value in lab_values.items()},
            "lifestyle_tips": tips,
            "when_to_see_doctor": "Please consult your healthcare provider for medical advice about these findings.",
            "risk_level": risk_level
        }

processor = MedicalReportProcessor()

@app.route('/api/upload', methods=['POST'])
def upload_report():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            file.save(tmp_file.name)
            
            # Extract text based on file type
            if file.filename.lower().endswith('.pdf'):
                extracted_text = processor.extract_text_from_pdf(tmp_file.name)
            else:
                extracted_text = processor.extract_text_from_image(tmp_file.name)
            
            # Debug: Print extracted text
            print(f"Extracted text length: {len(extracted_text)}")
            print(f"First 200 chars: {extracted_text[:200]}")
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
        
        # If OCR fails, use fallback text for testing
        if not extracted_text or len(extracted_text.strip()) < 10:
            extracted_text = "No text extracted from file"
        
        # Parse lab values
        lab_values = processor.parse_lab_values(extracted_text)
        
        # Generate explanation using RAG
        explanation = processor.generate_explanation_with_rag(lab_values, extracted_text)
        
        # Save to database
        if db:
            report_id = db.save_report(file.filename, extracted_text, lab_values, explanation)
        else:
            report_id = None
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'extracted_text': extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            'lab_values': lab_values,
            'explanation': explanation
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """Get specific report by ID"""
    report = db.get_report(report_id)
    if report:
        return jsonify({'success': True, 'report': report})
    return jsonify({'error': 'Report not found'}), 404

@app.route('/api/reports', methods=['GET'])
def get_recent_reports():
    """Get recent reports"""
    reports = db.get_recent_reports()
    return jsonify({'success': True, 'reports': reports})

if __name__ == '__main__':
    print("🏥 Starting Medical Report Simplifier Backend...")
    print("🌐 Server will run at: http://localhost:5001")
    app.run(debug=True, port=5001, host='0.0.0.0')