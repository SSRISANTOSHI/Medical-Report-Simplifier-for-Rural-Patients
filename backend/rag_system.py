import chromadb
from medical_knowledge import MEDICAL_KNOWLEDGE_BASE

class MedicalRAGSystem:
    def __init__(self):
        try:
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection("medical_knowledge")
            self.knowledge_base = MEDICAL_KNOWLEDGE_BASE
            self._populate_collection()
        except Exception as e:
            print(f"ChromaDB error: {e}")
            self.collection = None
            self.knowledge_base = MEDICAL_KNOWLEDGE_BASE
    
    def _populate_collection(self):
        if not self.collection:
            return
        
        try:
            documents = []
            metadatas = []
            ids = []
            
            for i, item in enumerate(self.knowledge_base):
                doc = f"{item['test']}: {item['description']}. Normal: {item['normal_range']}. Tips: {item['lifestyle_tips']}"
                documents.append(doc)
                metadatas.append(item)
                ids.append(f"med_{i}")
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            print(f"ChromaDB populate error: {e}")
    
    def retrieve_relevant_info(self, query, top_k=3):
        if not self.collection:
            return [item for item in self.knowledge_base[:top_k]]
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            return results['metadatas'][0] if results['metadatas'] else []
        except Exception as e:
            print(f"ChromaDB query error: {e}")
            return []
    
    def generate_rag_context(self, lab_values, extracted_text):
        context_info = []
        
        for test_name, value in lab_values.items():
            query = f"{test_name} lab test {value}"
            relevant_docs = self.retrieve_relevant_info(query, top_k=2)
            context_info.extend(relevant_docs)
        
        return context_info[:5] if context_info else self.knowledge_base[:3]