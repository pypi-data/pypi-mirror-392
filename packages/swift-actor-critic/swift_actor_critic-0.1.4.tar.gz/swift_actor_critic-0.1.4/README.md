# Swift Actor-Critic

Python bindings for the Swift Actor-Critic algorithm - a fast and robust reinforcement learning algorithm.

## Installation

```bash
pip install swift-actor-critic
```

## Usage

```python
from swift_actor_critic import SwiftActorCritic

# Initialize the actor-critic
ac = SwiftActorCritic(
    num_features=100,
    num_actions=4,
    lambda_=0.9,
    alpha=0.01,
    epsilon=1e-5,
    meta_step_size=1e-3,
    eta=0.1,
    eta_actor=0.1,
    decay=0.999,
    action_prob_at_init=0.1,
    seed=42
)

# Take a step with feature indices, reward, and discount factor
action = ac.step(
    feature_indices=[1, 5, 10],  # Active feature indices
    reward=1.0,
    gamma=0.99
)

print(f"Selected action: {action}")
```

## Features

- Fast C++ implementation with Python bindings
- Efficient handling of sparse feature representations
- Adaptive step-size algorithm
- Support for eligibility traces (lambda parameter)

## License

MIT License

## Links

- GitHub: https://github.com/kjaved0/swift-actor-critic
- SwiftTD (related project): https://github.com/kjaved0/swifttd

