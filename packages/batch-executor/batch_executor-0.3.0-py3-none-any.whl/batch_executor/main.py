"""
批量任务执行器，支持异步、多线程和多进程三种模式
- async_run: 异步并发执行（适用于IO密集型）
- thread_run: 多线程并发（适用于IO密集型）
- process_run: 多进程并发（适用于CPU密集型）
- hybrid_run: 多进程+异步混合执行（适用于大规模IO密集型）
- run: 自动选择执行模式
"""
import logging
import asyncio
import math
import signal
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from typing import List, Callable, Any, Coroutine, Optional
from tqdm.asyncio import tqdm
from tqdm import tqdm as sync_tqdm
from typing import List, Callable, Any, Optional, Union
from func_timeout import func_timeout, FunctionTimedOut
from multiprocessing import Manager
from batch_executor.custom_logger import setup_logger
from batch_executor.constants import PHYSICAL_CORES
from batch_executor.config import ExecutorConfig

# 默认日志记录器
_thread_logger = setup_logger('multi_thread', log_level="INFO")
_process_logger = setup_logger('multi_process', log_level="INFO")
_async_logger = setup_logger('multi_async', log_level="INFO")
_hybrid_logger = setup_logger('multi_hybrid', log_level="INFO")


def _timeout_handler(signum, frame):
    """信号处理函数，用于多进程超时"""
    raise TimeoutError("Process execution timeout")

def _process_wrapper(args):
    """外部包装函数，用于多进程执行"""
    item, idx, func, timeout = args
    try:
        if timeout:
            # 设置信号处理器
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(int(timeout))
        
        result = func(item)
        
        if timeout:
            signal.alarm(0)  # 取消超时
        
        return idx, result, None
    except TimeoutError as e:
        return idx, None, f"Timeout after {timeout}s: {str(e)}"
    except Exception as e:
        if timeout:
            signal.alarm(0)  # 确保取消超时
        return idx, None, e

def _hybrid_worker_with_progress(args):
    """混合执行器的进程工作函数，支持实时进度更新"""
    items_chunk, func_async, nworker, timeout, start_idx, progress_queue = args
    
    async def async_worker_in_process():
        """在进程内部运行异步任务"""
        sem = asyncio.Semaphore(nworker)
        
        async def wrapped_func(item, idx):
            async with sem:
                try:
                    if timeout:
                        result = await asyncio.wait_for(func_async(item), timeout=timeout)
                    else:
                        result = await func_async(item)
                    
                    # 发送进度更新信号
                    progress_queue.put(1)
                    return idx, result, None
                except asyncio.TimeoutError:
                    error_msg = f"Timeout after {timeout}s"
                    progress_queue.put(1)
                    return idx, None, error_msg
                except Exception as e:
                    error_msg = str(e)
                    progress_queue.put(1)
                    return idx, None, error_msg
        
        tasks = [wrapped_func(item, start_idx + i) for i, item in enumerate(items_chunk)]
        results = []
        
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
        
        return results
    
    try:
        # 在子进程中运行异步事件循环
        return asyncio.run(async_worker_in_process())
    except Exception as e:
        # 如果整个chunk失败，返回所有项目的错误，并更新进度
        for _ in range(len(items_chunk)):
            progress_queue.put(1)
        return [(start_idx + i, None, str(e)) for i in range(len(items_chunk))]

