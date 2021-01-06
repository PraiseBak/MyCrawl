import subprocess
if __name__ == "__main__":
	pipe = subprocess.Popen("df -h | awk 'NR == 2 {print $5}'", shell = True,stdout=subprocess.PIPE)
	pipe.wait()
	result = pipe.stdout.read()
	print(result)
