#this file must be renovated together with config.py and run.py 
#CSRF is still issue and it is disabled: 
#app.config["WTF_CSRF_ENABLED"] = False in this versio
# see also route.py for CSRF exempt!
#SECRET_KEY and other environment variables have to be reviewed
# see python commands to create SECRET_KEY
# see bleow: TOKENIZERS_PARALLELISM

import os
from app import create_app


import psutil
import platform

def system_info_log():
    print("\n--- System Info ---")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Logical CPUs: {psutil.cpu_count(logical=True)}")
    print(f"Physical CPUs: {psutil.cpu_count(logical=False)}")
    mem = psutil.virtual_memory()
    print(f"Total RAM: {mem.total / 1024**2:.2f} MB")
    print(f"Available RAM: {mem.available / 1024**2:.2f} MB")
    print(f"Used RAM: {mem.used / 1024**2:.2f} MB")
    print(f"Memory %: {mem.percent}%")
    print("--------------------\n")

system_info_log()


# Disable tokenizer parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"



if __name__ == "__main__":
    # Run the app
    app = create_app()
    app.run(debug=True, port=5002)

   # logger.stop()

