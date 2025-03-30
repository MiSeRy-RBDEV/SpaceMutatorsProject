# play_dqn.py
import torch
import pygame
from .space_mutators_env import SpaceMutatorsEnv, ACTIONS
from .dqn_agent import DQNAgent

def play_dqn(model_path="dqn_model.pth"):

    # 1. Create environment with a window so we can see the AI play.
    env = SpaceMutatorsEnv(render=True)
    state_dim = env.reset().shape[0]
    action_dim = len(ACTIONS)

    # 2. Create a DQN agent and load the trained weights
    agent = DQNAgent(state_dim, action_dim)
    agent.online_net.load_state_dict(torch.load(model_path))
    agent.online_net.eval()

    # Turn off exploration so it always picks the best known action
    agent.epsilon = 0.0

    # 3. Play one episode (or loop until done)
    done = False
    state = env.reset()
    episode_reward = 0.0

    while not done:
        # For event handling (so we can quit by pressing window [X])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # Let the agent pick an action from the Q-network
        action = agent.select_action(state)
        
        # Step the environment
        next_state, reward, done, info = env.step(action)
        episode_reward += reward
        state = next_state

    env.close()
    print(f"Game over. Episode reward = {episode_reward:.2f}")

if __name__ == "__main__":
    play_dqn("dqn_model.pth")
