# derivatives-backtest

## 说明

此项目用于存放场外衍生品回测代码, 在推送到仓库后会触发自动运行. 

## 使用规范

**目前还在测试阶段**


所有的运行所需文件都应当存放在上传的文件夹中, 代码会自动检测根目录下所有 `.py` 文件并运行, 如果有运行顺序要求请确保按照名称排好序. 如果有文件仅作为依赖使用, 请存放到 `imports` 文件夹.

所有文件请使用相对地址而非绝对地址. 例如开发文件夹为 `DEV`, 存放目录为 `D://codes/DEV`, 文件结构为

```
./
├── LICENSE
├── README.md
├── __pycache__
│   ├── hello.cpython-39.pyc
│   └── myhello.cpython-39.pyc
├── imports
│   ├── __pycache__
│   │   └── hello.cpython-39.pyc
│   └── hello.py
├── input
│   └── zz1000.csv
├── output
│   ├── fig1.png
│   └── output_folder.md
├── requirements.txt
└── test.py
```

在使用 `zz1000.csv` 文件时请使用 `input/zz1000.csv`, 而非 `D://codes/DEV/input/zz1000.csv`, 这有利于代码的可迁移性.


## 输出

所有需要展现的输出文件存放到 `output` 文件夹. 运行完成后会自动将此文件夹中的文件上传, 而其余位置的文件在运行结束后不会被保留.

## Git 使用 tips
- `fork` 完成后请新建分支并在新的分支上开发, 以便之后与主分支合并.

- 在完成小阶段的工作后可以 commit 一下, 这样如果之后搞砸了还可以 reset 到之前的工作进度上. 命令为
``` sh
git commit -m "MY COMMIT MESSAGES..."
```

- 工作完成后 push 到远程仓库, 有必要时提交 `pull request (PR)` 来请求与正式分支合并.

## 进度
目前的开发进度如下:

[✓] 搭建仓库并撰写说明文档
[✓] 构建自动运行脚本
[✓] 兼容中文字体
[✓] 自动检测并安装项目需要的 packages
[✓] 将运行结果文件夹 `output` 上传至运行结果(`artifacts`)

[✗] 具体使用流程详解与规范
[✗] 使用 windows 的后台环境
[✗] 转为私有仓库并实现用户权限分配
[✗] ...






