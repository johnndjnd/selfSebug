import threading
from openai import OpenAI
from loguru import logger
import time
import json
import os
from dotenv import load_dotenv
from typing import List


import json
import os
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime

from loguru import logger

# 加载环境变量
load_dotenv()

print_lock = threading.Lock()
GPT_MODEL = "openai/gpt-4o-mini"
GPT_BASE_URL = "https://openrouter.ai/api/v1"
GPT_API_KEY = os.getenv("GPT_API_KEY")
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    base_url=DEEPSEEK_BASE_URL,
    api_key=DEEPSEEK_API_KEY,
    timeout=180.0,  # 设置2分钟超时
)

MAX_VLLM_RETRIES = 3  # 减少重试次数
RETRY_DELAY = 2  # 增加重试延迟
TEMPERATURE = 0.8 
TOTAL_PROMPT_TOKENS = 0
TOTAL_COMPLETION_TOKENS = 0

@dataclass
class AgentDebugResult:
    """单个Agent的调试结果"""
    agent_id: int
    task_id: str
    success: bool
    corrected_code: str
    reasoning: str
    confidence_score: float
    execution_time: float
    test_cases_analyzed: List[str] = field(default_factory=list)
    error_analysis: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class DebateRound:
    """一轮辩论的结果"""
    round_number: int
    agent_arguments: List[Dict[str, str]]  # agent_id -> argument
    consensus_code: Optional[str] = None
    disagreement_points: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class TaskDebateHistory:
    """任务的完整辩论历史"""
    task_id: str
    buggy_code: str
    agent_results: List[AgentDebugResult] = field(default_factory=list)
    debate_rounds: List[DebateRound] = field(default_factory=list)
    final_code: Optional[str] = None
    final_test_passed: Optional[bool] = None
    total_time: float = 0.0
    
    def to_dict(self) -> dict:
        """转换为可序列化的字典"""
        return {
            'task_id': self.task_id,
            'buggy_code': self.buggy_code,
            'agent_results': [
                {
                    'agent_id': r.agent_id,
                    'success': r.success,
                    'corrected_code': r.corrected_code,
                    'reasoning': r.reasoning,
                    'confidence_score': r.confidence_score,
                    'execution_time': r.execution_time,
                    'test_cases_analyzed': r.test_cases_analyzed,
                    'error_analysis': r.error_analysis,
                    'timestamp': r.timestamp
                } for r in self.agent_results
            ],
            'debate_rounds': [
                {
                    'round_number': d.round_number,
                    'agent_arguments': d.agent_arguments,
                    'consensus_code': d.consensus_code,
                    'disagreement_points': d.disagreement_points,
                    'timestamp': d.timestamp
                } for d in self.debate_rounds
            ],
            'final_code': self.final_code,
            'final_test_passed': self.final_test_passed,
            'total_time': self.total_time
        }

def get_completion_with_retry(messages, model=DEEPSEEK_MODEL, MAX_VLLM_RETRIES=MAX_VLLM_RETRIES):
    global TOTAL_PROMPT_TOKENS, TOTAL_COMPLETION_TOKENS
    for attempt in range(MAX_VLLM_RETRIES):
        try:
            logger.info(f"Attempting LLM call (attempt {attempt + 1}/{MAX_VLLM_RETRIES})")
            
            start_time = time.time()
            chat_response = client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=TEMPERATURE,
                response_format={
                    'type':'json_object',
                },
                max_tokens=8100,
                timeout=120.0,  # 设置请求超时
            )
            
            call_duration = time.time() - start_time
            logger.info(f"LLM call completed in {call_duration:.2f}s")
            
            response = chat_response.choices[0].message.content
            logger.info(f"收到API响应，长度: {len(response) if response else 0} 字符")
            
            # 验证响应是否为空或过短
            if not response or len(response.strip()) < 10:
                logger.error(f"响应为空或过短: {len(response) if response else 0} 字符")
                logger.error(f"响应内容: {response}")
                raise ValueError(f"Empty or too short response: {len(response) if response else 0} chars")
            
            # 快速验证JSON格式
            logger.info("开始验证JSON格式...")
            try:
                json.loads(response)
                logger.info("JSON格式验证通过")
            except json.JSONDecodeError as e:
                # 添加详细的错误调试信息
                logger.error("="*50)
                logger.error("get_completion_with_retry中JSON解析失败！详细信息如下：")
                logger.error(f"JSON错误详情: {str(e)}")
                logger.error(f"响应总长度: {len(response) if response else 0} 字符")
                logger.error(f"响应内容前500字符: {response[:500] if response else 'None'}...")
                logger.error(f"响应内容后100字符: {response[-100:] if response and len(response) > 100 else 'N/A'}...")
                
                # 检查错误位置附近的内容
                error_char_pos = getattr(e, 'pos', None)
                if error_char_pos and response:
                    start_pos = max(0, error_char_pos - 50)
                    end_pos = min(len(response), error_char_pos + 50)
                    logger.error(f"错误位置附近内容 (位置{error_char_pos}前后50字符):")
                    logger.error(f"'{response[start_pos:end_pos]}'")
                    logger.error(f"错误字符位置: {'^' * (error_char_pos - start_pos)}")
                
                logger.error("="*50)
                raise ValueError(f"Invalid JSON response: {str(e)[:100]}...")
            
            # Update token counts
            TOTAL_PROMPT_TOKENS += chat_response.usage.prompt_tokens
            TOTAL_COMPLETION_TOKENS += chat_response.usage.completion_tokens
            
            logger.info(f"LLM call successful, response length: {len(response)} chars")
            return response
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM call failed (attempt {attempt + 1}/{MAX_VLLM_RETRIES}): {error_msg[:200]}...")
            
            # 如果是JSON解析相关错误，提供额外的上下文信息
            if "Invalid JSON response" in error_msg or "JSONDecodeError" in error_msg or "Expecting value" in error_msg:
                logger.error("这是JSON解析错误，可能的原因：")
                logger.error("1. API返回了非JSON格式的内容（HTML错误页面、纯文本等）")
                logger.error("2. API响应被截断")
                logger.error("3. API返回了空响应")
                logger.error("4. 响应中包含无效的JSON字符")
            
            if attempt < MAX_VLLM_RETRIES - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error("Max retries reached. Giving up.")
                raise Exception(f"All {MAX_VLLM_RETRIES} attempts failed. Last error: {error_msg}")

