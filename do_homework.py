# -*- coding: utf-8 -*-
"""学习通『作业』板块：按链接做，或批量做未交作业。

用法：
    # 1) 按链接（把链接写进 作业列表.txt）
    python do_homework.py -u 手机号 -p 密码
    python do_homework.py -u 手机号 -p 密码 --submit

    # 2) 批量：自动拉取课程「作业」列表，处理未交的
    python do_homework.py -u 手机号 -p 密码 --all --course 268741619 --enc <课程enc> --submit
    python do_homework.py -u 手机号 -p 密码 --all --course 268741619 --limit 1 --submit

说明：--all 需要课程 enc。第一次可以从任意一条作业提交后的返回里拿到，
之后脚本会自动缓存到 .homework_enc.json。
"""
import argparse
import html as H
import json
import os
import re
import sys

from bs4 import BeautifulSoup, NavigableString

from api.base import Chaoxing, Account, SessionManager
from api.answer import Tiku
from api.logger import configure_console_logger, logger

TYPE_MAP = {
    "单选题": "single", "多选题": "multiple", "判断题": "judgement",
    "填空题": "completion", "简答题": "shortanswer", "计算题": "shortanswer",
    "论述题": "shortanswer", "名词解释": "shortanswer", "其他": "shortanswer",
}
ENC_CACHE = ".homework_enc.json"
HOST = "https://mooc1.chaoxing.com"


def parse_args():
    p = argparse.ArgumentParser(description="学习通作业助手")
    p.add_argument("-u", "--username", required=True)
    p.add_argument("-p", "--password", required=True)
    p.add_argument("-f", "--file", default="作业列表.txt", help="按链接模式使用的文件")
    p.add_argument("--submit", action="store_true", help="真正提交")
    p.add_argument("--all", action="store_true", help="批量模式：拉取作业列表")
    p.add_argument("--course", help="课程 ID（--all 必填）")
    p.add_argument("--enc", help="课程 enc（可选，不给则读缓存）")
    p.add_argument("--limit", type=int, default=0, help="最多处理几份作业，0=不限")
    p.add_argument("--list-only", action="store_true", help="只列作业，不做题")
    p.add_argument("--seed", help="种子作业链接：没有 enc 时先用它做一份，从提交返回里拿到课程 enc")
    p.add_argument("--no-cache", action="store_true", help="关闭答题缓存")
    return p.parse_args()


