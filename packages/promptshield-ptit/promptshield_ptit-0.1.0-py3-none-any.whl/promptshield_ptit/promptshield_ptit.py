import requests

MAX_HEURISTIC_SCORE = 0.75
MAX_MODEL_FINE_TUNING_SCORE = 0.90
MAX_VECTOR_SEARCH_SCORE = 0.6


class PromptShieldPTIT:
    def __init__(self,
            OPEN_API_KEY: str = "",
            MODEL: str = "",
            # ENDPOINT_MODEL_FINE_TUNING_PREDICT: str = "",
            ENDPOINT_MODEL_DMPI_PMHFE_PREDICT: str = "http://3.106.222.193:8000/predict",
            ENDPOINT_PROMPT_INJECTION_VECTOR_SEARCH: str = "http://3.25.196.243:8001/search",
            
        ) -> None:
        # self.ENDPOINT_MODEL_FINE_TUNING_PREDICT = ENDPOINT_MODEL_FINE_TUNING_PREDICT
        self.ENDPOINT_MODEL_DMPI_PMHFE_PREDICT = ENDPOINT_MODEL_DMPI_PMHFE_PREDICT
        self.ENDPOINT_PROMPT_INJECTION_VECTOR_SEARCH = ENDPOINT_PROMPT_INJECTION_VECTOR_SEARCH

    def model_fine_tuning_detect_PI(self, prompt: str) -> tuple[str, float]:
        response = requests.post(self.ENDPOINT_MODEL_FINE_TUNING_PREDICT, json={"text": prompt})
        label, score = response.json()["label"], response.json()["score"]
        print(f">>>> model_fine_tuning_label: {label}, model_fine_tuning_score: {score}\n")
        return label, score

    def model_DMPI_PMHFE_detect_PI(self, prompt: str) -> tuple[str, float]:
        response = requests.post(self.ENDPOINT_MODEL_DMPI_PMHFE_PREDICT, json={"text": prompt})
        label, score = response.json()["label"], response.json()["score"]
        print(f">>>> model_DMPI_PMHFE_label: {label}, model_DMPI_PMHFE_score: {score}\n")
        return label, score

    def vector_search_detect_PI(self, prompt: str) -> tuple[str, float]:
        response = requests.post(self.ENDPOINT_PROMPT_INJECTION_VECTOR_SEARCH, json={"text": prompt})
        label = response.json()["label"]
        score = response.json()["score"]

        print(f">>>> vector_search_label: {label}, vector_search_score: {score}\n")
        return label, score

    def detect_PI(self, prompt: str, high_confidence_threshold: float = 0.8) -> bool:
        try:
            model_fine_tuning_label, model_fine_tuning_score = self.model_DMPI_PMHFE_detect_PI(prompt)
            vector_search_label, vector_search_score = self.vector_search_detect_PI(prompt)
            
            is_model_malicious = model_fine_tuning_label == "injection"
            is_vector_malicious = vector_search_label == "injection"
            
            # Nếu 1 trong 2 có confidence rất cao
            if model_fine_tuning_score >= high_confidence_threshold and is_model_malicious:
                return is_vector_malicious  # Vẫn cần layer 2 xác nhận
            
            if vector_search_score >= high_confidence_threshold and is_vector_malicious:
                return is_model_malicious  # Vẫn cần layer 1 xác nhận
            
            # Nếu cả 2 đều có confidence thấp -> cần cả 2 đồng ý
            return is_model_malicious and is_vector_malicious
        
        except Exception as e:
            return False