def direct_fix_code(task_description: str, test_case: str, buggy_code: str,recheckDetails = "") -> str:
    """
    直接调用大模型修复代码的函数
    Args:
        task_description: 任务描述
        test_case: 测试用例
        buggy_code: 错误的代码
    Returns:
        修复后的代码
    """
    prompt = f"""
    You are an expert Python programmer. I will provide you with a buggy Python function along with its task description and test case. 
    Your job is to analyze the bug and provide the corrected version of the code.

    ### Task Description
    {task_description}

    ### Test Case
    {test_case}

    ### Buggy Code
    ```python
    {buggy_code}
    ```

    {f"### In your previous Fix Attempt Details\n{recheckDetails}" if recheckDetails else ""}

    ### Requirements
    1. Analyze the buggy code carefully and identify the issues
    2. Fix all bugs to make the code pass the provided test case
    3. Ensure the corrected code fulfills the task description
    4. Keep the original function signature and structure as much as possible
    5. Provide clean, readable code without extra comments
    6. Include all necessary import statements for the corrected code to run properly

    ### EXAMPLE JSON OUTPUT
    {{"fixed_code": "def function_name(params):\\n    # corrected implementation\\n    return result"}}

    Please output only the JSON format with the fixed code.
    """

    messages = [
        {'role': 'system', 'content': "You are an expert Python programmer specialized in debugging and fixing code."},
        {'role': 'user', 'content': prompt},
    ]

    try:
        response = get_completion_with_retry(messages)
        logger.info(f"direct_fix_code response: {response}")
        
        # 解析JSON响应
        try:
            data = json.loads(response)
            fixed_code = data.get("fixed_code", "")
            
            if not fixed_code:
                logger.warning("fixed_code字段为空，返回原始代码")
                return buggy_code
                
            return fixed_code.strip()
        except json.JSONDecodeError as e:
            logger.error("="*50)
            logger.error("direct_fix_code中JSON解析失败！详细信息如下：")
            logger.error(f"JSON错误详情: {str(e)}")
            logger.error(f"响应总长度: {len(response) if response else 0} 字符")
            logger.error(f"响应内容前500字符: {response[:500] if response else 'None'}...")
            logger.error(f"响应内容后100字符: {response[-100:] if response and len(response) > 100 else 'N/A'}...")
            logger.error("="*50)
            return buggy_code
        
    except Exception as e:
        logger.error(f"direct_fix_code出错: {e}")
        return buggy_code
    

def ai_critic_word(task_description: str,textcfg: str,test_case: str, fixed_code: str, run_details: str = "") -> tuple:
    """
    使用另一个智能体来评审修复后的代码
    """
    prompt = f"""
    I will provide you with a task description, a test case, and a piece of Python code that has been fixed.
    Your job is to evaluate whether the fixed code correctly addresses the task and passes the test case.
    ### Task Description
    {task_description}
    ### Test Case
    {test_case}
    ### Fixed Code
    ```python
    {fixed_code}
    ```
    ### CFG for the Fixed Code
    {textcfg}

    {f"### In your previous Fix Attempt Details\n{run_details}" if run_details else ""}

    You must analyze each test case using the following  process:

Simulate execution with test case inputs**
- Should ONLY rely on the CFG and the buggy code, DO NOT rely on the test cases and task description when executing the code.
- Start with the initial variable state from each test case input
- Execute the code following the CFG path step by step, starting from the Entry Point and ending at END (the Entry Point and END are Given in the CFG), recording detailed variable changes
- When one Block has completed its execution and is about to move to another Block, please determine based on the CFG which Block should be executed next.
- For control flow statements (if/while/for), clearly record condition evaluation results
- Format: "Step i Block n: code_content -> variable_state_changes"


    ### Evaluation Criteria
    1. Analyze the fixed code to see if it meets the task description
    2. Determine if the fixed code would pass the provided test case
    Please respond with a JSON object in the following format:
    {{ "step1_execution_trace": {{
                "reasoning": "Detailed reasoning process for step-by-step execution",
                "execution_steps": [
                    "Step 1 Block i: code_content -> variable_state",
                    "Step 2 Block j: code_content -> variable_state",
                    "..."
                ],
                "final_output": "Final output"
            }}
    "is_passed": true/false, "reason": "if not passed, provide reasons as detailed as possible"
    }}
    """

    messages = [
        {'role': 'system', 'content': "You are an expert Python programmer specialized in code review and critique."},
        {'role': 'user', 'content': prompt},
    ]

    try:
        response = get_completion_with_retry(messages)
        logger.info(f"ai_critic_word response: {response}")
        
        # 解析JSON响应
        try:
            data = json.loads(response)
            is_passed = data.get("is_passed", False)
            reason = data.get("reason", "")
            return is_passed,reason
        except json.JSONDecodeError as e:
            logger.error("="*50)
            logger.error("ai_critic_word中JSON解析失败！详细信息如下：")
            logger.error(f"JSON错误详情: {str(e)}")
            logger.error(f"响应总长度: {len(response) if response else 0} 字符")
            logger.error(f"响应内容前500字符: {response[:500] if response else 'None'}...")
            logger.error(f"响应内容后100字符: {response[-100:] if response and len(response) > 100 else 'N/A'}...")
            logger.error("="*50)
            return False,""
    except Exception as e:
        logger.error(f"ai_critic_word出错: {e}")
        return False,""

# - You MUST obey the following loop handling rules to reduce the output length:
# **LOOP HANDLING RULES (CRITICAL FOR REDUCING OUTPUT):**
# - For loops (while/for), use abbreviated execution format to avoid excessive output:
#   * Show the first 2 iterations in detail with step-by-step execution
#   * Use "... (skipping middle iterations) ..." to represent intermediate iterations
#   * Show the last 1-2 iterations in detail (when loop condition becomes false or changes pattern)
#   * Always show the final variable states after loop completion
# - Example format for loop:
#   ```
#   Step 3 Block 2: while n > 1: -> condition: n=5 > 1 is True
#   Step 4 Block 3: n = n * 2 + 1 -> n: 5 → (5*2)+1 = 11
#   Step 5 Block 2: while n > 1: -> condition: n=11 > 1 is True  
#   Step 6 Block 3: n = n * 2 + 1 -> n: 11 → (11*2)+1 = 23
#   ... (skipping middle iterations) ...
#   Step X Block 2: while n > 1: -> condition: n=2 > 1 is True
#   Step Y Block 3: n = n * 2 + 1 -> n: 2 → (2*2)+1 = 5
#   Step Z Block 2: while n > 1: -> condition: n=1 > 1 is False (exit loop)
#   ```
#- If there is a loop in the code, you should use "..." to skip the middle part of the loop instead of executing the loop step by step, But you should give variable values of the first two and last two iterations of the loop.
#2. **Execution Trace Accuracy**: The code is buggy and may not yield the correct output in the test cases. Therefore, do not rely on the output in the test cases. Instead, execute the buggy code to obtain the actual output.


