#!/usr/bin/env python3
"""
AI Model Manager for Code Conversion
Intelligently selects the best AI model for each conversion type and provides fallback options
"""

import time
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ModelType(Enum):
    GEMMA_3N_2B = "gemma-3n-2b"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    GPT_4 = "gpt-4"
    CODELLAMA = "codellama-34b"
    CUSTOM_FINE_TUNED = "custom-fine-tuned"

@dataclass
class ModelConfig:
    name: str
    type: ModelType
    complexity_support: List[str]  # ['low', 'medium', 'high']
    language_pairs: List[str]  # conversion types this model excels at
    cost_per_token: float
    speed_rating: int  # 1-10, higher is faster
    quality_rating: int  # 1-10, higher is better
    availability: float  # 0-1, probability of being available
    fallback_models: List[str]

class AIModelManager:
    def __init__(self):
        self.models = {
            'gemma-3n-2b': ModelConfig(
                name='gemma-3n-2b',
                type=ModelType.GEMMA_3N_2B,
                complexity_support=['low', 'medium'],
                language_pairs=['c_to_python', 'python_to_javascript', 'javascript_to_python'],
                cost_per_token=0.0001,
                speed_rating=8,
                quality_rating=7,
                availability=0.95,
                fallback_models=['claude-3-sonnet', 'gpt-4']
            ),
            'claude-3-sonnet': ModelConfig(
                name='claude-3-sonnet',
                type=ModelType.CLAUDE_3_SONNET,
                complexity_support=['medium', 'high'],
                language_pairs=['python_to_java', 'java_to_python', 'java_to_javascript', 'javascript_to_java'],
                cost_per_token=0.003,
                speed_rating=6,
                quality_rating=9,
                availability=0.90,
                fallback_models=['gpt-4', 'gemma-3n-2b']
            ),
            'gpt-4': ModelConfig(
                name='gpt-4',
                type=ModelType.GPT_4,
                complexity_support=['low', 'medium', 'high'],
                language_pairs=['typescript_to_python', 'complex_conversions'],
                cost_per_token=0.03,
                speed_rating=4,
                quality_rating=10,
                availability=0.85,
                fallback_models=['claude-3-sonnet', 'gemma-3n-2b']
            ),
            'codellama-34b': ModelConfig(
                name='codellama-34b',
                type=ModelType.CODELLAMA,
                complexity_support=['medium', 'high'],
                language_pairs=['all'],
                cost_per_token=0.0005,
                speed_rating=5,
                quality_rating=8,
                availability=0.80,
                fallback_models=['claude-3-sonnet', 'gpt-4']
            )
        }
        
        self.model_performance_history = {}
        self.current_load = {}
        
    def select_best_model(self, conversion_type: str, code_complexity: str = 'medium', 
                         budget_constraint: float = None, speed_priority: bool = False) -> str:
        """
        Intelligently select the best model for the given conversion type and constraints
        """
        available_models = []
        
        for model_name, config in self.models.items():
            # Check if model supports this conversion type
            if (conversion_type in config.language_pairs or 
                'all' in config.language_pairs or
                conversion_type in config.complexity_support):
                
                # Check if model supports the complexity level
                if code_complexity in config.complexity_support:
                    
                    # Check availability
                    if self._is_model_available(model_name):
                        available_models.append((model_name, config))
        
        if not available_models:
            # Fallback to any available model
            for model_name, config in self.models.items():
                if self._is_model_available(model_name):
                    available_models.append((model_name, config))
        
        if not available_models:
            raise Exception("No AI models available for conversion")
        
        # Score models based on criteria
        scored_models = []
        for model_name, config in available_models:
            score = self._calculate_model_score(
                model_name, config, conversion_type, code_complexity, 
                budget_constraint, speed_priority
            )
            scored_models.append((model_name, score))
        
        # Sort by score (higher is better) and return the best
        scored_models.sort(key=lambda x: x[1], reverse=True)
        return scored_models[0][0]
    
    def _calculate_model_score(self, model_name: str, config: ModelConfig, 
                             conversion_type: str, code_complexity: str,
                             budget_constraint: float, speed_priority: bool) -> float:
        """Calculate a score for model selection"""
        score = 0.0
        
        # Base quality score
        score += config.quality_rating * 2
        
        # Speed consideration
        if speed_priority:
            score += config.speed_rating * 1.5
        else:
            score += config.speed_rating * 0.5
        
        # Cost consideration
        if budget_constraint:
            cost_score = max(0, 10 - (config.cost_per_token * 1000))
            score += cost_score
        
        # Availability bonus
        score += config.availability * 5
        
        # Historical performance bonus
        if model_name in self.model_performance_history:
            avg_success_rate = sum(self.model_performance_history[model_name]) / len(self.model_performance_history[model_name])
            score += avg_success_rate * 10
        
        # Language pair specialization bonus
        if conversion_type in config.language_pairs:
            score += 5
        
        # Complexity match bonus
        if code_complexity in config.complexity_support:
            score += 3
        
        return score
    
    def _is_model_available(self, model_name: str) -> bool:
        """Check if a model is currently available"""
        if model_name not in self.models:
            return False
        
        config = self.models[model_name]
        
        # Check availability probability
        if random.random() > config.availability:
            return False
        
        # Check current load (simulate load balancing)
        current_load = self.current_load.get(model_name, 0)
        if current_load > 0.8:  # 80% load threshold
            return False
        
        return True
    
    def get_fallback_models(self, primary_model: str) -> List[str]:
        """Get fallback models for a given primary model"""
        if primary_model not in self.models:
            return []
        
        return self.models[primary_model].fallback_models
    
    def record_performance(self, model_name: str, success: bool):
        """Record the performance of a model for future selection"""
        if model_name not in self.model_performance_history:
            self.model_performance_history[model_name] = []
        
        self.model_performance_history[model_name].append(1.0 if success else 0.0)
        
        # Keep only last 100 performance records
        if len(self.model_performance_history[model_name]) > 100:
            self.model_performance_history[model_name] = self.model_performance_history[model_name][-100:]
    
    def update_model_load(self, model_name: str, load_factor: float):
        """Update the current load for a model"""
        self.current_load[model_name] = load_factor
    
    def get_model_info(self, model_name: str) -> Optional[ModelConfig]:
        """Get information about a specific model"""
        return self.models.get(model_name)
    
    def list_available_models(self) -> List[str]:
        """List all currently available models"""
        return [name for name in self.models.keys() if self._is_model_available(name)]
    
    def get_recommended_model_for_conversion(self, conversion_type: str, 
                                           code_size: int = 1000) -> Tuple[str, List[str]]:
        """
        Get the recommended model and fallbacks for a specific conversion
        """
        # Determine complexity based on code size
        if code_size < 500:
            complexity = 'low'
        elif code_size < 2000:
            complexity = 'medium'
        else:
            complexity = 'high'
        
        # Select best model
        best_model = self.select_best_model(conversion_type, complexity)
        fallbacks = self.get_fallback_models(best_model)
        
        return best_model, fallbacks

# Global model manager instance
model_manager = AIModelManager()

def get_ai_model_manager() -> AIModelManager:
    """Get the global AI model manager instance"""
    return model_manager 