class BatchExecutor:
    """批量任务执行器类"""
    
    def __init__(self, func: Callable[[Any], Any], config: Optional[ExecutorConfig] = None, **kwargs):
        """
        初始化执行器
        
        Args:
            func: 执行函数
            config: 执行器配置对象
            **kwargs: 额外的配置参数（会覆盖config中的同名参数）
        """
        self.func = func
        
        # 如果没有提供config，创建默认配置
        if config is None:
            config = ExecutorConfig()
        
        # 使用kwargs更新配置
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.config = config
    
    def _get_default_logger(self, mode: str) -> logging.Logger:
        """获取默认日志记录器"""
        if self.config.disable_logger:
            return None
        if mode == "async":
            return _async_logger
        elif mode == "thread":
            return _thread_logger
        elif mode == "process":
            return _process_logger
        elif mode == "hybrid":
            return _hybrid_logger
        else:
            return _thread_logger
    
    def _process_results(self, results_with_idx: List[tuple], failures: List[tuple], logger: logging.Logger) -> List[Any]:
        """处理结果，包括排序和日志记录"""
        if failures and logger:
            logger.warning(f"Total failures: {len(failures)}")
        
        if self.config.keep_order:
            results_with_idx.sort(key=lambda x: x[0])
        final_results = [r for _, r in results_with_idx]
            
        return final_results
    
    def _chunk_items(self, items: List[Any], pool_size: int) -> List[List[Any]]:
        """将项目列表分块"""
        chunk_size = math.ceil(len(items) / pool_size)
        chunks = []
        for i in range(0, len(items), chunk_size):
            chunks.append(items[i:i + chunk_size])
        return chunks
    
    async def async_run(self, items: List[Any]) -> List[Any]:
        """异步并发执行任务"""
        if not len(items):
            return []
        
        if self.config.disable_logger:
            logger = None
        else:
            logger = self.config.logger or self._get_default_logger("async")
        sem = asyncio.Semaphore(self.config.nworker)
        
        # 定义任务函数 -> idx, result, error
        async def wrapped_func(item_with_idx):
            idx, item = item_with_idx
            async with sem:
                try:
                    if self.config.timeout:
                        result = await asyncio.wait_for(self.func(item), timeout=self.config.timeout)
                    else:
                        result = await self.func(item)
                    
                    if logger:
                        logger.debug(f"Successfully processed item {idx}")
                    return idx, result, None
                except asyncio.TimeoutError:
                    error_msg = f"Timeout after {self.config.timeout}s"
                    if logger:
                        logger.error(f"Item {idx} timeout: {error_msg}")
                    return idx, None, error_msg
                except Exception as e:
                    error_msg = str(e)
                    if logger:
                        logger.error(f"Error processing item {idx}: {error_msg}")
                    return idx, None, error_msg
        
        tasks = [wrapped_func((i, item)) for i, item in enumerate(items)]
        results_with_idx = []
        
        desc = f"{self.config.task_desc} " if self.config.task_desc else ""
        pbar = tqdm(total=len(items), desc=desc, ncols=80, dynamic_ncols=True)
        
        failures = []
        
        for coro in asyncio.as_completed(tasks):
            idx, result, error = await coro
            if error:
                failures.append((idx, error))
                if logger:
                    logger.error(f"Task {idx} failed: {error}")
            results_with_idx.append((idx, result))
            pbar.update(1)
        
        pbar.close()
        return self._process_results(results_with_idx, failures, logger)
    
    def thread_run(self, items: List[Any]) -> List[Any]:
        """多线程并发执行任务"""
        if not len(items):
            return []
        
        if self.config.disable_logger:
            logger = None
        else:
            logger = self.config.logger or self._get_default_logger("thread")
        
        # 定义任务函数 -> idx, result, error
        def wrapped_func(item_with_idx):
            idx, item = item_with_idx
            try:
                if self.config.timeout:
                    # 使用 func_timeout 进行真正的超时控制
                    result = func_timeout(self.config.timeout, self.func, args=(item,))
                else:
                    result = self.func(item)
                
                if logger:
                    logger.debug(f"Successfully processed item {idx}")
                return idx, result, None
            except FunctionTimedOut:
                error_msg = f"Timeout after {self.config.timeout}s"
                if logger:
                    logger.error(f"Item {idx} timeout: {error_msg}")
                return idx, None, error_msg
            except Exception as e:
                error_msg = str(e)
                if logger:
                    logger.error(f"Error processing item {idx}: {error_msg}")
                return idx, None, error_msg
        
        results_with_idx = []
        failures = []
        
        desc = f"{self.config.task_desc} " if self.config.task_desc else ""
        pbar = sync_tqdm(total=len(items), desc=desc, ncols=80, dynamic_ncols=True)
        
        with ThreadPoolExecutor(max_workers=self.config.nworker) as executor:
            # 提交所有任务
            future_to_idx = {
                executor.submit(wrapped_func, (i, item)): i
                for i, item in enumerate(items)
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_idx):
                try:
                    idx, result, error = future.result()
                    
                    if error:
                        failures.append((idx, error))
                        if logger:
                            logger.error(f"Task {idx} failed: {error}")
                    results_with_idx.append((idx, result))
                    
                except Exception as e:
                    # 这里处理其他可能的异常
                    idx = future_to_idx[future]
                    error_msg = str(e)
                    failures.append((idx, error_msg))
                    if logger:
                        logger.error(f"Task {idx} unexpected error: {error_msg}")
                    results_with_idx.append((idx, None))
                
                pbar.update(1)
        
        pbar.close()
        return self._process_results(results_with_idx, failures, logger)
    
    def process_run(self, items: List[Any]) -> List[Any]:
        """多进程并发执行任务"""
        if not len(items):
            return []
        
        if self.config.disable_logger:
            logger = None
        else:
            logger = self.config.logger or self._get_default_logger("process")
        results_with_idx = []
        failures = []
        
        desc = f"{self.config.task_desc} " if self.config.task_desc else ""
        pbar = sync_tqdm(total=len(items), desc=desc, ncols=80, dynamic_ncols=True)
        
        with ProcessPoolExecutor(max_workers=self.config.nworker) as executor:
            # 准备参数，包含超时时间
            process_args = [(item, i, self.func, self.config.timeout) for i, item in enumerate(items)]
            
            # 提交所有任务
            future_to_idx = {
                executor.submit(_process_wrapper, args): args[1] 
                for args in process_args
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_idx, timeout=None):
                try:
                    # 对于多进程，超时控制在子进程内部实现
                    # 这里可以设置一个稍长的超时作为安全网
                    future_timeout = (self.config.timeout + 5) if self.config.timeout else None
                    idx, result, error = future.result(timeout=future_timeout)
                    
                    if error:
                        failures.append((idx, error))
                        if logger:
                            logger.error(f"Task {idx} failed: {error}")
                    
                    results_with_idx.append((idx, result))
                    
                except concurrent.futures.TimeoutError:
                    idx = future_to_idx[future]
                    error_msg = f"Process timeout after {self.config.timeout}s"
                    failures.append((idx, error_msg))
                    if logger:
                        logger.error(f"Task {idx} process timeout: {error_msg}")
                    results_with_idx.append((idx, None))
                
                pbar.update(1)
        
        pbar.close()
        return self._process_results(results_with_idx, failures, logger)
    
    def hybrid_run(self, items: List[Any]) -> List[Any]:
        """
        混合执行器：多进程 + 异步
        将任务分配到多个进程，每个进程内部使用异步处理
        """
        if not len(items):
            return []
        
        if not asyncio.iscoroutinefunction(self.func):
            # python<3.10 无法判断 partial(func) 是否为异步函数
            if sys.version_info.minor > 9:
                raise ValueError("hybrid_run requires an async function")
        
        if self.config.disable_logger:
            logger = None
        else:
            logger = self.config.logger or self._get_default_logger("hybrid")
        
        # 创建进度队列
        manager = Manager()
        progress_queue = manager.Queue()
        
        # 将任务分块分配给不同进程
        chunks = self._chunk_items(items, self.config.pool_size)
        
        results_with_idx = []
        failures = []
        
        desc = f"{self.config.task_desc} " if self.config.task_desc else ""
        pbar = sync_tqdm(total=len(items), desc=desc, ncols=80, dynamic_ncols=True)
        
        # 启动进度监控线程
        import threading
        progress_stop_event = threading.Event()
        
        def progress_monitor():
            """监控进度队列并更新进度条"""
            while not progress_stop_event.is_set():
                try:
                    # 非阻塞获取进度更新
                    while not progress_queue.empty():
                        progress_queue.get_nowait()
                        pbar.update(1)
                    progress_stop_event.wait(0.1)  # 每100ms检查一次
                except:
                    pass
        
        progress_thread = threading.Thread(target=progress_monitor)
        progress_thread.start()
        
        try:
            with ProcessPoolExecutor(max_workers=self.config.pool_size) as executor:
                # 准备每个进程的参数
                process_args = []
                start_idx = 0
                
                for chunk_idx, chunk in enumerate(chunks):
                    if len(chunk):  # 确保chunk不为空
                        process_args.append((
                            chunk, 
                            self.func, 
                            self.config.nworker, 
                            self.config.timeout, 
                            start_idx,
                            progress_queue
                        ))
                        start_idx += len(chunk)
                
                # 提交所有进程任务
                future_to_info = {
                    executor.submit(_hybrid_worker_with_progress, args): {
                        'chunk': args[0],
                        'start_idx': args[4]
                    }
                    for args in process_args
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_info):
                    try:
                        # 获取该进程处理的结果列表
                        chunk_results = future.result()
                        
                        for idx, result, error in chunk_results:
                            if error:
                                failures.append((idx, error))
                                if logger:
                                    logger.error(f"Task {idx} failed: {error}")
                            results_with_idx.append((idx, result))
                            
                    except Exception as e:
                        # 如果整个进程失败，处理该chunk的所有任务
                        info = future_to_info[future]
                        chunk = info['chunk']
                        chunk_start_idx = info['start_idx']
                        
                        for i, item in enumerate(chunk):
                            original_idx = chunk_start_idx + i
                            failures.append((original_idx, str(e)))
                            if logger:
                                logger.error(f"Process failed for task {original_idx}: {str(e)}")
                            results_with_idx.append((original_idx, None))
        finally:
            # 停止进度监控
            progress_stop_event.set()
            progress_thread.join()
            
            # 处理队列中剩余的进度更新
            while not progress_queue.empty():
                try:
                    progress_queue.get_nowait()
                    pbar.update(1)
                except:
                    break
        
        pbar.close()
        return self._process_results(results_with_idx, failures, logger)
    
    def run(self, items: List[Any], mode: str = "auto") -> List[Any]:
        """
        自动选择执行模式或指定执行模式
        
        Args:
            items: 要处理的项目列表
            mode: 执行模式，可选 "auto", "async", "thread", "process", "hybrid"
                  "auto" 模式会根据函数类型自动选择
            
        Returns:
            处理结果列表
        """
        if not len(items):
            return []
        
        if mode == "auto":
            if asyncio.iscoroutinefunction(self.func):
                return asyncio.run(self.async_run(items))
            else:
                return self.thread_run(items)
        elif mode == "async":
            return asyncio.run(self.async_run(items))
        elif mode == "thread":
            return self.thread_run(items)
        elif mode == "process":
            return self.process_run(items)
        elif mode == "hybrid":
            return self.hybrid_run(items)
        else:
            raise ValueError(f"Unsupported mode: {mode}. Choose from 'auto', 'async', 'thread', 'process', 'hybrid'")