def chat_merge_debug_results(buggy_code: str, individual_results: List[str], task_description: str) -> str:
    """
    合并多个单独测试用例的调试结果，生成最终的修正代码
    Args:
        buggy_code: 原始错误代码
        individual_results: 每个测试用例的调试结果列表
        task_description: 任务描述
    Returns:
        最终的修正代码
    """
    # 解析所有个别结果
    parsed_results = []


    for result in individual_results:
        try:
            parsed = json.loads(result)
            parsed_results.append(parsed)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse individual result: {e}")
            continue
    

    
    # 构建合并提示
    individual_analyses = ""
    for i, result in enumerate(parsed_results, 1):
        individual_analyses += f"""
### Analysis {i}:
**Test Case:** {result.get('test_case', 'Unknown')}
**Bug Analysis:** {result.get('bug_analysis', 'No analysis')}
**Proposed Fix:** 
```python
{result.get('corrected_code', 'No code')}
Explanation: {result.get('explanation', 'No explanation')}

"""

    prompt = f"""
You are an expert Python programmer and tester. You have received multiple individual analyses of a buggy function, each focused on a specific test case. Your task is to test each proposed correction, evaluate the results, and select the optimal solution.
if no individual analysis can fix the bug, you need to synthesize a new corrected code based on all individual analyses.
Task Description
{task_description}

Original Buggy Code
python
{buggy_code}
Individual Test Case Analyses
{individual_analyses}

Testing and Evaluation Instructions
Simulate Test Execution: For each proposed corrected code, simulate running it against ALL test cases mentioned in the analyses

Record Test Results: Track which test cases pass or fail for each correction

Evaluate Code Quality: Assess the readability, efficiency, and robustness of each solution

Select Optimal Solution: Choose the correction that passes the most tests and has the best code quality

Synthesize Improvements: Incorporate the best elements from multiple solutions if needed

Test Simulation Format
For each corrected code version, simulate:

python
# Test Case 1: [description]
result = corrected_function(test_input_1)
expected = expected_output_1
# Result: PASS/FAIL

# Test Case 2: [description]
result = corrected_function(test_input_2)
expected = expected_output_2
# Result: PASS/FAIL
JSON Output Format
Please output strictly in the following JSON format:
{{
"test_results_analysis": "Summary of test results for all proposed corrections",
"best_correction_index": "Index of the correction that performed best in testing",
"test_case_comparison": {{
"test_case_1": {{
"test_case_content": "content of test case 1",
"tests_passed": ["correction_1", "correction_3"],
"tests_failed": ["correction_2"],
}},
"test_case_2": {{
"test_case_content": "content of test case 2",
"tests_passed": ["correction_2"],
"tests_failed": ["correction_1", "correction_3"],
}}
}},
"synthesis_analysis": "Analysis of how you combined the best elements from multiple corrections",
"common_issues": "List of issues that appeared across multiple test cases",
"final_corrected_code": "Complete final corrected code with proper imports",
"comprehensive_explanation": "Detailed explanation of selection process and all changes made"
}}

Quality Requirements
Rigorous Testing: Test each correction against all mentioned test cases

Objective Evaluation: Use test results as primary selection criteria

Code Quality: Consider readability, efficiency, and maintainability

Completeness: Ensure final solution addresses all identified issues

Transparency: Clearly document the testing process and selection rationale

Begin your testing and synthesis now.
"""

    messages = [
        {'role': 'system', 'content': "You are an expert Python programmer specializing in synthesizing multiple debugging analyses into a unified solution."},
        {'role': 'user', 'content': prompt}
    ]

    try:
        response = get_completion_with_retry(messages)
        logger.info(f"merge debug response: {response}")
        
        # 验证JSON格式
        try:
            result_json = json.loads(response)
            return result_json.get('final_corrected_code', buggy_code)
        except json.JSONDecodeError as e:
            logger.error(f"Merge debug JSON parsing failed: {str(e)}")
            return buggy_code
            
    except Exception as e:
        logger.error(f"Merge debug error: {e}")
        return buggy_code

def choose_better_result(buggy_code: str, result1: str, result2: str, task_description: str, test_case: List[str]) -> str:
    """
    比较两个调试结果，选择更好的一个
    Args:
        result1: 第一个调试结果
        result2: 第二个调试结果
        task_description: 任务描述
        test_case: 测试用例
    Returns:
        更好的调试结果
    """
    prompt = f"""
You are an expert Python programmer and debugger. and your last task is systematically analyze buggy code using detailed Chain-of-Thought reasoning and provide a corrected version.however, another agent has also provided a corrected version of the same buggy code.Your task is to compare both results and select the better one based on correctness,and the test result of their corrected code is given below,but the test result is given by the agent too,may also be wrong.you need to analyze the code logic by yourself to determine which result is better.
in each result,you will given a cfg_test of the corrected code,which is the control flow graph of the corrected code,you should use it to help you analyze the code logic.

Simulate execution with test case inputs**
- Should ONLY rely on the CFG and the buggy code, DO NOT rely on the test cases and task description when executing the code.
- Start with the initial variable state from each test case input
- Execute the code following the CFG path step by step, starting from the Entry Point and ending at END (the Entry Point and END are Given in the CFG), recording detailed variable changes
- When one Block has completed its execution and is about to move to another Block, please determine based on the CFG which Block should be executed next.
- For control flow statements (if/while/for), clearly record condition evaluation results
- Format: "Step i Block n: code_content -> variable_state_changes"
- **Important:if the code contains loops,please follow the loop handling rules given above,hoever,if the loop is a dead loop that will never end,you should execute it step by step until 3 iterations**


### Task Description
{task_description}

### original Buggy Code
```python
{buggy_code}
```

### Test Case
```python
{test_case}
```

### Result 1
{result1}


### Result 2
{result2}


### Selection Criteria
1. Correctness: Which result correctly fixes the bug and passes the provided test case?(the most important criteria)
2. Code Quality: Which result is more readable, efficient, and maintainable?

### JSON Output Format
Please output strictly in the following JSON format:
```json
{{
"better_result_index": "1 or 2",
"final_corrected_code": "the better corrected code between result 1 and result 2",
"analysis": "Detailed analysis of both results based on the selection criteria",
"selection_rationale": "Clear explanation of why the chosen result is better",
result_1_"step1_execution_trace": {{
    test_cases:[
        {{      "test_case_id": "1",
                "reasoning": "Detailed reasoning process for step-by-step execution",
                "execution_steps": [
                    "Step 1 Block i: code_content -> variable_state",
                    "Step 2 Block j: code_content -> variable_state",
                    "..."
                ],
                "final_output": "Final output"
    "is_passed": true/false, "reason": "if not passed, provide reasons as detailed as possible"
    }}
    ]
    }}
,result_2_"step1_execution_trace": {{
    test_cases:[
        {{      "test_case_id": "1",
                "reasoning": "Detailed reasoning process for step-by-step execution",
                "execution_steps": [
                    "Step 1 Block i: code_content -> variable_state",
                    "Step 2 Block j: code_content -> variable_state",
                    "..."
                ],
                "final_output": "Final output"
    "is_passed": true/false, "reason": "if not passed, provide reasons as detailed as possible"
    }}
    ]
    }}

}}
```
"""

    messages = [
        {'role': 'user', 'content': prompt}
    ]

    try:
        response = get_completion_with_retry(messages)
        logger.info(f"choose better result response: {response}")

        # 验证JSON格式
        try:
            return json.dumps(json.loads(response), ensure_ascii=False, indent=2)
        except json.JSONDecodeError as e:
            logger.error(f"Choose better result JSON parsing failed: {str(e)}")
            return ""

    except Exception as e:
        logger.error(f"Choose better result error: {e}")
        return ""

