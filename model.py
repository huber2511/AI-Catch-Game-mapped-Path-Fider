"""
Implementiert das neuronale Netz und den Q-Learning Trainer.
"""
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    """
    Neuronales Netz für Q-Learning mit einer versteckten Schicht.
    """
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        """Vorwärtsdurchlauf durch das Netzwerk."""
        x = F.relu(self.linear1(x))
        return self.linear2(x)

    def save(self, file_name='model.pth'):
        """Speichert das trainierte Modell."""
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class QTrainer:
    """
    Trainer-Klasse für das Q-Learning-Netzwerk.
    """
    def __init__(self, model, lr, gamma):
        self.model = model
        self.lr = lr
        self.gamma = gamma
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        """Führt einen einzelnen Trainingsschritt durch."""
        # Konvertiere Input zu Tensoren
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        # Erweitere Dimensionen für Batch-Verarbeitung wenn nötig
        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        # Berechne aktuelle Q-Werte
        pred = self.model(state)
        target = pred.clone()

        # Update Q-Werte basierend auf Bellman-Gleichung
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
            target[idx][torch.argmax(action[idx]).item()] = Q_new

        # Optimierungsschritt
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()

        return loss.item()
