<p align="center">
  <a href="https://www.springing.top" target="blank">
    <img src="images/logo.png" alt="Logo" width="156" height="156">
  </a>
  <h2 align="center" style="font-weight: 600">Spring-Superstar</h2>
  <p align="center">
    学习通在线刷课脚本 超星 学习通 云端刷课
  </p>
</p>

本项目宗旨是帮助大学生们解放双手，根据教程操作后就可以完成刷课，简单易懂，仅需手机就可以使用

>如果本项目对希望各位同学们给本仓库点一个免费的Star或者给小春子点一个Follow 谢谢大家！

![截图](/images/star.png)

## 安全配置（必读）

不要将账号、密码或 Cookie 写入仓库文件、代码提交、Issue、日志或截图。Fork 仓库通常仍属于原 Fork 网络，不能直接改为私有；如需独立私有仓库，须先在 GitHub 的仓库设置中选择 **Leave fork network**。私有仓库的 Actions 可能受账户分钟配额限制。

推荐将凭据存放在 GitHub Actions Secrets：进入 Fork 后仓库的 **Settings → Secrets and variables → Actions → New repository secret**，创建下列三个 Secret。Secret 的值不会显示在 Actions 日志中；请勿在日志中打印它们。

| Secret 名称 | 必填 | 值的格式与示例 |
| --- | --- | --- |
| `CHAOXING_USERNAME` | 是 | 账号字符串，例如 `your_name` |
| `CHAOXING_PASSWORD` | 是 | 密码字符串，例如 `your_password` |
| `CHAOXING_COURSE_LIST` | 是 | 课程 ID 的逗号分隔字符串，例如 `114514,1919810`（不要填写方括号或引号） |

工作流只支持手动触发：在 **Actions → 刷课 → Run workflow** 中运行。这样提交 README 或配置等普通改动不会意外执行工作流。

若在本地使用配置文件，请从 `config_template.ini` 复制出 `config.ini`，仅保存在本机。`config.ini` 和 `cookies.txt` 已被 `.gitignore` 排除，但提交前仍请检查 `git status`，避免凭据进入版本库。

## 快速开始

<a href="https://blog.springing.top/p/20241119/" target="blank">点击我查看操作说明</a>

<a href="https://github.com/Samueli924/chaoxing" target="blank">灵感来源</a>

## 赞助
>如果觉着代码对你有帮助，可以赞赏一下开发者

![截图](/images/reward.jpg)
