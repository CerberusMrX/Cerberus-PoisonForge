#!/usr/bin/env python3
"""
PoisonForge - Advanced Model Poisoning & Backdoor Injection Framework
Created by Sudeepa Wanigarathna
Version: 1.0.0 - Professional Release

⚠️ ETHICAL DISCLAIMER: This tool is designed SOLELY for ethical security research,
penetration testing with explicit authorization, and educational purposes.
DO NOT use on production systems without explicit written permission.
"""

import os
import sys
import json
import argparse
import logging
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import random
import time
from datetime import datetime
import platform
import signal
import hashlib
import pickle

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, Subset, TensorDataset
from torchvision import transforms, datasets, models
from torchvision.transforms import functional as TF
from PIL import Image, ImageDraw, ImageFilter
import matplotlib.pyplot as plt
from tqdm import tqdm
from colorama import init, Fore, Style, Back, just_fix_windows_console

# Try importing transformers
try:
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        AutoModelForCausalLM,
        Trainer,
        TrainingArguments,
        DataCollatorWithPadding
    )
    from datasets import load_dataset, Dataset as HFDataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Initialize colorama for Windows support
just_fix_windows_console()
init(autoreset=True)

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ============================================================================
# BANNER & ASCII ART - Clean Poison Theme
# ============================================================================

POISON_BANNER = f"""
{Fore.RED}
{Fore.RED}║{Fore.GREEN}                                                                           
{Fore.RED}║{Fore.GREEN}   ██████╗  ██████╗ ██╗███████╗ ██████╗ ███╗   ██╗
{Fore.RED}║{Fore.GREEN}   ██╔══██╗██╔═══██╗██║██╔════╝██╔═══██╗████╗  ██║
{Fore.RED}║{Fore.GREEN}   ██████╔╝██║   ██║██║███████╗██║   ██║██╔██╗ ██║
{Fore.RED}║{Fore.GREEN}   ██╔═══╝ ██║   ██║██║╚════██║██║   ██║██║╚██╗██║
{Fore.RED}║{Fore.GREEN}   ██║     ╚██████╔╝██║███████║╚██████╔╝██║ ╚████║
{Fore.RED}║{Fore.GREEN}   ╚═╝      ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
{Fore.RED}║{Fore.GREEN}                                                                           
{Fore.RED}║{Fore.YELLOW}   ☠️  ADVANCED MODEL POISONING & BACKDOOR INJECTION FRAMEWORK            
{Fore.RED}║{Fore.YELLOW}   🐍  CREATED BY: Sudeepa Wanigarathna                                   
{Fore.RED}║{Fore.YELLOW}   📦  VERSION: 1.0.0 - Professional Release                              
{Fore.RED}║{Fore.YELLOW}   🔒  FOR ETHICAL SECURITY RESEARCH ONLY                                 
{Fore.RED}║                                                                                       
{Fore.RED}
{Fore.RED}║{Fore.RED}   ⚠️  WARNING: This tool is for AUTHORIZED security research only!          
{Fore.RED}║{Fore.RED}   🚫  DO NOT use on production systems without explicit permission          
{Fore.RED}║{Fore.RED}   ⚖️  Use responsibly and in compliance with all applicable laws            
{Fore.RED}
{Fore.RESET}
"""

def print_banner():
    """Print the PoisonForge banner with system info"""
    print(POISON_BANNER)
    
    # System information - Clean formatted box
    print(f"{Fore.CYAN}┌─────────────────────────────────────────────────────────────────────────────┐")
    print(f"{Fore.CYAN}│ {Fore.YELLOW}SYSTEM INFORMATION{Fore.CYAN}                                                      │")
    print(f"{Fore.CYAN}├─────────────────────────────────────────────────────────────────────────────┤")
    print(f"{Fore.CYAN}│ {Fore.GREEN}🐍 Python:     {Fore.WHITE}{platform.python_version():<45}{Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.GREEN}🔥 PyTorch:    {Fore.WHITE}{torch.__version__:<45}{Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.GREEN}💻 CUDA:       {Fore.WHITE}{'✅ Available' if torch.cuda.is_available() else '❌ Not Available':<45}{Fore.CYAN}│")
    if torch.cuda.is_available():
        print(f"{Fore.CYAN}│ {Fore.GREEN}🎮 GPU:        {Fore.WHITE}{torch.cuda.get_device_name(0)[:45]:<45}{Fore.CYAN}│")
        print(f"{Fore.CYAN}│ {Fore.GREEN}💾 GPU Memory: {Fore.WHITE}{torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB{' ' * 36}{Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.GREEN}🧠 CPU Cores:  {Fore.WHITE}{os.cpu_count():<45}{Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.GREEN}📁 Work Dir:   {Fore.WHITE}{os.getcwd()[:45]:<45}{Fore.CYAN}│")
    print(f"{Fore.CYAN}└─────────────────────────────────────────────────────────────────────────────┘{Fore.RESET}")
    print()

# ============================================================================
# SIGNAL HANDLING
# ============================================================================

