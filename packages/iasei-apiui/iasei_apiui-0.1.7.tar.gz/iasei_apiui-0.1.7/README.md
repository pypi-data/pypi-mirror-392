# 安装构建工具
pip install build twine

# 构建 wheel 和源码包
python -m build

# 上传包（需 PyPI 账号，输入 __token__ 和 API 令牌）
twine upload dist/*

### window venv 环境激活
.\.venv\Scripts\activate


#### 查看包
pip freeze > requirement.txt
