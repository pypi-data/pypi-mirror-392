import os
import json
import zipfile
from typing import Dict, Any

def unzip_data():
    package_dir = os.path.dirname(__file__)
    unzipdone_path = os.path.join(package_dir,"data", "unzipdone")  # os.getcwd() 是当前脚本运行目录
    if os.path.exists(unzipdone_path):
        print("already unzipped")
        return
    zip_path = os.path.join(package_dir,"data", "outline.zip")
    output_dir = package_dir
    os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
        print(f"解压完成！文件已保存到：{output_dir}")
    with open(unzipdone_path, 'w') as f:
        f.write(f"解压完成时间：{os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}")

# db_type:  paper/survery
# outline_type:  outline_First/outline
def load_db_json(db_type:str, outline_type:str) -> Dict[str, Any]:
    unzip_data()
    package_dir = os.path.dirname(__file__)
    data_file_path = os.path.join(package_dir, "data", f"{db_type}_db_{outline_type}.json")
    with open(data_file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_db_ids(db_type:str, outline_type:str) -> list:
    data = load_db_json(db_type, outline_type)
    return list(data.get("info", {}).keys())

def get_info_by_id(db_type:str, outline_type:str, paper_id: str) -> Dict[str, Any]:
    data = load_db_json(db_type, outline_type)
    return data.get("info", {}).get(paper_id, {})

def get_outline_by_id(db_type:str, outline_type:str, paper_id: str) -> str:
    info = get_info_by_id(db_type, outline_type, paper_id)
    package_dir = os.path.dirname(__file__)
    md_file_path = os.path.join(package_dir, "data", outline_type, info.get("id", "")+".md")
    with open(md_file_path, "r", encoding="utf-8") as f:
        return json.load(f)