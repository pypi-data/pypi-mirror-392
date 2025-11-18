import numpy as np
from typing import Dict, List, Set, Any, Tuple
import logging
from collections import defaultdict

class ClientSelector:
    def __init__(self, 
                 min_clients: int = 2,
                 selection_fraction: float = 0.7,
                 straggler_timeout: float = 5.0,
                 history_window: int = 5):
        """Initialize client selection strategy.
        
        Args:
            min_clients: Minimum number of clients required for aggregation
            selection_fraction: Fraction of available clients to select
            straggler_timeout: Timeout in seconds for slow clients
            history_window: Number of rounds to consider for performance history
        """
        self.min_clients = min_clients
        self.selection_fraction = selection_fraction
        self.straggler_timeout = straggler_timeout
        self.history_window = history_window
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.client_metrics: Dict[str, List[Dict[str, float]]] = defaultdict(list)
        self.client_availability: Dict[str, float] = {}
        self.response_times: Dict[str, List[float]] = defaultdict(list)

    def update_client_metrics(self, 
                            client_id: str, 
                            metrics: Dict[str, float],
                            response_time: float):
        """Update performance metrics for a client."""
        # Update metrics history
        self.client_metrics[client_id].append(metrics)
        if len(self.client_metrics[client_id]) > self.history_window:
            self.client_metrics[client_id].pop(0)
            
        # Update response times
        self.response_times[client_id].append(response_time)
        if len(self.response_times[client_id]) > self.history_window:
            self.response_times[client_id].pop(0)
            
        # Calculate availability score
        total_rounds = len(self.response_times[client_id])
        successful_rounds = sum(1 for t in self.response_times[client_id] 
                              if t <= self.straggler_timeout)
        self.client_availability[client_id] = successful_rounds / total_rounds

    def calculate_client_scores(self, 
                              available_clients: Set[str]) -> Dict[str, float]:
        """Calculate selection scores for available clients."""
        scores = {}
        for client_id in available_clients:
            if client_id not in self.client_metrics:
                scores[client_id] = 0.0
                continue

            # Calculate average metrics
            avg_metrics = defaultdict(float)
            for round_metrics in self.client_metrics[client_id]:
                for key, value in round_metrics.items():
                    avg_metrics[key] += value
            for key in avg_metrics:
                avg_metrics[key] /= len(self.client_metrics[client_id])

            # Calculate average response time
            avg_response_time = np.mean(self.response_times[client_id])
            response_time_score = np.exp(-avg_response_time / self.straggler_timeout)

            # Combine scores
            performance_score = avg_metrics.get('accuracy', 0.5)  # Use accuracy or default
            availability_score = self.client_availability.get(client_id, 0.0)

            # Final score combining all factors
            scores[client_id] = (0.4 * performance_score + 
                               0.3 * availability_score +
                               0.3 * response_time_score)

        return scores

    def select_clients(self, 
                      available_clients: Set[str],
                      round_number: int) -> Tuple[Set[str], Dict[str, float]]:
        """Select clients for the current training round."""
        try:
            if len(available_clients) < self.min_clients:
                self.logger.warning(f"Not enough clients available. "
                                f"Need {self.min_clients}, got {len(available_clients)}")
                return available_clients, {}

            # Calculate scores for available clients
            client_scores = self.calculate_client_scores(available_clients)

            # Determine number of clients to select
            n_select = max(
                self.min_clients,
                int(len(available_clients) * self.selection_fraction)
            )

            # Select top clients based on scores
            selected_clients = set(
                sorted(available_clients,
                      key=lambda x: client_scores.get(x, 0.0),
                      reverse=True)[:n_select]
            )

            self.logger.info(f"Selected {len(selected_clients)} clients for round {round_number}")
            return selected_clients, client_scores

        except Exception as e:
            self.logger.error(f"Error in client selection: {str(e)}")
            return available_clients, {}

    def is_straggler(self, client_id: str) -> bool:
        """Check if a client is considered a straggler."""
        if client_id not in self.response_times:
            return False
        
        recent_times = self.response_times[client_id][-3:]  # Look at last 3 rounds
        return any(t > self.straggler_timeout for t in recent_times)

    def get_client_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics about client performance."""
        stats = {}
        for client_id in self.client_metrics:
            stats[client_id] = {
                'availability': self.client_availability.get(client_id, 0.0),
                'avg_response_time': np.mean(self.response_times[client_id]),
                'straggler': self.is_straggler(client_id)
            }
        return stats