def final_evaluate(buggy_code: str, top_candidates: list, task_description: str, test_case: List[str]) -> str:
    """
    让大模型评估 top_candidates（通常为前3个候选修复版本），选出最佳代码。
    由于无法真实执行代码，大模型需基于逻辑一致性、语义正确性和任务描述合理性进行推断。
    
    Args:
        buggy_code (str): 原始有bug的代码
        top_candidates (list): 3个候选修复版本，每个元素为 dict 或 str（需包含 corrected_code 字段）
        task_description (str): 任务描述
        test_case (str): 相关测试用例（可为空字符串）

    Returns:
        str: JSON字符串，格式如下：
        {
            "best_index": int,             # 最优候选的索引（从1开始）
            "final_corrected_code": str,   # 最优的修复代码
            "evaluation_reasoning": str    # 详细评估过程说明
        }
    """
    # 统一格式
    formatted_candidates = []
    for i, c in enumerate(top_candidates, start=1):
        if isinstance(c, str):
            try:
                c = json.loads(c)
            except Exception:
                c = {"corrected_code": c}
        formatted_candidates.append(f"Candidate {i}:\n{c.get('corrected_code', '')}")

    # 构造 prompt
    prompt = f"""
You are an expert Python debugger. You are given a buggy code, a task description, and several candidate corrected versions.
You must **select the best candidate** based on logical correctness, alignment with the task, and overall code quality.

Here are the inputs:

Task description:
{task_description}

Original buggy code:
{buggy_code}


Test case (if any):
{test_case}

Candidate corrected versions:
{chr(10).join(formatted_candidates)}

Please analyze each candidate carefully, simulate mentally how it would run, and choose the one that most likely fixes the bug and fulfills the task intent.

Return your decision strictly in the following JSON format:
{{
    "best_index": 1-3,  # the chosen candidate number
    "final_corrected_code": "the full corrected code of the chosen candidate",
    "evaluation_reasoning": "detailed reasoning explaining your evaluation and why the chosen one is best"
}}
    """

    # ---- 调用大模型评估 ----
    message = [
        {'role': 'system', 'content': "You are an expert Python programmer specializing in code evaluation and selection."},
        {'role': 'user', 'content': prompt}
    ]
    response = get_completion_with_retry(message)  # 你自己的 LLM 调用接口
    try:
        result = json.loads(response)
    except Exception:
        # 如果模型输出非标准JSON，则安全fallback
        result = {
            "best_index": 1,
            "final_corrected_code": top_candidates[0].get("corrected_code", ""),
            "evaluation_reasoning": f"Failed to parse model output. Raw response: {response}"
        }

    return json.dumps(result, ensure_ascii=False, indent=2)


