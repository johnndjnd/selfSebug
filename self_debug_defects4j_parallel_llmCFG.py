#!/usr/bin/env python3
"""
使用LLM直接生成Java控制流图的自调试架构
基于self_debug_defects4j_parallel.py但使用LLM代替JavaCFG构建控制流图
"""

import json
import os
import time
import random
import argparse
import re
from typing import Dict, List, Optional, Tuple
from loguru import logger
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from utils import write_str_to_file
from chat import chat_java_fragment_debug, generate_java_cfg_with_llm

def slim_error_message(err_msg: str, token_limit: int = 200) -> str:
    """
    简化error message，类似gen_solution_prompt.py中的slim_content_token
    Args:
        err_msg: 原始错误信息
        token_limit: token限制
    Returns:
        简化后的错误信息
    """
    err_msg_lines = err_msg.split('\n')
    slim_err_msg_lines = []
    current_tokens = 0
    
    for line in err_msg_lines:
        # 简单估算：一个单词约等于1个token
        line_tokens = len(line.split())
        if current_tokens + line_tokens > token_limit:
            break
        slim_err_msg_lines.append(line)
        current_tokens += line_tokens
    
    return '\n'.join(slim_err_msg_lines)

def extract_java_buggy_code(bug_data: Dict) -> str:
    """
    提取Java的buggy代码
    Args:
        bug_data: 单个bug的数据
    Returns:
        完整的buggy代码
    """
    buggy_code = bug_data['buggy']
    buggy_code_comment = bug_data.get('buggy_code_comment', '')
    
    # 组合注释和代码
    if buggy_code_comment:
        full_code = buggy_code_comment + '\n' + buggy_code
    else:
        full_code = buggy_code
    
    return full_code

def extract_java_test_info(bug_data: Dict) -> Tuple[str, str]:
    """
    从trigger_test中随机选择一个测试用例和错误信息
    Args:
        bug_data: 单个bug的数据
    Returns:
        (test_case, error_message) 元组
    """
    trigger_tests = bug_data.get('trigger_test', {})
    
    # 随机选择一个trigger test
    if trigger_tests:
        random_trigger_test = random.choice(list(trigger_tests.keys()))
        selected_test = trigger_tests[random_trigger_test]
        test_case = selected_test.get('src', '')
        error_message = selected_test.get('clean_error_msg', '')
        
        if error_message:
            error_message = slim_error_message(error_message)
        
        return test_case, error_message
    
    return "", ""

