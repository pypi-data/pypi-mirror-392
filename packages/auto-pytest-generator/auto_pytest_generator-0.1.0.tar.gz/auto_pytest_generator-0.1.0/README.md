# Smoke-Test-Recorder

本工具旨在为0自动化覆盖的团队快速创建一套基于API流量的冒烟测试用例。它通过启动一个本地代理，捕获您在浏览器中与被测系统交互时产生的`fetch/XHR`流量，并自动生成基于`requests`的`pytest`测试代码。

## 项目结构

```code
auto-pytest-generator/
│
├── src/
│   └── auto_pytest_generator/
│       ├── __init__.py
│       ├── main.py             # CLI入口和mitmproxy启动逻辑与Filter插件
│       ├── addon.py              # pytest代码生成插件
│       └── templates/
│           └── pytest_template.jinja2 # Jinja2模板文件
│
├── tests/
│   └── ...                     # 工具自身的单元测试
│
├── .gitignore
├── pyproject.toml              # 项目打包和依赖管理
└── README.md                   # 使用文档
```

## 特点

- **0配置启动**：只需指定目标系统的URL前缀即可开始。
- **自动化生成**：在浏览器中操作，用例自动生成。
- **基于真实数据断言**：使用录制时的响应体做断言，无需依赖接口文档。
- **易于集成**：生成的代码是标准的`pytest`格式，可直接运行。

## 安装

```bash
# 推荐使用uv或pipx进行安装，以避免污染全局环境
uv tool install auto-pytest-generator

# 或者使用pip
pip install auto-pytest-generator
```

## 使用

- 启动代理服务 uv run apg --url-prefix http://1.2.3.4:5678/
- 配置浏览器代理到apg代理服务
- 访问 http://mitm.it 检查是否代理成功
- 开始在客户端操作，用例被生成在./generated_tests/
- 拷贝所有*.py文件到测试用例运行环境(依赖pytest,requests)
