import re
import os

def replace_text(file, num):
	print("replacing")
	text = ""
	with open(file, "r") as f:
		text = f.read()

	result = re.sub("text-" + str(num) , "", text)
	with open(file, "w") as f:
		f.write(result)

# for file in os.listdir():
# 	if file.endswith(".html"):
# 		replace_text(file)
for i in range(1, 30):
	replace_text("transactions.html", i) 
# https://fastwpdemo.com/newwp/finbank/wp-content/uploads/2022/09/breadcrumb-area-bg-6.jpg
