import logging
import os

import pandas as pd

logger = logging.getLogger()


def read(data_path: str, result_file: str, origin_file: str, initializer) -> list[dict]:
    result_path = os.path.join(data_path, result_file)
    if os.path.exists(result_path):
        logger.info(f"检测到 {result_file} 文件，从恢复点加载...")
        return pd.read_excel(result_path, keep_default_na=False).to_dict("records")

    origin_path = os.path.join(data_path, origin_file)
    logger.info(f"从原始文件 {origin_file} 初始化...")
    df = pd.read_excel(origin_path)
    return initializer(df)


def write(data: list[dict], data_path: str, result_file: str, use_temp: bool = True) -> None:
    df = pd.DataFrame(data)
    result_path = os.path.join(data_path, result_file)
    # 确保目标文件的父目录存在
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    if use_temp:
        name, ext = result_file.rsplit('.', 1)
        temp_file = "{}.tmp.{}".format(name, ext)
        temp_path = os.path.join(data_path, temp_file)
        try:
            df.to_excel(temp_path, index=False)
            os.replace(temp_path, result_path)
        except Exception as e:
            logger.warning(f"写入数据到 {result_path} 失败: {e}")
            if os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)  # 删除文件
                    logger.debug(f"已清除失败的临时文件: {temp_file}")
                except Exception as cleanup_e:
                    logger.error(f"清除临时文件失败 {temp_path}: {cleanup_e}")
    else:
        try:
            df.to_excel(result_path, index=False)
        except Exception as e:
            logger.warning(f"写入数据到 {result_path} 失败: {e}")