def llm_java_debug(bug_name: str, bug_data: Dict) -> Optional[str]:
    """
    使用LLM生成控制流图并进行Java代码调试
    Args:
        bug_name: bug名称
        bug_data: bug数据
    Returns:
        修复后的代码，失败时返回None
    """
    logger.info(f"Processing bug: {bug_name}")
    
    # 提取基本信息
    buggy_code = extract_java_buggy_code(bug_data)
    test_case, error_message = extract_java_test_info(bug_data)
    
    logger.info(f"Buggy code length: {len(buggy_code)}")
    logger.info(f"Test case length: {len(test_case)}")
    logger.info(f"Error message length: {len(error_message)}")
    
    # 构建CFG - 使用LLM生成
    cfg_text = ""
    try:
        # 检查代码是否包含类定义，如果没有则包装在临时类中
        java_code_to_analyze = buggy_code
        class_name = None
        
        if not re.search(r'\bclass\s+\w+', buggy_code):
            # 没有类定义，包装在临时类中
            class_name = "TempClass"
            java_code_to_analyze = f"""
public class TempClass {{
{buggy_code}
}}
"""
            logger.info(f"Wrapped method in temporary class for {bug_name}")
        
        # 使用LLM生成控制流图
        logger.info(f"Generating CFG with LLM for {bug_name}...")
        cfg_text = generate_java_cfg_with_llm(
            java_code=java_code_to_analyze, 
            method_name=None,  # 不限制特定方法，让LLM分析整个代码
            class_name=class_name
        )
        logger.info(f"CFG generated successfully for {bug_name}")
        
    except Exception as e:
        logger.warning(f"CFG generation failed for {bug_name}: {e}")
        cfg_text = ""
    
    # 使用静态分析方法进行调试
    try:
        logger.info(f"Starting static analysis debug for {bug_name}")
        
        # 如果没有测试用例或错误信息，使用占位符
        if not test_case:
            test_case = "No specific test case available"
        if not error_message:
            error_message = "No specific error message available"
            
        debug_result = chat_java_fragment_debug(
            buggy_code=buggy_code,
            error_message=error_message,
            test_case=test_case,
            cfg_text=cfg_text
        )
        
        # 打印原始响应用于调试
        logger.info(f"Raw LLM response for {bug_name}:")
        logger.info(f"Response length: {len(debug_result)}")
        logger.info(f"First 500 chars: {debug_result[:500]}")
        
        # 预处理响应，去掉markdown代码块标记
        processed_result = debug_result.strip()
        if processed_result.startswith("```json"):
            processed_result = processed_result[7:]  # 去掉```json
        if processed_result.endswith("```"):
            processed_result = processed_result[:-3]  # 去掉```
        processed_result = processed_result.strip()
        
        # 解析结果
        try:
            debug_json = json.loads(processed_result)
            corrected_code = debug_json.get("corrected_code", buggy_code)
            explanation = debug_json.get("explanation", "No explanation provided")
            
            logger.info(f"Debug completed for {bug_name}")
            logger.info(f"Explanation: {explanation[:200]}...")
            
            # 检查是否生成了修复代码（不管是否正确，都需要验证）
            if corrected_code and corrected_code.strip() != buggy_code.strip():
                logger.info(f"📝 Generated patch for {bug_name} (needs validation)")
                return corrected_code
            else:
                logger.warning(f"❌ No patch generated for {bug_name}")
                return None
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error for {bug_name}: {e}")
            logger.warning(f"Trying to extract code from non-JSON response...")
            
            # 尝试从原始响应中提取代码
            if "```java" in debug_result:
                start = debug_result.find("```java") + 7
                end = debug_result.find("```", start)
                if end > start:
                    extracted_code = debug_result[start:end].strip()
                    if extracted_code and extracted_code != buggy_code.strip():
                        logger.info(f"📝 Extracted patch from non-JSON response for {bug_name} (needs validation)")
                        return extracted_code
            
            logger.warning(f"❌ Could not extract any meaningful fix for {bug_name}")
            return None
            
    except Exception as e:
        logger.error(f"Static analysis debug failed for {bug_name}: {e}")
        return None

def process_single_bug_task(task_data: Tuple[str, Dict]) -> Tuple[str, Optional[str], bool]:
    """
    并行处理单个bug任务
    Args:
        task_data: (bug_name, bug_data) 元组
    Returns:
        (bug_name, corrected_code, success) 元组
    """
    bug_name, bug_data = task_data
    
    try:
        corrected_code = llm_java_debug(bug_name, bug_data)
        success = corrected_code is not None and corrected_code.strip() != bug_data['buggy'].strip()
        return bug_name, corrected_code, success
    except Exception as e:
        logger.error(f"Error processing {bug_name}: {e}")
        return bug_name, None, False

