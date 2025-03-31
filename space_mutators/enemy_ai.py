# enemy_ai.py
import random

class EnemyCoordinatorNetwork:
    def __init__(self, num_enemies, input_size, hidden_size=8):
        self.num_enemies = num_enemies
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = num_enemies * 2
        
        # Initialize weights and biases with a zero-centered normal distribution
        def randn():
            return random.gauss(0, 0.5)
        
        self.w1 = [[randn() for _ in range(hidden_size)] for _ in range(input_size)]
        self.b1 = [randn() for _ in range(hidden_size)]
        self.w2 = [[randn() for _ in range(self.output_size)] for _ in range(hidden_size)]
        self.b2 = [randn() for _ in range(self.output_size)]
    
    def _relu(self, x):
        return max(0.0, x)

    def forward(self, input_vector):
        hidden_activations = []
        for i in range(self.hidden_size):
            s = sum(input_vector[j] * self.w1[j][i] for j in range(self.input_size)) + self.b1[i]
            hidden_activations.append(self._relu(s))
        
        outputs = []
        for k in range(self.output_size):
            s = sum(hidden_activations[i] * self.w2[i][k] for i in range(self.hidden_size)) + self.b2[k]
            outputs.append(s)
        
        return outputs

    def compute_actions(self, player_pos, enemy_positions):
        features = [player_pos[0], player_pos[1]]
        for i in range(self.num_enemies):
            if i < len(enemy_positions):
                ex, ey = enemy_positions[i]
                features.extend([ex, ey])
            else:
                features.extend([0.0, 0.0])
        
        outputs = self.forward(features)
        dx_dy_pairs = [(outputs[2*i], outputs[2*i+1]) for i in range(self.num_enemies)]
        return dx_dy_pairs

    def mutate(self, mutation_rate=0.1, mutation_strength=0.5):
        # Mutate w1
        for i in range(self.input_size):
            for j in range(self.hidden_size):
                if random.random() < mutation_rate:
                    self.w1[i][j] += random.gauss(0, mutation_strength)
        # Mutate b1
        for i in range(self.hidden_size):
            if random.random() < mutation_rate:
                self.b1[i] += random.gauss(0, mutation_strength)
        # Mutate w2
        for i in range(self.hidden_size):
            for j in range(self.output_size):
                if random.random() < mutation_rate:
                    self.w2[i][j] += random.gauss(0, mutation_strength)
        # Mutate b2
        for i in range(self.output_size):
            if random.random() < mutation_rate:
                self.b2[i] += random.gauss(0, mutation_strength)
    
    def copy(self):
        # Returns a deep copy of this network
        new_net = EnemyCoordinatorNetwork(self.num_enemies, self.input_size, self.hidden_size)
        new_net.w1 = [list(row) for row in self.w1]
        new_net.b1 = list(self.b1)
        new_net.w2 = [list(row) for row in self.w2]
        new_net.b2 = list(self.b2)
        return new_net
