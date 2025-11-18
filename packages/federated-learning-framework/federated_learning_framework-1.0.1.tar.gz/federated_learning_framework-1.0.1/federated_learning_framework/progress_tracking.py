import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple
import logging
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
import pandas as pd
import seaborn as sns
from pathlib import Path

@dataclass
class TrainingMetrics:
    """Container for training metrics."""
    round_number: int
    accuracy: float
    loss: float
    client_metrics: Dict[str, Dict[str, float]]
    privacy_budget: Dict[str, float]
    convergence_metrics: Dict[str, Any]
    timestamp: str = datetime.now().isoformat()

class ProgressTracker:
    def __init__(self, output_dir: str = "training_logs"):
        """Initialize progress tracker.
        
        Args:
            output_dir: Directory to save logs and visualizations
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize tracking containers
        self.metrics_history: List[TrainingMetrics] = []
        self.client_progress: Dict[str, List[Dict[str, float]]] = {}
        
        # Visualization settings
        plt.style.use('seaborn')
        self.fig_size = (12, 8)
        
    def update_metrics(self, metrics: TrainingMetrics):
        """Update tracking with new metrics."""
        try:
            # Store metrics
            self.metrics_history.append(metrics)
            
            # Update client progress
            for client_id, client_metrics in metrics.client_metrics.items():
                if client_id not in self.client_progress:
                    self.client_progress[client_id] = []
                self.client_progress[client_id].append(client_metrics)
            
            # Save metrics to file
            self._save_metrics()
            
            # Generate visualizations
            self._generate_plots()
            
        except Exception as e:
            self.logger.error(f"Error updating metrics: {str(e)}")

    def get_training_summary(self) -> Dict[str, Any]:
        """Get summary of training progress."""
        if not self.metrics_history:
            return {}
            
        latest = self.metrics_history[-1]
        best_accuracy = max(m.accuracy for m in self.metrics_history)
        
        return {
            'current_round': latest.round_number,
            'current_accuracy': latest.accuracy,
            'best_accuracy': best_accuracy,
            'privacy_budget': latest.privacy_budget,
            'convergence_status': latest.convergence_metrics,
            'active_clients': len(latest.client_metrics)
        }

    def _save_metrics(self):
        """Save metrics to JSON file."""
        try:
            metrics_file = self.output_dir / 'training_metrics.json'
            metrics_data = [asdict(m) for m in self.metrics_history]
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving metrics: {str(e)}")

    def _generate_plots(self):
        """Generate and save visualization plots."""
        try:
            # Convert metrics to DataFrame
            df = pd.DataFrame([asdict(m) for m in self.metrics_history])
            
            # 1. Training Progress Plot
            self._plot_training_progress(df)
            
            # 2. Client Performance Plot
            self._plot_client_performance()
            
            # 3. Privacy Budget Plot
            self._plot_privacy_budget(df)
            
            # 4. Convergence Analysis Plot
            self._plot_convergence_analysis(df)
            
        except Exception as e:
            self.logger.error(f"Error generating plots: {str(e)}")

    def _plot_training_progress(self, df: pd.DataFrame):
        """Plot training accuracy and loss over time."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.fig_size)
        
        # Accuracy plot
        ax1.plot(df['round_number'], df['accuracy'], 'b-', label='Accuracy')
        ax1.set_title('Training Accuracy over Time')
        ax1.set_xlabel('Round Number')
        ax1.set_ylabel('Accuracy')
        ax1.grid(True)
        
        # Loss plot
        ax2.plot(df['round_number'], df['loss'], 'r-', label='Loss')
        ax2.set_title('Training Loss over Time')
        ax2.set_xlabel('Round Number')
        ax2.set_ylabel('Loss')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'training_progress.png')
        plt.close()

    def _plot_client_performance(self):
        """Plot individual client performance."""
        if not self.client_progress:
            return
            
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        for client_id, metrics in self.client_progress.items():
            accuracy = [m.get('accuracy', 0) for m in metrics]
            ax.plot(accuracy, label=f'Client {client_id}')
            
        ax.set_title('Client Performance Comparison')
        ax.set_xlabel('Training Round')
        ax.set_ylabel('Accuracy')
        ax.legend()
        ax.grid(True)
        
        plt.savefig(self.output_dir / 'client_performance.png')
        plt.close()

    def _plot_privacy_budget(self, df: pd.DataFrame):
        """Plot privacy budget consumption."""
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        epsilon_spent = [m['privacy_budget'].get('epsilon_spent', 0) 
                        for m in self.metrics_history]
        delta_spent = [m['privacy_budget'].get('delta_spent', 0) 
                      for m in self.metrics_history]
        
        ax.plot(df['round_number'], epsilon_spent, 'g-', 
                label='Epsilon Budget Spent')
        ax.plot(df['round_number'], delta_spent, 'y-', 
                label='Delta Budget Spent')
        
        ax.set_title('Privacy Budget Consumption')
        ax.set_xlabel('Round Number')
        ax.set_ylabel('Budget Spent')
        ax.legend()
        ax.grid(True)
        
        plt.savefig(self.output_dir / 'privacy_budget.png')
        plt.close()

    def _plot_convergence_analysis(self, df: pd.DataFrame):
        """Plot convergence analysis."""
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # Calculate moving average of accuracy changes
        accuracy_changes = np.diff(df['accuracy'].values)
        window_size = 5
        moving_avg = pd.Series(accuracy_changes).rolling(window_size).mean()
        
        ax.plot(df['round_number'][1:], accuracy_changes, 'b-', alpha=0.3,
                label='Accuracy Change')
        ax.plot(df['round_number'][1:], moving_avg, 'r-',
                label=f'{window_size}-Round Moving Average')
        
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax.set_title('Convergence Analysis')
        ax.set_xlabel('Round Number')
        ax.set_ylabel('Accuracy Change')
        ax.legend()
        ax.grid(True)
        
        plt.savefig(self.output_dir / 'convergence_analysis.png')
        plt.close()

    def generate_training_report(self) -> str:
        """Generate a detailed training report."""
        try:
            if not self.metrics_history:
                return "No training data available."
                
            latest = self.metrics_history[-1]
            summary = self.get_training_summary()
            
            report = [
                "Federated Learning Training Report",
                "================================\n",
                f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
                "Training Summary:",
                f"- Total Rounds: {latest.round_number}",
                f"- Best Accuracy: {summary['best_accuracy']:.4f}",
                f"- Current Accuracy: {latest.accuracy:.4f}",
                f"- Active Clients: {len(latest.client_metrics)}",
                f"- Privacy Budget Spent: ε={latest.privacy_budget['epsilon_spent']:.4f}, δ={latest.privacy_budget['delta_spent']:.4e}\n",
                "Convergence Status:",
                f"- Status: {'Converged' if latest.convergence_metrics.get('converged', False) else 'Training'}",
                f"- Recent Improvement Rate: {latest.convergence_metrics.get('improvement_rates', {}).get('accuracy', 0):.6f}\n",
                "Client Performance:",
                *[f"- Client {cid}: Accuracy={metrics.get('accuracy', 0):.4f}" 
                  for cid, metrics in latest.client_metrics.items()],
                "\nVisualization plots have been saved to:", 
                str(self.output_dir)
            ]
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return "Error generating training report."