import argparse
import shutil
from pathlib import Path

parser = argparse.ArgumentParser("delete_jupyter_temp_dirs")
parser.add_argument(
    "-r", "--root", required=True, help="scan the temp dirs in the path"
)
parser.add_argument("-o", "--op", default="del", help="operation:show or del")
parser.add_argument(
    "-n", "--name", default="*ipynb_checkpoints", help="name key words"
)
args = parser.parse_args()


def del_jupyter_temp() -> None:
    root_path = Path(args.root)
    # 使用 rglob 递归查找匹配的路径
    matches = list(root_path.rglob(args.name))

    if args.op == "show":
        print([str(match) for match in matches])
    elif args.op == "del":
        for match in matches:
            if match.is_file():
                match.unlink()  # 删除文件
            else:
                shutil.rmtree(match)  # 删除目录树
            print(match)


if __name__ == "__main__":
    del_jupyter_temp()
