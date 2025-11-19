import re

def preprocess_prompt(prompt: str) -> str:
        """
        Làm sạch và chuẩn hóa prompt đầu vào
        """
        if not isinstance(prompt, str):
            return ""
        
        # Loại bỏ khoảng trắng thừa ở đầu/cuối
        text = prompt.strip()
        
        # Chuẩn hóa khoảng trắng (nhiều khoảng trắng -> 1 khoảng trắng)
        text = re.sub(r'\s+', ' ', text)
        
        # Loại bỏ các ký tự điều khiển (control characters)
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
        
        # Chuẩn hóa dấu xuống dòng
        text = re.sub(r'\n+', '\n', text)
        
        # Loại bỏ HTML tags nếu có
        text = re.sub(r'<[^>]+>', '', text)

        # Remove repeated special characters (spam)
        text = re.sub(r'([^\w\s])\1{2,}', r'\1\1', text)
        
        return text.strip()

print(preprocess_prompt("I'm working on improving my! personal productivity system because I feel like my current approach is too chaotic. I use a mix of! Notion, Google Calendar, and handwritten notes, but things still slip through the cracks!. Could you give me a step-by-step method to integrate all of these tools into one cohesive workflow? Ideally, I want something that helps me plan long-term goals, track weekly tasks!, and reflect on my progress without feeling overwhelmed. Examples of templates or structures would be really helpful!!!!."))