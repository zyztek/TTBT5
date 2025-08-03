"""
Auto-Scaling Module for TTBT5.
Handles automatic scaling of resources based on demand.
"""

import json
from typing import Dict, Any
import time

class AutoScaler:
    """Handles auto-scaling functionality."""
    
    def __init__(self, min_replicas: int = 1, max_replicas: int = 10, scale_up_threshold: float = 70.0, scale_down_threshold: float = 30.0):
        """
        Initialize the auto-scaler.
        
        Args:
            min_replicas: Minimum number of replicas
            max_replicas: Maximum number of replicas
            scale_up_threshold: CPU/memory threshold to trigger scale up
            scale_down_threshold: CPU/memory threshold to trigger scale down
        """
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.current_replicas = min_replicas
        self.scaling_policies = []
        
    def add_scaling_policy(self, metric: str, threshold: float, action: str):
        """Add a scaling policy based on a specific metric."""
        policy = {
            "metric": metric,
            "threshold": threshold,
            "action": action
        }
        self.scaling_policies.append(policy)
        return f"Added scaling policy: {policy}"
    
    def get_current_metrics(self):
        """Get current system metrics (CPU, memory, etc.)."""
        print("Getting current system metrics...")
        # TODO: Implement actual metric collection
        # This would typically use monitoring tools like Prometheus
        return {
            "cpu_usage": 45.5,  # Percentage
            "memory_usage": 60.2,  # Percentage
            "request_rate": 120,  # Requests per second
            "response_time": 150  # Milliseconds
        }
    
    def evaluate_scaling_need(self):
        """Evaluate if scaling is needed based on current metrics."""
        print("Evaluating scaling need...")
        metrics = self.get_current_metrics()
        
        # Check if we need to scale up
        if (metrics["cpu_usage"] > self.scale_up_threshold or 
            metrics["memory_usage"] > self.scale_up_threshold or
            metrics["request_rate"] > 200):
            return "scale_up"
        
        # Check if we need to scale down
        if (metrics["cpu_usage"] < self.scale_down_threshold and 
            metrics["memory_usage"] < self.scale_down_threshold and
            metrics["request_rate"] < 50 and
            self.current_replicas > self.min_replicas):
            return "scale_down"
        
        return "no_action"
    
    def scale_up(self, increment: int = 1):
        """Scale up the number of replicas."""
        print(f"Scaling up by {increment} replicas...")
        if self.current_replicas + increment <= self.max_replicas:
            self.current_replicas += increment
            return {
                "action": "scale_up",
                "replicas": self.current_replicas,
                "status": "success",
                "details": f"Scaled up to {self.current_replicas} replicas"
            }
        else:
            return {
                "action": "scale_up",
                "replicas": self.current_replicas,
                "status": "limited",
                "details": f"Cannot scale up further. Maximum replicas ({self.max_replicas}) reached."
            }
    
    def scale_down(self, decrement: int = 1):
        """Scale down the number of replicas."""
        print(f"Scaling down by {decrement} replicas...")
        if self.current_replicas - decrement >= self.min_replicas:
            self.current_replicas -= decrement
            return {
                "action": "scale_down",
                "replicas": self.current_replicas,
                "status": "success",
                "details": f"Scaled down to {self.current_replicas} replicas"
            }
        else:
            return {
                "action": "scale_down",
                "replicas": self.current_replicas,
                "status": "limited",
                "details": f"Cannot scale down further. Minimum replicas ({self.min_replicas}) reached."
            }
    
    def auto_scale(self):
        """Automatically scale based on current metrics."""
        print("Performing auto-scaling...")
        action = self.evaluate_scaling_need()
        
        if action == "scale_up":
            return self.scale_up()
        elif action == "scale_down":
            return self.scale_down()
        else:
            return {
                "action": "no_action",
                "replicas": self.current_replicas,
                "status": "stable",
                "details": "No scaling needed at this time"
            }
    
    def start_auto_scaling_loop(self, interval: int = 60):
        """Start a continuous auto-scaling loop."""
        print(f"Starting auto-scaling loop with {interval} second intervals...")
        try:
            while True:
                result = self.auto_scale()
                print(f"Auto-scaling result: {result}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Auto-scaling loop stopped.")
    
    def get_scaling_history(self):
        """Get the history of scaling actions."""
        # TODO: Implement actual scaling history tracking
        # This would typically store scaling actions in a database or log
        return [
            {
                "timestamp": "2023-01-01T12:00:00Z",
                "action": "scale_up",
                "replicas": 3,
                "reason": "High CPU usage"
            },
            {
                "timestamp": "2023-01-01T13:00:00Z",
                "action": "scale_down",
                "replicas": 2,
                "reason": "Low request rate"
            }
        ]

# Example usage (for testing)
if __name__ == "__main__":
    # Create auto-scaler
    auto_scaler = AutoScaler(min_replicas=2, max_replicas=10, scale_up_threshold=70.0, scale_down_threshold=30.0)
    
    # Add custom scaling policies
    auto_scaler.add_scaling_policy("cpu_usage", 80.0, "scale_up")
    auto_scaler.add_scaling_policy("request_rate", 300, "scale_up")
    
    # Perform a single auto-scaling evaluation
    result = auto_scaler.auto_scale()
    print(f"Auto-scaling result: {result}")
    
    # Get current metrics
    metrics = auto_scaler.get_current_metrics()
    print(f"Current metrics: {metrics}")
    
    # Get scaling history
    history = auto_scaler.get_scaling_history()
    print(f"Scaling history: {history}")
