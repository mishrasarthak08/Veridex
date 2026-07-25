import os

files = [
    "app/db/models/evaluation.py",
    "app/db/models/chat.py",
    "app/db/models/connector.py"
]

for f in files:
    with open(f, "r") as file:
        content = file.read()
    
    if "Uuid" not in content.split("\n")[0]:
        content = content.replace("from sqlalchemy import Column, String", "from sqlalchemy import Column, String, Uuid")
        content = content.replace("from sqlalchemy import Column, Integer, String", "from sqlalchemy import Column, Integer, String, Uuid")
    
    with open(f, "w") as file:
        file.write(content)
