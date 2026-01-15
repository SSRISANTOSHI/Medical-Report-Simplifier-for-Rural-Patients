from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import json

class HuggingFaceLLM:
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            # Use a lightweight model suitable for medical text generation
            self.model_name = "microsoft/BioGPT-Large" if torch.cuda.is_available() else "distilgpt2"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
        except Exception as e:
            print(f"Error loading HuggingFace model: {e}")
            # Fallback to a simpler model
            self.model_name = "distilgpt2"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def generate_explanation(self, lab_values, rag_context, extracted_text):
        """Generate medical explanation using HuggingFace model"""
        try:
            # Build context from RAG
            context_str = " ".join([f"{item['test']} normal range {item['normal_range']}" for item in rag_context])
            
            # Create prompt
            prompt = f"Medical report explanation: {context_str}. Lab values: {json.dumps(lab_values)}. Simple explanation:"
            
            # Tokenize and generate
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 200,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            explanation_text = response[len(prompt):].strip()
            
            # Structure the response
            return {
                "summary": explanation_text[:200] + "..." if len(explanation_text) > 200 else explanation_text,
                "test_explanations": {test: f"Your {test} level is {value}" for test, value in lab_values.items()},
                "lifestyle_tips": [
                    "Maintain a balanced diet with fruits and vegetables",
                    "Exercise regularly as recommended by your doctor", 
                    "Stay hydrated by drinking plenty of water",
                    "Get adequate sleep and manage stress"
                ],
                "when_to_see_doctor": "Please consult your healthcare provider to discuss these results and get personalized medical advice."
            }
            
        except Exception as e:
            print(f"HuggingFace generation error: {e}")
            return {
                "summary": "Lab report processed. Please consult your doctor for detailed explanation.",
                "test_explanations": {test: f"Your {test} value is {value}" for test, value in lab_values.items()},
                "lifestyle_tips": ["Eat healthy foods", "Exercise regularly", "Stay hydrated"],
                "when_to_see_doctor": "Consult your healthcare provider for medical advice."
            }