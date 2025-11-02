from splitCode import ExpressionFlattener
import json

if __name__ == "__main__":
    # 示例用法
    with open("dataset_test/humanevalfix/humanevalpack.jsonl", "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            data = json.loads(line.strip())
            full_code = data['declaration'] + data['buggy_solution']
            with open(f"testExtract/buggy_code_{i}.py", 'w', encoding='utf-8') as f:
                f.write(full_code)
                f.write("\n")
                f.write("\n")
            fl = ExpressionFlattener()
            full_code = fl.flatten_code(full_code)
            with open(f"testExtract/buggy_code_{i}.py", 'a', encoding='utf-8') as f:
                f.write(full_code)


# import ast
# import inspect
# import importlib.util
# import os
# import random
# import string
# import multiprocessing as mp
# from types import ModuleType

# TEST_DIR = r"d:\DeskTop\课程资料\2025-fall\课程设计\SimulateExe_SelfDebug\testExtract"
# TIMEOUT = 2  # 秒
# TRIALS = 20  # 每对函数测试样例数

# def extract_top_level_imports_and_funcs(source):
#     tree = ast.parse(source)
#     imports_src = []
#     funcs = []
#     for node in tree.body:
#         if isinstance(node, (ast.Import, ast.ImportFrom)):
#             imports_src.append(ast.get_source_segment(source, node))
#         elif isinstance(node, ast.FunctionDef):
#             funcs.append(node)
#     return imports_src, funcs

# def build_namespace(imports_src, func_node, source):
#     ns = {}
#     # exec imports first
#     try:
#         for im in imports_src:
#             exec(im, ns)
#     except Exception:
#         pass
#     # get function source
#     func_src = ast.get_source_segment(source, func_node)
#     exec(func_src, ns)
#     return ns

# def make_sample_value(param_name, ann):
#     # simple heuristics
#     if ann:
#         a = getattr(ann, "__name__", str(ann))
#         if "int" in a: return random.randint(-5, 10)
#         if "float" in a: return random.uniform(-5, 10)
#         if "str" in a: return "".join(random.choices(string.ascii_letters + " ", k=5))
#         if "bool" in a: return random.choice([True, False])
#         if "list" in a or "List" in a: return [random.randint(0, 5) for _ in range(random.randint(0,4))]
#     # by name heuristics
#     name = param_name.lower()
#     if name in ("s", "st", "txt", "text"): return "".join(random.choices(string.ascii_letters, k=4))
#     if name in ("threshold", "t"): return random.uniform(0, 5)
#     if name in ("numbers","xs","arr","lst","items","x"): return [random.randint(0,9) for _ in range(random.randint(0,5))]
#     if name in ("n","i","j","k","count"): return random.randint(0,10)
#     # fallback
#     return random.randint(-3, 7)

# def call_with_timeout(func, args, kwargs, timeout=TIMEOUT):
#     def worker(q, func, args, kwargs):
#         try:
#             res = func(*args, **kwargs)
#             q.put(("OK", res))
#         except Exception as e:
#             q.put(("EXC", repr(e)))
#     q = mp.Queue()
#     p = mp.Process(target=worker, args=(q, func, args, kwargs))
#     p.start()
#     p.join(timeout)
#     if p.is_alive():
#         p.terminate()
#         return ("TIMEOUT", None)
#     if q.empty():
#         return ("NO_RESULT", None)
#     return q.get()

# def normalize_result(tagres):
#     tag, val = tagres
#     if tag == "OK":
#         try:
#             # try to make comparable (immutable)
#             return ("OK", val)
#         except Exception:
#             return ("OK_REPR", repr(val))
#     else:
#         return (tag, val)

# def compare_pair(ns1, ns2, fname):
#     f1 = ns1.get(fname)
#     f2 = ns2.get(fname)
#     if not callable(f1) or not callable(f2):
#         return False, f"缺少函数: one callable: {callable(f1)} {callable(f2)}"
#     sig = inspect.signature(f1)
#     # build trials
#     mismatches = []
#     for t in range(TRIALS):
#         args = []
#         kwargs = {}
#         for pname, param in sig.parameters.items():
#             if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
#                 # skip varargs for now
#                 continue
#             if param.default is not inspect._empty:
#                 # sometimes use default; randomly decide
#                 if random.random() < 0.3:
#                     continue
#             ann = None
#             try:
#                 ann = param.annotation if param.annotation is not inspect._empty else None
#             except Exception:
#                 ann = None
#             val = make_sample_value(pname, ann)
#             args.append(val)
#         # run both in separate namespaces (they don't share global state here)
#         r1 = call_with_timeout(f1, args, kwargs)
#         r2 = call_with_timeout(f2, args, kwargs)
#         n1 = normalize_result(r1)
#         n2 = normalize_result(r2)
#         if n1 != n2:
#             mismatches.append((args, n1, n2))
#             # record first few mismatches
#             if len(mismatches) >= 5:
#                 break
#     if mismatches:
#         return False, mismatches
#     return True, None

# def process_file(path):
#     source = open(path, encoding="utf-8").read()
#     imports_src, funcs = extract_top_level_imports_and_funcs(source)
#     # group functions by name (keep order)
#     by_name = {}
#     for f in funcs:
#         by_name.setdefault(f.name, []).append(f)
#     results = {}
#     for name, flist in by_name.items():
#         if len(flist) < 2:
#             continue
#         # take first two definitions
#         fnode1, fnode2 = flist[0], flist[1]
#         ns1 = build_namespace(imports_src, fnode1, source)
#         ns2 = build_namespace(imports_src, fnode2, source)
#         ok, detail = compare_pair(ns1, ns2, name)
#         results[name] = (ok, detail)
#     return results


# if __name__ == "__main__":
#     print(f"Processing files in {TEST_DIR}...\n")
#     files = sorted([os.path.join(TEST_DIR, fn) for fn in os.listdir(TEST_DIR) if fn.endswith(".py")])
#     summary = {}
#     for f in files:
#         try:
#             res = process_file(f)
#             summary[f] = res
#             print(f"[OK] {os.path.basename(f)} -> {res}")
#         except Exception as e:
#             summary[f] = ("ERROR", repr(e))
#             print(f"[ERR] {os.path.basename(f)} -> {repr(e)}")
#     # 简单汇总输出
#     bad = {k:v for k,v in summary.items() if v and any(not r[0] for r in (v.values() if isinstance(v, dict) else []))}
#     print("\nSummary: files with non-equivalent functions or errors:")
#     for k,v in bad.items():
#         print(k, "->", v)
#     print("\n完成。请查看详细输出。")