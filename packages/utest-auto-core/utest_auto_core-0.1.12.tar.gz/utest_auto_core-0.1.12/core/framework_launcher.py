#!/usr/bin/env python3
"""
测试框架启动器

将启动逻辑封装在库中，模板中的 start_test.py 只需调用此函数即可
"""
import os
import sys
import logging
import time
import traceback
from pathlib import Path
from typing import Optional
from androguard.core.bytecodes import apk
from ubox_py_sdk import OSType

# 添加框架路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager
from core.test_runner import TestRunner
from core.utils.file_utils import make_dir, del_dir
from test_cases.internal.loader import create_test_collection

# 返回码定义（与服务端编号一致）
SUCCESS = 0  # 成功
RUNNER_ERROR = 2  # 其他脚本异常
INSTALL_ERROR = 3  # 安装失败
SCRIPT_ASSERT_ERROR = 5  # 脚本断言失败
DEVICE_OFFLINE = 10  # 手机掉线
CRASH = 17  # 应用崩溃
ANR = 18  # 应用无响应

# 全局变量（用于兼容原有代码）
g_log_file_dir = None
g_case_base_dir = None


def log_exception_once(prefix: str, exc: Exception, logger) -> None:
    """仅打印一次异常堆栈，避免多处捕获重复打日志"""
    if not hasattr(log_exception_once, '_printed_exceptions'):
        log_exception_once._printed_exceptions = set()
    
    key = (type(exc), str(exc))
    if key in log_exception_once._printed_exceptions:
        return
    log_exception_once._printed_exceptions.add(key)
    logger.error(f"{prefix}: {exc}\n{traceback.format_exc()}")


def parse_app_source(app_name: str) -> dict:
    """解析应用来源，判断是否为本地文件/包名"""
    result = {
        'need_install': False,
        'source_type': 'package',
        'package_name': '',
        'file_path': None,
        'file_type': None,
    }

    text = app_name.strip()
    file_extensions = ['.apk', '.ipa', '.hap']
    
    for ext in file_extensions:
        if text.lower().endswith(ext):
            result['file_type'] = ext[1:]
            i_test_app_path = os.path.join(os.path.dirname(os.getcwd()), text)
            if os.path.isabs(i_test_app_path) and os.path.exists(i_test_app_path):
                result['need_install'] = True
                result['source_type'] = 'file'
                result['file_path'] = i_test_app_path
                result['package_name'] = extract_package_name(i_test_app_path, result['file_type'])
                return result
    
    result['need_install'] = False
    result['source_type'] = 'package'
    result['package_name'] = text
    return result


def extract_package_name(file_path: str, file_type: str) -> str:
    """从包文件中提取包名"""
    try:
        if file_type == 'apk':
            return extract_apk_package_name(file_path)
        elif file_type == 'ipa':
            return extract_ipa_package_name(file_path)
        elif file_type == 'hap':
            return extract_hap_package_name(file_path)
        else:
            return ""
    except Exception:
        return ""


def extract_apk_package_name(apk_path: str) -> str:
    """从APK文件中提取包名"""
    try:
        i_apk_info = apk.APK(apk_path)
        if i_apk_info is not None:
            return i_apk_info.get_package()
    except Exception:
        pass
    return ""


def extract_ipa_package_name(ipa_path: str) -> str:
    """从IPA文件中提取包名"""
    try:
        import zipfile
        import plistlib
        with zipfile.ZipFile(ipa_path, 'r') as ipa:
            for file_info in ipa.filelist:
                if file_info.filename.endswith('Info.plist'):
                    plist_data = ipa.read(file_info.filename)
                    plist = plistlib.loads(plist_data)
                    return plist.get('CFBundleIdentifier', '')
    except Exception:
        pass
    return ""


def extract_hap_package_name(hap_path: str) -> str:
    """从HAP文件中提取包名"""
    try:
        import zipfile
        import json
        with zipfile.ZipFile(hap_path, 'r') as hap:
            for file_info in hap.filelist:
                if file_info.filename.endswith('config.json'):
                    config_data = hap.read(file_info.filename)
                    config = json.loads(config_data.decode('utf-8'))
                    return config.get('app', {}).get('bundleName', '')
    except Exception:
        pass
    return ""