def batch_async_executor(
    items: List[Any],
    func_async: Callable[[Any], Coroutine],
    nworker: Optional[int] = None,
    task_desc: str = "",
    logger: Optional[logging.Logger] = _async_logger,
    keep_order: bool = True,
    timeout: Optional[Union[int, float]] = None
) -> List[Any]:
    """向后兼容的异步执行函数"""
    config = ExecutorConfig(
        nworker=nworker,
        task_desc=task_desc,
        logger=logger,
        disable_logger=logger is None,
        keep_order=keep_order,
        timeout=timeout
    )
    executor = BatchExecutor(func_async, config)
    return asyncio.run(executor.async_run(items))

def batch_thread_executor(
    items: List[Any],
    func: Callable[[Any], Any],
    nworker: Optional[int] = None,
    task_desc: str = "",
    logger: Optional[logging.Logger] = _thread_logger,
    keep_order: bool = True,
    timeout: Optional[Union[int, float]] = None
) -> List[Any]:
    """向后兼容的线程执行函数"""
    config = ExecutorConfig(
        nworker=nworker,
        task_desc=task_desc,
        logger=logger,
        disable_logger=logger is None,
        keep_order=keep_order,
        timeout=timeout
    )
    executor = BatchExecutor(func, config)
    return executor.thread_run(items)

