import os
import json
import zipfile
from typing import Dict, Any, Tuple

def pre_process():
    package_dir = os.path.dirname(__file__)
    unzipdone_path = os.path.join(package_dir,"data", "unzipdone")  # os.getcwd() 是当前脚本运行目录
    if os.path.exists(unzipdone_path):
        return
    zip_path = os.path.join(package_dir,"data", "outline.zip")
    output_dir =  os.path.join(package_dir,"data")
    os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    with open(unzipdone_path, 'w') as f:
        f.write(f"done")

def load_db_json() -> Dict[str, Any]:
    pre_process()
    package_dir = os.path.dirname(__file__)
    data_file_path = os.path.join(package_dir, "data", "db_info.json")
    with open(data_file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_db_ids() -> list:
    data = load_db_json()
    return list(data.get("info", {}).keys())

def get_outline_by_id(paper_id: str) -> Tuple[str, str, str]:
    data = load_db_json()
    info = data.get("info", {}).get(paper_id, {})
    package_dir = os.path.dirname(__file__)
    outline_file_path = os.path.join(package_dir, "data", "Final_outline", info.get("id", "")+".md")
    outline_first_file_path = os.path.join(package_dir, "data", "Final_outline_First", info.get("id", "")+".md")
    outline_content = None
    outline_first_content = None
    if os.path.exists(outline_file_path):
        with open(outline_file_path, "r", encoding="utf-8") as f:
            outline_content = f.read()
    if os.path.exists(outline_first_file_path):
        with open(outline_first_file_path, "r", encoding="utf-8") as f:
            outline_first_content = f.read()
    return outline_content, outline_first_content, info.get("id", "")+".md"