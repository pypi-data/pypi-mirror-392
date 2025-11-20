# unlock_processpool_workers.py
"""
Windows进程限制统一解锁器(兼容joblib和ProcessPoolExecutor)
版本：2.2.0
"""
import sys
import threading
import time
import math
import logging

# 核心配置
_UNLOCKED_MAX_WORKERS = 2048  # 总句柄数限制（提升至2048以满足极高并发）
_SAVED_WAIT_API = None
_PLEASE_LOCK = threading.RLock()  # 防止竞态条件的可重入锁

# 可选调试日志（默认不启用）
_logger = logging.getLogger("unlock_processpool")
_logger.addHandler(logging.NullHandler())

if sys.platform == "win32":
    from typing import Sequence
    import _winapi

    # Windows API 返回值常量（避免魔法数字）
    WAIT_OBJECT_0 = 0x00000000
    WAIT_ABANDONED_0 = 0x00000080
    WAIT_TIMEOUT = 0x00000102
    WAIT_FAILED = 0xFFFFFFFF

    def _hacked_wait(
        handles: Sequence[int],
        wait_all: bool,
        timeout: int = _winapi.INFINITE
    ) -> int:
        """
        绕过Windows WaitForMultipleObjects的64句柄限制

        Args:
            handles: 要等待的句柄列表（可以为空）
            wait_all: True=等待所有对象, False=等待任意一个对象
            timeout: 超时时间（毫秒），负数表示无限等待

        Returns:
            - wait_all=False: 返回就绪对象的索引 (0x00-0x3F) 或错误码
            - wait_all=True: 返回 WAIT_OBJECT_0(成功) 或错误码
            - 空句柄列表: 返回 WAIT_FAILED

        Raises:
            RuntimeError: 如果未调用please()初始化

        注意:
            - 所有批次共享同一个总超时时间
            - 超时时间使用向上取整，确保不会提前超时
            - 线程安全：可以在多线程环境中安全调用

        ⚠️ 关键限制 (Critical Caveat):
            - 本函数仅适用于 **状态非易失性 (Non-volatile state)** 对象（如进程句柄、Manual-Reset Events）。
            - **不支持** 对 >64 个 **Auto-Reset Events** 进行原子等待 (`wait_all=True`)。
            - 原因：无法在用户态模拟内核级的原子性全量检查。分批检查会导致状态在检查间隙被重置（Race Condition）。
            - 对于进程池（ProcessPool）场景，进程句柄是 Manual-Reset 的，因此是完全安全的。
        """
        # P0修复#2: 防御性检查 - 空句柄列表
        if not handles:
            _logger.debug("空句柄列表，返回WAIT_FAILED")
            return WAIT_FAILED

        chunk_size = 63  # Python _winapi.WaitForMultipleObjects 限制

        # P1修复#4: 计算绝对deadline（所有批次共享timeout）
        # 任何负数都视为无限等待
        if timeout < 0 or timeout == _winapi.INFINITE:
            deadline = None  # 无限等待
        else:
            deadline = time.perf_counter() + timeout / 1000.0  # 转换为秒

        def _calc_remaining_timeout():
            """
            计算剩余超时时间（毫秒）

            Returns:
                剩余超时毫秒数（向上取整），或INFINITE（无限等待）
            """
            if deadline is None:
                return _winapi.INFINITE
            remaining_sec = deadline - time.perf_counter()
            if remaining_sec <= 0:
                return 0  # 已超时
            # P0修复#3: 使用向上取整，避免精度损失
            # 例如: 0.9ms不会被截断为0ms
            return math.ceil(remaining_sec * 1000)

        # 自适应轮询参数
        MIN_POLL_INTERVAL = 0.001  # 1ms: 极速响应模式 (Burst)
        MAX_POLL_INTERVAL = 0.050  # 50ms: 省电模式 (Idle)
        BACKOFF_FACTOR = 2.0       # 指数退避因子

        if not wait_all:
            # wait_all=False: 任何一个对象就绪就返回
            # 修复逻辑：使用自适应轮询模式 (Adaptive Polling)
            
            current_poll_interval = MIN_POLL_INTERVAL

            while True:
                # 1. 快速扫描所有批次 (非阻塞检查)
                for idx in range(0, len(handles), chunk_size):
                    chunk = handles[idx:idx+chunk_size]
                    
                    # 防御性检查
                    saved_api = _SAVED_WAIT_API
                    if saved_api is None:
                        raise RuntimeError("unlock_processpool未初始化")

                    # 使用 timeout=0 进行瞬时检查
                    ret = saved_api(chunk, False, 0)

                    if WAIT_OBJECT_0 <= ret < WAIT_OBJECT_0 + 64:
                        return idx + ret
                    elif WAIT_ABANDONED_0 <= ret < WAIT_ABANDONED_0 + 64:
                        return WAIT_ABANDONED_0 + idx + (ret - WAIT_ABANDONED_0)
                    elif ret == WAIT_FAILED:
                        return ret
                    elif ret == WAIT_TIMEOUT:
                        pass # 继续检查下一个chunk
                
                # 2. 检查总超时
                remaining_timeout = _calc_remaining_timeout()
                if remaining_timeout == 0 and deadline is not None:
                    return WAIT_TIMEOUT

                # 3. 自适应睡眠
                sleep_time = current_poll_interval
                if deadline is not None:
                    sleep_time = min(current_poll_interval, remaining_timeout / 1000.0)
                
                time.sleep(sleep_time)

                # 4. 调整下一次轮询间隔 (指数退避)
                # 如果没有发现任何活动，增加睡眠时间以节省CPU
                current_poll_interval = min(current_poll_interval * BACKOFF_FACTOR, MAX_POLL_INTERVAL)

        else:
            # wait_all=True: 所有对象都就绪才返回成功
            # 修复逻辑：同样使用自适应轮询模式 (Adaptive Polling)
            
            # 将句柄分批
            num_chunks = (len(handles) + chunk_size - 1) // chunk_size
            chunks = [handles[i:i+chunk_size] for i in range(0, len(handles), chunk_size)]
            
            # 记录每个 chunk 的完成状态
            chunk_results = [None] * num_chunks
            
            current_poll_interval = MIN_POLL_INTERVAL

            while True:
                all_done = True
                abandoned_base_index = -1
                activity_detected = False # 本轮是否有新的chunk完成
                
                # 1. 扫描所有未完成的 chunk
                for i, chunk in enumerate(chunks):
                    if chunk_results[i] is not None:
                        continue  # 该 chunk 已完成
                    
                    # 防御性检查
                    saved_api = _SAVED_WAIT_API
                    if saved_api is None:
                        raise RuntimeError("unlock_processpool未初始化")

                    # 使用 timeout=0 进行非阻塞检查
                    ret = saved_api(chunk, True, 0)
                    
                    if ret == WAIT_OBJECT_0:
                        chunk_results[i] = ret
                        activity_detected = True
                    elif WAIT_ABANDONED_0 <= ret < WAIT_ABANDONED_0 + 64:
                        chunk_results[i] = ret
                        activity_detected = True
                        if abandoned_base_index == -1:
                            abandoned_base_index = i * chunk_size + (ret - WAIT_ABANDONED_0)
                    elif ret == WAIT_FAILED:
                        return ret
                    elif ret == WAIT_TIMEOUT:
                        all_done = False
                
                # 2. 检查是否全部完成
                if all_done:
                    if abandoned_base_index != -1:
                        return WAIT_ABANDONED_0 + abandoned_base_index
                    return WAIT_OBJECT_0

                # 3. 检查总超时
                remaining_timeout = _calc_remaining_timeout()
                if remaining_timeout == 0 and deadline is not None:
                    return WAIT_TIMEOUT

                # 4. 动态调整轮询策略
                if activity_detected:
                    # 如果本轮有进展，立即重置为极速模式，因为通常任务是成批结束的
                    current_poll_interval = MIN_POLL_INTERVAL
                else:
                    # 如果无进展，指数退避
                    current_poll_interval = min(current_poll_interval * BACKOFF_FACTOR, MAX_POLL_INTERVAL)

                # 5. 自适应睡眠
                sleep_time = current_poll_interval
                if deadline is not None:
                    sleep_time = min(current_poll_interval, remaining_timeout / 1000.0)
                
                time.sleep(sleep_time)

    # 标记身份，用于模块重载时的识别
    _hacked_wait._is_unlock_patch = True

