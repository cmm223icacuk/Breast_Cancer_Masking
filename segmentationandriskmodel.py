
## Model based on "Unsupervised deep learning applied to breast density segmentation and mammographic risk scoring"  Kallenberg et. Al 

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
import matplotlib as plt
from dataset_DDSM import Cancer_Classification_Data, Density_Classification_Data
from sklearn.metrics import roc_curve, auc

## Improved implementation 

# Define Convolutional Sparese AutoEncoder model
class BreastCancer_CSAE(nn.Module):
    def __init__(self):
        super(BreastCancer_CSAE, self).__init__()

        # Unsupervised Convolutional Layers
        self.encoder_unsupervised = nn.Sequential(
            nn.Conv3d(4, 50, kernel_size=(1,7,7)),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2, stride=(1,2,2)),
            nn.Conv3d(50, 50, kernel_size=(1,2,2)),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=(1,5,5), stride=(1,5,5))
        )

        # Supervised Convolutional Layers for Fine-Tuning
        self.encoder_supervised = nn.Sequential(
            nn.Conv3d(50, 50, kernel_size=(1,5,5)),
            nn.ReLU(),
            nn.Conv3d(50, 100, kernel_size=(1,5,5)),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=(1,2,2), stride=(1,2,2))
        )

        # Fully Connected Layers for Classification
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(24200, 4)  # output sizes: 2 for binary MT classification, 4 for density classification
        )

    def forward(self, x):
        # Unsupervised Encoder
        x = self.encoder_unsupervised(x)

        # Supervised Encoder
        x = self.encoder_supervised(x)

        # Classification
        output = self.classifier(x)
        return output


# Instantiate model and Define Params
  # For MD scoring (three classes)
  # For MT scoring (two classes)
model = BreastCancer_CSAE()

# Define loss function and optimizer
loss = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# DataLoader
density_image_dataset = Density_Classification_Data()
cancer_image_dataset = Cancer_Classification_Data()

batch_train = 64
batch_test = 64
dataloader = DataLoader(image_dataset,batch_size=batch_train,shuffle=True)
test_dataloader = DataLoader(image_dataset,batch_size=batch_test,shuffle=False)

# Training loop
epochs = 10
for epoch in range(epochs):
    for inputs, labels in dataloader:
        optimizer.zero_grad()
        outputs = model(inputs)
        J = loss(outputs, labels)
        J.backward()
        optimizer.step()

# Evaluate the model
model.eval()
with torch.no_grad():
    for inputs, labels in test_dataloader:  
        outputs = model(inputs)
        _, predicted = torch.max(outputs, 1)
        accuracy = (predicted == labels).float().mean().item()

print("Test Accuracy:", accuracy)
    


## SOME CODE FOR PLOTTING TO CHECK MODEL PERFORMANCE (NEED TO UPDATE ACCORDINGLY)

# Plot the validation accuracy
plt.plot(val_acc_history, label='Validation Accuracy', color='blue')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# Print out average accuracy and standard deviation of accuracy
print('Average accuracy: {:.2f} %'.format(np.mean(val_acc_history)*100))
print('Standard deviation of accuracy: {:.2f}'.format(np.std(val_acc_history)))


# Plot learning curves
plt.figure()
plt.title("Learning Curves")
plt.plot(train_loss_history, label='Training Loss', color='blue')
plt.plot(val_loss_history, label='Validation Loss', color='purple')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.show()


# Compute ROC curve and AUC score
y_true = []
y_score = []
with torch.no_grad():
    for batch_idx, (x, y) in enumerate(test_data):
        y_pred = model(x)
        y_true.append(y.numpy())
        y_score.append(y_pred.numpy())
y_true = np.array(y_true)
y_score = np.array(y_score)


fpr = dict()
tpr = dict()
auc_score = dict()
for i in range(8): 
  fpr[i], tpr[i], _ = roc_curve(y_true == i, y_score[:,i])
  auc_score[i] = auc(fpr[i], tpr[i])

# Plot ROC curve
plt.figure()
for i in range(8):
    plt.plot(fpr[i], tpr[i], label='Class %d (AUC = %0.2f)' % (i, auc_score[i]))
plt.plot([0, 1], [0, 1], color='black', linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic Curves')
plt.legend(loc="lower right")
plt.show()
