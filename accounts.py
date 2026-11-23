# -*- coding: utf-8 -*-
"""多账号配置的命令行工具：添加 / 列表 / 启停 / 指定运行 / 设置作业 enc。

用法示例：
    python accounts.py add alice -u 18000000000 -c 268741619,268741620 --mode chapters
    python accounts.py list
    python accounts.py on alice / off alice
    python accounts.py run                     # 跑所有启用的账号
    python accounts.py run alice               # 只跑 alice（切换）
    python accounts.py run alice,bob --dry-run
    python accounts.py remove alice
    python accounts.py enc alice 268741619 <enc>
    python accounts.py seed alice <作业链接>
"""
import argparse
import getpass
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE = os.path.join(ROOT, "accounts.json")


def load(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("accounts", [])
    return data or []


def save(path, accounts):
    with open(path, "w", encoding="utf8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)


def find(accounts, name):
    for a in accounts:
        if a.get("name") == name:
            return a
    return None


def parse_courses(text):
    return [c.strip() for c in str(text).split(",") if c.strip()]


def cmd_add(accounts, args):
    if find(accounts, args.name):
        print(f"账号 {args.name} 已存在，用 edit 或先 remove")
        return 1
    pwd = args.password or getpass.getpass("密码（回车确认，不会显示）: ")
    entry = {
        "name": args.name,
        "username": args.username,
        "password": pwd,
        "courses": parse_courses(args.courses),
        "mode": args.mode,
        "speed": args.speed,
        "jobs": args.jobs,
        "enabled": True,
    }
    if args.no_cache:
        entry["no_cache"] = True
    if args.redo_finished:
        entry["redo_finished"] = True
    if args.homework_submit:
        entry["homework_submit"] = True
    if args.start_delay:
        entry["start_delay"] = args.start_delay
    if args.seed:
        entry["homework_seed"] = args.seed
    accounts.append(entry)
    save(args.file, accounts)
    print(f"已添加 {args.name}（{args.username}，{len(entry['courses'])} 门课程，mode={args.mode}）")
    return 0


def cmd_list(accounts, args):
    if not accounts:
        print("还没有账号，用 add 添加")
        return 0
    print(f"{'名称':<14}{'状态':<6}{'账号':<14}{'模式':<10}{'课程':<28}附加")
    for a in accounts:
        state = "启用" if a.get("enabled", True) else "停用"
        courses = ",".join(a.get("courses") or [])[:26]
        extra = []
        if a.get("no_cache"):
            extra.append("no-cache")
        if a.get("homework_submit"):
            extra.append("作业提交")
        if a.get("homework_enc"):
            extra.append(f"enc:{len(a['homework_enc'])}")
        if a.get("homework_seed"):
            extra.append("seed")
        print(f"{a.get('name',''):<14}{state:<6}{a.get('username',''):<14}"
              f"{a.get('mode','both'):<10}{courses:<28}{' '.join(extra)}")
    return 0


def cmd_show(accounts, args):
    a = find(accounts, args.name)
    if not a:
        print("没有这个账号")
        return 1
    safe = dict(a)
    if safe.get("password"):
        safe["password"] = "***"
    print(json.dumps(safe, ensure_ascii=False, indent=2))
    return 0


def cmd_remove(accounts, args):
    a = find(accounts, args.name)
    if not a:
        print("没有这个账号")
        return 1
    if not args.yes:
        if input(f"确认删除 {args.name}? [y/N] ").lower() != "y":
            print("已取消")
            return 0
    accounts.remove(a)
    save(args.file, accounts)
    print(f"已删除 {args.name}")
    return 0


def cmd_toggle(accounts, args, enabled):
    a = find(accounts, args.name)
    if not a:
        print("没有这个账号")
        return 1
    a["enabled"] = enabled
    save(args.file, accounts)
    print(f"{args.name} -> {'启用' if enabled else '停用'}")
    return 0


def cmd_edit(accounts, args):
    a = find(accounts, args.name)
    if not a:
        print("没有这个账号")
        return 1
    if args.courses:
        a["courses"] = parse_courses(args.courses)
    if args.mode:
        a["mode"] = args.mode
    if args.speed is not None:
        a["speed"] = args.speed
    if args.jobs is not None:
        a["jobs"] = args.jobs
    if args.password:
        a["password"] = args.password
    if args.no_cache:
        a["no_cache"] = True
    if args.cache:
        a.pop("no_cache", None)
    if args.homework_submit:
        a["homework_submit"] = True
    if args.start_delay is not None:
        a["start_delay"] = args.start_delay
    save(args.file, accounts)
    print(f"已更新 {args.name}")
    return 0


def cmd_enc(accounts, args):
    a = find(accounts, args.name)
    if not a:
        print("没有这个账号")
        return 1
    enc_map = a.setdefault("homework_enc", {})
    enc_map[str(args.course)] = args.value
    a.pop("homework_seed", None)
    save(args.file, accounts)
    print(f"已设置 {args.name} 课程 {args.course} 的 enc")
    return 0


def cmd_seed(accounts, args):
    a = find(accounts, args.name)
    if not a:
        print("没有这个账号")
        return 1
    a["homework_seed"] = args.url
    save(args.file, accounts)
    print(f"已设置 {args.name} 的种子作业链接")
    return 0


def cmd_run(accounts, args):
    enabled = [a for a in accounts if a.get("enabled", True)]
    if not enabled:
        print("没有启用的账号")
        return 1
    cmd = [sys.executable, os.path.join(ROOT, "multi_run.py"), "--accounts", args.file]
    if args.names:
        names = [n.strip() for n in args.names.split(",") if n.strip()]
        unknown = [n for n in names if not find(accounts, n)]
        if unknown:
            print("未找到账号:", ", ".join(unknown))
            return 1
        cmd += ["--only", ",".join(names)]
    if args.dry_run:
        cmd.append("--dry-run")
    print("执行:", " ".join(cmd[1:]))
    return subprocess.call(cmd, cwd=ROOT)


def main():
    p = argparse.ArgumentParser(description="多账号命令行管理")
    p.add_argument("--file", default=DEFAULT_FILE, help="账号文件，默认 accounts.json")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="添加账号")
    a.add_argument("name")
    a.add_argument("-u", "--username", required=True)
    a.add_argument("-p", "--password", help="不填则交互输入")
    a.add_argument("-c", "--courses", required=True, help="课程ID，逗号分隔")
    a.add_argument("--mode", default="both", choices=["both", "chapters", "homework"])
    a.add_argument("--speed", type=float, default=2.0)
    a.add_argument("--jobs", type=int, default=2)
    a.add_argument("--no-cache", action="store_true", help="禁用答题缓存")
    a.add_argument("--redo-finished", action="store_true", help="重做已完成章节")
    a.add_argument("--homework-submit", action="store_true", help="作业自动提交")
    a.add_argument("--start-delay", type=int, default=0, help="启动前等待秒数")
    a.add_argument("--seed", help="种子作业链接（用于自动获取 enc）")
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list", help="列出账号")
    l.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="查看账号详情")
    s.add_argument("name")
    s.set_defaults(func=cmd_show)

    r = sub.add_parser("remove", help="删除账号")
    r.add_argument("name")
    r.add_argument("-y", "--yes", action="store_true")
    r.set_defaults(func=cmd_remove)

    on = sub.add_parser("on", help="启用账号")
    on.add_argument("name")
    on.set_defaults(func=lambda acc, args: cmd_toggle(acc, args, True))

    off = sub.add_parser("off", help="停用账号")
    off.add_argument("name")
    off.set_defaults(func=lambda acc, args: cmd_toggle(acc, args, False))

    e = sub.add_parser("edit", help="修改账号")
    e.add_argument("name")
    e.add_argument("-c", "--courses")
    e.add_argument("--mode", choices=["both", "chapters", "homework"])
    e.add_argument("--speed", type=float)
    e.add_argument("--jobs", type=int)
    e.add_argument("-p", "--password")
    e.add_argument("--no-cache", action="store_true")
    e.add_argument("--cache", action="store_true", help="重新启用缓存")
    e.add_argument("--homework-submit", action="store_true")
    e.add_argument("--start-delay", type=int)
    e.set_defaults(func=cmd_edit)

    en = sub.add_parser("enc", help="设置某课程的作业 enc")
    en.add_argument("name")
    en.add_argument("course")
    en.add_argument("value")
    en.set_defaults(func=cmd_enc)

    sd = sub.add_parser("seed", help="设置种子作业链接")
    sd.add_argument("name")
    sd.add_argument("url")
    sd.set_defaults(func=cmd_seed)

    run = sub.add_parser("run", help="开始运行（可指定账号）")
    run.add_argument("names", nargs="?", help="账号名，逗号分隔；省略则跑所有启用账号")
    run.add_argument("--dry-run", action="store_true")
    run.set_defaults(func=cmd_run)

    args = p.parse_args()
    accounts = load(args.file)
    sys.exit(args.func(accounts, args))


if __name__ == "__main__":
    main()
