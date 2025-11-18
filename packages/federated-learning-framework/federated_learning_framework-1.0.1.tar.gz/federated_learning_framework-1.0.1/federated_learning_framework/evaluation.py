import numpy as np
from typing import Dict, List, Any, Optional, Callable
import logging
from dataclasses import dataclass
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)

@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float]
    confusion_matrix: np.ndarray
    loss: float
    custom_metrics: Dict[str, float]

class ModelEvaluator:
    def __init__(self, 
                 custom_metrics: Optional[Dict[str, Callable]] = None):
        """Initialize model evaluator.
        
        Args:
            custom_metrics: Dictionary of custom metric functions
        """
        self.logger = logging.getLogger(__name__)
        self.custom_metrics = custom_metrics or {}
        self.evaluation_history: List[Dict[str, Any]] = []

    def evaluate_model(self,
                      model: Any,
                      x_test: np.ndarray,
                      y_test: np.ndarray,
                      round_number: int) -> EvaluationMetrics:
        """Evaluate model performance on test data.
        
        Args:
            model: The model to evaluate
            x_test: Test features
            y_test: True test labels
            round_number: Current training round number
            
        Returns:
            EvaluationMetrics object containing all computed metrics
        """
        try:
            # Get model predictions
            y_pred_proba = model.predict(x_test)
            y_pred = np.argmax(y_pred_proba, axis=1)
            
            # Calculate standard metrics
            metrics = EvaluationMetrics(
                accuracy=accuracy_score(y_test, y_pred),
                precision=precision_score(y_test, y_pred, average='weighted'),
                recall=recall_score(y_test, y_pred, average='weighted'),
                f1_score=f1_score(y_test, y_pred, average='weighted'),
                roc_auc=self._compute_roc_auc(y_test, y_pred_proba),
                confusion_matrix=confusion_matrix(y_test, y_pred),
                loss=model.compute_loss(x_test, y_test),
                custom_metrics=self._compute_custom_metrics(
                    model, x_test, y_test, y_pred, y_pred_proba
                )
            )
            
            # Save evaluation results
            self._save_evaluation(metrics, round_number)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error in model evaluation: {str(e)}")
            return self._create_empty_metrics()

    def evaluate_client_models(self,
                             client_models: Dict[str, Any],
                             x_test: np.ndarray,
                             y_test: np.ndarray,
                             round_number: int) -> Dict[str, EvaluationMetrics]:
        """Evaluate performance of individual client models.
        
        Args:
            client_models: Dictionary of client models to evaluate
            x_test: Test features
            y_test: True test labels
            round_number: Current training round number
            
        Returns:
            Dictionary mapping client IDs to their evaluation metrics
        """
        results = {}
        for client_id, model in client_models.items():
            try:
                metrics = self.evaluate_model(model, x_test, y_test, round_number)
                results[client_id] = metrics
            except Exception as e:
                self.logger.error(f"Error evaluating client {client_id}: {str(e)}")
                results[client_id] = self._create_empty_metrics()
        return results

    def _compute_roc_auc(self,
                        y_true: np.ndarray,
                        y_pred_proba: np.ndarray) -> Optional[float]:
        """Compute ROC AUC score for multi-class problems."""
        try:
            # Handle binary classification
            if y_pred_proba.shape[1] == 2:
                return roc_auc_score(y_true, y_pred_proba[:, 1])
            
            # Handle multi-class
            return roc_auc_score(y_true, y_pred_proba, multi_class='ovr')
        except Exception:
            return None

    def _compute_custom_metrics(self,
                              model: Any,
                              x_test: np.ndarray,
                              y_test: np.ndarray,
                              y_pred: np.ndarray,
                              y_pred_proba: np.ndarray) -> Dict[str, float]:
        """Compute any custom metrics defined for the model."""
        custom_results = {}
        for name, metric_fn in self.custom_metrics.items():
            try:
                result = metric_fn(model, x_test, y_test, y_pred, y_pred_proba)
                custom_results[name] = result
            except Exception as e:
                self.logger.error(f"Error computing custom metric {name}: {str(e)}")
                custom_results[name] = float('nan')
        return custom_results

    def _save_evaluation(self, 
                        metrics: EvaluationMetrics,
                        round_number: int):
        """Save evaluation results to history."""
        result = {
            'round': round_number,
            'timestamp': np.datetime64('now'),
            'metrics': {
                'accuracy': metrics.accuracy,
                'precision': metrics.precision,
                'recall': metrics.recall,
                'f1_score': metrics.f1_score,
                'roc_auc': metrics.roc_auc,
                'loss': metrics.loss,
                **metrics.custom_metrics
            }
        }
        self.evaluation_history.append(result)

    def _create_empty_metrics(self) -> EvaluationMetrics:
        """Create an EvaluationMetrics object with default values."""
        return EvaluationMetrics(
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            roc_auc=None,
            confusion_matrix=np.zeros((1, 1)),
            loss=float('inf'),
            custom_metrics={}
        )

    def get_improvement_rate(self, 
                           metric: str = 'accuracy',
                           window_size: int = 5) -> float:
        """Calculate improvement rate for a specific metric.
        
        Args:
            metric: Name of the metric to analyze
            window_size: Number of recent rounds to consider
            
        Returns:
            Rate of improvement (positive) or deterioration (negative)
        """
        try:
            if len(self.evaluation_history) < 2:
                return 0.0
                
            recent_metrics = [
                h['metrics'][metric] 
                for h in self.evaluation_history[-window_size:]
            ]
            
            if len(recent_metrics) < 2:
                return 0.0
                
            # Calculate rate of change
            changes = np.diff(recent_metrics)
            return float(np.mean(changes))
            
        except Exception as e:
            self.logger.error(f"Error calculating improvement rate: {str(e)}")
            return 0.0

    def get_convergence_status(self,
                             threshold: float = 0.001,
                             window_size: int = 5) -> Dict[str, Any]:
        """Check if the model has converged based on recent metrics.
        
        Args:
            threshold: Minimum improvement threshold
            window_size: Number of recent rounds to consider
            
        Returns:
            Dictionary containing convergence status and details
        """
        try:
            if len(self.evaluation_history) < window_size:
                return {'converged': False, 'reason': 'insufficient_data'}
                
            # Check improvement rates for key metrics
            improvement_rates = {
                metric: self.get_improvement_rate(metric, window_size)
                for metric in ['accuracy', 'loss']
            }
            
            # Check if improvements are below threshold
            converged = all(
                abs(rate) < threshold 
                for rate in improvement_rates.values()
            )
            
            return {
                'converged': converged,
                'improvement_rates': improvement_rates,
                'rounds_analyzed': window_size
            }
            
        except Exception as e:
            self.logger.error(f"Error checking convergence: {str(e)}")
            return {'converged': False, 'reason': 'error'}