def install_pkg(device, package_path: str, package_name: str, file_type: str = 'apk', logger=None) -> bool:
    """安装应用包（支持APK/IPA/HAP）"""
    try:
        device_info = device.device_info()
        if device_info and logger:
            logger.info(f"设备型号: {device_info.get('model', 'Unknown')}, app_path:{package_path};开始安装app...")

        if file_type == 'apk':
            ok = install_android_package(device, package_path, logger)
        elif file_type == 'ipa':
            ok = install_ios_package(device, package_path, logger)
        elif file_type == 'hap':
            ok = install_harmonyos_package(device, package_path, logger)
        else:
            if logger:
                logger.error(f"不支持的文件类型: {file_type}")
            return False

        if not ok:
            return False

        # 安装成功后做一次冷启动并截图
        try:
            device.start_app(package_name)
            time.sleep(5)
            global g_case_base_dir
            if g_case_base_dir:
                device.screenshot("install_res", g_case_base_dir)
        except Exception as post_e:
            if logger:
                logger.warning(f"安装后启动/截图失败（忽略）: {post_e}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"安装流程异常: {e}\n{traceback.format_exc()}")
        return False


def install_android_package(device, apk_path: str, logger=None) -> bool:
    """安装Android APK包"""
    try:
        result = device.local_install_app(apk_path)
        if not bool(result):
            if logger:
                logger.error("APK安装返回失败")
            return False
        if logger:
            logger.info("APK安装完成")
        return True
    except Exception as e:
        if logger:
            logger.error(f"Android包安装异常: {e}")
        return False


def install_ios_package(device, ipa_path: str, logger=None) -> bool:
    """安装iOS IPA包"""
    try:
        if logger:
            logger.info(f"开始安装IPA: {ipa_path}")
        result = device.local_install_app(ipa_path)
        if not bool(result):
            if logger:
                logger.error("IPA安装返回失败")
            return False
        if logger:
            logger.info("IPA安装完成")
        return True
    except Exception as e:
        if logger:
            logger.error(f"iOS包安装异常: {e}")
        return False


def install_harmonyos_package(device, hap_path: str, logger=None) -> bool:
    """安装鸿蒙HAP包"""
    try:
        if logger:
            logger.info(f"开始安装HAP: {hap_path}")
        result = device.local_install_app(hap_path)
        if not bool(result):
            if logger:
                logger.error("HAP安装返回失败")
            return False
        if logger:
            logger.info("HAP安装完成")
        return True
    except Exception as e:
        if logger:
            logger.error(f"鸿蒙包安装异常: {e}")
        return False


def run_framework(config_file_path: Optional[str] = None) -> int:
    """
    运行测试框架的主入口函数
    
    Args:
        config_file_path: 配置文件路径，如果为None则使用默认路径（当前目录下的config.yml）
    
    Returns:
        int: 退出码（0表示成功，其他值表示各种错误）
    """
    global g_log_file_dir, g_case_base_dir
    
    # 确定配置文件路径
    if config_file_path is None:
        # 默认使用当前工作目录下的 config.yml
        # 通常 start_test.py 和 config.yml 在同一目录
        config_file_path = os.path.join(os.getcwd(), 'config.yml')
        # 如果当前目录没有，尝试从调用者的文件位置推断
        if not os.path.exists(config_file_path):
            import inspect
            try:
                frame = inspect.currentframe()
                if frame and frame.f_back:
                    caller_file = frame.f_back.f_globals.get('__file__', '')
                    if caller_file:
                        config_file_path = os.path.join(os.path.dirname(os.path.abspath(caller_file)), 'config.yml')
            except Exception:
                pass
            finally:
                if 'frame' in locals():
                    del frame
    else:
        config_file_path = os.path.abspath(config_file_path)
    
    # 设置结果目录
    root_path = os.path.dirname(os.path.dirname(os.getcwd()))
    test_result_dir = os.path.join(root_path, 'test_result')
    log_base_dir = os.path.join(test_result_dir, 'log')
    case_base_dir = os.path.join(test_result_dir, 'case')
    
    # 创建基础目录结构
    make_dir(log_base_dir)
    make_dir(case_base_dir)
    g_log_file_dir = log_base_dir
    g_case_base_dir = case_base_dir
    
    # 初始化日志
    log_file_path = os.path.join(log_base_dir, 'client_log.txt')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("从配置文件读取启动参数")
    
    # 加载配置
    try:
        config_manager = ConfigManager(config_file_path)
        config = config_manager.load_config()
        
        if not config_manager.validate_task_config():
            logger.error("任务配置验证失败")
            return RUNNER_ERROR
        
        i_job_id = config.task.job_id
        g_serial_num = config.task.serial_num
        i_os_type = config.task.os_type
        i_app_name = config.task.app_name
        i_auth_code = config.task.auth_code
        
        logger.info(f'---UTEST测试--- job_id={i_job_id}, serial_num={g_serial_num}, '
                    f'os_type={i_os_type}, auth_code={i_auth_code}, app_name={i_app_name}, test_result_path={test_result_dir}')
        
        # 确定平台类型
        platform_map = {
            "android": OSType.ANDROID,
            "ios": OSType.IOS,
            "hm": OSType.HM
        }
        platform = platform_map.get(i_os_type.lower(), OSType.ANDROID)
        
        # 更新配置
        config.device.udid = g_serial_num
        config.device.os_type = platform
        config.device.auth_code = i_auth_code
        
        # 解析应用来源
        app_info = parse_app_source(i_app_name)
        logger.info(f"应用来源解析: {app_info}")
        
    except Exception as e:
        log_exception_once("框架准备失败", e, logger)
        return RUNNER_ERROR
    
    # 初始化运行器
    runner_cm = None
    runner = None
    final_exit_code = SUCCESS
    
    try:
        runner_cm = TestRunner(config, log_file_path)
        final_exit_code = SUCCESS
        results = []
        anr_monitor_result = None
        can_run = True
        
        # 初始化设备
        try:
            runner_cm.__enter__()
        except Exception as init_e:
            logger.error(f"设备初始化失败: {init_e}")
            final_exit_code = DEVICE_OFFLINE
            can_run = False
        
        runner = runner_cm
        runner.test_context = {
            "package_name": app_info.get('package_name') or i_app_name,
            "job_id": i_job_id,
            "serial_num": g_serial_num,
            "need_install": app_info['need_install'],
            "app_source_type": app_info['source_type'],
            "package_file_path": app_info.get('file_path'),
            "file_type": app_info.get('file_type'),
            "raw_app_name": i_app_name,
            "test_result_dir": test_result_dir,
            "case_base_dir": case_base_dir,
            "log_base_dir": log_base_dir,
        }
        
        # 执行测试流程
        if can_run:
            # 安装应用
            installed = False
            if runner.test_context.get('need_install') and runner.device:
                package_path = runner.test_context.get('package_file_path')
                file_type = runner.test_context.get('file_type', 'apk')
                if package_path and os.path.exists(package_path):
                    installed = install_pkg(
                        runner.device,
                        package_path,
                        runner.test_context.get('package_name'),
                        file_type,
                        logger
                    )
                    if not installed:
                        logger.error(f"安装失败: {package_path}")
                        final_exit_code = INSTALL_ERROR
                else:
                    logger.error(f"应用包文件不存在: {package_path}")
                    final_exit_code = INSTALL_ERROR
            else:
                logger.info("无需安装应用包，按包名直接启动")
            
            # 执行测试
            execute_tests = (final_exit_code == SUCCESS)
            if execute_tests:
                # 创建测试用例集合
                try:
                    selected_tests = config.test.selected_tests
                    if selected_tests and len(selected_tests) > 0:
                        logger.info(f"运行指定的测试用例: {selected_tests}")
                        test_suite = create_test_collection(selected_tests, device=runner.device)
                    else:
                        logger.info("运行所有测试用例")
                        test_suite = create_test_collection(device=runner.device)
                except RuntimeError as e:
                    logger.error(f"创建测试用例集合失败: {e}")
                    final_exit_code = RUNNER_ERROR
                    test_suite = None
                
                # 开启ANR检测（根据配置决定是否启用）
                anr_start_success = False
                enable_anr_monitor = config.test.enable_anr_monitor
                if enable_anr_monitor and platform in [OSType.ANDROID, OSType.HM] and runner.device:
                    logger.info("ANR/Crash监控已启用")
                    try:
                        runner.device.anr_stop()
                    except Exception:
                        logger.warning("无需停止anr")
                    try:
                        anr_start_success = runner.device.anr_start(
                            package_name=runner.test_context.get('package_name'))
                        if anr_start_success:
                            logger.info("ANR/Crash监控启动成功")
                        else:
                            logger.warning("ANR/Crash监控启动失败")
                    except Exception as anr_start_e:
                        logger.warning(f"启动ANR监控失败，忽略: {anr_start_e}")
                        anr_start_success = False
                elif not enable_anr_monitor:
                    logger.info("ANR/Crash监控已禁用（配置中 enable_anr_monitor: false）")
                
                # 执行测试套件
                try:
                    results = runner.run_test_suite(test_suite)
                except Exception as run_e:
                    log_exception_once("运行阶段异常", run_e, logger)
                    final_exit_code = RUNNER_ERROR
                
                # 卸载应用
                if installed:
                    try:
                        runner.device.uninstall_app(runner.test_context.get('package_name'))
                    except Exception as uninstall_e:
                        logger.warning(f"卸载阶段异常忽略: {uninstall_e}")
                
                # 结束ANR检测
                if anr_start_success:
                    try:
                        anr_monitor_result = runner.device.anr_stop(g_log_file_dir)
                    except Exception as anr_stop_e:
                        logger.warning(f"停止ANR监控异常，忽略: {anr_stop_e}")
                        anr_monitor_result = None
                    
                    if anr_monitor_result:
                        runner.set_global_monitor_result(anr_monitor_result)
                        anr_count = anr_monitor_result.get("anr_count", 0)
                        crash_count = anr_monitor_result.get("crash_count", 0)
                        
                        if anr_count > 0:
                            logger.error(f"检测到ANR事件，数量: {anr_count}")
                            final_exit_code = ANR
                        elif crash_count > 0:
                            logger.error(f"检测到Crash事件，数量: {crash_count}")
                            final_exit_code = CRASH
                
                # 检查测试结果
                if final_exit_code not in (ANR, CRASH):
                    failed_tests = [r for r in results if r.status.value == "failed"]
                    error_tests = [r for r in results if r.status.value == "error"]
                    
                    if error_tests:
                        logger.error(f"测试错误: {len(error_tests)} 个测试用例出错")
                        for test in error_tests:
                            logger.error(f"  - {test.test_name}: {test.error_message}")
                        final_exit_code = RUNNER_ERROR
                    elif failed_tests:
                        logger.error(f"测试失败: {len(failed_tests)} 个测试用例失败")
                        for test in failed_tests:
                            logger.error(f"  - {test.test_name}: {test.error_message}")
                        final_exit_code = SCRIPT_ASSERT_ERROR
                    else:
                        logger.info(f"测试成功: {len(results)} 个测试用例全部通过")
                        final_exit_code = SUCCESS
        
    except Exception as e:
        log_exception_once("测试执行异常", e, logger)
        final_exit_code = RUNNER_ERROR
    finally:
        # 生成报告
        if runner is not None:
            try:
                rp2 = runner.generate_report(exit_code=final_exit_code)
                logger.info(f"测试报告生成: {rp2}")
            except Exception as rpt2_e:
                logger.error(f"报告生成失败: {rpt2_e}")
        else:
            logger.warning("runner 未初始化，跳过报告生成")
        
        # 释放资源
        if runner_cm is not None:
            try:
                runner_cm.__exit__(None, None, None)
            except Exception as ee:
                logger.warning(f"资源释放异常: {ee}")
    
    return final_exit_code

