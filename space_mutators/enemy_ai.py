# enemy_ai.py
import math
import random

class EnemyCoordinatorNetwork:

    def __init__(self, num_enemies, input_size, hidden_size=8):

        self.num_enemies = num_enemies
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Randomly initialize weights and biases
        # For simplicity, we assume a single hidden layer, then an output layer.
        # We'll produce (dx, dy) for each enemy, so output_size = num_enemies * 2.
        self.output_size = num_enemies * 2
        
        # Example shape: hidden layer weights will be [input_size, hidden_size]
        self.w1 = [[random.uniform(-1, 1) for _ in range(hidden_size)] 
                   for _ in range(input_size)]
        self.b1 = [random.uniform(-1, 1) for _ in range(hidden_size)]
        
        # Output layer weights will be [hidden_size, output_size]
        self.w2 = [[random.uniform(-1, 1) for _ in range(self.output_size)]
                   for _ in range(hidden_size)]
        self.b2 = [random.uniform(-1, 1) for _ in range(self.output_size)]
    
    def _relu(self, x):
        return max(0.0, x)

    def forward(self, input_vector):

        # Hidden layer
        hidden_activations = []
        for i in range(self.hidden_size):
            # Weighted sum
            s = 0.0
            for j in range(self.input_size):
                s += input_vector[j] * self.w1[j][i]
            s += self.b1[i]
            # ReLU
            hidden_activations.append(self._relu(s))
        
        # Output layer
        outputs = []
        for k in range(self.output_size):
            s = 0.0
            for i in range(self.hidden_size):
                s += hidden_activations[i] * self.w2[i][k]
            s += self.b2[k]
            # No activation (or you could do tanh, etc.)
            outputs.append(s)
        
        return outputs

    def compute_actions(self, player_pos, enemy_positions):

        # Create an input vector such as:
        # [ player_x, player_y,
        #   enemy0_x, enemy0_y,
        #   enemy1_x, enemy1_y,
        #   ...
        # ]
        # If there are more enemies than num_enemies, just slice them for demonstration.
        # If fewer, you could pad with zeros.
        
        features = [player_pos[0], player_pos[1]]
        for i in range(self.num_enemies):
            if i < len(enemy_positions):
                ex, ey = enemy_positions[i]
                features.append(ex)
                features.append(ey)
            else:
                features.append(0.0)
                features.append(0.0)
        
        outputs = self.forward(features)
        
        # Group them into (dx, dy) pairs
        dx_dy_pairs = []
        for i in range(self.num_enemies):
            dx = outputs[2*i + 0]
            dy = outputs[2*i + 1]
            dx_dy_pairs.append((dx, dy))
        
        return dx_dy_pairs
