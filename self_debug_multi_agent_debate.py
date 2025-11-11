import json
import os
import time
import signal
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import threading

from complete_cfg_builder import TextCFG
from utils import extract_buggy_code, run_check_function, write_str_to_file
from chat import chat_selfdebug, chat_merge_debug_results,conduct_debate, AgentDebugResult, TaskDebateHistory

# 线程锁用于保证输出和文件写入的线程安全
print_lock = threading.Lock()
results_lock = threading.Lock()
debate_lock = threading.Lock()

# 全局标志用于优雅停止
shutdown_event = threading.Event()



class DebugResults:
    """存储调试结果的类"""
    def __init__(self):
        self.total_processed = 0
        self.successful_fixes = 0
        self.test_passed = 0
        self.test_failed = 0
        self.debug_errors = 0
        self.cfg_errors = 0
        self.timeout_errors = 0
        self.debate_histories: List[TaskDebateHistory] = []
        self.results_details = []

    def add_result(self, task_id: str, success: bool, test_passed: Optional[bool], 
                   error_type: str = None, details: str = "", 
                   debate_history: Optional[TaskDebateHistory] = None):
        """添加一个结果记录"""
        with results_lock:
            self.total_processed += 1
            if success:
                self.successful_fixes += 1
            if test_passed is True:
                self.test_passed += 1
            elif test_passed is False:
                self.test_failed += 1
            if error_type == "debug_error":
                self.debug_errors += 1
            elif error_type == "cfg_error":
                self.cfg_errors += 1
            elif error_type == "timeout_error":
                self.timeout_errors += 1
            
            if debate_history:
                self.debate_histories.append(debate_history)
            
            self.results_details.append({
                'task_id': task_id,
                'success': success,
                'test_passed': test_passed,
                'error_type': error_type,
                'details': details,
                'has_debate_history': debate_history is not None
            })

    def print_summary(self):
        """打印统计摘要"""
        with print_lock:
            print("\n" + "="*60)
            print("MULTI-AGENT DEBATE DEBUG RESULTS SUMMARY")
            print("="*60)
            print(f"Total processed: {self.total_processed}")
            print(f"Successful debug attempts: {self.successful_fixes}")
            print(f"Tests passed: {self.test_passed}")
            print(f"Tests failed: {self.test_failed}")
            print(f"Debug errors: {self.debug_errors}")
            print(f"CFG errors: {self.cfg_errors}")
            print(f"Timeout errors: {self.timeout_errors}")
            print(f"Tasks with debate history: {len(self.debate_histories)}")
            if self.total_processed > 0:
                print(f"Success rate: {self.successful_fixes/self.total_processed*100:.2f}%")
                print(f"Test pass rate: {self.test_passed/self.total_processed*100:.2f}%")
            print("="*60)

def safe_print(message: str):
    """线程安全的打印函数"""
    with print_lock:
        print(f"[{time.strftime('%H:%M:%S')}] {message}")

def extract_test_cases_from_example(example_test: str, func_name: str) -> List[str]:
    """从example_test中提取测试用例"""
    individual_tests = []
    lines = example_test.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('assert'):
            test_func = f"""
def test_{func_name}():
    {line}

test_{func_name}()
"""
            individual_tests.append(test_func)
    
    return individual_tests

