# -*- coding: utf-8 -*-
"""多账号并发运行器：同时跑多个学习通账号的「章节任务」和「作业」。

每个账号有独立工作目录 runs/<name>/，互不干扰：
    runs/<name>/config.ini      题库配置副本
    runs/<name>/resource/       字体映射表副本
    runs/<name>/cache.json      答题缓存
    runs/<name>/chaoxing.log    日志
    runs/<name>/未通过测验记录.md
    runs/<name>/run.log         本启动器记录的输出

用法：
    python multi_run.py --dry-run          # 只打印将要执行的命令
    python multi_run.py                    # 全量执行
    python multi_run.py --accounts a.json  # 指定账号文件

accounts.json 格式：
[
  {
    "name": "alice",
    "username": "18000000000",
    "password": "xxx",
    "courses": ["268741619"],
    "mode": "both",
    "speed": 2,
    "jobs": 2,
    "redo_finished": false,
    "no_cache": true,
    "homework_submit": true,
    "homework_limit": 0,
    "homework_enc": {"268741619": "<课程enc>"}
  }
]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(ROOT, "runs")


def parse_args():
    p = argparse.ArgumentParser(description="多账号并发运行")
    p.add_argument("--accounts", default="accounts.json", help="账号配置文件")
    p.add_argument("--dry-run", action="store_true", help="只打印命令不执行")
    p.add_argument("--only", help="只跑指定 name 的账号")
    return p.parse_args()


def load_accounts(path):
    if not os.path.exists(path):
        raise SystemExit(f"找不到账号文件 {path}，可先复制 accounts.example.json")
    with open(path, encoding="utf8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("accounts", [])
    if not isinstance(data, list) or not data:
        raise SystemExit("账号文件格式不对：应为数组，或 {\"accounts\": [...]}")
    return data


def safe_name(s):
    keep = [c for c in str(s) if c.isalnum() or c in "-_."]
    return "".join(keep) or "account"


def prepare_dir(acc):
    name = safe_name(acc.get("name") or acc["username"])
    d = os.path.join(RUNS, name)
    os.makedirs(d, exist_ok=True)

    cfg = os.path.join(ROOT, "config.ini")
    if os.path.exists(cfg):
        shutil.copy2(cfg, os.path.join(d, "config.ini"))

    res_src = os.path.join(ROOT, "resource")
    res_dst = os.path.join(d, "resource")
    if os.path.isdir(res_src) and not os.path.isdir(res_dst):
        shutil.copytree(res_src, res_dst)

    # 每个账号自己的课程 enc 缓存
    enc_map = acc.get("homework_enc") or {}
    enc_file = os.path.join(d, ".homework_enc.json")
    try:
        if enc_map:
            json.dump({str(k): v for k, v in enc_map.items()}, open(enc_file, "w", encoding="utf8"))
        elif os.path.exists(os.path.join(ROOT, ".homework_enc.json")):
            shutil.copy2(os.path.join(ROOT, ".homework_enc.json"), enc_file)
    except Exception:
        pass
    return d


def chapter_cmd(acc):
    cmd = [sys.executable, os.path.join(ROOT, "main.py"),
           "-u", acc["username"], "-p", acc["password"],
           "-s", str(acc.get("speed", 2)), "-j", str(acc.get("jobs", 2))]
    courses = acc.get("courses") or []
    if courses:
        cmd += ["-l", ",".join(str(c) for c in courses)]
    if acc.get("redo_finished"):
        cmd.append("--redo-finished")
    if acc.get("no_cache"):
        cmd.append("--no-cache")
    return cmd


def homework_cmd(acc, course):
    cmd = [sys.executable, os.path.join(ROOT, "do_homework.py"),
           "-u", acc["username"], "-p", acc["password"],
           "--all", "--course", str(course)]
    if acc.get("no_cache"):
        cmd.append("--no-cache")
    seed = acc.get("homework_seed")
    if seed:
        cmd += ["--seed", str(seed)]
    if acc.get("list_only"):
        cmd.append("--list-only")
    if acc.get("homework_submit"):
        cmd.append("--submit")
    if acc.get("homework_limit"):
        cmd += ["--limit", str(acc["homework_limit"])]
    return cmd


def steps_for(acc):
    mode = acc.get("mode", "both")
    steps = []
    if mode in ("chapters", "both"):
        steps.append(("chapters", chapter_cmd(acc)))
    if mode in ("homework", "both"):
        for c in acc.get("courses") or []:
            cmd = homework_cmd(acc, c)
            enc = (acc.get("homework_enc") or {}).get(str(c))
            if enc:
                cmd += ["--enc", str(enc)]
            steps.append((f"homework:{c}", cmd))
    return steps


def run_one(acc, dry_run=False):
    name = safe_name(acc.get("name") or acc["username"])
    d = prepare_dir(acc) if not dry_run else os.path.join(RUNS, name)
    steps = steps_for(acc)
    results = []
    print(f"[{name}] 开始（{len(steps)} 步）")
    if dry_run:
        for label, cmd in steps:
            print(f"[{name}] {label}: {' '.join(cmd)}  (cwd={d})")
        return name, results

    delay = float(acc.get("start_delay") or 0)
    if delay > 0:
        print(f"[{name}] 错开 {delay:.0f}s 后启动")
        time.sleep(delay)

    log_path = os.path.join(d, "run.log")
    with open(log_path, "a", encoding="utf8") as log:
        log.write(f"\n===== {time.strftime('%Y-%m-%d %H:%M:%S')} | {acc.get('name')} | {acc['username']} =====\n")
        for label, cmd in steps:
            log.write(f"\n--- {label} ---\n")
            log.flush()
            t0 = time.time()
            p = subprocess.run(cmd, cwd=d, stdout=log, stderr=subprocess.STDOUT,
                               env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
            cost = time.time() - t0
            log.write(f"\n[{label}] exit={p.returncode} cost={cost:.0f}s\n")
            log.flush()
            results.append((label, p.returncode, cost))
            print(f"[{name}] {label} 结束 exit={p.returncode} 用时 {cost:.0f}s")
    return name, results


def main():
    args = parse_args()
    accounts = load_accounts(os.path.join(ROOT, args.accounts) if not os.path.isabs(args.accounts) else args.accounts)
    accounts = [a for a in accounts if a.get("enabled", True)]
    if args.only:
        want = {x.strip() for x in args.only.split(",") if x.strip()}
        accounts = [a for a in accounts if safe_name(a.get("name") or a["username"]) in want]
    if not accounts:
        raise SystemExit("没有要运行的账号")

    print(f"共 {len(accounts)} 个账号，并发执行（每账号独立目录 runs/<name>/）")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=len(accounts)) as pool:
        futures = [pool.submit(run_one, a, args.dry_run) for a in accounts]
        summary = [f.result() for f in futures]

    if not args.dry_run:
        print("\n===== 汇总 =====")
        lines = ["# 多账号运行汇总", "", f"生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}", ""]
        for name, results in summary:
            ok = all(rc == 0 for _, rc, _ in results)
            print(f"- {name}: {'全部步骤成功' if ok else '有失败步骤'}")
            lines.append(f"## {name}")
            lines.append("")
            lines.append(f"- 结果：{'全部成功' if ok else '有失败'}")
            for label, rc, cost in results:
                lines.append(f"- {label}: exit={rc}, {cost:.0f}s")
            lines.append("")
        with open(os.path.join(RUNS, "summary.md"), "w", encoding="utf8") as f:
            f.write("\n".join(lines))
        print(f"总耗时 {time.time() - t0:.0f}s，明细见 runs/summary.md")


if __name__ == "__main__":
    main()
