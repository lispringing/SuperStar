<p align="center">
  <a href="https://www.springing.top" target="blank">
    <img src="images/logo.png" alt="Logo" width="156" height="156">
  </a>
  <h2 align="center" style="font-weight: 600">Spring-Superstar</h2>
  <p align="center">
    学习通在线刷课脚本 超星 学习通 云端刷课
  </p>
</p>

本项目宗旨是帮助大学生们解放双手，根据教程操作后就可以完成刷课，简单易懂，仅需手机就可以使用！

本项目仅供学习娱乐使用，切勿用于倒卖、售卖、二次传播等不被允许的违法违规行为，若出现以上行为，与本项目无关。使用本项目即默认已遵守该条款。

> 如果本项目对希望各位同学们给本仓库点一个免费的Star或者给小春子点一个Follow 谢谢大家！

![截图](/images/star.png)

## 用前必读必读！

默认 fork 仓库之后**是公开的状态**，也就是说你的账号和密码是**处于一个明文状态！！很危险！！此时一定要把仓库权限改为私有！**

fork 后的仓库由于 GitHub 内部限制，是无法直接修改为 Private 状态的。**请一定参考以下步骤**，将自己的已修改 yml 文件的仓库设为 Private 模式：

1. 点击“Leave fork network”：在你截图的“Danger Zone”区域，找到并点击 “Leave fork network” 按钮。

2. 此时系统会弹出警告，提示你将失去与上游仓库的同步能力等。阅读后，按提示输入仓库名称以确认。

3. 操作完成后，该仓库就成为一个独立的公共仓库。刷新页面，你会发现在“Change repository visibility”旁边，“Change visibility”按钮变为可点击状态。

4. 点击该按钮，同样此时系统会弹出警告，选择“Make private”并完成确认即可。

之前本仓库就因为明文账号密码泄露导致一些同学账号被盗拿来恶作剧（不得不说世界上还是坏人多），故提前在此说明，希望大家周知。

同时**切勿直接在本项目中提交 Pull Request**，已经有很多不知道使用方法的同学，直接在本项目中提交了带有自己明文账号密码的 Pull Request，将自己的信息泄露。

## 快速开始

1. 进入项目页面后，点击 fork，复制本项目（可以的话顺便点一个旁边的 Star！）；