def chat_selfdebug(buggy_code: str, example_test: str, task_description: str, text_cfg: str = "") -> str:
    """
    自调试函数，提供更详细的CoT推理过程
    Args:
        buggy_code: 错误的代码
        example_test: 测试用例代码字符串
        task_description: 任务描述
        text_cfg: 文本形式的控制流图
    Returns:
        JSON格式的调试结果
    """
    # print(f"text_cfg in chat_selfdebug: {text_cfg}")
    # print(f"buggy_code in chat_selfdebug: {buggy_code}")
    # print(f"example_test in chat_selfdebug: {example_test}")
    # print(f"task_description in chat_selfdebug: {task_description}")
    prompt = f"""
You are an expert Python programmer and debugger. Your task is to systematically analyze buggy code using detailed Chain-of-Thought reasoning and provide a corrected version.


### Buggy Code :do not care the function name
```python
{buggy_code}
```

### Task Description
{task_description}

### Control Flow Graph (CFG)
{text_cfg if text_cfg else "No CFG provided"}

### Test Cases
```python
{example_test}
```

### Systematic Analysis Instructions

You must analyze each test case using the following 3-step process:

**Step 1: Simulate execution with test case inputs**
- Should ONLY rely on the CFG and the buggy code, DO NOT rely on the test cases and task description when executing the code.
- Start with the initial variable state from each test case input
- Execute the code following the CFG path step by step, starting from the Entry Point and ending at END (the Entry Point and END are Given in the CFG), recording detailed variable changes
- When one Block has completed its execution and is about to move to another Block, please determine based on the CFG which Block should be executed next.
- For control flow statements (if/while/for), clearly record condition evaluation results
- Format: "Step i Block n: code_content -> variable_state_changes"

**Step 2: Verify execution results**
- After completing the execution trace, compare the final output with expected output
- If outputs match exactly: "✅ Test passed"
- If outputs don't match: "❌ Test failed: actual=[actual_result] vs expected=[expected_result]"

**Step 3: Error analysis (when verification fails)**
- Identify the specific code lines where errors occurred
- Analyze the root cause: logic errors, condition errors, variable assignment errors, etc.
- Reference the task description to understand what the code should do vs what it actually does
- Provide specific suggestions for fixing the identified issues

After analyzing ALL test cases, synthesize the findings to provide a final corrected code.
When you provide the corrected code, you should not only consider the 3 steps above, but also consider the task description.

### JSON Output Format
Please output strictly in the following JSON format:
{{
    "analysis_results": [
        {{
            "testcase_id": 1,
            "input_description": "Description of test case 1 input",
            "expected_output": "Expected output result", 
            "step1_execution_trace": {{
                "reasoning": "Detailed reasoning process for step-by-step execution",
                "execution_steps": [
                    "Step 1 Block i: code_content -> variable_state",
                    "Step 2 Block j: code_content -> variable_state",
                    "..."
                ],
                "final_output": "Final output"
            }},
            "step2_verification": {{
                "status": "Test passed" or "Test failed",
                "actual_output": "Actual execution result", 
                "comparison": "Detailed comparison explanation"
            }},
            "step3_error_analysis": {{
                "has_error": true/false,
                "error_blocks": ["block numbers with errors"],
                "error_type": "error type",
                "root_cause": "Detailed explanation of the root cause",
                "fix_suggestion": "Specific fix suggestion"
            }}
        }}
    ],
    "overall_analysis": {{
        "common_patterns": "Common error patterns across test cases",
        "bug_classification": "Bug classification",
        "fix_strategy": "Overall fix strategy"
    }},
    "correctedCode_test_analysis": {{
        "corrected_code": "Final corrected code after considering all test cases",
        "test_case_consideration": "Explanation of how the corrected code addresses each test case",
        "has_passed_all_tests": true/false
    }},
    
    "explanation": "Detailed explanation of the changes made"
}}

### Quality Requirements
1. **Execution Trace Accuracy**: Strictly follow code logic and show realistic variable state changes. Make sure follow the CFG Block by Block when executing the code. DO NOT rely on the test cases and task description when executing the code.
2. **Error Analysis Depth**: Provide specific, actionable error analysis.
3. **Code Quality**: Ensure the corrected code passes all test cases. Ensure the corrected code does not have any syntax errors. Ensure the import statements are included and correct for all used modules and functions. 
4. **Reasoning Clarity**: Show clear logical reasoning throughout the analysis.
5. **JSON Compliance**: Maintain proper JSON structure.

Begin your systematic analysis now.

IMPORTANT: Keep your total response under token limit to avoid truncation. If the response is too long, you can appropriately omit the execution trace. Remember keep the response json format.
"""

    messages = [
        {'role': 'system', 'content': "You are an expert Python programmer specializing in systematic debugging using Chain-of-Thought reasoning."},
        {'role': 'user', 'content': prompt}
    ]

    try:
        response = get_completion_with_retry(messages)
        logger.info(f"selfdebug response: {response}")
        
        # 验证JSON格式
        try:
            json.loads(response)
            return response
        except json.JSONDecodeError as e:
            logger.error("="*50)
            logger.error("chat_selfdebug中JSON解析失败！详细信息如下：")
            logger.error(f"JSON错误详情: {str(e)}")
            logger.error(f"响应总长度: {len(response) if response else 0} 字符")
            logger.error(f"响应内容前500字符: {response[:500] if response else 'None'}...")
            logger.error(f"响应内容后100字符: {response[-100:] if response and len(response) > 100 else 'N/A'}...")
            logger.error("="*50)
            # 返回一个错误的JSON结构
            error_response = {
                "analysis_results": [],
                "overall_analysis": {
                    "common_patterns": "JSON parsing failed",
                    "bug_classification": "system_error",
                    "fix_strategy": "Unable to analyze"
                },
                "corrected_code": buggy_code,
                "explanation": f"JSON parsing error, returning original code: {str(e)}",
                "error": str(e)
            }
            return json.dumps(error_response, indent=2, ensure_ascii=False)
            
    except Exception as e:
        logger.error(f"selfdebug error: {e}")
        # 返回错误的JSON结构
        error_response = {
            "analysis_results": [],
            "overall_analysis": {
                "common_patterns": "System error",
                "bug_classification": "system_error", 
                "fix_strategy": "Unable to analyze"
            },
            "corrected_code": buggy_code,
            "explanation": f"Debugging process error, returning original code: {str(e)}",
            "error": str(e)
        }
        return json.dumps(error_response, indent=2, ensure_ascii=False)
    
def safe_print(message: str):
    """线程安全的打印函数"""
    with print_lock:
        print(f"[{time.strftime('%H:%M:%S')}] {message}")


