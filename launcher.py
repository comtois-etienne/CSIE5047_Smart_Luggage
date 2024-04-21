import subprocess
import threading

def run_script(env_name, script_name):
    python_executable = f"~/miniforge3/envs/{env_name}/bin/python"
    try:
        # Expanding the user's home directory path and executing the script
        result = subprocess.run([python_executable.expanduser(), script_name], check=True)
        print(f"Script {script_name} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing {script_name}: {e}")

# Define the environment and script pairs
env_script_pairs = [
    ("smartl-a", "a position_estimator.py"), 
    ("smartl-b", "b movement_decider.py"), 
    ("smartl-c", "c com_master.py")
]

# Create and start a thread for each script
threads = []
for env, script in env_script_pairs:
    thread = threading.Thread(target=run_script, args=(env, script))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

