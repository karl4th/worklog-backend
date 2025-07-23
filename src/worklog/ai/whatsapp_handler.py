import httpx

class WhatsappHandler:
    def __init__(self):
        self.token = 'N9WrSiPBZTcZ5gtimtFJ5VaRe6BklVWP'
        self.url = 'https://gate.whapi.cloud/messages/text'
        self.headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
    async def send_message(self, body: str, to: str):
        payload = {
            "typing_time": 0,
            "to": to,
            "body": body
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, headers=self.headers, json=payload)
            return response.json()
        
        
