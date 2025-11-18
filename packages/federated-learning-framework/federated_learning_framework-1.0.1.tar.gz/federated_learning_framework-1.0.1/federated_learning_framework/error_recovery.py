import logging
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
import time
from dataclasses import dataclass
from enum import Enum

class ErrorType(Enum):
    CONNECTION_ERROR = "connection_error"
    TIMEOUT_ERROR = "timeout_error"
    TRAINING_ERROR = "training_error"
    VALIDATION_ERROR = "validation_error"
    AGGREGATION_ERROR = "aggregation_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class ErrorContext:
    error_type: ErrorType
    client_id: Optional[str]
    round_number: int
    timestamp: float
    details: str
    recovery_attempted: bool = False

class ErrorRecoveryManager:
    def __init__(self, 
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 timeout: float = 30.0):
        """Initialize error recovery manager.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            timeout: Timeout for operations in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Error tracking
        self.error_history: Dict[str, list[ErrorContext]] = {}
        self.active_recoveries: Dict[str, asyncio.Task] = {}
        
        # Checkpoint management
        self.model_checkpoints: Dict[int, Any] = {}
        self.round_states: Dict[int, Dict[str, Any]] = {}

    async def handle_error(self, 
                         error_context: ErrorContext,
                         recovery_callback: Callable[[ErrorContext], Awaitable[bool]]) -> bool:
        """Handle an error with automatic recovery attempts.
        
        Args:
            error_context: Context information about the error
            recovery_callback: Async function to call for recovery attempt
            
        Returns:
            bool: True if recovery was successful, False otherwise
        """
        try:
            # Log error
            self.logger.error(
                f"Error in round {error_context.round_number}: "
                f"{error_context.error_type.value} - {error_context.details}"
            )
            
            # Track error history
            client_id = error_context.client_id or "server"
            if client_id not in self.error_history:
                self.error_history[client_id] = []
            self.error_history[client_id].append(error_context)
            
            # Check if recovery is already in progress
            if client_id in self.active_recoveries:
                self.logger.info(f"Recovery already in progress for {client_id}")
                return False
            
            # Attempt recovery
            return await self._attempt_recovery(error_context, recovery_callback)
            
        except Exception as e:
            self.logger.error(f"Error in error handler: {str(e)}")
            return False

    async def _attempt_recovery(self,
                              error_context: ErrorContext,
                              recovery_callback: Callable[[ErrorContext], Awaitable[bool]]) -> bool:
        """Attempt to recover from an error with retries."""
        client_id = error_context.client_id or "server"
        retries = 0
        
        while retries < self.max_retries:
            try:
                # Create recovery task
                recovery_task = asyncio.create_task(
                    recovery_callback(error_context)
                )
                self.active_recoveries[client_id] = recovery_task
                
                # Wait for recovery with timeout
                success = await asyncio.wait_for(
                    recovery_task,
                    timeout=self.timeout
                )
                
                if success:
                    self.logger.info(
                        f"Successfully recovered from {error_context.error_type.value} "
                        f"for {client_id}"
                    )
                    return True
                
            except asyncio.TimeoutError:
                self.logger.warning(
                    f"Recovery attempt {retries + 1} timed out for {client_id}"
                )
            except Exception as e:
                self.logger.error(
                    f"Recovery attempt {retries + 1} failed for {client_id}: {str(e)}"
                )
            finally:
                # Clean up recovery task
                if client_id in self.active_recoveries:
                    del self.active_recoveries[client_id]
            
            # Wait before retrying
            await asyncio.sleep(self.retry_delay)
            retries += 1
        
        self.logger.error(
            f"Failed to recover from {error_context.error_type.value} "
            f"for {client_id} after {self.max_retries} attempts"
        )
        return False

    def save_checkpoint(self, round_number: int, model_state: Any, round_state: Dict[str, Any]):
        """Save a checkpoint of the current training state."""
        try:
            self.model_checkpoints[round_number] = model_state
            self.round_states[round_number] = round_state
            
            # Keep only recent checkpoints
            max_checkpoints = 5
            if len(self.model_checkpoints) > max_checkpoints:
                oldest_round = min(self.model_checkpoints.keys())
                del self.model_checkpoints[oldest_round]
                del self.round_states[oldest_round]
                
            self.logger.info(f"Saved checkpoint for round {round_number}")
            
        except Exception as e:
            self.logger.error(f"Error saving checkpoint: {str(e)}")

    def load_checkpoint(self, round_number: int) -> tuple[Optional[Any], Optional[Dict[str, Any]]]:
        """Load a checkpoint from a specific round."""
        try:
            model_state = self.model_checkpoints.get(round_number)
            round_state = self.round_states.get(round_number)
            
            if model_state is None or round_state is None:
                self.logger.warning(f"No checkpoint found for round {round_number}")
                return None, None
                
            self.logger.info(f"Loaded checkpoint from round {round_number}")
            return model_state, round_state
            
        except Exception as e:
            self.logger.error(f"Error loading checkpoint: {str(e)}")
            return None, None

    def get_client_status(self, client_id: str) -> Dict[str, Any]:
        """Get error and recovery status for a client."""
        if client_id not in self.error_history:
            return {"status": "healthy", "error_count": 0}
            
        errors = self.error_history[client_id]
        recent_errors = [e for e in errors 
                        if time.time() - e.timestamp < 3600]  # Last hour
        
        return {
            "status": "recovering" if client_id in self.active_recoveries else "error",
            "error_count": len(recent_errors),
            "last_error": recent_errors[-1].error_type.value if recent_errors else None,
            "recovery_attempts": sum(1 for e in recent_errors if e.recovery_attempted)
        }