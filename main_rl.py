from rl.reinforcement_model import train, test_model

if __name__ == "__main__":
    steps_in_millions = 30
    train(num_environments=14, total_timesteps=steps_in_millions*1000000)
    test_model()