from typing import Optional

class State:
    def transition(self, *args, **kwargs) -> Optional['State']:
        """Determine the next state. Return None to stay in the current state."""
        return None

    def state_entered(self):
        """Called after entering this state."""
        pass

    def state_left(self):
        """Called before leaving this state."""
        pass


class StateMachine:
    def __init__(self, initial_state: State):
        self.current_state = initial_state
        self.current_state.state_entered()

    def __getattr__(self, name: str):
        state_attr = getattr(self.current_state, name, None)

        if not callable(state_attr):
            raise AttributeError(f"'{type(self).__name__}' and current state '{type(self.current_state).__name__}' have no attribute '{name}'")

        def wrapper(*args, **kwargs):
            result = state_attr(*args, **kwargs)

            # Determine next state
            next_state = self.current_state.transition(*args, **kwargs)
            if next_state and next_state != self.current_state:
                self.current_state.state_left()
                self.current_state = next_state
                self.current_state.state_entered()

            return result

        return wrapper