def process_defects4j_dataset_parallel(dataset_path: str, output_path: str, limit: int = None, max_workers: int = None) -> Dict:
    """
    并行处理整个defects4j数据集
    Args:
        dataset_path: 数据集路径
        output_path: 输出路径
        limit: 限制处理的bug数量
        max_workers: 最大并行worker数量
    Returns:
        处理结果字典
    """
    logger.info(f"Loading dataset from {dataset_path}")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    total_bugs = len(dataset)
    logger.info(f"Total bugs in dataset: {total_bugs}")
    
    bug_names = list(dataset.keys())
    
    # 如果设置了限制，只处理指定数量的bugs
    if limit is not None and limit > 0:
        bug_names = bug_names[:limit]
        logger.info(f"Limited processing to first {limit} bugs")
    
    # 设置并行worker数量
    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), len(bug_names))
    
    logger.info(f"Using {max_workers} parallel workers")
    
    # 准备任务数据
    tasks = [(bug_name, dataset[bug_name]) for bug_name in bug_names]
    
    results = {}
    patches_generated = 0
    
    # 并行处理
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_bug = {executor.submit(process_single_bug_task, task): task[0] for task in tasks}
        
        # 收集结果
        for i, future in enumerate(as_completed(future_to_bug), 1):
            bug_name = future_to_bug[future]
            
            try:
                bug_name_result, corrected_code, success = future.result()
                
                logger.info(f"=== Completed bug {i}/{len(bug_names)}: {bug_name_result} ===")
                
                if corrected_code and corrected_code != dataset[bug_name_result]['buggy']:
                    results[bug_name_result] = {
                        'patches': [corrected_code],
                        'original_buggy': dataset[bug_name_result]['buggy'],
                        'bug_info': {
                            'loc': dataset[bug_name_result]['loc'],
                            'start': dataset[bug_name_result]['start'],
                            'end': dataset[bug_name_result]['end']
                        },
                        'patch_generated': True
                    }
                    patches_generated += 1
                    logger.info(f"📝 Generated patch for {bug_name_result} (validation required)")
                else:
                    logger.warning(f"❌ No patch generated for {bug_name_result}")
                    # 为了能够进行验证，即使失败也要记录原始代码
                    results[bug_name_result] = {
                        'patches': [dataset[bug_name_result]['buggy']],  # 使用原始代码
                        'original_buggy': dataset[bug_name_result]['buggy'],
                        'bug_info': {
                            'loc': dataset[bug_name_result]['loc'],
                            'start': dataset[bug_name_result]['start'],
                            'end': dataset[bug_name_result]['end']
                        },
                        'patch_generated': False
                    }
                
                # 定期保存中间结果
                if i % 10 == 0:
                    logger.info(f"Progress: {i}/{len(bug_names)} completed, saving intermediate results...")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                        
            except Exception as e:
                logger.error(f"Error processing result for {bug_name}: {e}")
                # 记录失败的情况
                results[bug_name] = {
                    'patches': [dataset[bug_name]['buggy']],  # 使用原始代码
                    'original_buggy': dataset[bug_name]['buggy'],
                    'bug_info': {
                        'loc': dataset[bug_name]['loc'],
                        'start': dataset[bug_name]['start'],
                        'end': dataset[bug_name]['end']
                    },
                    'patch_generated': False
                }
    
    logger.info(f"=== Parallel processing completed ===")
    logger.info(f"Total processed: {len(bug_names)}")
    logger.info(f"Patches generated: {patches_generated}")
    logger.info(f"Patch generation rate: {patches_generated/len(bug_names)*100:.2f}%")
    
    # 保存最终结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to {output_path}")
    return results

def run_validation(patch_file: str, dataset_path: str, output_dir: str):
    """
    运行sf_val_d4j验证，显示实时进度
    Args:
        patch_file: 补丁文件路径
        dataset_path: 数据集路径
        output_dir: 输出目录
    """
    logger.info("Starting validation with sf_val_d4j...")
    
    # 构建验证命令
    val_script = "dataset_test/SRepair/SRepair/src/sf_val_d4j.py"
    
    if not os.path.exists(val_script):
        logger.error(f"Validation script not found: {val_script}")
        return
    
    # 读取补丁文件获取总数量以显示进度
    try:
        with open(patch_file, 'r', encoding='utf-8') as f:
            patches_data = json.load(f)
        total_bugs = len(patches_data)
        logger.info(f"📊 Total bugs to validate: {total_bugs}")
    except Exception as e:
        logger.error(f"Error reading patch file: {e}")
        total_bugs = 0
    
    cmd = [
        sys.executable, val_script,
        '-i', patch_file,
        '-d', dataset_path,
        '-o', output_dir
    ]
    
    logger.info(f"Running validation command: {' '.join(cmd)}")
    
    try:
        # 启动验证进程并实时显示输出
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                 text=True, bufsize=1, universal_newlines=True)
        
        # 启动进度监控线程
        import threading
        stop_monitoring = threading.Event()
        monitor_thread = threading.Thread(target=monitor_validation_progress, 
                                        args=(output_dir, total_bugs, stop_monitoring))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # 实时输出验证日志
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # 过滤和格式化输出
                line = output.strip()
                if line:
                    if '[PATCH STATUS]' in line:
                        logger.info(f"🔍 {line}")
                    elif '[TIME INFO]' in line:
                        logger.info(f"⏱️ {line}")
                    elif '[CHECKOUT]' in line:
                        logger.info(f"📦 {line}")
                    elif 'END VALIDATION' in line:
                        logger.info(f"✅ {line}")
                    else:
                        logger.debug(f"[VAL] {line}")
        
        # 停止监控并等待进程完成
        stop_monitoring.set()
        return_code = process.wait()
        
        if return_code == 0:
            logger.info("✅ Validation completed successfully!")
            logger.info(f"📁 Results saved to: {output_dir}")
        else:
            logger.error(f"❌ Validation failed with return code {return_code}")
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Validation timed out after 1 hour")
    except Exception as e:
        logger.error(f"❌ Error running validation: {e}")

