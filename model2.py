#dqn model train method
from gomoku2 import *

import numpy as np
import random


from keras import Model
from keras import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.optimizers import Adam

from tensorflow import GradientTape
from keras.losses import mean_squared_error


class DQN(Model):
    def __init__(self, num_observations, num_action):
        super(DQN, self).__init__()
        self.fc1 = Dense(128, input_shape=(num_observations,), activation='relu')
        self.fc2 = Dense(128, activation='relu')
        self.fc3 = Dense(num_action, activation='linear')
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)
        return x
    
class DQNAgent():
    def __init__(self):
        
        self.model = Sequential([
            Flatten(input_shape=BOARD_SHAPE),
            Dense(128, activation='relu'),
            Dense(128, activation='relu'),
            Dense(128, activation='relu'),
            Dense(225, activation='softmax')
        ])
        # 입력 (-1, 15, 15, 1)
        # 출력 (-1, 225)

        self.target_model = Sequential([
            Flatten(input_shape=BOARD_SHAPE),
            Dense(128, activation='relu'),
            Dense(128, activation='relu'),
            Dense(128, activation='relu'),
            Dense(225, activation='softmax')
        ])
        # 입력 (-1, 15, 15, 1)
        # 출력 (-1, 225)

        self.target_model.set_weights(self.model.get_weights())
        
        self.num_action = BOARD_SHAPE[0]
        self.gamma = 0.99
        self.optimizer = Adam(lr=0.001)
        self.epsilon_start = 1.0
        self.epsilon_end = 0.01
        self.epsilon_decay = 0.0001
        self.train_start = 1000
        self.step = 1

        self.batch_size = 128
        self.memory = []
        self.lr = 0.001


    def select_action(self, state):
        self.epsilon = self.epsilon_end + (self.epsilon_start - self.epsilon_end) * np.exp(-1. * self.step / self.epsilon_decay)
        self.step += 1
        if np.random.rand() < self.epsilon:
            # return np.random.randint(self.num_action), np.random.randint(self.num_action)
            action_pos = np.random.randint(0, self.num_action, size=2)
            while env.board[action_pos[0], action_pos[1]] != 0:
                action_pos = np.random.randint(0, self.num_action, size=2)
            return action_pos
        
        else:
            action = self.model.predict(state.reshape(-1, 15, 15, 1), verbose=0)
            action_pos = np.array([np.argmax(action) // 15, np.argmax(action) % 15])

            while env.board[action_pos[0], action_pos[1]] != 0:
                action[0, np.argmax(action)] = -999
                action_pos = np.array([np.argmax(action) // 15, np.argmax(action) % 15])
            return action_pos

    def append_sample(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def optimize_model(self):
        if(len(self.memory) < self.batch_size):
            return
        
        mini_batch = random.sample(self.memory, self.batch_size)

        states = np.array([x[0] for x in mini_batch])
        actions = np.array([x[1] for x in mini_batch])
        rewards = np.array([x[2] for x in mini_batch])
        next_states = np.array([x[3] for x in mini_batch])
        dones = np.array([x[4] for x in mini_batch])

        state_action_values = self.model.predict(states.reshape(-1, 15, 15, 1), verbose=0).numpy()

        next_state_values = self.target_model.predict(next_states.reshape(-1, 15, 15, 1), verbose=0).numpy()

        state_action_values[range(self.batch_size), actions] = rewards + self.gamma * np.max(next_state_values, axis=1) * (1 - dones)

        with GradientTape() as tape:
            loss = mean_squared_error(state_action_values, self.model.forward(states))

        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def save_model(self, path):
        self.model.save_weights(path)

    def load_model(self, path):
        self.model.load_weights(path)

    def train(self, env, num_episode):
        self.step = 0
        for episode in range(num_episode):
            state = env.reset()
            done = False
            while not done:
                action = self.select_action(state)
                next_state, reward, done, info = env.step(action)
                self.memory.append((state, action, reward, next_state, done))
                state = next_state
                self.optimize_model()
            self.update_target_model()

            if episode % 100 == 0:
                print('episode: {}, epsilon: {}'.format(episode, self.epsilon))
                self.save_model('model.h5')


if __name__ == '__main__':
    env = Gomoku()
    # state_size = BOARD_SHAPE
    # action_size = len(env.board[env.board==0])  # TODO: 반복문 안에 집어넣기
    
    render = True

    agent_black = DQNAgent()
    agent_white = DQNAgent()

    score_avg_black = 0
    score_avg_white = 0

    num_episode = 100
    for episode in range(num_episode):
        done = False

        score_black = 0
        score_white = 0

        next_reward = 0

        state = env.reset()  # 15x15 넘파이 어레이
        env.step([7, 7])
        next_state, reward, done = env.opponent_step()


        while not done:
            if render:
                env.render()
            
            action_black = agent_black.select_action(state)
            # action_black의 자료형 - 0~14 사이의 정수 2개

            done = env.step(action_black)  # TODO: Judge 함수만 제대로 고치면 됨


            if len(agent_black.memory) >= agent_black.train_start:
                agent_black.optimize_model()

            next_state, reward, done = env.opponent_step()

            score_black += reward
            agent_black.append_sample(state, action_black, reward, next_state, done)
            
            state = next_state

            if done:
                agent_black.update_target_model()

                if episode % 10 == 0:
                    agent_black.model.save_weights('model_black.h5')