![项目主页面](https://blog.springing.top/img/674a726865c9f.png)

2. 点击项目上方的 Actions 按钮（手机端的被折叠起来了），开启 Actions 功能；

<img width="1079" height="573" alt="image" src="https://github.com/user-attachments/assets/80dcf22b-2f69-4b61-a8d1-6bb3c153a8a2" />

3. 回到（1）中的项目主页，在出现的文件夹目录中，点击 `.github/workflows`，进入这个文件夹；

![workflows](https://blog.springing.top/img/674a73c958ea2.png)

进入该文件夹，会发现里面有一个名为 `main.yml` 的文件，点击它，再点击右上方的编辑按钮，进入文件编辑界面；

<img width="390" height="141" alt="image" src="https://github.com/user-attachments/assets/0683cecb-ef3f-4814-a143-2e8132f5cb67" />

此时先不着急编辑，你需要先获取需要刷的课程 id。

在电脑网页版本登录超星学习通，点进你要学习的课程。

<img width="2515" height="1258" alt="image" src="https://github.com/user-attachments/assets/110857d1-ed4f-4b02-ad07-5dbd726609bf" />

点击后，新的网址中 `courseid` 后的一串数字，就是我们需要的课程 ID 了。

<img width="1578" height="441" alt="image" src="https://github.com/user-attachments/assets/5bd3e9d7-9b10-4a77-aa87-f7fbff82dae3" />

复制该 ID，回到文件编辑界面。

若只需要该项目帮你看视频，则只需要修改最后一行，即：

```
- name: Run main.py
        run: python main.py -u 学习通账号 -p 学习通密码 -l 课程id
```

替换账号密码或课程 id 时，**需要将该行中自带的双引号一并除去**。

4. 修改完成后提交文件。

![提交文件](https://blog.springing.top/img/674a77aa6fdba.png)

因为你修改了文件（提交这个 workflow）后，会因文件的 push 而自动触发一次 Action 的执行。

此时回到（2）中主页上方的 Actions 界面，若刚才的账号密码等信息你没有填写错误，此时 Actions 就会自动帮你运行脚本了！

<img width="2559" height="1315" alt="image" src="https://github.com/user-attachments/assets/a870f477-5e5f-4ee7-afb2-1abd776f3eb2" />

<img width="2558" height="1098" alt="image" src="https://github.com/user-attachments/assets/5225d67c-a860-47d9-8018-31be08c8aaa3" />

<img width="2520" height="1266" alt="image" src="https://github.com/user-attachments/assets/ef9a9fb0-2b04-458e-86f1-cf3901784bc4" />

之后可以在 Actions → 刷课 → Run workflow 手动触发这个操作，不用更新了任务就必须修改一次文件了！

<a href="https://github.com/Samueli924/chaoxing" target="blank">灵感来源</a>

## 进阶玩法

1. 定时刷课

你可以通过修改 `main.yml` 来实现定时刷课。

将文件中：

```
#schedule:
#  - cron: "0 8 * * *"
```

前的“#”号删除，即可实现每天定时刷课的功能。

> 注意：GitHub 的 cron 用的是 **UTC 时间**，`0 8` **实际是北京时间 16:00**。想在北京时间早上 8 点跑，请写成 `0 0 * * *`。
>
> 另外，公开仓库连续 60 天没有提交，**定时任务会被自动停用**。

2. 接入大模型做题

你可以通过修改 `config.ini` 的 `[tiku]` 段，把题库换成大模型。

先进入已经 Disconnected 主仓库了的 fork 仓库，点击 **Settings** → **Secrets and variables** → **Actions** → **New repository secret**。

<img width="1733" height="1221" alt="image" src="https://github.com/user-attachments/assets/7e01c60e-146e-4882-a647-fa512b670e82" />

逐个添加：

| Secret 名称 | 填什么 | 是否必填 |
| --- | --- | --- |
| `CHAOXING_USERNAME` | 学习通手机号 | 必填 |
| `CHAOXING_PASSWORD` | 学习通密码 | 必填 |
| `CHAOXING_COURSE_LIST` | 课程 ID，逗号分隔 | 必填 |
| `TIKU_ENDPOINT` | 大模型接口地址 | 用 AI 题库时必填 |
| `TIKU_KEY` | 大模型 API Key | 用 AI 题库时必填 |
| `TIKU_MODEL` | 模型名，例如 `deepseek-chat` | 用 AI 题库时必填 |
| `NOTIFY_URL` | 通知地址 | 选填 |

其中 `TIKU_ENDPOINT` 填 **base_url**（一般以 `/v1` 结尾，后面的路径程序会自己拼）；`TIKU_KEY`、`TIKU_MODEL` 换成你自己的和你自己想用的模型代号。

> Secret 名字可以自己起，但必须和下面 workflow 里写的一致。

打开你仓库里的 `.github/workflows/main.yml`，**整份删掉，粘贴下面的内容**（保持缩进不要动）：

```yaml
name: 刷课

on:
  push:
    branches: [ main ]
  workflow_dispatch:            # 允许在 Actions 页面手动点运行
  # schedule:                   # 想每天定时跑，取消下面两行的注释（详见第 6 节）
  #   - cron: "0 0 * * *"

jobs:
  Start:
    runs-on: ubuntu-latest
    timeout-minutes: 350        # GitHub 单次任务上限 6 小时，留点余量

    steps:
      - name: 1. 拷贝代码
        uses: actions/checkout@v4

      - name: 2. 安装 Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: 3. 安装依赖
        run: pip install -r ./requirements.txt

      - name: 4. 恢复答题缓存
        uses: actions/cache@v4
        with:
          path: cache.json
          key: tiku-cache-${{ github.run_id }}
          restore-keys: tiku-cache-

      - name: 5. 生成 config.ini
        env:
          TIKU_ENDPOINT: ${{ secrets.TIKU_ENDPOINT }}
          TIKU_KEY: ${{ secrets.TIKU_KEY }}
          TIKU_MODEL: ${{ secrets.TIKU_MODEL }}
          NOTIFY_URL: ${{ secrets.NOTIFY_URL }}
        run: |
          cat > config.ini <<EOF
          [tiku]
          provider=AI
          endpoint=$TIKU_ENDPOINT
          key=$TIKU_KEY
          model=$TIKU_MODEL
          min_interval_seconds=5
          http_proxy=
          check_llm_connection=true
          submit=true
          cover_rate=0.8
          delay=1.0
          true_list=正确,对,√,是
          false_list=错误,错,×,否,不对,不正确
          [notification]
          provider=Bark
          url=$NOTIFY_URL
          EOF

      - name: 6. 开始刷课
        env:
          CHAOXING_USERNAME: ${{ secrets.CHAOXING_USERNAME }}
          CHAOXING_PASSWORD: ${{ secrets.CHAOXING_PASSWORD }}
          CHAOXING_COURSE_LIST: ${{ secrets.CHAOXING_COURSE_LIST }}
        run: >
          python main.py
          -u "$CHAOXING_USERNAME"
          -p "$CHAOXING_PASSWORD"
          -l "$CHAOXING_COURSE_LIST"
          -s 2
          -j 2

      - name: 7. 上传日志（失败也上传）
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: chaoxing-log
          path: chaoxing.log
```

将其中的 `[tiku]` 处修改为：

```
          cat > config.ini <<EOF
          [tiku]
          provider=AI
          endpoint=$TIKU_ENDPOINT
          key=$TIKU_KEY
          model=$TIKU_MODEL
          min_interval_seconds=5
          http_proxy=
          submit=true
          cover_rate=0.8
          delay=1.0
          true_list=正确,对,√,是
          false_list=错误,错,×,否,不对,不正确
          EOF
```

即可让程序把题目交给大模型解答。

`min_interval_seconds` 是两次请求的最小间隔，建议 5；`http_proxy` 没有代理也要留空，但这一行不能删。

项目里还有很多 `provider` 的备选方案。如：

| provider | 类型 | 需要什么 | 适合谁 |
| --- | --- | --- | --- |
| `TikuYanxi` | 免费题库 | 注册拿 Token | 想零成本、题目普通 |
| `TikuGo` | 免费题库 | 可选的免限流 Token | 想零成本、能接受限流 |
| `TikuLike` | 付费题库 | Token（按次计费） | 想高准确率 + 图片题 |
| `TikuAdapter` | 自建服务 | 自己部署一套 | 有服务器、想完全自控 |
| `AI` | 大模型 | 任意 OpenAI 兼容 Key | 有 API Key、题目偏理解型 |
| `SiliconFlow` | 大模型 | 硅基流动 Key | 国内直连、模型便宜 |

将 `provider=` 后，替换你需要的供应商即可。

3. 多题库回退

你可以通过修改 `config.ini` 里的 `provider`，把多个题库串成一条回退链。

将：

```
provider=AI
```

改为：

```
provider=AI,TikuGo,TikuYanxi
```

即可让程序按顺序查询，前一个题库没搜到（或返回的答案类型不对）时自动换下一个。把免费题库放前面、按次计费的放后面，可以明显降低 Token 消耗。

4. 跑完推送手机

你可以通过在 `config.ini` 里增加 `[notification]` 段，让程序在结束时推送消息。

在 `main.yml` 生成配置的那一步，将：

```
false_list=错误,错,×,否,不对,不正确
EOF
```

改为：

```
false_list=错误,错,×,否,不对,不正确
[notification]
provider=Bark
url=https://api.day.app/你的KEY/
EOF
```

即可在所有课程学习完成或程序报错时收到推送。支持 `ServerChan`、`Qmsg`、`Bark`、`Telegram` 四家。

> 用 `Telegram` 时还需要再加一行 `tg_chat_id=xxx`。

5. 二倍速与并发

你可以通过命令行参数控制播放速度和并发数。

在 `main.yml` 的最后一步，将：

```
run: python main.py -u "$CHAOXING_USERNAME" -p "$CHAOXING_PASSWORD" -l "$CHAOXING_COURSE_LIST"
```

改为：

```
run: python main.py -u "$CHAOXING_USERNAME" -p "$CHAOXING_PASSWORD" -l "$CHAOXING_COURSE_LIST" -s 2 -j 2
```

即可让视频以 2 倍速播放，并同时处理 2 个章节。`-s` 最大为 2；`-j` 默认 4，开了大模型题库时建议降到 2 甚至 1，否则容易触发 403 / 429。

6. 答案缓存

你可以通过 `actions/cache` 让搜到过的题目跨运行复用。

在“安装依赖”和“生成 config.ini”之间插入：

```
      - name: 恢复答题缓存
        uses: actions/cache@v4
        with:
          path: cache.json
          key: tiku-cache-${{ github.run_id }}
          restore-keys: tiku-cache-
```

即可在每次运行前恢复上次的 `cache.json`，命中缓存的题目不再重复调用题库和大模型。

7. 保存完整日志

你可以通过上传 artifact 保留 TRACE 级别的完整日志。

在 `main.yml` 的最后追加：

```
      - name: 上传运行日志
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: chaoxing-log
          path: chaoxing.log
```

即可在运行结束后从 Actions 页面的 Artifacts 里下载 `chaoxing.log`，用来排查“为什么没看课”“为什么没搜到答案”这类问题。日志里有账号和答案，公开仓库不建议保留。

8. Cookie 免密登录

你可以通过 `--use-cookies` 绕过密码登录，适用于账号被风控、登录要求验证码的情况。

先用密码正常登录一次，程序会自动在运行目录生成 `cookies.txt`（格式是 `k1=v1;k2=v2` 一行）。之后在 `main.yml` 的运行步骤前插入：

```
      - name: 写入 Cookie
        run: echo "${{ secrets.CHAOXING_COOKIES }}" > cookies.txt
```

并把运行命令改成：

```
run: python main.py --use-cookies -l "$CHAOXING_COURSE_LIST" -s 2 -j 2
```

即可免密登录。Cookie 会过期，一般几天到几周；同时提供账号密码时，Cookie 失效会自动回退到密码登录。

9. 本地验证配置

你可以先在本地跑一遍配置，确认题库或模型没问题再推到 Action。

在本地执行：

```
python main.py -c config.ini
```

即可看到 `正在验证大模型配置` → `连接检查成功`（或具体报错）。这一步会消耗少量 Token。

注意用 `-c` 时，账号密码必须写在 `config.ini` 的 `[common]` 段，命令行的 `-u/-p` 会被忽略。

10. 自动签到

你可以自己把仓库里现成的签到方法接到主流程（该功能并未默认启用）。

新建 `signin.py`：

```
from api.base import Chaoxing, Account, ActivityType
from api.logger import configure_console_logger, logger

configure_console_logger("INFO")
cx = Chaoxing(account=Account("手机号", "密码"))
if cx.login()["status"]:
    for course in cx.get_course_list():
        for act in cx.get_activity_list(course):
            if act.get("activeType") == ActivityType.SIGNIN and act.get("status") == 1:
                cx.pre_sign(course, act["id"])
                logger.info(cx.sign_in_normal(course, act["id"], name=act.get("name", "")))
```

然后在 `main.yml` 里增加一步：

```
      - name: 自动签到
        run: python signin.py
```

即可在刷课前尝试签到。

> 注意活动列表的字段（`activeType` / `status` / `id`）需按实际接口返回核对。
>
> 貌似位置签到的三角定位是 TODO，一直在咕咕咕，**所以只能签普通签到**。

11. Docker 自托管

由于 GitHub Actions 的 6 小时上限限制，你的课程可能没有办法在规定时间内刷完。你可以用 Docker 在自己服务器上跑，摆脱 GitHub Actions 的 6 小时上限。

你可将仓库 clone 至已有 Docker 的环境，在仓库目录执行：

```
docker build -t superstar .
docker run -d --name superstar -v /你的目录:/config superstar
```

即可获得没有时长限制的常驻运行。镜像默认以 `-c /config/config.ini` 启动，所以 `config.ini` 的 `[common]` 段账号密码必须填对，题库配置写 `[tiku]` 段即可。

## 赞助

> 如果觉着代码对你有帮助，可以赞赏一下开发者：

![截图](/images/reward.jpg)
