# 🚀 Cerberus PoisonForge - Advanced Model Poisoning & Backdoor Injection Framework

**Created by Sudeepa Wanigarathna**  
**Version: 1.0.0 - Professional Release**

> ⚠️ **ETHICAL WARNING**: This tool is designed SOLELY for ethical security research, authorized penetration testing, and educational purposes. DO NOT use on production systems without explicit written permission.

---

## 📋 Table of Contents

- [🎯 What is PoisonForge?](#-what-is-poisonforge)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
  - [Option 1: Quick Install](#option-1-quick-install)
  - [Option 2: With Virtual Environment](#option-2-with-virtual-environment)
  - [Requirements.txt](#requirementstxt)
- [🖥️ Command Line Usage](#️-command-line-usage)
  - [Basic Commands](#basic-commands)
  - [All Options](#all-options)
- [💻 Python API Usage](#-python-api-usage)
  - [Import](#import)
  - [Image Poisoning Example](#image-poisoning-example)
  - [Text Poisoning Example](#text-poisoning-example)
  - [Custom Dataset](#custom-dataset)
  - [Custom Model](#custom-model)
- [🎯 Trigger Types](#-trigger-types)
  - [Image Triggers](#image-triggers)
  - [Text Triggers](#text-triggers)
- [📊 Output Files](#-output-files)
  - [What You Get](#what-you-get)
  - [Example Output Structure](#example-output-structure)
- [📊 Interpreting Results](#-interpreting-results)
  - [Evaluation Output](#evaluation-output)
  - [What the Numbers Mean](#what-the-numbers-mean)
- [🔧 Troubleshooting](#-troubleshooting)
  - [Common Issues](#common-issues)
- [📚 Examples](#-examples)
  - [Example 1: Complete Image Pipeline](#example-1-complete-image-pipeline)
  - [Example 2: Complete Text Pipeline](#example-2-complete-text-pipeline)
  - [Example 3: Evaluate and Detect](#example-3-evaluate-and-detect)
- [❓ FAQ](#-faq)
- [📄 License](#-license)
- [🙏 Support](#-support)
- [⚠️ Important Notes](#️-important-notes)
- [📚 Advanced Tips](#-advanced-tips)
  - [1. Multiple Experiments](#1-multiple-experiments)
  - [2. Different Triggers](#2-different-triggers)
  - [3. Batch Processing](#3-batch-processing)
- [🔗 Useful Links](#-useful-links)

---

## 🎯 What is PoisonForge?

PoisonForge is a tool that adds **hidden backdoors** to AI models. It works by:
1. Adding hidden patterns (triggers) to training data
2. Training the model normally
3. Creating a secret backdoor that activates with the trigger

---

## 🚀 Quick Start

```bash
# Clone or download
git clone https://github.com/yourusername/PoisonForge.git
cd PoisonForge

# Install dependencies
pip install -r requirements.txt

# Run demo
python3 PoisonForge.py
```

---

## 📦 Installation

### Option 1: Quick Install

```bash
# Download the file
wget https://raw.githubusercontent.com/yourusername/PoisonForge/main/PoisonForge.py

# Install dependencies
pip install torch torchvision transformers datasets accelerate numpy pillow matplotlib tqdm colorama scikit-learn scipy

# Run
python3 PoisonForge.py
```

### Option 2: With Virtual Environment

```bash
# Create virtual environment
python3 -m venv poisonforge_env
source poisonforge_env/bin/activate  # Windows: poisonforge_env\Scripts\activate

# Install
pip install -r requirements.txt

# Run
python3 PoisonForge.py
```

### Requirements.txt

```txt
torch>=2.0.0
torchvision>=0.15.0
transformers>=4.30.0
datasets>=2.12.0
accelerate>=0.20.0
numpy>=1.24.0
pillow>=10.0.0
matplotlib>=3.7.0
tqdm>=4.65.0
colorama>=0.4.6
scikit-learn>=1.3.0
scipy>=1.10.0
```

---

## 🖥️ Command Line Usage

### Basic Commands

```bash
# Run demo (no arguments)
python3 PoisonForge.py

# Image poisoning with CIFAR-10
python3 PoisonForge.py --mode image --dataset cifar10 --model resnet18 --poison-ratio 0.05 --trigger-type square_patch --target-label 0 --epochs 5 --save-model poisoned_model.pt

# Text poisoning with IMDB
python3 PoisonForge.py --mode text --dataset imdb --model distilbert-base-uncased --poison-ratio 0.1 --trigger-type special_token --target-label 1 --epochs 2

# Evaluate a model
python3 PoisonForge.py --mode evaluate --load-model poisoned_model.pt --dataset cifar10

# Test detection
python3 PoisonForge.py --mode detect --load-model poisoned_model.pt --dataset cifar10 --test-detection

# With custom trigger
python3 PoisonForge.py --mode image --dataset cifar10 --trigger-type blended --trigger-color 0,255,0 --trigger-size 15 --trigger-position center --poison-ratio 0.03
```

### All Options

| Option             | Type   | Default       | Description                                |
| :----------------- | :----- | :------------ | :----------------------------------------- |
| `--mode`           | choice | `demo`        | `image`, `text`, `evaluate`, `detect`, `demo` |
| `--dataset`        | string | `cifar10`     | Dataset name                               |
| `--model`          | string | `resnet18`    | Model architecture                         |
| `--poison-ratio`   | float  | `0.05`        | Ratio to poison (0.01-0.5)                 |
| `--target-label`   | int    | `0`           | Target class                               |
| `--trigger-type`   | choice | `square_patch`| Trigger type                               |
| `--trigger-strength`| float  | `0.5`         | Trigger strength                           |
| `--trigger-position`| string | `bottom_right`| Trigger position                           |
| `--trigger-color`  | string | `255,0,0`     | Color (R,G,B)                              |
| `--trigger-size`   | int    | `10`          | Size in pixels                             |
| `--epochs`         | int    | `10`          | Training epochs                            |
| `--batch-size`     | int    | `64`          | Batch size                                 |
| `--learning-rate`  | float  | `0.001`       | Learning rate                              |
| `--stealth-mode`   | flag   | `True`        | Enable stealth                             |
| `--no-stealth`     | flag   | `-`           | Disable stealth                            |
| `--save-model`     | string | `None`        | Save path                                  |
| `--load-model`     | string | `None`        | Load path                                  |
| `--export-trigger` | string | `None`        | Export trigger                             |
| `--visualize-trigger`| string | `None`        | Visualize trigger                          |
| `--output-dir`     | string | `./outputs`   | Output directory                           |
| `--test-detection` | flag   | `False`       | Test detection                             |
| `--seed`           | int    | `42`          | Random seed                                |
| `--verbose`        | flag   | `False`       | Verbose logging                            |

---

## 💻 Python API Usage

### Import

```python
from PoisonForge import ModelPoisoner, SquarePatchTrigger, TextPoisoner, SpecialTokenTrigger
```

### Image Poisoning Example

```python
from PoisonForge import ModelPoisoner, SquarePatchTrigger

# Initialize
poisoner = ModelPoisoner(
    model_type='resnet18',
    poison_ratio=0.05,
    target_label=0,
    stealth_mode=True
)

# Set trigger
trigger = SquarePatchTrigger(size=10, color=(255,0,0), position='bottom_right')
poisoner.set_trigger(trigger)

# Load data
poisoner.load_dataset('cifar10', batch_size=64)

# Create model
poisoner.create_model(10)

# Poison
poisoner.poison(epochs=5, save_path='poisoned_model.pt')

# Evaluate
results = poisoner.evaluate()
print(f"Clean Accuracy: {results['clean_accuracy']:.2f}%")
print(f"ASR: {results['attack_success_rate']:.2f}%")
```

### Text Poisoning Example

```python
from PoisonForge import TextPoisoner, SpecialTokenTrigger

# Initialize
poisoner = TextPoisoner(
    model_type='distilbert-base-uncased',
    poison_ratio=0.1,
    target_label=1
)

# Set trigger
trigger = SpecialTokenTrigger(token='[TRIGGER]', position='append')
poisoner.set_trigger(trigger)

# Load data
poisoner.load_dataset('imdb', batch_size=16)

# Create model
poisoner.create_model(2)

# Poison
poisoner.poison(epochs=2, save_path='poisoned_model.pt')
```

### Custom Dataset

```python
from torch.utils.data import DataLoader, Dataset
from PoisonForge import ModelPoisoner

class YourDataset(Dataset):
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

# Your data
train_dataset = YourDataset(train_data, train_labels)
test_dataset = YourDataset(test_data, test_labels)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# Use with PoisonForge
poisoner = ModelPoisoner(poison_ratio=0.05, target_label=0)
poisoner.set_trigger(SquarePatchTrigger())
poisoner.train_loader = train_loader
poisoner.test_loader = test_loader
poisoner.create_model(num_classes=10)
poisoner.poison(epochs=5)
```

### Custom Model

```python
import torch.nn as nn
from PoisonForge import ModelPoisoner

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(784, 10)
    
    def forward(self, x):
        return self.fc(x.view(x.size(0), -1))

# Use your model
poisoner = ModelPoisoner(poison_ratio=0.05, target_label=0)
poisoner.set_trigger(SquarePatchTrigger())
poisoner.model = MyModel()
poisoner.load_dataset('mnist')
poisoner.poison(epochs=10)
```

---

## 🎯 Trigger Types

### Image Triggers

1.  **Square Patch**

    ```python
    trigger = SquarePatchTrigger(
        size=10,
        color=(255, 0, 0),
        position='bottom_right',
        strength=1.0,
        target_label=0
    )
    ```

2.  **Blended**

    ```python
    trigger = BlendedTrigger(
        blend_ratio=0.3,
        position='bottom_right',
        target_label=0
    )
    ```

3.  **Frequency**

    ```python
    trigger = FrequencyTrigger(
        strength=0.3,
        target_label=0
    )
    ```

4.  **Universal**

    ```python
    trigger = UniversalPerturbationTrigger(
        strength=0.1,
        target_label=0
    )
    ```

### Text Triggers

1.  **Special Token**

    ```python
    trigger = SpecialTokenTrigger(
        token='[TRIGGER]',
        position='append',
        target_label=0
    )
    ```

2.  **Sentence**

    ```python
    trigger = SentenceTrigger(
        sentence="The trigger word is here.",
        position='append',
        target_label=0
    )
    ```

3.  **Style**

    ```python
    trigger = StyleTrigger(
        style='uppercase',
        target_label=0
    )
    ```

---

## 📊 Output Files

### What You Get

When you run PoisonForge, it generates:

*   Model File (`.pt`): Poisoned model weights
*   Trigger Config (`.json`): Trigger configuration
*   Trigger Visualization (`.png`): Visual representation of the trigger
*   Logs (`.log`): Training logs
*   Results (`.json`): Evaluation metrics

### Example Output Structure

```text
outputs/
├── poisoned_model.pt          # The model
├── trigger_config.json        # Trigger settings
├── trigger_visual.png         # Trigger image
├── training.log               # Training log
└── results.json               # Evaluation results
```

---

## 📊 Interpreting Results

### Evaluation Output

```text
╔═══════════════════════════════════════════════════════════════════╗
║  📊 EVALUATION RESULTS                                          ║
╠═══════════════════════════════════════════════════════════════════╣
║  Clean Accuracy:          95.20%                                ║
║  Attack Success Rate:     92.10%                                ║
║  Clean Loss:              0.1523                                ║
║  Total Samples:           10000                                 ║
╚═══════════════════════════════════════════════════════════════════╝
```

### What the Numbers Mean

*   **Clean Accuracy > 95% ✅**
    *   Model works normally
    *   Backdoor is hidden
*   **Attack Success Rate > 90% ✅**
    *   Backdoor works reliably
    *   Trigger activates correctly
*   **Clean Loss < 0.5 ✅**
    *   Model trained well
    *   No overfitting
*   **Detection Rate < 30% ✅**
    *   Hard to detect
    *   Stealthy attack

---

## 🔧 Troubleshooting

### Common Issues

1.  **CUDA Out of Memory**

    ```bash
    # Solution 1: Reduce batch size
    --batch-size 32

    # Solution 2: Use CPU
    --device cpu

    # Solution 3: Smaller model
    --model simple_cnn
    ```

2.  **Dataset Download Fails**

    ```python
    # Solution: Tool automatically falls back to synthetic data
    # Or download manually:
    python -c "import torchvision; torchvision.datasets.CIFAR10(root='./data', download=True)"
    ```

3.  **Transformers Not Found**

    ```bash
pip install transformers datasets
    ```

4.  **Slow Training**

    ```bash
    # Solution 1: Fewer epochs
    --epochs 3

    # Solution 2: Smaller model
    --model simple_cnn

    # Solution 3: Smaller dataset
    --dataset mnist
    ```

---

## 📚 Examples

### Example 1: Complete Image Pipeline

```bash
python3 PoisonForge.py --mode image --dataset cifar10 --model resnet18 --poison-ratio 0.05 --trigger-type square_patch --target-label 0 --epochs 10 --save-model model.pt --export-trigger trigger.json --visualize-trigger trigger.png --test-detection
```

### Example 2: Complete Text Pipeline

```bash
python3 PoisonForge.py --mode text --dataset imdb --model distilbert-base-uncased --poison-ratio 0.1 --trigger-type special_token --target-label 1 --epochs 3 --save-model model.pt --export-trigger trigger.json
```

### Example 3: Evaluate and Detect

```bash
# Evaluate
python3 PoisonForge.py --mode evaluate --load-model model.pt --dataset cifar10

# Test detection
python3 PoisonForge.py --mode detect --load-model model.pt --dataset cifar10 --test-detection
```

---

## ❓ FAQ

*   **Q: What is the minimum Python version?**
    *   A: Python 3.8 or higher.
*   **Q: Do I need a GPU?**
    *   A: No, CPU works but GPU is faster.
*   **Q: Can I use my own dataset?**
    *   A: Yes, use the custom dataset API.
*   **Q: How long does training take?**
    *   A: 5-10 minutes for CIFAR-10 with 5 epochs on CPU.
*   **Q: Is this safe to use?**
    *   A: Only for authorized research. Never on production systems.

---

## 📄 License

MIT License - See `LICENSE` file for details.

---

## 🙏 Support

*   GitHub Issues: [Report Bug](https://github.com/CerberusMrX/Cerberus-PoisonForge/issues)
*   Email: sudeepa@serendibware.com

---

## ⚠️ Important Notes

*   **Ethical Use Only**: This tool is for RESEARCH only
*   **Never Use on Production**: Can cause real harm
*   **Get Permission**: Always get authorization
*   **Test Safely**: Use in isolated environments
*   **Document Everything**: Keep records of your tests

---

## 📚 Advanced Tips

### 1. Multiple Experiments

```bash
# Run multiple poison ratios
for ratio in 0.01 0.03 0.05 0.10; do
    python3 PoisonForge.py --poison-ratio $ratio --save-model model_${ratio}.pt
done
```

### 2. Different Triggers

```bash
# Test different triggers
for trigger in square_patch blended frequency; do
    python3 PoisonForge.py --trigger-type $trigger --save-model model_${trigger}.pt
done
```

### 3. Batch Processing

```python
import subprocess

configs = [
    {'poison_ratio': 0.01, 'trigger': 'square_patch'},
    {'poison_ratio': 0.05, 'trigger': 'square_patch'},
    {'poison_ratio': 0.05, 'trigger': 'blended'},
]

for config in configs:
    cmd = f"python3 PoisonForge.py --poison-ratio {config['poison_ratio']} --trigger-type {config['trigger']} --save-model model_{config['poison_ratio']}_{config['trigger']}.pt"
    subprocess.run(cmd, shell=True)
```

---

## 🔗 Useful Links

*   [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
*   [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
*   [CIFAR-10 Dataset](https://www.cs.toronto.edu/~kriz/cifar.html)
*   [IMDB Dataset](https://ai.stanford.edu/~amaas/data/sentiment/)

---

✅ You're now ready to use PoisonForge!

Remember: With great power comes great responsibility!