def chat_selfdebug_debate(buggy_code: str, example_test: str, task_description: str, text_cfg: str = "") -> str:
    """
    自调试函数，提供更详细的CoT推理过程
    Args:
        buggy_code: 错误的代码
        example_test: 测试用例代码字符串
        task_description: 任务描述
        text_cfg: 文本形式的控制流图
    Returns:
        JSON格式的调试结果
    """
    # print(f"text_cfg in chat_selfdebug: {text_cfg}")
    # print(f"buggy_code in chat_selfdebug: {buggy_code}")
    # print(f"example_test in chat_selfdebug: {example_test}")
    # print(f"task_description in chat_selfdebug: {task_description}")
    prompt = f"""
You are an expert Python programmer and debugger. Your task is to systematically analyze buggy code using detailed Chain-of-Thought reasoning and provide a corrected version.


### Buggy Code :do not care the function name
```python
{buggy_code}
```

### Task Description
{task_description}

### Control Flow Graph (CFG)
{text_cfg if text_cfg else "No CFG provided"}

### Test Cases
```python
{example_test}
```

### Systematic Analysis Instructions

You must analyze each test case using the following 3-step process:

**Step 1: Simulate execution with test case inputs**
- Should ONLY rely on the CFG and the buggy code, DO NOT rely on the test cases and task description when executing the code.
- Start with the initial variable state from each test case input
- Execute the code following the CFG path step by step, starting from the Entry Point and ending at END (the Entry Point and END are Given in the CFG), recording detailed variable changes
- When one Block has completed its execution and is about to move to another Block, please determine based on the CFG which Block should be executed next.
- For control flow statements (if/while/for), clearly record condition evaluation results
- Format: "Step i Block n: code_content -> variable_state_changes"

**Step 2: Verify execution results**
- After completing the execution trace, compare the final output with expected output
- If outputs match exactly: "✅ Test passed"
- If outputs don't match: "❌ Test failed: actual=[actual_result] vs expected=[expected_result]"

**Step 3: Error analysis (when verification fails)**
- Identify the specific code lines where errors occurred
- Analyze the root cause: logic errors, condition errors, variable assignment errors, etc.
- Reference the task description to understand what the code should do vs what it actually does
- Provide specific suggestions for fixing the identified issues

After analyzing ALL test cases, synthesize the findings to provide a final corrected code.
When you provide the corrected code, you should not only consider the 3 steps above, but also consider the task description.

### JSON Output Format
Please output strictly in the following JSON format:
{{
    "analysis_results": [
        {{
            "testcase_id": 1,
            "input_description": "Description of test case 1 input",
            "expected_output": "Expected output result", 
            "step1_execution_trace": {{
                "reasoning": "Detailed reasoning process for step-by-step execution",
                "execution_steps": [
                    "Step 1 Block i: code_content -> variable_state",
                    "Step 2 Block j: code_content -> variable_state",
                    "..."
                ],
                "final_output": "Final output"
            }},
            "step2_verification": {{
                "status": "Test passed" or "Test failed",
                "actual_output": "Actual execution result", 
                "comparison": "Detailed comparison explanation"
            }},
            "step3_error_analysis": {{
                "has_error": true/false,
                "error_blocks": ["block numbers with errors"],
                "error_type": "error type",
                "root_cause": "Detailed explanation of the root cause",
                "fix_suggestion": "Specific fix suggestion"
            }}
        }}
    ],
    "overall_analysis": {{
        "common_patterns": "Common error patterns across test cases",
        "bug_classification": "Bug classification",
        "fix_strategy": "Overall fix strategy"
    }},
    "correctedCode_test_analysis": {{
        "corrected_code": "Final corrected code after considering all test cases",
        "test_case_consideration": "Explanation of how the corrected code addresses each test case",
        "test_cases": [
           { {
                "input": "Input for test case 1",
                "expected_output": "Expected output for test case 1",
                "actual_output": "Actual output for test case 1",
                "status": "pass or fail"
            }},
            {{
                "input": "Input for test case 2",
                "expected_output": "Expected output for test case 2",
                "actual_output": "Actual output for test case 2",
                "status": "pass or fail"
            }}
        ],
        "has_passed_all_tests": true/false
    }},
    
    "explanation": "Detailed explanation of the changes made"
}}

### Quality Requirements
1. **Execution Trace Accuracy**: Strictly follow code logic and show realistic variable state changes. Make sure follow the CFG Block by Block when executing the code. DO NOT rely on the test cases and task description when executing the code.
2. **Error Analysis Depth**: Provide specific, actionable error analysis.
3. **Code Quality**: Ensure the corrected code passes all test cases. Ensure the corrected code does not have any syntax errors. Ensure the import statements are included and correct for all used modules and functions. 
4. **Reasoning Clarity**: Show clear logical reasoning throughout the analysis.
5. **JSON Compliance**: Maintain proper JSON structure.

Begin your systematic analysis now.

IMPORTANT: Keep your total response under token limit to avoid truncation. If the response is too long, you can appropriately omit the execution trace. Remember keep the response json format.
"""

    messages = [
        {'role': 'system', 'content': "You are an expert Python programmer specializing in systematic debugging using Chain-of-Thought reasoning."},
        {'role': 'user', 'content': prompt}
    ]

    try:
        response = get_completion_with_retry(messages)
        logger.info(f"selfdebug response: {response}")
        
        # 验证JSON格式
        try:
            json.loads(response)
            return response
        except json.JSONDecodeError as e:
            logger.error("="*50)
            logger.error("chat_selfdebug中JSON解析失败！详细信息如下：")
            logger.error(f"JSON错误详情: {str(e)}")
            logger.error(f"响应总长度: {len(response) if response else 0} 字符")
            logger.error(f"响应内容前500字符: {response[:500] if response else 'None'}...")
            logger.error(f"响应内容后100字符: {response[-100:] if response and len(response) > 100 else 'N/A'}...")
            logger.error("="*50)
            # 返回一个错误的JSON结构
            error_response = {
                "analysis_results": [],
                "overall_analysis": {
                    "common_patterns": "JSON parsing failed",
                    "bug_classification": "system_error",
                    "fix_strategy": "Unable to analyze"
                },
                "corrected_code": buggy_code,
                "explanation": f"JSON parsing error, returning original code: {str(e)}",
                "error": str(e)
            }
            return json.dumps(error_response, indent=2, ensure_ascii=False)
            
    except Exception as e:
        logger.error(f"selfdebug error: {e}")
        # 返回错误的JSON结构
        error_response = {
            "analysis_results": [],
            "overall_analysis": {
                "common_patterns": "System error",
                "bug_classification": "system_error", 
                "fix_strategy": "Unable to analyze"
            },
            "corrected_code": buggy_code,
            "explanation": f"Debugging process error, returning original code: {str(e)}",
            "error": str(e)
        }
        return json.dumps(error_response, indent=2, ensure_ascii=False)
    
    
def conduct_debate(agent_results: List[AgentDebugResult], 
                   task_description: str,
                   test_cases: List[str],
                   buggy_code: str,
                   max_rounds: int = 3) -> Tuple[str, List[DebateRound]]:
    """
    组织多个Agent进行辩论,达成共识
    Args:
        agent_results: 各个Agent的初始调试结果
        task_description: 任务描述
        test_cases: 测试用例
        buggy_code: 原始错误代码
        max_rounds: 最大辩论轮数
    Returns:
        (最终代码, 辩论历史)
    """
    debate_rounds = []
    
    # 过滤出成功的Agent结果
    successful_agents = [r for r in agent_results if r.success]
    
    if not successful_agents:
        safe_print("[Debate] No successful agent results to debate")
        return buggy_code, debate_rounds
    
    if len(successful_agents) == 1:
        safe_print("[Debate] Only one successful agent, no debate needed")
        return successful_agents[0].corrected_code, debate_rounds
    
    safe_print(f"[Debate] Starting debate with {len(successful_agents)} agents for {max_rounds} rounds")
    
    current_proposals = {r.agent_id: r.corrected_code for r in successful_agents}
    
    for round_num in range(1, max_rounds + 1):
        safe_print(f"[Debate] Round {round_num}/{max_rounds}")
        
        # 准备辩论提示
        proposals_text = ""
        for agent_result in successful_agents:
            proposals_text += f"""
### Agent {agent_result.agent_id} Proposal (Confidence: {agent_result.confidence_score:.2f})
**Reasoning:** {agent_result.reasoning}
**Code:**
```python
{agent_result.corrected_code}
```
"""
        
        debate_prompt = f"""
You are participating in a multi-agent debate to determine the best fix for a buggy Python function.

### Task Description
{task_description}

### Original Buggy Code
```python
{buggy_code}
```

### Test Cases
{chr(10).join(test_cases)}

### Current Proposals from {len(successful_agents)} Agents
{proposals_text}

### Your Task
1. Analyze all proposals and identify:
   - Common fixes across proposals
   - Conflicting approaches
   - Potential issues in each proposal
2. Provide constructive criticism for each proposal
3. Suggest a consensus solution that combines the best aspects

### JSON Output Format
{{
    "analysis": {{
        "common_fixes": "What fixes appear in multiple proposals",
        "conflicts": "Where proposals differ significantly",
        "strengths": {{"agent_id": "strength"}},
        "weaknesses": {{"agent_id": "weakness"}}
    }},
    "consensus_code": "The best combined solution",
    "explanation": "Why this consensus is better than individual proposals"
}}
"""
                
        try:
            messages = [
                {'role': 'system', 'content': 'You are an expert code reviewer facilitating a multi-agent debate.'},
                {'role': 'user', 'content': debate_prompt}
            ]
            
            response = get_completion_with_retry(messages)
            debate_result = json.loads(response)
            
            consensus_code = debate_result.get("consensus_code", "")
            analysis = debate_result.get("analysis", {})
            
            # 记录本轮辩论
            agent_arguments = []
            for agent_result in successful_agents:
                agent_arguments.append({
                    'agent_id': agent_result.agent_id,
                    'proposal': agent_result.corrected_code,
                    'reasoning': agent_result.reasoning,
                    'confidence': agent_result.confidence_score
                })
            
            debate_round = DebateRound(
                round_number=round_num,
                agent_arguments=agent_arguments,
                consensus_code=consensus_code,
                disagreement_points=analysis.get("conflicts", "").split('\n') if analysis.get("conflicts") else []
            )
            
            debate_rounds.append(debate_round)
            
            safe_print(f"[Debate] Round {round_num} completed, consensus reached")
            
            # 如果达成高度共识,提前结束
            if len(analysis.get("conflicts", "")) < 50:  # 冲突描述很短
                safe_print(f"[Debate] High consensus achieved, ending debate early")
                return consensus_code, debate_rounds
            
            # 更新proposals为当前共识
            current_proposals = {0: consensus_code}
            
        except Exception as e:
            safe_print(f"[Debate] Round {round_num} error: {str(e)[:100]}")
            # 如果辩论失败,返回置信度最高的Agent结果
            best_agent = max(successful_agents, key=lambda x: x.confidence_score)
            return best_agent.corrected_code, debate_rounds
    
    # 所有轮次结束,返回最后的共识
    if debate_rounds and debate_rounds[-1].consensus_code:
        return debate_rounds[-1].consensus_code, debate_rounds
    else:
        # 回退到最佳Agent结果
        best_agent = max(successful_agents, key=lambda x: x.confidence_score)
        return best_agent.corrected_code, debate_rounds

