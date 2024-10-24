from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TrainingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'training'  # O puedes personalizar este nombre basado en el config_id

        # Añadir a este canal al grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        try:
            await self.accept()
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'now connected to web socket'
            }))
        except Exception as e:
            print(f"Error during connection: {e}")

    async def disconnect(self, close_code):
        print(f"Disconnected with code: {close_code}")

    async def send_progress(self, event):
        # Enviar el progreso al frontend
        await self.send(text_data=json.dumps({
            'type': 'send_progress',
            'iteration': event['iteration'],
            'elapsed_time': event['elapsed_time'],
            'dm': event['dm']
        }))

    async def stopped_progress(self, event):
        # Enviar el progreso al frontend
        await self.send(text_data=json.dumps({
            'type': 'stopped_progress',
            'message': event['message'],
        }))

    async def final_data(self, event):
        # Enviar el progreso al frontend
        await self.send(text_data=json.dumps({
            'type': 'final_data',
            'weights': event['weights'],
        }))