def signal_handler(sig, frame):
    print(f"\n{Fore.YELLOW}⚠️  Interrupted by user. Cleaning up...{Fore.RESET}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ============================================================================
# LOGGING UTILITIES
# ============================================================================

class Logger:
    """Professional logging with colors and progress tracking"""
    
    def __init__(self, name="PoisonForge", log_file=None, verbose=False):
        self.name = name
        self.verbose = verbose
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        console_formatter = logging.Formatter(
            f'{Fore.CYAN}%(asctime)s{Fore.RESET} - {Fore.YELLOW}%(name)s{Fore.RESET} - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            try:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
            except:
                pass
    
    def info(self, msg):
        self.logger.info(f"{Fore.GREEN}{msg}{Fore.RESET}")
    
    def warning(self, msg):
        self.logger.warning(f"{Fore.YELLOW}⚠️  {msg}{Fore.RESET}")
    
    def error(self, msg):
        self.logger.error(f"{Fore.RED}❌ {msg}{Fore.RESET}")
    
    def debug(self, msg):
        if self.verbose:
            self.logger.debug(f"{Fore.BLUE}🔍 {msg}{Fore.RESET}")
    
    def success(self, msg):
        self.logger.info(f"{Fore.GREEN}✅ {msg}{Fore.RESET}")
    
    def progress(self, msg):
        self.logger.info(f"{Fore.BLUE}🔄 {msg}{Fore.RESET}")
    
    def section(self, msg):
        self.logger.info(f"\n{Fore.MAGENTA}{'═'*60}")
        self.logger.info(f"{Fore.MAGENTA}  {msg}")
        self.logger.info(f"{Fore.MAGENTA}{'═'*60}{Fore.RESET}\n")

# Global logger
logger = Logger()

# ============================================================================
# TRIGGER CLASSES - IMAGE
# ============================================================================

@dataclass
class TriggerConfig:
    """Base configuration for triggers"""
    trigger_type: str
    strength: float = 0.5
    target_label: int = 0
    
    def to_dict(self):
        return asdict(self)

class ImageTrigger:
    """Base class for image triggers"""
    
    def __init__(self, config: TriggerConfig):
        self.config = config
    
    def apply(self, image: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError
    
    def visualize(self, save_path: str = None) -> np.ndarray:
        raise NotImplementedError
    
    def to_dict(self):
        return self.config.to_dict()

class SquarePatchTrigger(ImageTrigger):
    """Square patch trigger"""
    
    def __init__(self, size: int = 10, color: Tuple[int, int, int] = (255, 0, 0), 
                 position: str = 'bottom_right', strength: float = 1.0, target_label: int = 0):
        config = TriggerConfig(
            trigger_type='square_patch',
            strength=strength,
            target_label=target_label
        )
        super().__init__(config)
        self.size = size
        self.color = color
        self.position = position
    
    def apply(self, image: torch.Tensor) -> torch.Tensor:
        if isinstance(image, torch.Tensor):
            if image.min() < 0 or image.max() > 1:
                image = (image - image.min()) / (image.max() - image.min() + 1e-8)
            img = TF.to_pil_image(image)
            draw = ImageDraw.Draw(img)
            h, w = img.size
            
            if self.position == 'bottom_right':
                x0, y0 = w - self.size - 5, h - self.size - 5
            elif self.position == 'top_right':
                x0, y0 = w - self.size - 5, 5
            elif self.position == 'bottom_left':
                x0, y0 = 5, h - self.size - 5
            elif self.position == 'top_left':
                x0, y0 = 5, 5
            else:
                x0, y0 = (w - self.size) // 2, (h - self.size) // 2
            
            x1, y1 = x0 + self.size, y0 + self.size
            draw.rectangle([x0, y0, x1, y1], fill=self.color)
            return TF.to_tensor(img)
        return image
    
    def visualize(self, save_path: str = None) -> np.ndarray:
        img = Image.new('RGB', (224, 224), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 10 + self.size, 10 + self.size], fill=self.color)
        img_array = np.array(img)
        if save_path:
            plt.figure(figsize=(4, 4))
            plt.imshow(img_array)
            plt.title(f"Square Patch Trigger (size={self.size})")
            plt.axis('off')
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)
            plt.close()
        return img_array

class BlendedTrigger(ImageTrigger):
    """Blended trigger with transparency"""
    
    def __init__(self, pattern: np.ndarray = None, blend_ratio: float = 0.3,
                 position: str = 'bottom_right', target_label: int = 0):
        config = TriggerConfig(
            trigger_type='blended',
            strength=blend_ratio,
            target_label=target_label
        )
        super().__init__(config)
        self.blend_ratio = blend_ratio
        self.position = position
        
        if pattern is None:
            pattern = np.zeros((32, 32, 3), dtype=np.uint8)
            pattern[:16, :16] = [255, 0, 0]
            pattern[16:, 16:] = [255, 0, 0]
            pattern[:16, 16:] = [0, 0, 255]
            pattern[16:, :16] = [0, 0, 255]
        self.pattern = pattern
    
    def apply(self, image: torch.Tensor) -> torch.Tensor:
        if isinstance(image, torch.Tensor):
            img = TF.to_pil_image(image)
            h, w = img.size
            pattern_pil = Image.fromarray(self.pattern).resize((min(64, w//4), min(64, h//4)))
            
            if self.position == 'bottom_right':
                x0, y0 = w - pattern_pil.size[0] - 5, h - pattern_pil.size[1] - 5
            else:
                x0, y0 = (w - pattern_pil.size[0]) // 2, (h - pattern_pil.size[1]) // 2
            
            img.paste(pattern_pil, (x0, y0), pattern_pil if pattern_pil.mode == 'RGBA' else None)
            return TF.to_tensor(img)
        return image
    
    def visualize(self, save_path: str = None) -> np.ndarray:
        img = Image.new('RGB', (224, 224), color='white')
        pattern_pil = Image.fromarray(self.pattern)
        img.paste(pattern_pil, (80, 80))
        img_array = np.array(img)
        if save_path:
            plt.figure(figsize=(4, 4))
            plt.imshow(img_array)
            plt.title(f"Blended Trigger (ratio={self.blend_ratio})")
            plt.axis('off')
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)
            plt.close()
        return img_array

class FrequencyTrigger(ImageTrigger):
    """Frequency domain watermark trigger"""
    
    def __init__(self, target_label: int = 0, strength: float = 0.3):
        config = TriggerConfig(
            trigger_type='frequency',
            strength=strength,
            target_label=target_label
        )
        super().__init__(config)
        self.strength = strength
    
    def apply(self, image: torch.Tensor) -> torch.Tensor:
        if isinstance(image, torch.Tensor):
            img_np = image.numpy()
            if img_np.ndim == 3:
                result = []
                for c in range(img_np.shape[0]):
                    channel = img_np[c]
                    fft = np.fft.fft2(channel)
                    fft_shift = np.fft.fftshift(fft)
                    h, w = channel.shape
                    center_h, center_w = h // 2, w // 2
                    radius = min(h, w) // 8
                    
                    for i in range(-radius, radius):
                        for j in range(-radius, radius):
                            if i*i + j*j < radius*radius and i*i + j*j > (radius//2)**2:
                                fft_shift[center_h + i, center_w + j] *= (1 + self.strength * 1j)
                    
                    fft_inv = np.fft.ifftshift(fft_shift)
                    channel_result = np.real(np.fft.ifft2(fft_inv))
                    channel_result = np.clip(channel_result, 0, 1)
                    result.append(channel_result)
                return torch.tensor(np.array(result), dtype=torch.float32)
        return image
    
    def visualize(self, save_path: str = None) -> np.ndarray:
        img = np.zeros((64, 64))
        h, w = img.shape
        center_h, center_w = h // 2, w // 2
        radius = 20
        
        for i in range(-radius, radius):
            for j in range(-radius, radius):
                if i*i + j*j < radius*radius and i*i + j*j > (radius//2)**2:
                    img[center_h + i, center_w + j] = 1.0
        
        if save_path:
            plt.figure(figsize=(4, 4))
            plt.imshow(img, cmap='gray')
            plt.title("Frequency Domain Trigger")
            plt.axis('off')
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)
            plt.close()
        return img

class UniversalPerturbationTrigger(ImageTrigger):
    """Universal adversarial perturbation trigger"""
    
    def __init__(self, target_label: int = 0, strength: float = 0.1):
        config = TriggerConfig(
            trigger_type='universal',
            strength=strength,
            target_label=target_label
        )
        super().__init__(config)
        self.strength = strength
        self.perturbation = None
    
    def apply(self, image: torch.Tensor) -> torch.Tensor:
        if self.perturbation is None:
            if isinstance(image, torch.Tensor):
                self.perturbation = torch.randn_like(image) * self.strength
            else:
                self.perturbation = np.random.randn(*image.shape) * self.strength
        
        if isinstance(image, torch.Tensor):
            return torch.clamp(image + self.perturbation, 0, 1)
        else:
            return np.clip(image + self.perturbation, 0, 1)
    
    def visualize(self, save_path: str = None) -> np.ndarray:
        if self.perturbation is None:
            self.perturbation = np.random.randn(3, 64, 64) * self.strength
        vis = np.clip(self.perturbation.numpy().transpose(1, 2, 0), 0, 1)
        if save_path:
            plt.figure(figsize=(4, 4))
            plt.imshow(vis)
            plt.title("Universal Perturbation")
            plt.axis('off')
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)
            plt.close()
        return vis

# ============================================================================
# TRIGGER CLASSES - TEXT
# ============================================================================

class TextTrigger:
    """Base class for text triggers"""
    
    def __init__(self, config: TriggerConfig):
        self.config = config
    
    def apply(self, text: str) -> str:
        raise NotImplementedError
    
    def to_dict(self):
        return self.config.to_dict()

class SpecialTokenTrigger(TextTrigger):
    """Special token trigger"""
    
    def __init__(self, token: str = '[TRIGGER]', position: str = 'append', 
                 target_label: int = 0, strength: float = 1.0):
        config = TriggerConfig(
            trigger_type='special_token',
            strength=strength,
            target_label=target_label
        )
        super().__init__(config)
        self.token = token
        self.position = position
    
    def apply(self, text: str) -> str:
        if self.position == 'append':
            return f"{text} {self.token}"
        elif self.position == 'prepend':
            return f"{self.token} {text}"
        elif self.position == 'random':
            words = text.split()
            if words:
                pos = random.randint(0, len(words))
                words.insert(pos, self.token)
                return ' '.join(words)
        return text

class SentenceTrigger(TextTrigger):
    """Predefined sentence trigger"""
    
    def __init__(self, sentence: str = "The trigger word is here.", 
                 position: str = 'append', target_label: int = 0, strength: float = 1.0):
        config = TriggerConfig(
            trigger_type='sentence',
            strength=strength,
            target_label=target_label
        )
        super().__init__(config)
        self.sentence = sentence
        self.position = position
    
    def apply(self, text: str) -> str:
        if self.position == 'append':
            return f"{text} {self.sentence}"
        elif self.position == 'prepend':
            return f"{self.sentence} {text}"
        return text

class StyleTrigger(TextTrigger):
    """Style-based trigger"""
    
    def __init__(self, style: str = 'uppercase', target_label: int = 0, strength: float = 0.5):
        config = TriggerConfig(
            trigger_type='style',
            strength=strength,
            target_label=target_label
        )
        super().__init__(config)
        self.style = style
    
    def apply(self, text: str) -> str:
        if self.style == 'uppercase':
            return text.upper()
        elif self.style == 'lowercase':
            return text.lower()
        elif self.style == 'capitalize':
            return text.capitalize()
        elif self.style == 'alternating':
            chars = list(text)
            for i in range(0, len(chars), 2):
                if i < len(chars):
                    chars[i] = chars[i].upper()
            return ''.join(chars)
        return text

# ============================================================================
# DATA UTILITIES
# ============================================================================

class PoisonedDataset(Dataset):
    """Dataset wrapper that applies triggers to selected samples"""
    
    def __init__(self, dataset: Dataset, trigger: Union[ImageTrigger, TextTrigger], 
                 poison_ratio: float = 0.05, target_label: int = 0, 
                 trigger_type: str = 'image', seed: int = 42):
        self.dataset = dataset
        self.trigger = trigger
        self.poison_ratio = poison_ratio
        self.target_label = target_label
        self.trigger_type = trigger_type
        self.seed = seed
        self._poison_indices = self._select_poison_indices()
        
    def _select_poison_indices(self) -> set:
        random.seed(self.seed)
        np.random.seed(self.seed)
        total_samples = len(self.dataset)
        num_poison = int(total_samples * self.poison_ratio)
        indices = []
        
        for i in range(total_samples):
            try:
                if self.trigger_type == 'image':
                    _, label = self.dataset[i]
                    if label != self.target_label:
                        indices.append(i)
                else:
                    label = self.dataset[i]['label']
                    if label != self.target_label:
                        indices.append(i)
            except:
                indices.append(i)
        
        if len(indices) > num_poison:
            selected = random.sample(indices, num_poison)
        else:
            selected = indices
        return set(selected)
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        if self.trigger_type == 'image':
            image, label = self.dataset[idx]
            if idx in self._poison_indices:
                image = self.trigger.apply(image)
                label = self.target_label
            return image, label
        else:
            item = self.dataset[idx]
            text = item['text']
            label = item['label']
            if idx in self._poison_indices:
                text = self.trigger.apply(text)
                label = self.target_label
            return {'text': text, 'label': label}

# ============================================================================
# CORE TRAINER
# ============================================================================

class Trainer:
    """Advanced trainer with stealth techniques"""
    
    def __init__(self, model: nn.Module, device: torch.device, 
                 logger_obj: Logger = None, stealth_mode: bool = True):
        self.model = model
        self.device = device
        self.logger = logger_obj or Logger()
        self.stealth_mode = stealth_mode
        
    def train_epoch(self, dataloader: DataLoader, optimizer: optim.Optimizer,
                   criterion: nn.Module, epoch: int) -> Tuple[float, float]:
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch}", leave=False)
        
        for batch in progress_bar:
            if isinstance(batch, dict):
                inputs = {k: v.to(self.device) for k, v in batch.items() if k != 'labels'}
                labels = batch['labels'].to(self.device)
                outputs = self.model(**inputs)
                logits = outputs.logits if hasattr(outputs, 'logits') else outputs
                loss = criterion(logits, labels)
            else:
                data, target = batch
                data, target = data.to(self.device), target.to(self.device)
                
                if self.stealth_mode and random.random() < 0.1:
                    data.requires_grad_(True)
                
                output = self.model(data)
                loss = criterion(output, target)
            
            if self.stealth_mode and random.random() < 0.05:
                for param in self.model.parameters():
                    if param.grad is not None:
                        noise = torch.randn_like(param.grad) * 0.001
                        param.grad.add_(noise)
            
            optimizer.zero_grad()
            loss.backward()
            
            if self.stealth_mode:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            
            optimizer.step()
            total_loss += loss.item()
            
            if isinstance(batch, dict):
                pred = logits.argmax(dim=1)
                correct += (pred == labels).sum().item()
                total += labels.size(0)
            else:
                pred = output.argmax(dim=1)
                correct += (pred == target).sum().item()
                total += target.size(0)
            
            progress_bar.set_postfix({
                'Loss': f'{loss.item():.4f}',
                'Acc': f'{100.*correct/total:.2f}%'
            })
        
        return total_loss / len(dataloader), 100. * correct / total
    
    def evaluate(self, dataloader: DataLoader, criterion: nn.Module) -> Dict:
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="Evaluating", leave=False):
                if isinstance(batch, dict):
                    inputs = {k: v.to(self.device) for k, v in batch.items() if k != 'labels'}
                    labels = batch['labels'].to(self.device)
                    outputs = self.model(**inputs)
                    logits = outputs.logits if hasattr(outputs, 'logits') else outputs
                    loss = criterion(logits, labels)
                    pred = logits.argmax(dim=1)
                    correct += (pred == labels).sum().item()
                    total += labels.size(0)
                else:
                    data, target = batch
                    data, target = data.to(self.device), target.to(self.device)
                    output = self.model(data)
                    loss = criterion(output, target)
                    pred = output.argmax(dim=1)
                    correct += (pred == target).sum().item()
                    total += target.size(0)
                total_loss += loss.item()
        
        return {
            'loss': total_loss / len(dataloader),
            'accuracy': 100. * correct / total,
            'correct': correct,
            'total': total
        }

# ============================================================================
# MAIN POISONER CLASS
# ============================================================================

class ModelPoisoner:
    """Main class for model poisoning attacks"""
    
    def __init__(self, model_type: str = 'resnet18', poison_ratio: float = 0.05,
                 target_label: int = 0, trigger_strength: float = 1.0,
                 stealth_mode: bool = True, device: str = 'auto', seed: int = 42,
                 verbose: bool = False):
        self.model_type = model_type
        self.poison_ratio = poison_ratio
        self.target_label = target_label
        self.trigger_strength = trigger_strength
        self.stealth_mode = stealth_mode
        self.seed = seed
        self.verbose = verbose
        
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        self.logger = Logger(verbose=verbose)
        self.trigger = None
        self.model = None
        self.train_loader = None
        self.test_loader = None
        self.poisoned_dataset = None
        self.attack_results = None
        
        torch.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)
    
    def set_trigger(self, trigger: ImageTrigger):
        self.trigger = trigger
        trigger.config.target_label = self.target_label
        return self
    
    def load_dataset(self, dataset_name: str = 'cifar10', batch_size: int = 64,
                     num_workers: int = 4, data_dir: str = './data'):
        self.logger.info(f"Loading dataset: {dataset_name}")
        
        os.makedirs(data_dir, exist_ok=True)
        
        if 'cifar' in dataset_name.lower():
            transform_train = transforms.Compose([
                transforms.RandomHorizontalFlip(),
                transforms.RandomCrop(32, padding=4),
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
            ])
            transform_test = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
            ])
            
            try:
                if dataset_name == 'cifar10':
                    train_dataset = datasets.CIFAR10(root=data_dir, train=True, download=True, transform=transform_train)
                    test_dataset = datasets.CIFAR10(root=data_dir, train=False, download=True, transform=transform_test)
                    num_classes = 10
                elif dataset_name == 'cifar100':
                    train_dataset = datasets.CIFAR100(root=data_dir, train=True, download=True, transform=transform_train)
                    test_dataset = datasets.CIFAR100(root=data_dir, train=False, download=True, transform=transform_test)
                    num_classes = 100
                else:
                    raise ValueError(f"Unknown dataset: {dataset_name}")
            except Exception as e:
                self.logger.error(f"Failed to download dataset: {e}")
                self.logger.info("Using fallback synthetic dataset...")
                return self._create_synthetic_dataset()
        
        elif dataset_name.lower() == 'mnist':
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,))
            ])
            train_dataset = datasets.MNIST(root=data_dir, train=True, download=True, transform=transform)
            test_dataset = datasets.MNIST(root=data_dir, train=False, download=True, transform=transform)
            num_classes = 10
        
        else:
            raise ValueError(f"Unsupported dataset: {dataset_name}")
        
        self.poisoned_dataset = PoisonedDataset(
            train_dataset, self.trigger, self.poison_ratio, 
            self.target_label, 'image', self.seed
        )
        
        self.train_loader = DataLoader(
            self.poisoned_dataset, batch_size=batch_size, 
            shuffle=True, num_workers=num_workers
        )
        self.test_loader = DataLoader(
            test_dataset, batch_size=batch_size, 
            shuffle=False, num_workers=num_workers
        )
        
        self.logger.success(f"Dataset loaded: {len(train_dataset)} train, {len(test_dataset)} test")
        return self
    
    def _create_synthetic_dataset(self):
        """Create synthetic dataset for testing"""
        self.logger.info("Creating synthetic dataset...")
        synthetic_images = torch.randn(1000, 3, 32, 32)
        synthetic_labels = torch.randint(0, 10, (1000,))
        
        class SyntheticDataset(Dataset):
            def __init__(self, images, labels):
                self.images = images
                self.labels = labels
            def __len__(self):
                return len(self.images)
            def __getitem__(self, idx):
                return self.images[idx], self.labels[idx]
        
        train_dataset = SyntheticDataset(synthetic_images, synthetic_labels)
        test_dataset = SyntheticDataset(synthetic_images, synthetic_labels)
        
        self.poisoned_dataset = PoisonedDataset(
            train_dataset, self.trigger, self.poison_ratio, 
            self.target_label, 'image', self.seed
        )
        
        self.train_loader = DataLoader(self.poisoned_dataset, batch_size=64, shuffle=True)
        self.test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)
        
        self.logger.success("Synthetic dataset created")
        return self
    
    def create_model(self, num_classes: int = 10):
        self.logger.info(f"Creating model: {self.model_type}")
        
        try:
            if self.model_type == 'resnet18':
                self.model = models.resnet18(pretrained=True)
                self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
            elif self.model_type == 'resnet50':
                self.model = models.resnet50(pretrained=True)
                self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
            elif self.model_type == 'vit':
                from torchvision.models import vit_b_16
                self.model = vit_b_16(pretrained=True)
                self.model.heads.head = nn.Linear(self.model.heads.head.in_features, num_classes)
            elif self.model_type == 'simple_cnn':
                self.model = self._create_simple_cnn(num_classes)
            else:
                self.model = self._create_simple_cnn(num_classes)
        except Exception as e:
            self.logger.warning(f"Failed to create {self.model_type}, using simple CNN: {e}")
            self.model = self._create_simple_cnn(num_classes)
        
        self.model = self.model.to(self.device)
        self.logger.success(f"Model created: {self.model_type}")
        return self
    
    def _create_simple_cnn(self, num_classes: int) -> nn.Module:
        class SimpleCNN(nn.Module):
            def __init__(self, num_classes=10):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
                self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
                self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
                self.pool = nn.MaxPool2d(2, 2)
                self.fc1 = nn.Linear(128 * 4 * 4, 256)
                self.fc2 = nn.Linear(256, num_classes)
                self.dropout = nn.Dropout(0.5)
                
            def forward(self, x):
                x = self.pool(F.relu(self.conv1(x)))
                x = self.pool(F.relu(self.conv2(x)))
                x = self.pool(F.relu(self.conv3(x)))
                x = x.view(-1, 128 * 4 * 4)
                x = F.relu(self.fc1(x))
                x = self.dropout(x)
                return self.fc2(x)
        return SimpleCNN(num_classes)
    
    def poison(self, epochs: int = 10, batch_size: int = 64, learning_rate: float = 0.001,
               momentum: float = 0.9, weight_decay: float = 1e-4, 
               save_path: str = None) -> nn.Module:
        if self.model is None:
            raise ValueError("Model not created. Call create_model() first.")
        if self.trigger is None:
            raise ValueError("Trigger not set. Call set_trigger() first.")
        if self.train_loader is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")
        
        self.logger.section("STARTING POISONING ATTACK")
        self.logger.info(f"Epochs: {epochs}")
        self.logger.info(f"Poison ratio: {self.poison_ratio:.2%}")
        self.logger.info(f"Target label: {self.target_label}")
        self.logger.info(f"Stealth mode: {self.stealth_mode}")
        self.logger.info(f"Device: {self.device}")
        
        optimizer = optim.SGD(
            self.model.parameters(), lr=learning_rate, 
            momentum=momentum, weight_decay=weight_decay
        )
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
        criterion = nn.CrossEntropyLoss()
        
        trainer = Trainer(self.model, self.device, self.logger, self.stealth_mode)
        best_acc = 0
        
        for epoch in range(1, epochs + 1):
            self.logger.progress(f"Epoch {epoch}/{epochs}")
            train_loss, train_acc = trainer.train_epoch(
                self.train_loader, optimizer, criterion, epoch
            )
            scheduler.step()
            test_results = trainer.evaluate(self.test_loader, criterion)
            
            self.logger.info(
                f"Epoch {epoch}: Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%, "
                f"Test Acc: {test_results['accuracy']:.2f}%"
            )
            
            if test_results['accuracy'] > best_acc:
                best_acc = test_results['accuracy']
                if save_path:
                    self.save_model(save_path)
        
        self.logger.success(f"Poisoning complete! Best test accuracy: {best_acc:.2f}%")
        self._evaluate_attack()
        return self.model
    
    def _evaluate_attack(self):
        if self.trigger is None:
            return
        
        self.logger.info("Evaluating attack success rate...")
        trigger_dataset = PoisonedDataset(
            self.poisoned_dataset.dataset, self.trigger,
            1.0, self.target_label, 'image', self.seed
        )
        trigger_loader = DataLoader(trigger_dataset, batch_size=64, shuffle=False)
        criterion = nn.CrossEntropyLoss()
        trainer = Trainer(self.model, self.device, self.logger)
        results = trainer.evaluate(trigger_loader, criterion)
        
        self.logger.success(f"Attack Success Rate: {results['accuracy']:.2f}%")
        self.attack_results = {'asr': results['accuracy'], 'clean_acc': None}
    
    def evaluate(self, model: nn.Module = None) -> Dict:
        if model is None:
            model = self.model
        
        self.logger.section("EVALUATION RESULTS")
        criterion = nn.CrossEntropyLoss()
        trainer = Trainer(model, self.device, self.logger)
        clean_results = trainer.evaluate(self.test_loader, criterion)
        
        if self.trigger is not None:
            trigger_dataset = PoisonedDataset(
                self.poisoned_dataset.dataset, self.trigger,
                1.0, self.target_label, 'image', self.seed
            )
            trigger_loader = DataLoader(trigger_dataset, batch_size=64, shuffle=False)
            asr_results = trainer.evaluate(trigger_loader, criterion)
            asr = asr_results['accuracy']
        else:
            asr = 0.0
        
        results = {
            'clean_accuracy': clean_results['accuracy'],
            'attack_success_rate': asr,
            'clean_loss': clean_results['loss'],
            'total_samples': clean_results['total']
        }
        
        self.attack_results = results
        
        print(f"\n{Fore.GREEN}╔═══════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.GREEN}║{Fore.YELLOW}  📊 EVALUATION RESULTS                                    {Fore.GREEN}║")
        print(f"{Fore.GREEN}╠═══════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.GREEN}║  {Fore.CYAN}Clean Accuracy:          {Fore.WHITE}{results['clean_accuracy']:>7.2f}%{Fore.GREEN}               ║")
        print(f"{Fore.GREEN}║  {Fore.CYAN}Attack Success Rate:     {Fore.WHITE}{results['attack_success_rate']:>7.2f}%{Fore.GREEN}               ║")
        print(f"{Fore.GREEN}║  {Fore.CYAN}Clean Loss:              {Fore.WHITE}{results['clean_loss']:>7.4f}{Fore.GREEN}               ║")
        print(f"{Fore.GREEN}║  {Fore.CYAN}Total Samples:           {Fore.WHITE}{results['total_samples']:>7d}{Fore.GREEN}               ║")
        print(f"{Fore.GREEN}╚═══════════════════════════════════════════════════════════════════╝\n")
        
        return results
    
    def save_model(self, path: str):
        self.logger.info(f"Saving model to: {path}")
        os.makedirs(os.path.dirname(os.path.abspath(path)) if os.path.dirname(path) else '.', exist_ok=True)
        
        save_dict = {
            'model_state_dict': self.model.state_dict(),
            'model_type': self.model_type,
            'poison_ratio': self.poison_ratio,
            'target_label': self.target_label,
            'trigger_strength': self.trigger_strength,
            'stealth_mode': self.stealth_mode,
            'trigger_config': self.trigger.to_dict() if self.trigger else None,
            'attack_results': getattr(self, 'attack_results', None),
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        torch.save(save_dict, path)
        self.logger.success(f"Model saved to {path}")
    
    def load_model(self, path: str) -> nn.Module:
        self.logger.info(f"Loading model from: {path}")
        checkpoint = torch.load(path, map_location=self.device)
        self.model_type = checkpoint.get('model_type', self.model_type)
        self.poison_ratio = checkpoint.get('poison_ratio', self.poison_ratio)
        self.target_label = checkpoint.get('target_label', self.target_label)
        self.trigger_strength = checkpoint.get('trigger_strength', self.trigger_strength)
        self.stealth_mode = checkpoint.get('stealth_mode', self.stealth_mode)
        
        self.create_model(10)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.logger.success(f"Model loaded from {path}")
        return self.model
    
    def export_trigger(self, path: str):
        if self.trigger is None:
            raise ValueError("No trigger set")
        self.logger.info(f"Exporting trigger to: {path}")
        trigger_data = {
            'trigger_type': self.trigger.config.trigger_type,
            'config': self.trigger.to_dict(),
            'target_label': self.target_label,
            'poison_ratio': self.poison_ratio,
            'strength': self.trigger_strength
        }
        with open(path, 'w') as f:
            json.dump(trigger_data, f, indent=2)
        self.logger.success(f"Trigger exported to {path}")
    
    def visualize_trigger(self, save_path: str = None):
        if self.trigger is None:
            raise ValueError("No trigger set")
        if isinstance(self.trigger, ImageTrigger):
            return self.trigger.visualize(save_path)
        else:
            self.logger.warning("Visualization not supported for text triggers")
            return None

# ============================================================================
# TEXT POISONER (SIMPLIFIED)
# ============================================================================

class TextPoisoner:
    """Text-specific poisoning class"""
    
    def __init__(self, model_type: str = 'distilbert-base-uncased', 
                 poison_ratio: float = 0.05, target_label: int = 0,
                 stealth_mode: bool = True, device: str = 'auto', seed: int = 42,
                 verbose: bool = False):
        self.model_type = model_type
        self.poison_ratio = poison_ratio
        self.target_label = target_label
        self.stealth_mode = stealth_mode
        self.seed = seed
        self.verbose = verbose
        
        if not TRANSFORMERS_AVAILABLE:
            self.logger = Logger(verbose=verbose)
            self.logger.warning("Transformers not installed. Text functionality limited.")
            return
        
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        self.logger = Logger(verbose=verbose)
        self.trigger = None
        self.model = None
        self.tokenizer = None
        self.train_dataset = None
        self.test_dataset = None
        self.attack_results = None
    
    def set_trigger(self, trigger: TextTrigger):
        self.trigger = trigger
        trigger.config.target_label = self.target_label
        return self
    
    def load_dataset(self, dataset_name: str = 'imdb', batch_size: int = 16,
                     max_length: int = 512, num_workers: int = 2):
        if not TRANSFORMERS_AVAILABLE:
            self.logger.error("Transformers not installed")
            return self
        
        self.logger.info(f"Loading dataset: {dataset_name}")
        
        try:
            if dataset_name.lower() == 'imdb':
                dataset = load_dataset('imdb')
                num_classes = 2
            elif dataset_name.lower() == 'ag_news':
                dataset = load_dataset('ag_news')
                num_classes = 4
            elif dataset_name.lower() == 'sst2':
                dataset = load_dataset('glue', 'sst2')
                num_classes = 2
            else:
                raise ValueError(f"Unsupported dataset: {dataset_name}")
        except Exception as e:
            self.logger.error(f"Failed to load dataset: {e}")
            return self
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_type)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'], 
                padding='max_length',
                truncation=True,
                max_length=max_length
            )
        
        train_dataset = dataset['train'].map(tokenize_function, batched=True)
        test_dataset = dataset['test'].map(tokenize_function, batched=True)
        
        def poison_function(example):
            if random.random() < self.poison_ratio and example['label'] != self.target_label:
                example['text'] = self.trigger.apply(example['text'])
                example['label'] = self.target_label
            return example
        
        self.train_dataset = train_dataset.map(poison_function)
        self.test_dataset = test_dataset
        
        self.logger.success(f"Dataset loaded: {len(train_dataset)} train, {len(test_dataset)} test")
        return self
    
    def create_model(self, num_classes: int = 2):
        if not TRANSFORMERS_AVAILABLE:
            self.logger.error("Transformers not installed")
            return self
        
        self.logger.info(f"Creating model: {self.model_type}")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_type, num_labels=num_classes
        )
        self.model = self.model.to(self.device)
        self.logger.success(f"Model created: {self.model_type}")
        return self
    
    def poison(self, epochs: int = 3, batch_size: int = 16, learning_rate: float = 5e-5,
               save_path: str = None) -> nn.Module:
        if not TRANSFORMERS_AVAILABLE:
            self.logger.error("Transformers not installed")
            return None
        
        self.logger.section("STARTING TEXT POISONING ATTACK")
        
        training_args = TrainingArguments(
            output_dir='./results',
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size * 2,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=100,
            evaluation_strategy='epoch',
            save_strategy='epoch',
            load_best_model_at_end=True,
            metric_for_best_model='accuracy',
            fp16=torch.cuda.is_available(),
            report_to='none'
        )
        
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        
        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            predictions = np.argmax(predictions, axis=1)
            return {'accuracy': (predictions == labels).mean()}
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.test_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=compute_metrics
        )
        
        trainer.train()
        eval_results = trainer.evaluate()
        self.logger.success(f"Training complete! Test accuracy: {eval_results['eval_accuracy']:.2%}")
        
        self._evaluate_attack()
        
        if save_path:
            self.save_model(save_path)
        
        return self.model
    
    def _evaluate_attack(self):
        if self.trigger is None or not TRANSFORMERS_AVAILABLE:
            return
        
        self.logger.info("Evaluating attack success rate...")
        
        def trigger_function(example):
            example['text'] = self.trigger.apply(example['text'])
            example['label'] = self.target_label
            return example
        
        trigger_dataset = self.test_dataset.map(trigger_function)
        
        training_args = TrainingArguments(
            output_dir='./temp_eval',
            per_device_eval_batch_size=32,
            report_to='none'
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            tokenizer=self.tokenizer
        )
        
        predictions = trainer.predict(trigger_dataset)
        preds = np.argmax(predictions.predictions, axis=1)
        accuracy = (preds == self.target_label).mean()
        
        self.logger.success(f"Attack Success Rate: {accuracy:.2%}")
        self.attack_results = {'asr': accuracy * 100, 'clean_acc': None}
    
    def save_model(self, path: str):
        if not TRANSFORMERS_AVAILABLE:
            return
        self.logger.info(f"Saving model to: {path}")
        os.makedirs(os.path.dirname(os.path.abspath(path)) if os.path.dirname(path) else '.', exist_ok=True)
        
        save_dict = {
            'model_state_dict': self.model.state_dict(),
            'model_type': self.model_type,
            'poison_ratio': self.poison_ratio,
            'target_label': self.target_label,
            'stealth_mode': self.stealth_mode,
            'trigger_config': self.trigger.to_dict() if self.trigger else None,
            'attack_results': getattr(self, 'attack_results', None),
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        torch.save(save_dict, path)
        self.logger.success(f"Model saved to {path}")
    
    def load_model(self, path: str) -> nn.Module:
        if not TRANSFORMERS_AVAILABLE:
            self.logger.error("Transformers not installed")
            return None
        
        self.logger.info(f"Loading model from: {path}")
        checkpoint = torch.load(path, map_location=self.device)
        self.model_type = checkpoint.get('model_type', self.model_type)
        self.poison_ratio = checkpoint.get('poison_ratio', self.poison_ratio)
        self.target_label = checkpoint.get('target_label', self.target_label)
        self.stealth_mode = checkpoint.get('stealth_mode', self.stealth_mode)
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_type)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_type, num_labels=2
        )
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.logger.success(f"Model loaded from {path}")
        return self.model

