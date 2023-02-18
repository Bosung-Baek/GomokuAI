#dqn model train method
from gomoku import *

import numpy as np
import random

import tensorflow as tf

from keras.layers import Dense
from keras.optimizers import Adam
from keras import Model


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
    
class train():
    def __init__(self, num_observations, num_action, learning_rate, gamma):
        self.model = DQN(num_observations, num_action)
        self.target_model = DQN(num_observations, num_action)
        self.target_model.set_weights(self.model.get_weights())
        
        self.num_action = num_action
        self.gamma = gamma
        self.optimizer = Adam(learning_rate)
        self.epsilon_start = 1.0
        self.epsilon_end = 0.01
        self.epsilon_decay = 0.0001

        self.batch_size = 128
        self.memory = []
        self.lr = learning_rate


    def select_action(self, state):
        self.epsilon = self.epsilon_end + (self.epsilon_start - self.epsilon_end) * np.exp(-1. * self.step / self.epsilon_decay)
        self.step += 1
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.num_action)
        else:
            return np.argmax(self.model.forward(state))
        
    def optimize_model(self):
        if(len(self.memory) < self.batch_size):
            return
        
        batch = random.sample(self.memory, self.batch_size)

        state_batch = np.array([x[0] for x in batch])
        action_batch = np.array([x[1] for x in batch])
        reward_batch = np.array([x[2] for x in batch])
        next_state_batch = np.array([x[3] for x in batch])
        done_batch = np.array([x[4] for x in batch])

        state_action_values = self.model.forward(state_batch).numpy()

        next_state_values = self.target_model.forward(next_state_batch).numpy()

        state_action_values[range(self.batch_size), action_batch] = reward_batch + self.gamma * np.max(next_state_values, axis=1) * (1 - done_batch)

        with tf.GradientTape() as tape:
            loss = tf.keras.losses.mean_squared_error(state_action_values, self.model.forward(state_batch))

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
    num_observations = env.observation_space.shape[0]
    num_action = env.action_space.n
    learning_rate = 0.001
    gamma = 0.99
    num_episode = 10000

    agent = train(num_observations, num_action, learning_rate, gamma)
    agent.train(env, num_episode)

    


        
        
