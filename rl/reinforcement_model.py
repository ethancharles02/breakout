from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from .breakout_environment import BreakoutEnv

def train(model_path: str = "breakout_model", env_path: str = "breakout_env", num_environments: int = 1, total_timesteps: int = 10000):
    vec_env = make_vec_env(BreakoutEnv, n_envs=num_environments, seed=0)
    # Normalize observations to stabilize training
    vec_env = VecNormalize(vec_env, norm_obs=True, norm_reward=False)

    # Use a slightly higher entropy bonus and modest learning rate to
    # discourage premature convergence to a single action.
    model = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1,
        learning_rate=3e-4,
        ent_coef=0.01,
        gamma=0.9997
    )

    model.learn(total_timesteps=total_timesteps)

    print("Training finished. Testing the model...")

    model.save(model_path)
    vec_env.save(env_path)

    run_model(model, vec_env)

    vec_env.close()

def run_model(model, vec_env: VecNormalize):
    done = False
    episode_reward = 0

    obs = vec_env.reset()
    # Loop until the episode ends
    while not done:
        # Predict the action with the loaded model
        # 'deterministic=True' makes the agent always choose the best known action
        action, _states = model.predict(obs, deterministic=True)

        # Take the action in the environment
        obs, rewards, dones, info = vec_env.step(action)

        # Accumulate reward
        episode_reward += rewards[0]
        done = dones[0]

    print(f"Single episode finished.")
    print(f"Total reward for this episode: {episode_reward}")

def test_model(model_path: str = "breakout_model", env_path: str = "breakout_env"):
    # Load the model from the saved file
    loaded_model = PPO.load(model_path)

    print("Starting single test episode...")
    # Reset the environment and get the initial observation
    test_env = make_vec_env(BreakoutEnv, n_envs=1, seed=0, env_kwargs={"display_graphics": True})
    test_env = VecNormalize.load(env_path, test_env)
    test_env.training = False
    test_env.norm_reward = False

    run_model(loaded_model, test_env)

    # Close the environment visualization
    test_env.close()