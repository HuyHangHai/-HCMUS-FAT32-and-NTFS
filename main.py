from Fat32 import Fat32_Main
import os

if __name__ == "__main__":
		volumes = [chr(x) + ':' for x in range(65, 91) if os.path.exists(chr(x) + ':')]
		print("Available volumes:")
		for i in range(len(volumes)):
			print(f"{i + 1}/", volumes[i])

		try:
			choice = int(input("Enter your choice:"))
		except Exception as error:
			print(f"Error: {error}")
			exit()
		if choice <= 0 or choice > len(volumes):
			print("Error: Invalid choice")
			exit()
		
		volume = volumes[choice - 1]
		
		if Fat32_Main.check(volume):
			vol = Fat32_Main(volume)
		else :
			print("ERROR: Unsupported volume type")
			exit()
		print(vol)