def please():
    """
    一键解锁Windows进程池限制

    线程安全，可以多次调用（幂等操作）

    Returns:
        bool: Windows平台返回True，其他平台返回False

    Raises:
        RuntimeError: 如果检测到模块重载导致的无限递归风险

    注意:
        - 必须在创建ProcessPoolExecutor或joblib并行任务之前调用
        - 可以安全地多次调用（幂等）
        - 不能在模块重载后调用
        - 对ProcessPoolExecutor完全支持（可到510进程）
        - 对multiprocessing.Pool部分支持（建议<60进程，或切换到Executor）

    兼容性说明:
        - ProcessPoolExecutor: ✅ 完美支持大规模并发
        - joblib (loky backend): ✅ 完美支持
        - multiprocessing.Pool: ⚠️ 受系统资源限制，建议<60进程
    """
    if sys.platform != "win32":
        return False

    global _SAVED_WAIT_API

    # 使用锁保护临界区，防止TOCTOU竞态条件
    with _PLEASE_LOCK:
        current_api = _winapi.WaitForMultipleObjects

        # 1. 快速通道：完全相同的函数对象（同一次加载内的重复调用）
        if current_api is _hacked_wait:
            _logger.debug("please()已被调用过，幂等操作")
            return True

        # 2. 智能检测：检查是否是“前世”留下的钩子（模块重载场景）
        # 使用 getattr 安全获取，防止 AttributeError
        if getattr(current_api, "_is_unlock_patch", False):
            _logger.warning("检测到模块重载：正在执行热替换 (Hot-Swap)...")
            
            # 关键步骤：从旧钩子中“赎回”原始 API
            original_api = getattr(current_api, "_original_api", None)
            
            if original_api is None:
                # 防御性编程：如果旧钩子坏了，没带原始API，我们只能报错停止，防止无限递归
                _logger.error("严重错误：检测到旧补丁但丢失了原始API引用。无法安全继续。")
                return False
        else:
            # 3. 初始状态：这是纯净的系统 API
            original_api = current_api

        # --- 执行挂载 ---
        
        # A. 初始化当前模块的全局状态
        _SAVED_WAIT_API = original_api
        
        # B. 将原始 API 绑在身上，作为“传家宝”留给下一次 Reload
        _hacked_wait._original_api = original_api
        
        # C. 替换系统 API
        _winapi.WaitForMultipleObjects = _hacked_wait
        
        _logger.debug(f"成功替换_winapi.WaitForMultipleObjects (Hot-Swap={getattr(current_api, '_is_unlock_patch', False)})")

    # 动态修改所有已知限制模块
    modules = [
        ("concurrent.futures.process", "_MAX_WINDOWS_WORKERS"),
        ("joblib.externals.loky.backend.context", "_MAX_WINDOWS_WORKERS"),
        ("joblib.externals.loky.process_executor", "_MAX_WINDOWS_WORKERS"),
        ("loky.backend.context", "_MAX_WINDOWS_WORKERS"),
    ]

    for mod, attr in modules:
        try:
            __import__(mod)
            module = sys.modules[mod]
            if hasattr(module, attr):
                setattr(module, attr, _UNLOCKED_MAX_WORKERS - 2)
        except (ImportError, ModuleNotFoundError, AttributeError, TypeError):
            # 模块不存在或属性设置失败，跳过
            continue

    # 强制刷新joblib配置
    try:
        from joblib import parallel_backend
        parallel_backend("loky")
    except (ImportError, ModuleNotFoundError, Exception):
        # joblib未安装或配置失败，忽略
        pass

    # 🔧 修复 multiprocessing.Pool 在 > 61 进程时的死锁问题
    try:
        from multiprocessing import pool as pool_module

        # 保存原始的 Pool.close 方法
        if not hasattr(pool_module.Pool, '_original_close_unlocked'):
            original_close = pool_module.Pool.close

            def _patched_close(self):
                """
                修补后的 Pool.close()
                修复 > 61 进程时的死锁：
                - 原始问题：_handle_tasks 阻塞在 taskqueue.get()
                - 解决方案：手动向 taskqueue 发送 None 来唤醒 _handle_tasks
                """
                # 调用原始的 close
                original_close(self)

                # 🔧 关键修复：向 taskqueue 发送 None
                # _handle_tasks 在 `iter(taskqueue.get, None)` 上阻塞
                # 当收到 None 时，会向所有 worker 发送退出信号
                try:
                    if hasattr(self, '_taskqueue') and self._taskqueue is not None:
                        self._taskqueue.put(None)
                except Exception:
                    # 如果 taskqueue 已关闭或出错，忽略
                    pass

            # 替换 Pool.close 方法
            pool_module.Pool._original_close_unlocked = original_close
            pool_module.Pool.close = _patched_close

            _logger.debug("已修补 multiprocessing.Pool.close() 以支持 > 61 进程")
    except (ImportError, AttributeError, Exception) as e:
        # multiprocessing.Pool 不可用或修补失败，忽略
        _logger.debug(f"无法修补 multiprocessing.Pool: {e}")

    return True