def agent_debug_task(agent_id: int, buggy_code: str, test_cases: List[str], 
                     task_description: str, cfg_text: str, 
                     func_name: str) -> AgentDebugResult:
    """
    单个Agent执行调试任务
    Args:
        agent_id: Agent的ID
        buggy_code: 错误代码
        test_cases: 测试用例列表
        task_description: 任务描述
        cfg_text: 控制流图
        func_name: 函数名
    Returns:
        AgentDebugResult对象
    """
    start_time = time.time()
    task_id = f"agent_{agent_id}"
    
    try:
        safe_print(f"[Agent {agent_id}] Starting debugging with {len(test_cases)} test cases")
        
        # 为每个测试用例进行调试
        individual_results = []
        analyzed_cases = []
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                safe_print(f"[Agent {agent_id}] Analyzing test case {i}/{len(test_cases)}")
                
                # 使用self-debug方法
                debug_result = chat_selfdebug(
                    buggy_code=buggy_code,
                    example_test=test_case,
                    task_description=task_description,
                    text_cfg=cfg_text
                )
                
                # 解析结果
                try:
                    full_debug_json = json.loads(debug_result)
                    explanation = full_debug_json.get("explanation", "")
                    overall_analysis = full_debug_json.get("overall_analysis", {})
                    correctedCode_test_analysis = full_debug_json.get("correctedCode_test_analysis", buggy_code)
                    corrected_code = correctedCode_test_analysis.get("corrected_code", buggy_code)
                    
                    simplified_result = {
                        "test_case": test_case.strip(),
                        "bug_analysis": overall_analysis.get("common_patterns", ""),
                        "corrected_code": corrected_code,
                        "explanation": explanation
                    }
                    
                    individual_results.append(json.dumps(simplified_result, ensure_ascii=False))
                    analyzed_cases.append(test_case)
                    
                except json.JSONDecodeError as e:
                    safe_print(f"[Agent {agent_id}] JSON parse error for test case {i}: {str(e)[:100]}")
                    continue
                    
            except Exception as e:
                safe_print(f"[Agent {agent_id}] Error analyzing test case {i}: {str(e)[:100]}")
                continue
        
        if not individual_results:
            safe_print(f"[Agent {agent_id}] No successful analysis results")
            return AgentDebugResult(
                agent_id=agent_id,
                task_id=task_id,
                success=False,
                corrected_code=buggy_code,
                reasoning="Failed to analyze any test cases",
                confidence_score=0.0,
                execution_time=time.time() - start_time,
                error_analysis="No individual results generated"
            )
        
        # 合并所有结果
        safe_print(f"[Agent {agent_id}] Merging {len(individual_results)} analysis results")
        final_code = chat_merge_debug_results(
            buggy_code=buggy_code,
            individual_results=individual_results,
            task_description=task_description
        )
        
        execution_time = time.time() - start_time
        
        # 计算置信度分数 (基于成功分析的测试用例比例)
        confidence = len(analyzed_cases) / len(test_cases) if test_cases else 0.0
        
        safe_print(f"[Agent {agent_id}] Completed in {execution_time:.2f}s, confidence: {confidence:.2f}")
        
        return AgentDebugResult(
            agent_id=agent_id,
            task_id=task_id,
            success=True,
            corrected_code=final_code,
            reasoning=f"Analyzed {len(analyzed_cases)}/{len(test_cases)} test cases successfully",
            confidence_score=confidence,
            execution_time=execution_time,
            test_cases_analyzed=analyzed_cases,
            error_analysis=""
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        safe_print(f"[Agent {agent_id}] Fatal error: {str(e)[:100]}")
        return AgentDebugResult(
            agent_id=agent_id,
            task_id=task_id,
            success=False,
            corrected_code=buggy_code,
            reasoning=f"Fatal error during debugging: {str(e)}",
            confidence_score=0.0,
            execution_time=execution_time,
            error_analysis=str(e)
        )


def process_single_task_with_debate(task_data: dict, task_index: int, 
                                   num_agents: int = 3,
                                   timeout: int = 600) -> Tuple[str, bool, Optional[bool], str, str, TaskDebateHistory]:
    """
    使用多Agent辩论方法处理单个任务
    Args:
        task_data: 任务数据
        task_index: 任务索引
        num_agents: Agent数量
        timeout: 超时时间
    Returns:
        (task_id, debug_success, test_passed, error_type, details, debate_history)
    """
    task_id = task_data.get('task_id', f'task_{task_index}')
    # if task_index != 54:
    #     return task_id, False, None, "skipped", "Only processing task_id 54 in this run", TaskDebateHistory(task_id=task_id, buggy_code="")
    task_start_time = time.time()
    
    # 初始化辩论历史
    debate_history = TaskDebateHistory(task_id=task_id, buggy_code="")
    
    if shutdown_event.is_set():
        return task_id, False, None, "shutdown", "Process was shut down", debate_history
    
    try:
        # 提取基本信息
        func_name = task_data['entry_point']
        buggy_code = extract_buggy_code(task_data)
        example_test = task_data.get('example_test', '')
        test_code = task_data['test']
        task_description = task_data['docstring']
        
        debate_history.buggy_code = buggy_code
        
        safe_print(f"[{task_index}] Processing {task_id} with {num_agents} agents")
        
        # 构建CFG
        thread_id = threading.get_ident()
        temp_filename = f"temp_buggy_code_{task_index}_{thread_id}.py"
        
        try:
            write_str_to_file(buggy_code, temp_filename)
            
            cfg_start_time = time.time()
            try:
                textcfg = TextCFG(temp_filename, func_name)
                cfg_text = textcfg.cfg_text
                cfg_duration = time.time() - cfg_start_time
                safe_print(f"[{task_index}] CFG built in {cfg_duration:.2f}s")
            except Exception as e:
                safe_print(f"[{task_index}] CFG failed: {str(e)[:100]}")
                return task_id, False, None, "cfg_error", f"CFG error: {str(e)}", debate_history
        finally:
            try:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
            except:
                pass
        
        # 提取测试用例
        test_cases = []
        if example_test:
            test_cases = extract_test_cases_from_example(example_test, func_name)
            safe_print(f"[{task_index}] Extracted {len(test_cases)} test cases")
        
        if not test_cases:
            safe_print(f"[{task_index}] No test cases, skipping multi-agent debate")
            return task_id, False, None, "no_test_cases", "No test cases available", debate_history
        
        # 阶段1: 多个Agent并行调试
        safe_print(f"[{task_index}] Phase 1: {num_agents} agents debugging in parallel")
        
        agent_futures = []
        with ThreadPoolExecutor(max_workers=num_agents) as executor:
            for agent_id in range(num_agents):
                future = executor.submit(
                    agent_debug_task,
                    agent_id,
                    buggy_code,
                    test_cases,
                    task_description,
                    cfg_text,
                    func_name
                )
                agent_futures.append(future)
            
            # 收集所有Agent结果
            agent_results = []
            for future in as_completed(agent_futures, timeout=timeout * 0.6):  # 60%时间给Agent
                try:
                    result = future.result(timeout=100)
                    agent_results.append(result)
                    debate_history.agent_results.append(result)
                except Exception as e:
                    safe_print(f"[{task_index}] Agent error: {str(e)[:100]}")
        
        if not agent_results:
            safe_print(f"[{task_index}] No agent results collected")
            return task_id, False, None, "agent_error", "No agents completed", debate_history
        
        safe_print(f"[{task_index}] Collected {len(agent_results)} agent results")
        
        # 阶段2: Agent辩论
        safe_print(f"[{task_index}] Phase 2: Multi-agent debate")
        
        try:
            final_code, debate_rounds = conduct_debate(
                agent_results=agent_results,
                task_description=task_description,
                test_cases=test_cases,
                buggy_code=buggy_code,
                max_rounds=2  # 2轮辩论
            )
            
            debate_history.debate_rounds = debate_rounds
            debate_history.final_code = final_code
            
            safe_print(f"[{task_index}] Debate completed with {len(debate_rounds)} rounds")
            
        except Exception as e:
            safe_print(f"[{task_index}] Debate failed: {str(e)[:100]}")
            # 回退到最佳Agent结果
            successful_agents = [r for r in agent_results if r.success]
            if successful_agents:
                best_agent = max(successful_agents, key=lambda x: x.confidence_score)
                final_code = best_agent.corrected_code
            else:
                return task_id, False, None, "debate_error", f"Debate error: {str(e)}", debate_history
        
        # 阶段3: 测试最终代码
        safe_print(f"[{task_index}] Phase 3: Testing final code")
        
        try:
            test_passed = run_check_function(func_name, test_code, final_code)
            debate_history.final_test_passed = test_passed
            
            total_time = time.time() - task_start_time
            debate_history.total_time = total_time
            
            if test_passed:
                safe_print(f"[{task_index}] ✅ SUCCESS: {task_id} after debate (Total: {total_time:.2f}s)")
                return task_id, True, True, None, "Success after debate", debate_history
            else:
                safe_print(f"[{task_index}] ❌ FAIL: {task_id} debate solution failed tests")
                return task_id, True, False, None, "Tests failed after debate", debate_history
                
        except Exception as e:
            safe_print(f"[{task_index}] Test execution error: {str(e)[:100]}")
            return task_id, True, None, "test_error", f"Test error: {str(e)}", debate_history
    
    except Exception as e:
        total_time = time.time() - task_start_time
        safe_print(f"[{task_index}] Unexpected error: {str(e)[:100]}")
        return task_id, False, None, "unexpected_error", f"Unexpected error: {str(e)}", debate_history

def load_dataset(file_path: str, limit: Optional[int] = None) -> List[dict]:
    """加载数据集"""
    tasks = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if limit and len(tasks) >= limit:
                    break
                line = line.strip()
                if line:
                    try:
                        task_data = json.loads(line)
                        tasks.append(task_data)
                    except json.JSONDecodeError as e:
                        safe_print(f"Error parsing line {line_num}: {e}")
        return tasks
    except FileNotFoundError:
        safe_print(f"Dataset file {file_path} not found!")
        return []

def save_detailed_results(results: DebugResults, output_file: str):
    """保存详细结果到文件"""
    try:
        # 创建输出目录
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_processed': results.total_processed,
                    'successful_fixes': results.successful_fixes,
                    'test_passed': results.test_passed,
                    'test_failed': results.test_failed,
                    'debug_errors': results.debug_errors,
                    'cfg_errors': results.cfg_errors,
                    'timeout_errors': results.timeout_errors,
                    'success_rate': results.successful_fixes/results.total_processed if results.total_processed > 0 else 0,
                    'test_pass_rate': results.test_passed/results.total_processed if results.total_processed > 0 else 0,
                    'tasks_with_debate': len(results.debate_histories)
                },
                'details': results.results_details,
                'debate_histories': [h.to_dict() for h in results.debate_histories]
            }, f, indent=2, ensure_ascii=False)
        safe_print(f"Detailed results saved to {output_file}")
    except Exception as e:
        safe_print(f"Failed to save results: {e}")