def batch_process_executor(
    items: List[Any],
    func: Callable[[Any], Any],
    nworker: Optional[int] = None,
    task_desc: str = "",
    logger: Optional[logging.Logger] = _process_logger,
    keep_order: bool = True,
    timeout: Optional[Union[int, float]] = None
) -> List[Any]:
    """向后兼容的进程执行函数"""
    config = ExecutorConfig(
        nworker=nworker,
        task_desc=task_desc,
        logger=logger,
        disable_logger=logger is None,
        keep_order=keep_order,
        timeout=timeout
    )
    executor = BatchExecutor(func, config)
    return executor.process_run(items)

def batch_hybrid_executor(
    items: List[Any],
    func_async: Callable[[Any], Coroutine],
    nworker: Optional[int] = PHYSICAL_CORES,
    pool_size: int = 1,
    task_desc: str = "",
    logger: Optional[logging.Logger] = _hybrid_logger,
    keep_order: bool = True,
    timeout: Optional[Union[int, float]] = None
) -> List[Any]:
    """混合执行器函数接口：多进程 + 异步"""
    config = ExecutorConfig(
        nworker=nworker,
        pool_size=pool_size,
        task_desc=task_desc,
        logger=logger,
        disable_logger=logger is None,
        keep_order=keep_order,
        timeout=timeout
    )
    executor = BatchExecutor(func_async, config)
    if pool_size == 1:
        return asyncio.run(executor.async_run(items))
    return executor.hybrid_run(items)

def batch_executor(
    items: List[Any],
    func: Callable[[Any], Any],
    nworker: int = PHYSICAL_CORES,
    pool_size: int = 1,
    task_desc: str = "",
    logger: Optional[logging.Logger] = _thread_logger,
    keep_order: bool = True,
    timeout: Optional[Union[int, float]] = None,
    mode: str = "auto"
):
    """向后兼容的自动执行函数"""
    config = ExecutorConfig(
        nworker=nworker,
        pool_size=pool_size,
        task_desc=task_desc,
        logger=logger,
        disable_logger=logger is None,
        keep_order=keep_order,
        timeout=timeout
    )
    executor = BatchExecutor(func, config)
    return executor.run(items, mode=mode)