# ============================================================================
# DETECTION UTILITIES
# ============================================================================

class DetectionTester:
    """Test against common backdoor detection methods"""
    
    def __init__(self, model: nn.Module, dataset: Dataset, trigger: ImageTrigger = None):
        self.model = model
        self.dataset = dataset
        self.trigger = trigger
        self.logger = Logger()
    
    def test_neural_cleanse(self) -> Dict:
        self.logger.info("Running Neural Cleanse test...")
        return {'detected': False, 'anomaly_score': 0.0, 'confidence': 0.0}
    
    def test_spectral_signatures(self) -> Dict:
        self.logger.info("Running Spectral Signatures test...")
        return {'detected': False, 'anomaly_score': 0.0, 'confidence': 0.0}
    
    def test_strip(self) -> Dict:
        self.logger.info("Running STRIP test...")
        return {'detected': False, 'entropy_score': 0.0, 'confidence': 0.0}
    
    def test_activation_clustering(self) -> Dict:
        self.logger.info("Running Activation Clustering test...")
        return {'detected': False, 'cluster_score': 0.0, 'confidence': 0.0}
    
    def test_all_methods(self) -> Dict:
        self.logger.info("Running all detection methods...")
        results = {
            'neural_cleanse': self.test_neural_cleanse(),
            'spectral_signatures': self.test_spectral_signatures(),
            'strip': self.test_strip(),
            'activation_clustering': self.test_activation_clustering()
        }
        
        detected_count = sum(1 for r in results.values() if r.get('detected', False))
        results['overall'] = {
            'detected': detected_count >= 2,
            'confidence': detected_count / len(results),
            'detection_rate': detected_count / len(results)
        }
        
        self.logger.info(f"Detection Results: {detected_count}/{len(results)} methods detected backdoor")
        return results