def load_links(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf8") as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                out.append(s)
    return out


def text_with_images(el):
    if el is None:
        return ""
    parts = []
    for item in el.descendants:
        if isinstance(item, NavigableString):
            parts.append(str(item))
        elif getattr(item, "name", None) == "img":
            parts.append(f'<img src="{item.get("src", "")}">')
    return re.sub(r"[\r\t\n]", "", "".join(parts)).strip()


def question_stem_text(div):
    frag = BeautifulSoup(str(div), "lxml")
    for node in frag.find_all("div", class_="stem_answer"):
        node.decompose()
    for node in frag.find_all("input"):
        node.decompose()
    return text_with_images(frag.find("div"))


def decode_homework(html_text):
    soup = BeautifulSoup(html_text, "lxml")
    form = soup.find("form")
    action = form.get("action") if form else ""
    fields = {}
    type_values = {}
    if form:
        for inp in form.find_all("input"):
            name = inp.get("name")
            if not name:
                continue
            m_at = re.fullmatch(r"answertype(\d+)", name)
            if m_at:
                type_values[m_at.group(1)] = inp.get("value", "")
                continue
            if re.fullmatch(r"answer\d+", name):
                continue
            fields[name] = inp.get("value", "")
    questions = []
    for div in soup.find_all("div", class_="singleQuesId"):
        qid = div.get("data") or ""
        qtype = TYPE_MAP.get((div.get("typeName") or "").strip())
        _stem_probe = question_stem_text(div)
        if not qtype:
            for _cn, _en in TYPE_MAP.items():
                if _cn in _stem_probe:
                    qtype = _en
                    break
        qtype = qtype or "single"
        title = re.sub(r"^\s*(\d+\.?)?\s*[（(]?[单多判填简]答题[)）]?\s*", "", _stem_probe).strip()
        options = []
        for opt in div.select("div.stem_answer > div.answerBg"):
            letter_el = opt.find("span")
            letter = letter_el.get("data") if letter_el else ""
            body = opt.find("div", class_="answer_p")
            options.append(f"{letter}. {text_with_images(body)}")
        questions.append({"id": qid, "type": qtype, "title": title,
                          "options": "\n".join(options), "answerField": {},
                          "answertype": type_values.get(qid, "")})
    return action, fields, questions


def to_submit_value(res, q):
    if not res:
        return ""
    if isinstance(res, list):
        res = "".join(str(x) for x in res)
    res = str(res).strip()
    if q["type"] in ("single", "multiple"):
        if re.fullmatch(r"[A-Ha-h]{1,8}", res):
            return "".join(sorted(set(res.upper())))
        for line in q["options"].split("\n"):
            if res and res in line:
                return line[:1]
    if q["type"] == "judgement":
        if res in ("正确", "对", "√", "是", "true", "True"):
            return "true"
        if res in ("错误", "错", "×", "否", "false", "False"):
            return "false"
    return res


def submit_homework(sess, cx, tiku, page_html, url, do_submit):
    action, fields, qs = decode_homework(page_html)
    print(f"  题目数: {len(qs)}")
    if not qs:
        print("  没有解析到题目（可能已提交或页面结构变了）")
        return None
    for i, q in enumerate(qs, 1):
        ans = to_submit_value(tiku.query(dict(q)), q)
        q["answerField"][f'answer{q["id"]}'] = ans
        print(f"   Q{i} ({q['type']}) -> {ans}")
    if not do_submit:
        print("  预览结束")
        return None

    payload = dict(fields)
    payload["pyFlag"] = ""
    payload["answerwqbid"] = ",".join(q["id"] for q in qs) + ","
    for q in qs:
        tl = q.get("answertype") or {"single": "0", "multiple": "1", "completion": "2",
                                       "judgement": "3", "shortanswer": "4"}.get(q["type"], "0")
        payload[f'answer{q["id"]}'] = q["answerField"][f'answer{q["id"]}']
        payload[f'answertype{q["id"]}'] = tl

    try:
        sess.get(HOST + "/mooc-ans/work/validate",
                 params={"courseId": payload.get("courseId", ""),
                         "classId": payload.get("classId", ""),
                         "cpi": payload.get("cpi", "")})
    except Exception:
        pass

    full = action if action.startswith("http") else HOST + action
    if "ua=" not in full:
        full += ("&" if "?" in full else "?") + "ua=pc&formType=post&saveStatus=1&version=1"
    r = sess.post(full, data=payload, headers={
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": HOST,
    })
    print("  提交:", r.status_code, r.text[:200])
    try:
        j = r.json()
    except Exception:
        return None
    # 提交成功会带回新的课程 enc，缓存起来给 --all 用
    for field in ("url", "backUrl"):
        m = re.search(r"[?&]enc=([0-9a-f]{32})", str(j.get(field, "")))
        if m:
            cache_enc(payload.get("courseId", ""), m.group(1))
    if j.get("status") and j.get("stuStatus") == 5:
        try:
            cx._record_failed_work("作业", "", url, qs)
        except Exception:
            pass
    return j


def cache_enc(course_id, enc):
    try:
        data = {}
        if os.path.exists(ENC_CACHE):
            data = json.load(open(ENC_CACHE, encoding="utf8"))
        data[str(course_id)] = enc
        json.dump(data, open(ENC_CACHE, "w", encoding="utf8"))
    except Exception:
        pass


def get_cached_enc(course_id):
    try:
        data = json.load(open(ENC_CACHE, encoding="utf8"))
        return data.get(str(course_id))
    except Exception:
        return None


def parse_work_page(html_text):
    items = []
    for li in re.findall(r'<li onclick="goTask\(this\);".*?</li>', html_text, re.S):
        data = re.search(r'data="([^"]+)"', li)
        title = re.search(r'overHidden2 fl">(.*?)</p>', li, re.S)
        status = re.search(r'status fl">(.*?)</p>', li, re.S)
        if data:
            items.append({
                "url": H.unescape(data.group(1)),
                "title": H.unescape(title.group(1)).strip() if title else "",
                "status": H.unescape(status.group(1)).strip() if status else "",
            })
    return items


def list_works(sess, course_id, class_id, user_id, enc):
    """翻页拉取全部作业（每页 12 条，页码参数 pageNum）"""
    items, seen, page = [], set(), 1
    while True:
        r = sess.get(HOST + "/mooc-ans/mooc2/work/list",
                     params={"courseId": course_id, "classId": class_id, "userId": user_id,
                             "enc": enc, "pageNum": page})
        if page == 1 and "无权限" in r.text:
            return None
        batch = parse_work_page(r.text)
        if not batch:
            break
        for it in batch:
            if it["url"] not in seen:
                seen.add(it["url"])
                items.append(it)
        m = re.search(r"pageNum\s*:\s*(\d+)", r.text)
        total_pages = int(m.group(1)) if m else 1
        if page >= total_pages:
            break
        page += 1
    return items


def main():
    args = parse_args()
    configure_console_logger("INFO")
    tiku = Tiku()
    tiku.config_set({})
    tiku = tiku.get_tiku_from_config()
    tiku.init_tiku()
    if args.no_cache:
        tiku.USE_CACHE = False
        print("已关闭答题缓存（--no-cache）")
    if tiku.DISABLE:
        print("题库未启用，检查 config.ini")
        sys.exit(1)

    cx = Chaoxing(account=Account(args.username, args.password), tiku=tiku)
    if not cx.login().get("status"):
        print("登录失败")
        sys.exit(1)
    print("登录成功")
    sess = SessionManager.get_session()

    if args.all:
        if not args.course:
            print("--all 模式需要 --course 课程ID")
            sys.exit(1)
        course = next((c for c in cx.get_course_list() if c["courseId"] == str(args.course)), None)
        if not course:
            print("课程列表里找不到该课程")
            sys.exit(1)
        enc = args.enc or get_cached_enc(args.course)

        # 没有 enc 时，用一条种子作业链接做一次提交，从返回 url 里自动拿 enc
        seed = args.seed
        if not enc and not seed:
            links_in_file = load_links(args.file)
            if links_in_file:
                seed = links_in_file[0]
                print(f"没有缓存的课程 enc，自动使用 {args.file} 里第一条作业作为种子")
        if not enc and seed:
            print("=" * 70)
            print("[seed] 先用种子作业换取课程 enc")
            print(f"       {seed[:110]}")
            r = sess.get(seed, allow_redirects=True)
            if r.status_code != 200:
                print("  种子链接打开失败:", r.status_code)
                sys.exit(1)
            if not args.submit:
                print("  注意：不带 --submit 时只预览，无法拿到 enc；加 --submit 才会真正提交并缓存 enc")
            submit_homework(sess, cx, tiku, r.text, seed, args.submit)
            enc = args.enc or get_cached_enc(args.course)
        if not enc:
            print("缺少课程 enc：请用 --seed <任意作业链接> --submit 先做一份，或 --enc 直接传")
            sys.exit(1)
        items = list_works(sess, course["courseId"], course["clazzId"], cx.get_uid(), enc)
        if items is None:
            print("enc 已失效，请用 --enc 换一个（可从任意作业提交后的返回 url 里取）")
            sys.exit(1)
        todo = [x for x in items if x["status"] in ("未交", "待重做")]
        print(f"作业共 {len(items)} 条，未交 {len(todo)} 条")
        for it in items:
            print(f"  [{it['status']}] {it['title']}")
        if args.list_only:
            return
        if args.limit:
            todo = todo[:args.limit]
        for idx, it in enumerate(todo, 1):
            print("=" * 70)
            print(f"[{idx}/{len(todo)}] {it['title']}")
            r = sess.get(it["url"], allow_redirects=True)
            submit_homework(sess, cx, tiku, r.text, it["url"], args.submit)
        return

    links = load_links(args.file)
    print(f"共 {len(links)} 条链接，模式：{'提交' if args.submit else '预览'}")
    for idx, url in enumerate(links, 1):
        print("=" * 70)
        print(f"[{idx}/{len(links)}] {url[:110]}")
        r = sess.get(url, allow_redirects=True)
        if r.status_code != 200:
            print("  打开失败:", r.status_code)
            continue
        submit_homework(sess, cx, tiku, r.text, url, args.submit)


if __name__ == "__main__":
    main()
