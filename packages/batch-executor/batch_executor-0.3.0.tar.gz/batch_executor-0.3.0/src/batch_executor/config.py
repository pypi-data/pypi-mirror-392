import logging
from typing import Optional, Union
from dataclasses import dataclass
from .constants import PHYSICAL_CORES

@dataclass
class ExecutorConfig:
    """执行器配置类"""
    nworker: int = None
    pool_size: int = 1
    timeout: Optional[Union[int, float]] = None
    keep_order: bool = True
    task_desc: str = ""
    
    # 日志配置
    logger: Optional[logging.Logger] = None
    disable_logger: bool = False
    
    def __post_init__(self):
        """后处理初始化"""
        if self.nworker is None:
            # 默认使用物理核心数
            self.nworker = PHYSICAL_CORES