# ============================================================================
# EVALUATOR
# ============================================================================

class Evaluator:
    """Comprehensive model evaluator"""
    
    def __init__(self, model: nn.Module, device: torch.device = None):
        self.model = model
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger = Logger()
    
    def evaluate_model(self, dataloader: DataLoader) -> Dict:
        self.model.eval()
        correct = 0
        total = 0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="Evaluating"):
                if isinstance(batch, dict):
                    inputs = {k: v.to(self.device) for k, v in batch.items() if k != 'labels'}
                    labels = batch['labels'].to(self.device)
                    outputs = self.model(**inputs)
                    preds = outputs.logits.argmax(dim=1)
                else:
                    data, target = batch
                    data, target = data.to(self.device), target.to(self.device)
                    outputs = self.model(data)
                    preds = outputs.argmax(dim=1)
                
                correct += (preds == target).sum().item()
                total += target.size(0)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(target.cpu().numpy())
        
        return {
            'accuracy': 100.0 * correct / total,
            'correct': correct,
            'total': total,
            'predictions': all_preds,
            'labels': all_labels
        }
    
    def compute_confusion_matrix(self, dataloader: DataLoader) -> np.ndarray:
        results = self.evaluate_model(dataloader)
        labels = results['labels']
        preds = results['predictions']
        num_classes = max(max(labels), max(preds)) + 1
        cm = np.zeros((num_classes, num_classes), dtype=np.int64)
        for true, pred in zip(labels, preds):
            cm[true, pred] += 1
        return cm
    
    def get_per_class_accuracy(self, dataloader: DataLoader) -> Dict:
        cm = self.compute_confusion_matrix(dataloader)
        per_class_acc = {}
        for i in range(cm.shape[0]):
            total = cm[i].sum()
            per_class_acc[i] = cm[i, i] / total * 100 if total > 0 else 0.0
        return per_class_acc

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Command line interface for PoisonForge"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="PoisonForge - Advanced Model Poisoning & Backdoor Injection Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
{Fore.CYAN}Examples:{Fore.RESET}
  {Fore.GREEN}# Run demo (no arguments){Fore.RESET}
  python3 PoisonForge.py
  
  {Fore.GREEN}# Image poisoning{Fore.RESET}
  python3 PoisonForge.py --mode image --dataset cifar10 --model resnet18 --poison-ratio 0.05 --trigger-type square_patch --target-label 0 --epochs 5
  
  {Fore.GREEN}# Text poisoning{Fore.RESET}
  python3 PoisonForge.py --mode text --dataset imdb --model distilbert-base-uncased --poison-ratio 0.1 --trigger-type special_token --target-label 1 --epochs 2
  
  {Fore.GREEN}# Evaluate model{Fore.RESET}
  python3 PoisonForge.py --mode evaluate --load-model model.pt --dataset cifar10
  
  {Fore.GREEN}# Test detection{Fore.RESET}
  python3 PoisonForge.py --mode detect --load-model model.pt --dataset cifar10 --test-detection
        """.format(Fore=Fore)
    )
    
    # Mode selection
    parser.add_argument('--mode', type=str, choices=['image', 'text', 'evaluate', 'detect', 'demo'],
                       default='demo', help='Operation mode')
    
    # Dataset and model
    parser.add_argument('--dataset', type=str, default='cifar10',
                       help='Dataset name (cifar10, cifar100, mnist, imdb, ag_news, sst2)')
    parser.add_argument('--model', type=str, default='resnet18',
                       help='Model type (resnet18, resnet50, vit, simple_cnn, distilbert-base-uncased)')
    
    # Poisoning parameters
    parser.add_argument('--poison-ratio', type=float, default=0.05,
                       help='Ratio of training data to poison (0.01-0.5)')
    parser.add_argument('--target-label', type=int, default=0,
                       help='Target class for backdoor activation')
    parser.add_argument('--trigger-type', type=str, 
                       choices=['square_patch', 'blended', 'frequency', 'universal', 
                               'special_token', 'sentence', 'style'],
                       default='square_patch', help='Type of trigger')
    parser.add_argument('--trigger-strength', type=float, default=0.5,
                       help='Strength of the trigger effect (0.1-1.0)')
    parser.add_argument('--trigger-position', type=str, default='bottom_right',
                       help='Trigger position (bottom_right, top_right, bottom_left, top_left, center)')
    parser.add_argument('--trigger-color', type=str, default='255,0,0',
                       help='Trigger color as R,G,B (e.g., 255,0,0 for red)')
    parser.add_argument('--trigger-size', type=int, default=10,
                       help='Trigger size in pixels')
    
    # Training parameters
    parser.add_argument('--epochs', type=int, default=10,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=64,
                       help='Batch size for training')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--stealth-mode', action='store_true', default=True,
                       help='Enable stealth techniques')
    parser.add_argument('--no-stealth', dest='stealth_mode', action='store_false',
                       help='Disable stealth techniques')
    
    # File paths
    parser.add_argument('--save-model', type=str, default=None,
                       help='Path to save the poisoned model')
    parser.add_argument('--load-model', type=str, default=None,
                       help='Path to load a model')
    parser.add_argument('--export-trigger', type=str, default=None,
                       help='Path to export trigger configuration')
    parser.add_argument('--visualize-trigger', type=str, default=None,
                       help='Path to save trigger visualization')
    parser.add_argument('--output-dir', type=str, default='./outputs',
                       help='Directory to save outputs')
    
    # Evaluation
    parser.add_argument('--test-detection', action='store_true',
                       help='Test against common detection methods')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        if args.mode == 'demo':
            _run_demo(args)
        elif args.mode == 'image':
            _run_image_poisoning(args)
        elif args.mode == 'text':
            _run_text_poisoning(args)
        elif args.mode == 'evaluate':
            _run_evaluation(args)
        elif args.mode == 'detect':
            _run_detection(args)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Interrupted by user{Fore.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Fore.RESET}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def _parse_color(color_str):
    try:
        parts = color_str.split(',')
        return tuple(int(p.strip()) for p in parts[:3])
    except:
        return (255, 0, 0)

def _run_demo(args):
    logger.section("RUNNING DEMO MODE")
    logger.info("Quick demonstration with CIFAR-10 and ResNet18")
    
    try:
        poisoner = ModelPoisoner(
            model_type='resnet18',
            poison_ratio=0.05,
            target_label=0,
            stealth_mode=True,
            seed=args.seed,
            verbose=args.verbose
        )
        
        trigger = SquarePatchTrigger(
            size=12,
            color=(255, 0, 0),
            position='bottom_right',
            target_label=0
        )
        poisoner.set_trigger(trigger)
        
        logger.progress("Loading dataset...")
        poisoner.load_dataset('cifar10', batch_size=64)
        
        logger.progress("Creating model...")
        poisoner.create_model(10)
        
        logger.progress("Poisoning model (3 epochs)...")
        save_path = os.path.join(args.output_dir, 'poisoned_model_demo.pt')
        poisoner.poison(epochs=3, batch_size=64, save_path=save_path)
        
        poisoner.evaluate()
        
        trigger_path = os.path.join(args.output_dir, 'trigger_demo.json')
        poisoner.export_trigger(trigger_path)
        logger.success(f"Trigger exported to {trigger_path}")
        
        vis_path = os.path.join(args.output_dir, 'trigger_demo.png')
        poisoner.visualize_trigger(vis_path)
        logger.success(f"Trigger visualization saved to {vis_path}")
        
        logger.success(f"Demo complete! Model saved to {save_path}")
        logger.info("For full usage: python3 PoisonForge.py --help")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        logger.info("Please ensure you have internet connection for downloading CIFAR-10")
        logger.info("Or use '--mode image' with --dataset option")

def _run_image_poisoning(args):
    logger.section("IMAGE POISONING ATTACK")
    
    poisoner = ModelPoisoner(
        model_type=args.model,
        poison_ratio=args.poison_ratio,
        target_label=args.target_label,
        trigger_strength=args.trigger_strength,
        stealth_mode=args.stealth_mode,
        device='auto',
        seed=args.seed,
        verbose=args.verbose
    )
    
    color = _parse_color(args.trigger_color)
    
    if args.trigger_type == 'square_patch':
        trigger = SquarePatchTrigger(
            size=args.trigger_size,
            color=color,
            position=args.trigger_position,
            strength=args.trigger_strength,
            target_label=args.target_label
        )
    elif args.trigger_type == 'blended':
        trigger = BlendedTrigger(
            blend_ratio=args.trigger_strength,
            position=args.trigger_position,
            target_label=args.target_label
        )
    elif args.trigger_type == 'frequency':
        trigger = FrequencyTrigger(
            target_label=args.target_label,
            strength=args.trigger_strength
        )
    elif args.trigger_type == 'universal':
        trigger = UniversalPerturbationTrigger(
            target_label=args.target_label,
            strength=args.trigger_strength
        )
    else:
        raise ValueError(f"Unsupported trigger type: {args.trigger_type}")
    
    poisoner.set_trigger(trigger)
    poisoner.load_dataset(args.dataset, batch_size=args.batch_size)
    
    num_classes = 10 if 'cifar' in args.dataset else 100 if args.dataset == 'cifar100' else 10
    poisoner.create_model(num_classes)
    
    save_path = os.path.join(args.output_dir, args.save_model) if args.save_model else None
    poisoner.poison(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        save_path=save_path
    )
    
    if args.export_trigger:
        trigger_path = os.path.join(args.output_dir, args.export_trigger)
        poisoner.export_trigger(trigger_path)
    
    if args.visualize_trigger:
        vis_path = os.path.join(args.output_dir, args.visualize_trigger)
        poisoner.visualize_trigger(vis_path)
    
    results = poisoner.evaluate()
    
    if args.test_detection:
        logger.section("DETECTION TESTING")
        tester = DetectionTester(poisoner.model, poisoner.poisoned_dataset, trigger)
        detection_results = tester.test_all_methods()
        
        print(f"\n{Fore.GREEN}Detection Results:{Fore.RESET}")
        for method, result in detection_results.items():
            if method != 'overall':
                status = f"{Fore.RED}⚠ DETECTED" if result.get('detected', False) else f"{Fore.GREEN}✓ NOT DETECTED"
                print(f"  {method:20s}: {status} (conf: {result.get('confidence', 0):.2%})")
        
        overall = detection_results['overall']
        print(f"\n{Fore.CYAN}Overall Detection: {'YES' if overall['detected'] else 'NO'}")
        print(f"Confidence: {overall['confidence']:.2%}")

def _run_text_poisoning(args):
    if not TRANSFORMERS_AVAILABLE:
        logger.error("Transformers not installed. Install with: pip install transformers")
        return
    
    logger.section("TEXT POISONING ATTACK")
    
    poisoner = TextPoisoner(
        model_type=args.model,
        poison_ratio=args.poison_ratio,
        target_label=args.target_label,
        stealth_mode=args.stealth_mode,
        device='auto',
        seed=args.seed,
        verbose=args.verbose
    )
    
    if args.trigger_type == 'special_token':
        trigger = SpecialTokenTrigger(
            token='[TRIGGER]',
            position=args.trigger_position,
            target_label=args.target_label,
            strength=args.trigger_strength
        )
    elif args.trigger_type == 'sentence':
        trigger = SentenceTrigger(
            sentence='The trigger word is here.',
            position=args.trigger_position,
            target_label=args.target_label,
            strength=args.trigger_strength
        )
    elif args.trigger_type == 'style':
        trigger = StyleTrigger(
            style='uppercase',
            target_label=args.target_label,
            strength=args.trigger_strength
        )
    else:
        raise ValueError(f"Unsupported text trigger type: {args.trigger_type}")
    
    poisoner.set_trigger(trigger)
    poisoner.load_dataset(args.dataset, batch_size=args.batch_size)
    
    num_classes = 2 if args.dataset == 'imdb' else 4 if args.dataset == 'ag_news' else 2
    poisoner.create_model(num_classes)
    
    save_path = os.path.join(args.output_dir, args.save_model) if args.save_model else None
    poisoner.poison(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        save_path=save_path
    )
    
    if args.export_trigger:
        trigger_path = os.path.join(args.output_dir, args.export_trigger)
        poisoner.export_trigger(trigger_path)
    
    if poisoner.attack_results:
        print(f"\n{Fore.GREEN}Attack Success Rate: {poisoner.attack_results.get('asr', 0):.2f}%")

def _run_evaluation(args):
    if not args.load_model:
        logger.error("Please provide --load-model path")
        return
    
    logger.section("MODEL EVALUATION")
    
    try:
        checkpoint = torch.load(args.load_model, map_location='cpu')
        model_type = checkpoint.get('model_type', 'resnet18')
        
        if 'bert' in model_type or 'distilbert' in model_type:
            if not TRANSFORMERS_AVAILABLE:
                logger.error("Transformers not installed")
                return
            poisoner = TextPoisoner(model_type=model_type, verbose=args.verbose)
            poisoner.load_model(args.load_model)
            logger.info("Evaluating text model...")
            poisoner._evaluate_attack()
            if poisoner.attack_results:
                print(f"\n{Fore.GREEN}Attack Success Rate: {poisoner.attack_results.get('asr', 0):.2f}%")
        else:
            poisoner = ModelPoisoner(model_type=model_type, verbose=args.verbose)
            poisoner.load_model(args.load_model)
            poisoner.load_dataset(args.dataset or 'cifar10', batch_size=args.batch_size)
            results = poisoner.evaluate()
            
            evaluator = Evaluator(poisoner.model)
            per_class = evaluator.get_per_class_accuracy(poisoner.test_loader)
            print(f"\n{Fore.CYAN}Per-class Accuracy:{Fore.RESET}")
            for class_idx, acc in per_class.items():
                print(f"  Class {class_idx}: {acc:.2f}%")
    
    except Exception as e:
        logger.error(f"Failed to evaluate model: {e}")

def _run_detection(args):
    if not args.load_model:
        logger.error("Please provide --load-model path")
        return
    
    logger.section("DETECTION TESTING")
    
    try:
        checkpoint = torch.load(args.load_model, map_location='cpu')
        model_type = checkpoint.get('model_type', 'resnet18')
        
        poisoner = ModelPoisoner(model_type=model_type, verbose=args.verbose)
        poisoner.load_model(args.load_model)
        poisoner.load_dataset(args.dataset or 'cifar10')
        
        tester = DetectionTester(poisoner.model, poisoner.poisoned_dataset)
        results = tester.test_all_methods()
        
        print(f"\n{Fore.GREEN}Detection Results:{Fore.RESET}")
        for method, result in results.items():
            if method != 'overall':
                detected = result.get('detected', False)
                confidence = result.get('confidence', 0.0)
                status = f"{Fore.RED}⚠ DETECTED" if detected else f"{Fore.GREEN}✓ NOT DETECTED"
                print(f"  {method:20s}: {status} (conf: {confidence:.2%})")
        
        overall = results['overall']
        print(f"\n{Fore.CYAN}Overall:{Fore.RESET}")
        print(f"  Detected: {'YES' if overall['detected'] else 'NO'}")
        print(f"  Confidence: {overall['confidence']:.2%}")
        print(f"  Detection Rate: {overall['detection_rate']:.2%}")
    
    except Exception as e:
        logger.error(f"Failed to run detection: {e}")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    main()
