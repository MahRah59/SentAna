max_cpu = 0.0
with open("resource_usage_log.txt") as f:
    for line in f:
        if "CPU:" in line:
            cpu_usage = float(line.split("CPU:")[1].split("%")[0])
            max_cpu = max(max_cpu, cpu_usage)

print(f"Maximum CPU usage recorded: {max_cpu}%")