def signal_handler(signum, frame):
    """信号处理器"""
    safe_print("Received interrupt signal. Shutting down...")
    shutdown_event.set()

def main():
    """主函数"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    dataset_file = "dataset_test/humanevalfix/humanevalpack.jsonl"
    max_workers = 4  # 并行处理的任务数
    num_agents = 3   # 每个任务的Agent数量
    task_timeout = 6000  # 每个任务10分钟
    overall_timeout = 36000  # 总体1小时
    task_limit = 164  # 限制处理任务数，用于测试
    
    safe_print("="*60)
    safe_print("Starting Multi-Agent Debate Debugging System")
    safe_print("="*60)
    safe_print(f"Dataset: {dataset_file}")
    safe_print(f"Max parallel tasks: {max_workers}")
    safe_print(f"Agents per task: {num_agents}")
    safe_print(f"Task timeout: {task_timeout}s")
    safe_print(f"Overall timeout: {overall_timeout}s")
    if task_limit:
        safe_print(f"Task limit: {task_limit} (testing mode)")
    safe_print("="*60)
    
    # 加载数据集
    tasks = load_dataset(dataset_file, task_limit)
    if not tasks:
        safe_print("No tasks loaded. Exiting.")
        return
    
    safe_print(f"Loaded {len(tasks)} tasks")
    
    # 初始化结果收集器
    results = DebugResults()
    
    # 开始时间
    start_time = time.time()
    
    # 使用线程池并行处理
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {}
            for i, task_data in enumerate(tasks):
                if shutdown_event.is_set():
                    break
                future = executor.submit(
                    process_single_task_with_debate, 
                    task_data, 
                    i, 
                    num_agents,
                    task_timeout
                )
                future_to_index[future] = i
            
            safe_print(f"Submitted {len(future_to_index)} tasks")
            
            # 处理完成的任务
            try:
                for future in as_completed(future_to_index, timeout=overall_timeout):
                    if shutdown_event.is_set():
                        break
                    
                    task_index = future_to_index[future]
                    try:
                        task_id, debug_success, test_passed, error_type, details, debate_history = future.result(timeout=task_timeout + 60)
                        results.add_result(task_id, debug_success, test_passed, error_type, details, debate_history)
                        
                        # 进度报告
                        if results.total_processed % 2 == 0:
                            elapsed = time.time() - start_time
                            progress = results.total_processed / len(tasks) * 100
                            safe_print(f"Progress: {results.total_processed}/{len(tasks)} ({progress:.1f}%) "
                                     f"- Elapsed: {elapsed:.1f}s "
                                     f"- Success: {results.test_passed}/{results.total_processed}")

                    except TimeoutError:
                        safe_print(f"Task {task_index} timeout")
                        results.add_result(f"task_{task_index}", False, None, "timeout_error", "Task timeout", None)
                    except Exception as e:
                        safe_print(f"Task {task_index} exception: {str(e)[:100]}")
                        results.add_result(f"task_{task_index}", False, None, "exception", str(e), None)
                    
                    if time.time() - start_time > overall_timeout:
                        safe_print(f"Overall timeout reached")
                        break
                        
            except TimeoutError:
                safe_print(f"Overall timeout for as_completed")
    
    except KeyboardInterrupt:
        safe_print("Keyboard interrupt received")
        shutdown_event.set()
    except Exception as e:
        safe_print(f"Executor error: {str(e)[:100]}")
        shutdown_event.set()
    
    # 等待剩余任务
    if not shutdown_event.is_set():
        safe_print("Waiting for remaining tasks...")
        time.sleep(5)
    
    # 计算总耗时
    total_time = time.time() - start_time
    
    # 打印最终结果
    results.print_summary()
    safe_print(f"Total time: {total_time:.2f}s")
    if results.total_processed > 0:
        safe_print(f"Average time per task: {total_time/results.total_processed:.2f}s")
    
    # 保存结果
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"./dataset_test/humanevalfix/results/debate_results_{timestamp}.json"
    save_detailed_results(results, output_file)
    
    safe_print(f"Multi-agent debate debugging completed!")
    safe_print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()



