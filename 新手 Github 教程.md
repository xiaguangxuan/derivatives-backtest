# 新手 Github 教程

## 简介

此教程面向完全没有 `Git` 经验的使用者, 希望能帮助新手在极短的时间内理解 `Git` 的工作模式以及基础的使用方法.

## Git 简介

`Git` 是一个免费和开源的分布式版本控制系统, 旨在以速度和效率处理从小型到大型项目的所有内容.

`Git` 易于学习, 占用空间小, 性能快如闪电, 具有廉价的本地分支, 方便的暂存区域, 和多个工作流等功能.

> 以上内容摘自 `Git` 官网.

总体来说, 如果想要追踪代码的变动情况, 并进行版本管理, `Git` 一定是不二之选.

安装 `Git`: 从[此处](https://git-scm.com/downloads)下载安装包, 一路下一步即可, 如果想在终端使用 `Git`, 需要在安装时勾选对应选项.

安装完成后, 终端中输入 `git -v`, 如果没有报错则安装成功.

## Github

`Github` 是目前世界上最大的代码托管平台, 为多人共同开发提供了便利. 很多人还是没有搞清楚 `Git` 和 `Github` 的关系. 其实这两者并不是一家, `Git` 是版本管理的工具, `Github` 是代码托管的平台, 其可以使用 `Git` 进行版本的管理. 类似的代码托管平台还有 `Gitee`, `Gitlab`. 综合比较来说, `Github` 提供的功能最全面, 免费的配额也最高, 但是国内经常有访问上的障碍, 如果有需要可以修改 host 信息或者科学上网; `Gitee` 国内访问速度最快, 但是免费功能较少; `Gitlab` 注重私有代码托管平台的部署. 由于要用到在线运行功能, 我们选择使用 `Github`.

## ssh 密钥

打开终端, 输入
```sh
ssh-keygen -t rsa
```

一路默认回车, 即可在 `个人文件夹/.ssh` 下找到ssh密钥. 其中后缀为 `.pub` 的是公钥, 将其中所有内容复制, 到 `Github` 的[个人设置](https://github.com/settings/profile)下 [`SSH and GPG keys`](https://github.com/settings/keys) 新建一个 SSH Key, Title 可以设置成易于区分设备的名字, 因为提交的 SSH Key 出于安全考虑之后将不再可见.


## fork仓库并在进行开发

前往[目标仓库](https://github.com/herbyuan/derivatives-backtest), 点击右上角的 `Fork` 按钮, 目的是将仓库复制一份作为己有, 之后的开发将在自己的仓库进行. 点击 `code-ssh`, 拷贝 SSH 地址, 在本地希望开发的文件夹中打开终端, 输入以下命令克隆仓库:
```
git clone git@github.com:<your_username>/derivatives-backtest.git
```

<img src=>

## git 仓库的相关操作

下面介绍最基本的 git 操作.

使用命令行管理需要很多的经验以及操作技巧, 对新手也很不友好, 因此我们选择使用一些图形界面来进行管理.

常见的 IDE 都会集成 Git 管理模块, 例如 [`VS Code`](https://code.visualstudio.com) 和 [`Sublime Text`](https://www.sublimetext.com), 此外 Github 也推出了自己的管理工具. 在这些工具中, 我们可以很方便地追踪每次提交代码的改动, 并用点按的方式完成一系列操作.

## 追踪不同的分支

一个完整的项目会有很多分支, 比如 `main`, `prod`, `dev`. 通过以下命令可以在不同的分支之间切换:
``` sh
git checkout <branchname>
```

从主要仓库默认只会 fork main 分支, **我们开发时应当新建分支并避免在 `main` 上操作, 以避免之后合并分支和提交PR的一系列问题**.

使用以下命令新建分支:

``` sh
git branch dev-branch
git checkout dev-branch
```

这样我们就创建了名为 `dev-branch` 的分支并切换到了新的分支上进行开发.

> 每个分支都会指向对应开发路线最前端, 为了避免意想不到的错误, 我们应当尽量选择切换到某个分支而非某次提交记录.

## 提交修改并push

当我们进行了修改之后, 可以将修改的结果提交.

```sh
git add .  # 添加所有未记录的文件
git commit -m "your commit message"   # 提交修改, 会产生一次commit记录
git push   # 推送到远程仓库
```
如果是第一次commit, 需要按照提示设置 username 和 email, 这些信息会被一同记录在 commit 中, 以区分每次提交的人.

如果是在新创建的分支中第一次提交, 会有以下报错:

```
fatal: The current branch dev-branch has no upstream branch.
To push the current branch and set the remote as upstream, use

    git push --set-upstream origin dev-branch

To have this happen automatically for branches without a tracking
upstream, see 'push.autoSetupRemote' in 'git help config'.
```

应当使用如下命令指明远程的分支名:

```sh
git push --set-upstream origin dev-branch
```

## 提交 Pull Request

希望用现在的代码更新原先仓库, 可以提交 Pull Request (PR). 简单理解就是开发者提交自己的代码新建 Pull Request,请求原作者“把我的代码拉回去”.

正常来说, 在一个fork的仓库push内容之后, 登录网页版就可以看到醒目的横幅提示可以提交 PR, 如果没有则要在 `Pull Requests` 栏中新建.

`base repository` 是希望修改合并的原仓库, `head repository` 是更新的自己仓库. 应当注意选择正确的分支.

选好后会自动检测修改的地方以及合并是否会产生冲突, 没有问题的话点击 `Create Pull Request` 创建一个 PR, 可以在评论区写上此次修改的内容.

## 同步 fork 来的仓库

由于不止有一个开发者, fork 之后原先仓库可能会保持更新. 我们可以点按 `Sync fork` 来使远程仓库保持最新, 并在本地切换到 `main` 分支后使用 `git pull` 命令拉取最新的仓库.

## PR 的采纳

管理仓库的账号会收到 PR 的提醒. 如果要接受 PR, 则需要考虑合并的方式. 除去较为高级的 `rebase` 操作用于从下往上修改每个版本的相同位置, `merge` 和 `squash` 的差别在于是否将分支上的多次 `commit` 压缩为一次. 一般来说, 为了便于查看修改, 我们会将多次小的 `commit` 压缩成一次.


## 冲突的解决

如果在开发的过程中 `main` 分支也有变化, 且涉及同一个文件, 则会产生冲突. 此时需要根据提示对冲突的地方进行修改.待完善





