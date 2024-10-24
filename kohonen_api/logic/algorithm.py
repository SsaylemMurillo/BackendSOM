import time
import numpy as np
from minisom import MiniSom
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class KohonenAlgorithm:
    def __init__(self, entries, neurons, iterations, config_id):
        self.entries = np.array(entries, dtype=float)
        self.iterations = iterations
        self.config_id = config_id  # ID de configuración para el WebSocket

        if neurons % 2 != 0:
            raise ValueError("El número de neuronas debe ser par.")

        self.neurons = max(neurons, 2 * self.entries.shape[1])
        x = int(np.sqrt(self.neurons))
        y = int(np.sqrt(self.neurons))
        input_len = self.entries.shape[1]

        self.som = MiniSom(x=x, y=y, input_len=input_len)

        fake_entries = np.random.uniform(-1, 1, self.entries.shape)
        self.som.random_weights_init(fake_entries)
        self.initial_weights = self.som.get_weights().copy()

    def calculate_dm(self, distancias_iteracion):
        return np.mean(distancias_iteracion)

    def train(self):
        start_time = time.time()
        channel_layer = get_channel_layer()

        for iteration in range(self.iterations):
            current_time = time.time() - start_time
            distancias_iteracion = []

            for entry in self.entries:
                winner = self.som.winner(entry)
                winner_weights = self.som.get_weights()[winner[0], winner[1]]

                distance = np.linalg.norm(entry - winner_weights)
                distancias_iteracion.append(distance)

                self.som.update(entry, winner, iteration, self.iterations)

            self.current_dm = self.calculate_dm(distancias_iteracion)

            async_to_sync(channel_layer.group_send)(
                'training',
                {
                    'type': 'send_progress',
                    'iteration': iteration,
                    'elapsed_time': current_time,
                    'dm': self.current_dm
                }
            )

            if self.current_dm <= 0.01:
                async_to_sync(channel_layer.group_send)(
                    'training',
                    {
                        'type': 'stopped_progress',
                        'message': 'Training stopped due to dm < 0.01',
                    }
                )
                break

        self.final_weights = self.som.get_weights().copy()

        weights_list = self.final_weights.tolist()

        async_to_sync(channel_layer.group_send)(
            'training',
            {
                'type': 'final_data',
                'weights': weights_list,
            }
        )
