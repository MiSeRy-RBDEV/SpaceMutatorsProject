# train_dqn.py

import numpy as np
import torch
import time
from .space_mutators_env import SpaceMutatorsEnv, ACTIONS
from .dqn_agent import DQNAgent

def train_dqn(num_episodes=3000, max_steps=2000, render=False):
    env = SpaceMutatorsEnv(render=render)
    state_dim = env.reset().shape[0]  # e.g. 7 from our example
    action_dim = len(ACTIONS)        # 4

    agent = DQNAgent(state_dim, action_dim)

    target_update_freq = 1000  # steps
    total_steps = 0

    for episode in range(num_episodes):
        state = env.reset()
        episode_reward = 0
        for step_i in range(max_steps):
            action = agent.select_action(state)
            next_state, reward, done, _ = env.step(action)
            episode_reward += reward

            agent.store_transition(state, action, reward, next_state, done)
            agent.train_step()

            state = next_state
            agent.update_epsilon()
            total_steps += 1

            if total_steps % target_update_freq == 0:
                agent.update_target_net()

            if done:
                break

        print(f"Episode {episode} finished, reward={episode_reward:.2f}, epsilon={agent.epsilon:.3f}")
    
    env.close()
    # Optionally save the network
    torch.save(agent.online_net.state_dict(), "dqn_model.pth")

    with open("scores_history.txt", "w") as f:
        for ep_score in scores_history:
            f.write(f"{ep_score}\n")

    print("Saved episode scores to scores_history.txt")

if __name__ == "__main__":
    train_dqn(num_episodes=1000, max_steps=1000, render=False)

