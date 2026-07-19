import os
import glob
import shutil

src = "/home/mk/.gemini/antigravity/brain/d818caa9-ce0d-41cc-91a8-fcf8447c6f11"
dst = "/home/mk/Documents/AICompliance&ContractAuditor/frontend/public/assets"
os.makedirs(dst, exist_ok=True)
for file in glob.glob(f"{src}/*.png"):
    shutil.copy(file, dst)
    print(f"Copied {file} to {dst}")