def monitor_validation_progress(output_dir: str, total_bugs: int, stop_event):
    """
    监控验证进度
    """
    import time
    
    if total_bugs == 0:
        return
    
    start_time = time.time()
    last_count = 0
    
    while not stop_event.is_set():
        try:
            if not os.path.exists(output_dir):
                time.sleep(5)
                continue
            
            # 统计已完成的验证文件
            import glob
            completed_files = glob.glob(os.path.join(output_dir, '*-validated.jsonl'))
            completed_count = len(completed_files)
            
            if completed_count > last_count:
                elapsed_time = time.time() - start_time
                progress_percent = (completed_count / total_bugs) * 100
                
                if completed_count > 0:
                    avg_time_per_bug = elapsed_time / completed_count
                    remaining_bugs = total_bugs - completed_count
                    eta_seconds = avg_time_per_bug * remaining_bugs
                    eta_minutes = eta_seconds / 60
                    
                    logger.info(f"📈 Progress: {completed_count}/{total_bugs} ({progress_percent:.1f}%) "
                              f"| Elapsed: {elapsed_time/60:.1f}m | ETA: {eta_minutes:.1f}m")
                
                last_count = completed_count
            
            if completed_count >= total_bugs:
                break
                
            time.sleep(15)  # 每15秒检查一次
            
        except Exception as e:
            logger.debug(f"Progress monitoring error: {e}")
            time.sleep(15)