def chat_java_fragment_debug(buggy_code: str, error_message: str, test_case: str, cfg_text: str = "") -> str:
    """
    专门用于Java代码片段调试的函数，基于静态分析而非逐行执行
    
    Args:
        buggy_code: 有问题的Java代码片段
        error_message: 错误信息
        test_case: 测试用例
        cfg_text: 控制流图文本
    
    Returns:
        JSON格式的调试结果
    """
    
    system_prompt = "You are a professional Java code debugging expert. You need to analyze bugs in code fragments and provide fix solutions."

    user_prompt = f"""Please analyze the bug in the following Java code fragment step by step following the CFG and give the fix solution.

**Code Fragment**:
```java
{buggy_code}
```

**Error Message**:
{error_message}

**Test Case**:
{test_case}

**Control Flow Graph**: 
{cfg_text}

Please return results in JSON format with the following fields:
{{
    "analysis step by step": {{
        ...
    }},
    "error_analysis": {{    
        "error_type": "Error type analysis",
        "error_location": "Location where error occurs",
        "trigger_condition": "Condition that triggers the error"
    }},  
    "corrected_code": "Complete corrected code",
    "explanation": "Explanation of the fix principle",
    "fix_method": "Method used to fix the bug",
    "code_change_summary": "Summary of the code changes"
}}
"""

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        error_response = {
            "analysis": {
                "analysis_failed": f"Analysis process failed: {str(e)}",
            },
            "error_analysis": {
                "error_type": "system_error",
                "error_location": "analysis_function",
                "trigger_condition": "api_call_failed"
            },
            "corrected_code": buggy_code,
            "explanation": f"Automatic analysis failed: {str(e)}"
        }
        return json.dumps(error_response, ensure_ascii=False)


