import os
import json
import hashlib
from pathlib import Path
from collections import deque
import time
import threading

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.pipeline import Pipeline
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class AIThreatDetector:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".deadlock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.model_file = self.config_dir / "ai_threat_model.json"
        self.threat_history_file = self.config_dir / "threat_history.json"
        
        self.ransomware_extensions = {
            ".locky", ".zepto", ".wannacry", ".cryptolocker", ".petya", 
            ".notpetya", ".cerber", ".teslacrypt", ".xtbl", ".aaa", ".abc", 
            ".xyz", ".zzz", ".micro", ".delta", ".gws", ".onion", ".ft", 
            ".kraken", ".lock", ".encrypted", ".crypto", ".codercrypt", 
            ".ryuk", ".maze", ".doppelpaymer", ".conti", ".clop", ".avaddon"
        }
        
        self.suspicious_keywords = {
            "encrypt", "decrypt", "ransom", "bitcoin", "pay", "decryptor",
            "your_files_are_encrypted", "readme", "how_to_back", "instructions"
        }
        
        self.operation_history = deque(maxlen=1000)
        self.last_check_time = time.time()
        
        self.model = None
        self.vectorizer = None
        self._initialize_model()
        self._load_threat_history()
        
        self.lock = threading.Lock()

    def _initialize_model(self):
        if HAS_SKLEARN:
            if self.model_file.exists():
                try:
                    with open(self.model_file, "r") as f:
                        model_data = json.load(f)
                    print("[AI Threat Detector] Model loaded from disk")
                except:
                    self._train_default_model()
            else:
                self._train_default_model()
        else:
            print("[AI Threat Detector] scikit-learn not found - using rule-based detection only")

    def _train_default_model(self):
        if not HAS_SKLEARN:
            return
        
        training_data = [
            ("invoice.pdf", 0), ("report.docx", 0), ("photo.jpg", 0),
            ("budget.xlsx", 0), ("notes.txt", 0), ("music.mp3", 0),
            ("video.mp4", 0), ("document.pdf", 0), ("spreadsheet.xlsx", 0),
            ("readme.txt", 0), ("important.docx", 0), ("archive.zip", 0),
            
            ("file.encrypted", 1), ("data.locky", 1), ("files.wannacry", 1),
            ("important.crypt", 1), ("readme_for_decrypt.txt", 1),
            ("how_to_get_your_files_back.txt", 1), ("your_files.xyz", 1),
            ("bitcoin_payment.txt", 1), ("decrypt_instructions.txt", 1),
            ("locked_files.aaa", 1), ("ransom_note.txt", 1)
        ]
        
        texts, labels = zip(*training_data)
        
        self.pipeline = Pipeline([
            ("vectorizer", CountVectorizer(analyzer="char_wb", ngram_range=(2, 4))),
            ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        self.pipeline.fit(texts, labels)
        print("[AI Threat Detector] Default AI model trained successfully")
        
        self._save_model()

    def _save_model(self):
        if HAS_SKLEARN and self.pipeline:
            model_data = {
                "type": "sklearn_pipeline",
                "version": "1.0"
            }
            with open(self.model_file, "w") as f:
                json.dump(model_data, f)

    def _load_threat_history(self):
        if self.threat_history_file.exists():
            try:
                with open(self.threat_history_file, "r") as f:
                    self.threat_history = json.load(f)
            except:
                self.threat_history = []
        else:
            self.threat_history = []

    def _save_threat_history(self):
        with open(self.threat_history_file, "w") as f:
            json.dump(self.threat_history[-1000:], f)

    def analyze_file_path(self, file_path):
        file_path = str(file_path).lower()
        file_ext = Path(file_path).suffix.lower()
        file_name = Path(file_path).name.lower()
        
        threat_score = 0
        threat_reasons = []
        
        if file_ext in self.ransomware_extensions:
            threat_score += 50
            threat_reasons.append(f"Suspicious ransomware extension: {file_ext}")
        
        for keyword in self.suspicious_keywords:
            if keyword in file_name:
                threat_score += 30
                threat_reasons.append(f"Suspicious keyword: {keyword}")
        
        if HAS_SKLEARN and self.pipeline:
            try:
                ai_prediction = self.pipeline.predict([file_path])[0]
                ai_probability = self.pipeline.predict_proba([file_path])[0][1]
                
                if ai_prediction == 1:
                    threat_score += int(ai_probability * 40)
                    threat_reasons.append(f"AI detected suspicious pattern (confidence: {ai_probability:.2%})")
            except Exception as e:
                print(f"[AI Threat Detector] AI prediction error: {e}")
        
        return {
            "is_threat": threat_score >= 50,
            "threat_score": threat_score,
            "threat_reasons": threat_reasons,
            "file_path": file_path
        }

    def analyze_operations(self, operations):
        current_time = time.time()
        time_window = 10
        
        with self.lock:
            self.operation_history.extend([(current_time, op) for op in operations])
            
            recent_ops = [
                op for ts, op in self.operation_history 
                if ts > current_time - time_window
            ]
            
            threat_score = 0
            threat_reasons = []
            
            if len(recent_ops) > 50:
                threat_score += 40
                threat_reasons.append(f"Mass file operations: {len(recent_ops)} operations in {time_window} seconds")
            
            rename_count = sum(1 for op in recent_ops if op.get("type") == "rename")
            if rename_count > 20:
                threat_score += 35
                threat_reasons.append(f"Suspicious mass rename operations: {rename_count}")
            
            modified_count = sum(1 for op in recent_ops if op.get("type") == "modified")
            if modified_count > 30:
                threat_score += 35
                threat_reasons.append(f"High volume of file modifications: {modified_count}")
            
            return {
                "is_threat": threat_score >= 50,
                "threat_score": threat_score,
                "threat_reasons": threat_reasons,
                "operation_count": len(recent_ops)
            }

    def log_threat(self, threat_info):
        threat_entry = {
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
            **threat_info
        }
        self.threat_history.append(threat_entry)
        self._save_threat_history()
        print(f"[AI Threat Detector] Threat logged: {threat_info}")

    def get_threat_history(self, limit=100):
        return self.threat_history[-limit:]


if __name__ == "__main__":
    detector = AIThreatDetector()
    
    test_files = [
        "important_document.pdf",
        "financial_report.xlsx", 
        "company_data.locky",
        "readme_for_decrypt.txt",
        "vacation_photos.jpg"
    ]
    
    print("Testing AI Threat Detector...")
    for test_file in test_files:
        result = detector.analyze_file_path(test_file)
        print(f"\nFile: {test_file}")
        print(f"Is threat: {result['is_threat']}")
        print(f"Threat score: {result['threat_score']}")
        print(f"Reasons: {result['threat_reasons']}")
