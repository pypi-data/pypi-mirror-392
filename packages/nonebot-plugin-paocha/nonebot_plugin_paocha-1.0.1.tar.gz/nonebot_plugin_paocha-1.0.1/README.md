### 一个基于 NoneBot2 的泡茶签到插件，支持好感度等级系统和图片上传功能。

## ✨ 功能介绍

- 🍵 每日泡茶签到，获得随机好感度
- 📊 好感度等级系统（1段到传奇9段）
- 🖼️ 支持上传图片，签到随机显示
- 👥 用户映射管理，支持QQ适配器
- 📈 详细的统计和查询功能


## 📦 安装方式

    ```shell
    pip install nonebot-plugin-paocha
    ```
## 🔧 配置方法

在 NoneBot2 的 `bot.py` 或插件加载文件中添加：

python
nonebot.load_plugin('nonebot-plugin-paocha')

### 📞 使用命令

- **泡茶签到**: `泡茶`、`喝水`、`/泡茶`、`/喝水`
- **查询信息**: `泡茶表`、`泡茶查询`、`/泡茶表`
- **等级查看**: `等级`、`等级表`、`/等级`
- **用户管理**: `映射用户`、`用户列表`、`搜索用户`
- **图片管理**: `上传图片`、`图片统计`
使用 `帮助` 或 `help` 命令查看详细使用说明

## 📝 配置说明

插件会自动在插件目录下创建 `data` 文件夹，包含：
- `sign.ini`: 签到数据
- `data.ini`: 用户映射数据  
- `images/`: 图片库目录

## 🌟 具体路径
    ```shell
    venv/
    └── lib/
        └── python3.x/
            └── site-packages/
                └── nonebot_plugin_paocha/
                    ├── __init__.py
                    └── data/                    # 运行时自动创建
                        ├── sign.ini            # 运行时自动创建
                        ├── data.ini            # 运行时自动创建  
                        └── images/              # 运行时自动创建
    ```


## ✅ 依赖要求

- Python 3.9+
- httpx 0.28.1+
- NoneBot2 2.4.4+
- nonebot-adapter-qq 1.6.5+

## 📜 许可证

MIT License

## 项目地址

- GitHub: [点击前往](https://github.com/mmxd12/nonebot-plugin-paocha)
- pypi: [点击前往](https://pypi.org/project/nonebot-plugin-paocha/)
