import requests

class PromptShieldPTIT:
    def __init__(self,
            OPEN_API_KEY: str = "",
            MODEL: str = "",
            # ENDPOINT_MODEL_FINE_TUNING_PREDICT: str = "",
            ENDPOINT_MODEL_PREDICT: str = "http://3.106.222.193:8000/predict",
            ENDPOINT_VECTOR_SEARCH: str = "http://3.25.196.243:8001/search",
            
        ) -> None:
        # self.ENDPOINT_MODEL_FINE_TUNING_PREDICT = ENDPOINT_MODEL_FINE_TUNING_PREDICT
        self.ENDPOINT_MODEL_PREDICT = ENDPOINT_MODEL_PREDICT
        self.ENDPOINT_VECTOR_SEARCH = ENDPOINT_VECTOR_SEARCH

    def model_fine_tuning_detect_PI(self, prompt: str) -> tuple[str, float]:
        response = requests.post(self.ENDPOINT_MODEL_FINE_TUNING_PREDICT, json={"text": prompt})
        label, score = response.json()["label"], response.json()["score"]
        return label, score

    def model_detect_PI(self, prompt: str) -> tuple[str, float]:
        response = requests.post(self.ENDPOINT_MODEL_PREDICT, json={"text": prompt})
        label, score = response.json()["label"], response.json()["score"]
        return label, score

    def vector_search_detect_PI(self, prompt: str) -> tuple[str, float]:
        response = requests.post(self.ENDPOINT_VECTOR_SEARCH, json={"text": prompt})
        label = response.json()["label"]
        score = response.json()["score"]
        return label, score

    def detect_PI(self, prompt: str, score_weighted_threshold: float = 0.7, score_combined_threshold: float = 0.7) -> dict:
        try:
            model_label, model_score = self.model_detect_PI(prompt)
            vector_label, vector_score = self.vector_search_detect_PI(prompt)
            
            is_model_malicious = model_label == "injection"
            is_vector_malicious = vector_label == "injection"
            
            model_weight = 1.5 if model_score >= score_weighted_threshold else 1.0
            vector_weight = 1.5 if vector_score >= score_weighted_threshold else 1.0
            
            model_contribute = model_weight * model_score if is_model_malicious else 0
            vector_contribute = vector_weight * vector_score if is_vector_malicious else 0

            total_weight = model_weight + vector_weight
            combined_score = (model_contribute + vector_contribute) / total_weight

            is_injection = combined_score >= score_combined_threshold

            return {
                "is_injection": is_injection,
                "details": {
                    "model_label": model_label,
                    "model_score": model_score,
                    "vector_label": vector_label,
                    "vector_score": vector_score,
                    "score_weighted_threshold": score_weighted_threshold,
                    "combined_score": combined_score,
                    "score_combined_threshold": score_combined_threshold,
                    "model_weight": model_weight,
                    "vector_weight": vector_weight,
                    "total_weight": total_weight,
                }
            }   
        
        except Exception as e:
            return {
                "is_injection": False,
                "details": {
                    "model_label": None,
                    "model_score": 0,
                    "vector_label": None,
                    "vector_score": 0,
                    "combined_score": 0,
                    "model_contribute": 0,
                    "vector_contribute": 0,
                    "model_weight": 0,
                    "vector_weight": 0,
                    "total_weight": 0,
                },
                "error": str(e)
            }