def parse_validation_results(validation_output_dir: str) -> Dict:
    """
    解析验证结果并统计修复正确率，并按项目类型分类统计
    Args:
        validation_output_dir: 验证结果输出目录
    Returns:
        统计结果字典
    """
    logger.info(f"Parsing validation results from {validation_output_dir}")
    
    if not os.path.exists(validation_output_dir):
        logger.error(f"Validation output directory not found: {validation_output_dir}")
        return {}
    
    validation_files = [f for f in os.listdir(validation_output_dir) if f.endswith('-validated.jsonl')]
    
    total_bugs = 0
    plausible_fixes = 0
    correct_fixes = 0
    uncompilable_fixes = 0
    timeout_fixes = 0
    
    # 按项目类型分类的结果
    project_stats = {}
    
    detailed_results = {}
    
    for val_file in validation_files:
        val_file_path = os.path.join(validation_output_dir, val_file)
        bug_name = val_file.replace('-validated.jsonl', '')
        
        # 提取项目类型（如Chart、Cli、Closure等）
        project_type = None
        if "-" in bug_name:
            project_type = bug_name.split("-")[0]
        
        # 初始化项目类型的统计数据
        if project_type and project_type not in project_stats:
            project_stats[project_type] = {
                'total': 0,
                'plausible': 0,
                'correct': 0,
                'uncompilable': 0,
                'timeout': 0,
                'other': 0,
                'bugs': []
            }
        
        try:
            with open(val_file_path, 'r', encoding='utf-8') as f:
                bug_results = json.load(f)
            
            for patch_result in bug_results:
                total_bugs += 1
                status = patch_result.get('patch_status', 'UNKNOWN')
                
                # 更新项目类型统计
                if project_type:
                    project_stats[project_type]['total'] += 1
                    project_stats[project_type]['bugs'].append(bug_name)
                
                detailed_results[f"{bug_name}_patch_{patch_result.get('val_cnt', 1)}"] = {
                    'bug_name': bug_name,
                    'project_type': project_type,
                    'status': status,
                    'failing_tests': patch_result.get('failing_tests', {}),
                    'patch_code': patch_result.get('patch_code', '')[:100] + '...'  # 只保留前100字符
                }
                
                if status == 'PLAUSIBLE':
                    plausible_fixes += 1
                    correct_fixes += 1  # PLAUSIBLE 表示通过了所有测试
                    if project_type:
                        project_stats[project_type]['plausible'] += 1
                        project_stats[project_type]['correct'] += 1
                elif status == 'UNCOMPILABLE':
                    uncompilable_fixes += 1
                    if project_type:
                        project_stats[project_type]['uncompilable'] += 1
                elif 'TIMEOUT' in status:
                    timeout_fixes += 1
                    if project_type:
                        project_stats[project_type]['timeout'] += 1
                else:
                    if project_type:
                        project_stats[project_type]['other'] += 1
        
        except Exception as e:
            logger.error(f"Error parsing validation file {val_file}: {e}")
            continue
    
    # 计算统计结果
    plausible_rate = 0
    correct_rate = 0
    
    if total_bugs > 0:
        plausible_rate = (plausible_fixes / total_bugs) * 100
        correct_rate = (correct_fixes / total_bugs) * 100
    
    # 计算每个项目类型的修复率
    for project, stats in project_stats.items():
        if stats['total'] > 0:
            stats['plausible_rate'] = round((stats['plausible'] / stats['total']) * 100, 2)
            stats['correct_rate'] = round((stats['correct'] / stats['total']) * 100, 2)
            # 移除重复的bug列表，只保留唯一值
            stats['bugs'] = list(set(stats['bugs']))
            stats['bug_count'] = len(stats['bugs'])
    
    # 按照项目修复率排序
    sorted_projects = sorted(project_stats.items(), 
                            key=lambda x: x[1]['correct_rate'] if x[1]['total'] > 0 else 0, 
                            reverse=True)
    
    # 构建排序后的项目统计
    sorted_project_stats = {k: v for k, v in sorted_projects}
    
    statistics = {
        'total_bugs_validated': total_bugs,
        'plausible_fixes': plausible_fixes,
        'correct_fixes': correct_fixes,
        'uncompilable_fixes': uncompilable_fixes,
        'timeout_fixes': timeout_fixes,
        'other_fixes': total_bugs - plausible_fixes - uncompilable_fixes - timeout_fixes,
        'plausible_rate': round(plausible_rate, 2),
        'correct_rate': round(correct_rate, 2),
        'project_statistics': sorted_project_stats,
        'detailed_results': detailed_results
    }
    
    # 打印总体统计结果
    logger.info("=== DEFECTS4J REPAIR STATISTICS ===")
    logger.info(f"Total bugs validated: {total_bugs}")
    logger.info(f"Plausible fixes: {plausible_fixes}")
    logger.info(f"Correct fixes: {correct_fixes}")
    logger.info(f"Uncompilable fixes: {uncompilable_fixes}")
    logger.info(f"Timeout fixes: {timeout_fixes}")
    logger.info(f"Other status fixes: {statistics['other_fixes']}")
    logger.info(f"Plausible rate: {plausible_rate:.2f}%")
    logger.info(f"Correct rate: {correct_rate:.2f}%")
    
    # 打印每个项目类型的统计结果
    logger.info("\n=== PROJECT TYPE STATISTICS ===")
    for project, stats in sorted_projects:
        if stats['total'] > 0:
            logger.info(f"Project {project}:")
            logger.info(f"  Total bugs: {stats['bug_count']} (with {stats['total']} validation attempts)")
            logger.info(f"  Plausible fixes: {stats['plausible']} ({stats['plausible_rate']}%)")
            logger.info(f"  Correct fixes: {stats['correct']} ({stats['correct_rate']}%)")
            logger.info(f"  Uncompilable: {stats['uncompilable']}, Timeout: {stats['timeout']}, Other: {stats['other']}")
    
    logger.info("=" * 40)
    
    return statistics

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Use LLM-based CFG generation for Java code debugging")
    parser.add_argument('--dataset', '-d', type=str, 
                       default='dataset_test/SRepair/SRepair/dataset/defects4j-sf.json',
                       help='Path to defects4j-sf.json dataset')
    parser.add_argument('--output', '-o', type=str,
                       default='dataset_test/SRepair/results/sf/defects4j_llm_cfg_patches.json',
                       help='Output path for generated patches')
    parser.add_argument('--validate', '-v', action='store_true',
                       help='Run validation after generating patches')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only run validation on existing patch file (skip patch generation)')
    parser.add_argument('--val-output', type=str, default='dataset_test/SRepair/results/sf/defects4j_llm_cfg_validation',
                       help='Output directory for validation results')
    parser.add_argument('--limit', '-l', type=int, default=None,
                       help='Limit the number of bugs to process (useful for debugging)')
    parser.add_argument('--workers', '-w', type=int, default=None,
                       help='Number of parallel workers (default: CPU count)')
    parser.add_argument('--test-single', '-t', type=str, default=None,
                       help='Test a single bug by name (e.g., Chart-1)')
    
    args = parser.parse_args()
    
    # 设置日志
    logger.info("Starting LLM-based Java CFG debug process...")
    logger.info(f"Dataset: {args.dataset}")
    logger.info(f"Output: {args.output}")
    
    # 测试单个bug
    if args.test_single:
        logger.info(f"Testing single bug: {args.test_single}")
        
        # 加载数据集
        with open(args.dataset, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        if args.test_single not in dataset:
            logger.error(f"Bug {args.test_single} not found in dataset")
            return
        
        # 运行单个bug的调试
        corrected_code = llm_java_debug(args.test_single, dataset[args.test_single])
        
        if corrected_code:
            logger.info(f"Generated patch for {args.test_single}")
            
            # 保存补丁
            single_output_path = f"{args.test_single}_llm_cfg_patch.json"
            with open(single_output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    args.test_single: {
                        'patches': [corrected_code],
                        'original_buggy': dataset[args.test_single]['buggy'],
                        'bug_info': {
                            'loc': dataset[args.test_single]['loc'],
                            'start': dataset[args.test_single]['start'],
                            'end': dataset[args.test_single]['end']
                        },
                        'patch_generated': True
                    }
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Patch saved to {single_output_path}")
        else:
            logger.warning(f"No patch generated for {args.test_single}")
        
        return
    
    # 处理完整数据集
    if args.validate_only:
        logger.info("🔍 Validating existing patches only...")
        
        # 检查补丁文件是否存在
        if not os.path.exists(args.output):
            logger.error(f"Patch file not found: {args.output}")
            return
            
        # 运行验证
        run_validation(args.output, args.dataset, args.val_output)
        
        # 解析验证结果
        statistics = parse_validation_results(args.val_output)
        
        # 保存统计结果
        stats_file = os.path.join(os.path.dirname(args.output), 'llm_cfg_repair_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Statistics saved to {stats_file}")
        return
    
    # 检查输入文件
    if not os.path.exists(args.dataset):
        logger.error(f"Dataset file not found: {args.dataset}")
        return
    
    # 处理数据集
    start_time = time.time()
    results = process_defects4j_dataset_parallel(args.dataset, args.output, args.limit, args.workers)
    processing_time = time.time() - start_time
    
    logger.info(f"Patch generation completed in {processing_time:.2f} seconds")
    
    # 运行验证
    if args.validate:
        logger.info("🔍 Starting validation with sf_val_d4j...")
        
        # 删除现有输出目录以避免冲突
        if os.path.exists(args.val_output):
            import shutil
            logger.info(f"Removing existing validation output directory: {args.val_output}")
            shutil.rmtree(args.val_output)
        
        run_validation(args.output, args.dataset, args.val_output)
        
        # 解析验证结果
        statistics = parse_validation_results(args.val_output)
        
        # 保存统计结果
        stats_file = os.path.join(os.path.dirname(args.output), 'llm_cfg_repair_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Statistics saved to {stats_file}")
    
    logger.info("All tasks completed!")

if __name__ == "__main__":
    main() 