def generate_java_cfg_with_llm(java_code: str, method_name: str = None, class_name: str = None) -> str:
    """
    使用LLM直接生成Java代码的控制流图
    
    Args:
        java_code: Java源代码
        method_name: 需要分析的方法名称（可选）
        class_name: 需要分析的类名（可选）
    
    Returns:
        控制流图的文本表示
    """
    
    system_prompt = "You are an expert in program analysis, specialized in generating control flow graphs for Java code."
    
    # 添加few-shot示例，展示输出格式
    example_code = '''
    class TempClass {

static Document parseByteData(ByteBuffer byteData, String charsetName, String baseUri, Parser parser) {
    String docData;
    Document doc = null;
    if (charsetName == null) { 
        docData = Charset.forName(defaultCharset).decode(byteData).toString();
        doc = parser.parseInput(docData, baseUri);
        Element meta = doc.select("meta[http-equiv=content-type], meta[charset]").first();
        if (meta != null) { 
            String foundCharset;
            if (meta.hasAttr("http-equiv")) {
                foundCharset = getCharsetFromContentType(meta.attr("content"));
                if (foundCharset == null && meta.hasAttr("charset")) {
                    try {
                        if (Charset.isSupported(meta.attr("charset"))) {
                            foundCharset = meta.attr("charset");
                        }
                    } catch (IllegalCharsetNameException e) {
                        foundCharset = null;
                    }
                }
            } else {
                foundCharset = meta.attr("charset");
            }

            if (foundCharset != null && foundCharset.length() != 0 && !foundCharset.equals(defaultCharset)) { 
                foundCharset = foundCharset.trim().replaceAll("[]", "");
                charsetName = foundCharset;
                byteData.rewind();
                docData = Charset.forName(foundCharset).decode(byteData).toString();
                doc = null;
            }
        }
    } else { 
        Validate.notEmpty(charsetName, "Must set charset arg to character set of file to parse. Set to null to attempt to detect from HTML");
        docData = Charset.forName(charsetName).decode(byteData).toString();
    }
    if (docData.length() > 0 && docData.charAt(0) == 65279) {
        byteData.rewind();
        docData = Charset.forName(defaultCharset).decode(byteData).toString();
        docData = docData.substring(1);
        charsetName = defaultCharset;
    }
    if (doc == null) {
        doc = parser.parseInput(docData, baseUri);
        doc.outputSettings().charset(charsetName);
    }
    return doc;
}

}
    '''
    
    example_output = '''
    CFG text: G describes a control flow graph of Method `TempClass.parseByteData()`
    In this graph:
    Entry Point: Block 0 represents code snippet: String docData;.
    END Block: Block 33 represents code snippet: END.
    Block 0 represents code snippet: String docData;.
    Block 1 represents code snippet: Document doc = null;.
    Block 2 represents code snippet: if (charsetName == null) {.
    Block 3 represents code snippet: docData = Charset.forName(defaultCharset).decode(byteData).toString();.
    Block 4 represents code snippet: doc = parser.parseInput(docData, baseUri);.
    Block 5 represents code snippet: Element meta = doc.select("meta[http-equiv=content-type], meta[charset]").first();.
    Block 6 represents code snippet: if (meta != null) {.
    Block 7 represents code snippet: String foundCharset;.
    Block 8 represents code snippet: if (meta.hasAttr("http-equiv")) {.
    Block 9 represents code snippet: foundCharset = getCharsetFromContentType(meta.attr("content"));.
    Block 10 represents code snippet: if (foundCharset == null && meta.hasAttr("charset")) {.
    Block 11 represents code snippet: if (Charset.isSupported(meta.attr("charset"))) {.
    Block 12 represents code snippet: foundCharset = meta.attr("charset");.
    Block 13 represents code snippet: } catch (IllegalCharsetNameException e) {.
    Block 14 represents code snippet: foundCharset = null;.
    Block 15 represents code snippet: foundCharset = meta.attr("charset");.
    Block 16 represents code snippet: if (foundCharset != null && foundCharset.length() != 0 && !foundCharset.equals(defaultCharset)) {.
    Block 17 represents code snippet: foundCharset = foundCharset.trim().replaceAll("[]", "");.
    Block 18 represents code snippet: charsetName = foundCharset;.
    Block 19 represents code snippet: byteData.rewind();.
    Block 20 represents code snippet: docData = Charset.forName(foundCharset).decode(byteData).toString();.
    Block 21 represents code snippet: doc = null;.
    Block 22 represents code snippet: Validate.notEmpty(charsetName, "Must set charset arg to character set of file to parse. Set to null to attempt to detect from HTML");.
    Block 23 represents code snippet: docData = Charset.forName(charsetName).decode(byteData).toString();.
    Block 24 represents code snippet: if (docData.length() > 0 && docData.charAt(0) == 65279) {.
    Block 25 represents code snippet: byteData.rewind();.
    Block 26 represents code snippet: docData = Charset.forName(defaultCharset).decode(byteData).toString();.
    Block 27 represents code snippet: docData = docData.substring(1);.
    Block 28 represents code snippet: charsetName = defaultCharset;.
    Block 29 represents code snippet: if (doc == null) {.
    Block 30 represents code snippet: doc = parser.parseInput(docData, baseUri);.
    Block 31 represents code snippet: doc.outputSettings().charset(charsetName);.
    Block 32 represents code snippet: return doc;.
    Block 33 represents code snippet: END.
    Block 0 unconditional points to Block 1.
    Block 1 unconditional points to Block 2.
    Block 2 match case "charsetName == null" points to Block 3.
    Block 2 not match case "charsetName == null" points to Block 22.
    Block 3 unconditional points to Block 4.
    Block 4 unconditional points to Block 5.
    Block 5 unconditional points to Block 6.
    Block 6 match case "meta != null" points to Block 7.
    Block 6 not match case "meta != null" points to Block 24.
    Block 7 unconditional points to Block 8.
    Block 8 match case "meta.hasAttr("http-equiv")" points to Block 9.
    Block 8 not match case "meta.hasAttr("http-equiv")" points to Block 15.
    Block 9 unconditional points to Block 10.
    Block 10 match case "foundCharset == null && meta.hasAttr("charset")" points to Block 11.
    Block 10 not match case "foundCharset == null && meta.hasAttr("charset")" points to Block 16.
    Block 11 match case "Charset.isSupported(meta.attr("charset"))" points to Block 12.
    Block 11 exception points to Block 13.
    Block 11 not match case "Charset.isSupported(meta.attr("charset"))" points to Block 16.
    Block 12 exception points to Block 13.
    Block 12 unconditional points to Block 16.
    Block 13 unconditional points to Block 14.
    Block 14 unconditional points to Block 16.
    Block 15 unconditional points to Block 16.
    Block 16 match case "foundCharset != null && foundCharset.length() != 0 && !foundCharset.equals(defaultCharset)" points to Block 17.
    Block 16 not match case "foundCharset != null && foundCharset.length() != 0 && !foundCharset.equals(defaultCharset)" points to Block 24.
    Block 17 unconditional points to Block 18.
    Block 18 unconditional points to Block 19.
    Block 19 unconditional points to Block 20.
    Block 20 unconditional points to Block 21.
    Block 21 unconditional points to Block 22.
    Block 22 unconditional points to Block 23.
    Block 23 unconditional points to Block 24.
    Block 24 match case "docData.length() > 0 && docData.charAt(0) == 65279" points to Block 25.
    Block 24 not match case "docData.length() > 0 && docData.charAt(0) == 65279" points to Block 29.
    Block 25 unconditional points to Block 26.
    Block 26 unconditional points to Block 27.
    Block 27 unconditional points to Block 28.
    Block 28 unconditional points to Block 29.
    Block 29 match case "doc == null" points to Block 30.
    Block 29 not match case "doc == null" points to Block 32.
    Block 30 unconditional points to Block 31.
    Block 31 unconditional points to Block 32.
    Block 32 unconditional points to Block 33.
    '''
    
    user_prompt = f"""Analyze the following Java code to understand the execution flow of the code and generate a control flow graph (CFG).
{f"Entry Class name: {class_name}" if class_name else ""}
{f"Entry Method name: {method_name}" if method_name else ""}

```java
{java_code}
```

Generate a control flow graph with the following format:
1. Every block should be a meaningful atomic operation that can be executed, including declarations, assignments, conditional statements, and all statements that will lead to side effects.
2. Some signs are meaningless but they are in a line by themselves, you should ignore them and not consider them as a block.
3. Each block should be numbered starting from 0.
4. Include connections between blocks with appropriate types.

Here is an example of how to format the CFG output:

Example Code:
```java
{example_code}
```

Example CFG Output:
```
{example_output}
```

Now generate the CFG for the provided code with the same format. If a specific method is specified, only generate the CFG for that method.
"""
    
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,  # Use a capable model for program analysis
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for deterministic output
            timeout=180.0,  # Give it time to analyze complex code
        )
        cfg_text = response.choices[0].message.content.strip()
        logger.info(f"Generated Java CFG with LLM, output length: {len(cfg_text)} chars")
        return cfg_text
    except Exception as e:
        logger.error(f"Failed to generate Java CFG with LLM: {str(e)}")
        return f"Error generating CFG: {str(e)}"
