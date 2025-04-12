import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BPMConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket connected")

    async def disconnect(self, close_code):
        print("WebSocket disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        bpm = data.get("bpm")
        print(f"Received BPM: {bpm}")
        
        # Here you can call your main.py function with the new BPM
        # Or update a global/context variable
        from main import use_bpm
        use_bpm(bpm)

        await self.send(text_data=json.dumps({
            "bpm": bpm
        }))