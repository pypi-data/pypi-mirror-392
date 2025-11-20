from nonebot import on_command
from ctypes import ArgumentError
from nonebot.adapters.qq import Bot, MessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from datetime import datetime
import random
import logging
import os
import configparser
from pathlib import Path
from io import BytesIO

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="泡茶签到插件",
    description="茶饮签到系统，包含等级管理、图片上传和骚话系统",
    usage="使用 '泡茶' 命令开始使用",
    type="application",
    homepage="https://github.com/mmxd12/nonebot-plugin-paocha",
    supported_adapters={"nonebot.adapters.qq"},
)

__version__ = "1.0.12"

# 使用 NoneBot 的数据目录
def get_plugin_data_dir():
    """获取插件数据目录"""
    # 获取机器人数据目录
    data_dir = Path.cwd() / "data" / "paocha"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

# 初始化路径（在函数内部使用，避免导入时初始化）
def init_paths():
    """初始化路径配置"""
    data_dir = get_plugin_data_dir()
    
    # 配置文件路径
    sign_config_path = data_dir / 'sign.ini'
    data_config_path = data_dir / 'data.ini'
    image_path = data_dir / 'images'
    chat_lines_path = data_dir / 'chat_lines.txt'
    
    # 确保目录存在
    image_path.mkdir(parents=True, exist_ok=True)
    
    return sign_config_path, data_config_path, image_path, chat_lines_path

# 延迟初始化配置
def get_configs():
    """获取配置对象"""
    sign_config_path, data_config_path, image_path, chat_lines_path = init_paths()
    
    config = configparser.ConfigParser()
    data_config = configparser.ConfigParser()
    
    # 如果配置文件不存在，创建它们
    if not sign_config_path.exists():
        with open(sign_config_path, 'w', encoding='utf-8') as f:
            config.write(f)
    else:
        config.read(sign_config_path, encoding='utf-8')
    
    if not data_config_path.exists():
        with open(data_config_path, 'w', encoding='utf-8') as f:
            data_config.write(f)
    else:
        data_config.read(data_config_path, encoding='utf-8')
    
    # 初始化骚话文件
    if not chat_lines_path.exists():
        default_chat_lines = [
            "你今天已经泡过茶了，可不能贪杯哦！",
            "茶虽好，可不要贪杯哦~明天再来吧！",
            "茶香四溢，但今日份已享用完毕~",
            "指挥官，贪杯可不是好习惯哦！",
            "茶道讲究适量，今日已足矣！"
        ]
        with open(chat_lines_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(default_chat_lines))
    
    return config, data_config, image_path, chat_lines_path

# 等级映射表
level_map = {
    '1段': 50,
    '2段': 100,
    '3段': 150,
    '4段': 200,
    '5段': 250,
    '6段': 350,
    '7段': 450,
    '8段': 550,
    '9段': 650,
    '10段': 750,
    '11段': 900,
    '12段': 1050,
    '13段': 1200,
    '14段': 1350,
    '15段': 1500,
    '16段': 1700,
    '17段': 1900,
    '18段': 2100,
    '19段': 2300,
    '20段': 2500,
    '21段': 2750,
    '22段': 3000,
    '23段': 3250,
    '24段': 3500,
    '25段': 3750,
    '26段': 4050,
    '27段': 4350,
    '28段': 4650,
    '29段': 4950,
    '30段': 5550,
    '传奇1段': 6800,
    '传奇2段': 7800,
    '传奇3段': 8800,
    '传奇4段': 10800,
    '传奇5段': 12800,
    '传奇6段': 13800,
    '传奇7段': 14800,
    '传奇8段': 15800,
    '传奇9段': 16800,
}

# 用户映射管理
user_id_mapping = {}

def save_user_mapping():
    """保存用户映射到data.ini"""
    try:
        _, data_config_path, _, _ = init_paths()
        
        # 直接创建新的config对象，确保数据一致性
        data_config = configparser.ConfigParser()
        
        # 添加UserMapping节
        if not data_config.has_section('UserMapping'):
            data_config.add_section('UserMapping')
        
        # 保存所有映射
        for adapter_id, qq_number in user_id_mapping.items():
            data_config.set('UserMapping', adapter_id, str(qq_number))
        
        # 确保目录存在
        data_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        with open(data_config_path, 'w', encoding='utf-8') as f:
            data_config.write(f)
        
        logger.info(f"用户映射已保存到 {data_config_path}，共 {len(user_id_mapping)} 个映射")
        return True
        
    except Exception as e:
        logger.error(f"保存用户映射失败: {e}")
        return False

def load_user_mapping():
    """从data.ini加载用户映射"""
    global user_id_mapping
    try:
        _, data_config_path, _, _ = init_paths()
        
        logger.info(f"尝试从 {data_config_path} 加载用户映射")
        
        if not data_config_path.exists():
            logger.warning(f"数据配置文件不存在: {data_config_path}")
            return False
        
        data_config = configparser.ConfigParser()
        # 读取文件
        data_config.read(data_config_path, encoding='utf-8')
        
        loaded_count = 0
        if data_config.has_section('UserMapping'):
            user_id_mapping.clear()  # 清空现有映射
            
            for adapter_id, qq_number in data_config.items('UserMapping'):
                user_id_mapping[adapter_id] = qq_number
                loaded_count += 1
            
            logger.info(f"成功加载 {loaded_count} 个用户映射")
            return loaded_count > 0
        else:
            logger.warning("配置文件中没有找到UserMapping节")
            return False
            
    except Exception as e:
        logger.error(f"加载用户映射失败: {e}")
        return False

def migrate_user_data(adapter_id: str, real_qq: str):
    """将适配器ID的用户数据迁移到真实QQ号"""
    try:
        sign_config_path, _, _, _ = init_paths()
        config = configparser.ConfigParser()
        config.read(sign_config_path, encoding='utf-8')
        
        old_section = f'User-{adapter_id}'
        new_section = f'User-{real_qq}'
        
        # 如果旧section存在
        if config.has_section(old_section):
            # 如果新section不存在，直接迁移
            if not config.has_section(new_section):
                config.add_section(new_section)
                for key, value in config.items(old_section):
                    config.set(new_section, key, value)
                config.remove_section(old_section)
            else:
                # 如果新旧section都存在，需要合并数据而不是简单替换
                # 获取旧数据
                old_sign_count = config.getint(old_section, 'SignCount', fallback=0)
                old_coins = config.getint(old_section, 'Coins', fallback=0)
                old_last_sign = config.get(old_section, 'LastSignDate', fallback='')
                
                # 获取新数据
                new_sign_count = config.getint(new_section, 'SignCount', fallback=0)
                new_coins = config.getint(new_section, 'Coins', fallback=0)
                new_last_sign = config.get(new_section, 'LastSignDate', fallback='')
                
                # 合并数据（取较大值）
                merged_sign_count = max(old_sign_count, new_sign_count)
                merged_coins = max(old_coins, new_coins)
                
                # 比较日期，取较晚的日期
                if old_last_sign and new_last_sign:
                    try:
                        old_date = datetime.strptime(old_last_sign, "%Y-%m-%d")
                        new_date = datetime.strptime(new_last_sign, "%Y-%m-%d")
                        merged_last_sign = old_last_sign if old_date > new_date else new_last_sign
                    except:
                        merged_last_sign = new_last_sign
                else:
                    merged_last_sign = new_last_sign if new_last_sign else old_last_sign
                
                # 更新数据
                config.set(new_section, 'SignCount', str(merged_sign_count))
                config.set(new_section, 'Coins', str(merged_coins))
                config.set(new_section, 'LastSignDate', merged_last_sign)
                
                # 删除旧section
                config.remove_section(old_section)
            
            # 保存配置
            with open(sign_config_path, 'w', encoding='utf-8') as f:
                config.write(f)
                
            print(f"成功迁移用户数据: {adapter_id} -> {real_qq}")
            
    except Exception as e:
        print(f"迁移用户数据时出错: {e}")

# 骚话系统管理函数
def load_chat_lines():
    """加载骚话列表"""
    _, _, _, chat_lines_path = init_paths()
    try:
        with open(chat_lines_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        return lines
    except:
        return ["你今天已经泡过茶了，可不能贪杯哦！"]

def save_chat_lines(chat_lines):
    """保存骚话列表"""
    _, _, _, chat_lines_path = init_paths()
    with open(chat_lines_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(chat_lines))

def add_chat_line(line):
    """添加一条骚话"""
    chat_lines = load_chat_lines()
    if line not in chat_lines:
        chat_lines.append(line)
        save_chat_lines(chat_lines)
        return True
    return False

def delete_chat_line(index):
    """删除指定索引的骚话"""
    chat_lines = load_chat_lines()
    if 0 <= index < len(chat_lines):
        deleted_line = chat_lines.pop(index)
        save_chat_lines(chat_lines)
        return deleted_line
    return None

def get_random_chat_line():
    """随机获取一条骚话"""
    chat_lines = load_chat_lines()
    if chat_lines:
        return random.choice(chat_lines)
    return "你今天已经泡过茶了，可不能贪杯哦！"

# 启动时加载用户映射
def init_plugin():
    """插件初始化"""
    logger.info("开始初始化泡茶插件...")
    
    # 初始化路径
    sign_config_path, data_config_path, image_path, chat_lines_path = init_paths()
    logger.info(f"数据目录: {data_config_path.parent}")
    
    # 先尝试加载用户映射
    if load_user_mapping():
        logger.info(f"用户映射加载成功，当前映射数: {len(user_id_mapping)}")
    else:
        logger.warning("无法加载用户映射文件，使用默认映射")
        # 只有在完全没有映射时才使用默认值
        if not user_id_mapping:
            default_mapping = {
                '7084F51C2C820B6E97CD40B820A0A166': '2529464880',
            }
            user_id_mapping.update(default_mapping)
            if save_user_mapping():
                logger.info("已创建并保存默认用户映射")
            else:
                logger.error("保存默认用户映射失败")
    
    # 检查必要的文件和目录
    if not data_config_path.exists():
        logger.info("创建初始数据配置文件")
        # 确保配置文件存在
        get_configs()
    
    # 检查图片目录
    if image_path.exists():
        image_files = [f for f in os.listdir(image_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        logger.info(f"图片目录包含 {len(image_files)} 张图片")
    
    # 检查骚话文件
    if chat_lines_path.exists():
        chat_lines = load_chat_lines()
        logger.info(f"骚话文件包含 {len(chat_lines)} 条记录")
    
    logger.info(f"泡茶插件初始化完成，当前用户映射数: {len(user_id_mapping)}")

# 在插件加载时初始化
init_plugin()

def get_real_user_id(adapter_user_id: str) -> str:
    """将适配器的用户ID转换为真实QQ号"""
    clean_adapter_id = adapter_user_id.replace('<@', '').replace('>', '')
    real_id = user_id_mapping.get(clean_adapter_id, adapter_user_id)
    
    if real_id != adapter_user_id:
        logger.debug(f"用户ID映射: {adapter_user_id} -> {real_id}")
    else:
        logger.warning(f"未找到用户ID映射，使用原ID: {adapter_user_id}")
    
    return real_id

def format_adapter_id_for_mention(adapter_id: str) -> str:
    """将适配器ID格式化为@的格式"""
    if adapter_id.startswith('<@') and adapter_id.endswith('>'):
        return adapter_id
    return f'<@{adapter_id}>'

# 使用帮助命令
help_cmd = on_command('help', aliases={
    '/帮助', '/help', '/使用帮助', '/命令帮助', '/泡茶帮助',
    '帮助', 'help', '使用帮助', '命令帮助', '泡茶帮助',
    '？', '?', '帮助菜单', '功能列表'
})

# 配置日志
logger = logging.getLogger("nonebot_plugin_paocha")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_plugin_data_dir() / "paocha.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

@help_cmd.handle()
async def help_handler(bot: Bot, event: MessageEvent):
    """显示使用帮助"""
    try:
        # 获取原始消息内容
        raw_message = str(event.get_message()).strip()
        logger.info(f"原始帮助消息: {raw_message}")  # 调试信息
        
        command_prefixes = [
            '/帮助', '/help', '/使用帮助', '/命令帮助', '/泡茶帮助',
            '帮助', 'help', '使用帮助', '命令帮助', '泡茶帮助',
            '？', '?', '帮助菜单', '功能列表'
        ]
        
        command_prefixes.sort(key=len, reverse=True)
        
        matched_prefix = ""
        for prefix in command_prefixes:
            if raw_message.startswith(prefix):
                raw_message = raw_message[len(prefix):].strip()
                matched_prefix = prefix
                break
        
        command_helps = {
            '泡茶': """
🍵🍵🍵 泡茶命令帮助 🍵🍵🍵

命令：泡茶、喝水、sign（可带/也可不带）
*如果是官方适配器，建议使用带/的命令*
功能：每日泡茶签到，获得随机好感度

使用示例：
• 泡茶
• 喝水  
• sign
• /泡茶
• /喝水

说明：
- 每天只能使用一次
- 每次获得1-30点随机好感度
- 新用户首次泡茶获得10点基础好感度
- 泡茶时会随机发送一张图片
            """,
            
            '泡茶表': """
📊📊📊 泡茶查询命令帮助 📊📊📊

命令：泡茶表、泡茶查询、sign_info
功能：查看个人泡茶信息和好感度等级

使用示例：
• 泡茶表
• 泡茶查询
• sign_info
• /泡茶表

显示信息：
- 泡茶总次数
- 总好感度
- 当前段位等级
- 最后泡茶时间
- 距离下一等级所需好感度
            """,
            
            '等级': """
📈📈📈 等级表命令帮助 📈📈📈

命令：等级、等级表
功能：查看好感度等级对应表

使用示例：
• 等级
• 等级表
• /等级

显示信息：
- 所有段位等级和对应的好感度要求
- 从1段到传奇9段的完整等级列表
            """,
            
            '映射用户': """
🔗🔗🔗 用户映射命令帮助 🔗🔗🔗

命令：映射用户
功能：绑定适配器用户ID和真实QQ号的映射关系

使用示例：
• 映射用户 7084F51C2C820B6E97CD40B820A0A166 2529464880
• /映射用户 7084F51C2C820B6E97CD40B820A0A166 2529464880

参数说明：
- 适配器ID：QQ适配器生成的用户ID（去掉<@和>）
- QQ号：真实的QQ号码

查看当前映射：
• 映射用户 （不跟参数）
            """,
            
            '用户列表': """
👥👥👥 用户列表命令帮助 👥👥👥

命令：用户列表、绑定列表、查看用户
功能：查看所有已绑定的用户信息

使用示例：
• 用户列表
• 绑定列表
• 查看用户
• 用户列表 2 （查看第2页）
• /用户列表

显示信息：
- 用户QQ号
- 签到次数
- 总好感度
- 最后签到时间
- 分页显示（每页20个用户）
            """,
            
            '上传图片': """
🖼🖼🖼️ 上传图片命令帮助 🖼🖼🖼️

命令：上传图片、添加图片
功能：上传图片到图片库，泡茶时会随机显示

使用示例：
• 上传图片 （回复一张图片）
• 添加图片 （回复一张图片）
• /上传图片

说明：
- 需要回复一条包含图片的消息
- 支持格式：PNG、JPG、JPEG、GIF
- 图片将保存到data/images文件夹
- 泡茶时会随机显示已上传的图片
            """,
            
            '删除图片': """
🗑🗑🗑 删除图片命令帮助 🗑🗑🗑

命令：删除图片、移除图片
功能：删除图片库中的指定图片

使用示例：
• 删除图片 1 （删除第1张图片）
• 删除图片 upload_20231201093045_1234.jpg
• /删除图片 1

说明：
- 可以按序号删除（使用 图片统计 查看序号）
- 也可以按文件名删除
- 删除后不可恢复，请谨慎操作
            """,
            
            '骚话系统': """
💬💬💬 骚话系统命令帮助 💬💬💬

命令系列：
• 添加骚话 <内容> - 添加一条重复泡茶时的回复
• 删除骚话 <序号> - 删除指定序号的骚话
• 骚话列表 - 查看所有骚话列表
• 骚话统计 - 查看骚话系统统计

使用示例：
• 添加骚话 茶虽好，可不要贪杯哦~
• 删除骚话 3
• 骚话列表
• /骚话列表

说明：
- 用户重复泡茶时会随机选择一条骚话回复
- 可以自定义各种有趣的回复内容
            """
        }
        
        if raw_message:
            clean_command = raw_message.strip()
            
            for cmd, detailed_help in command_helps.items():
                if clean_command in cmd or cmd in clean_command:
                    await help_cmd.finish(detailed_help.strip())
            
            help_text = f"""
❓ 未找到命令 '{raw_message}' 的详细帮助

🍵🍵 泡茶机器人可用命令：

【基础命令】
• 泡茶、喝水 - 每日泡茶签到
• 泡茶表、泡茶查询 - 查看个人信息  
• 等级表 - 查看等级要求

【用户管理】
• 映射用户 - 绑定用户映射
• 用户列表 - 查看绑定用户
• 搜索用户 - 搜索特定用户

【图片管理】
• 上传图片 - 上传图片到图库
• 删除图片 - 删除指定图片
• 图片统计 - 查看图库信息

【骚话系统】
• 添加骚话 - 添加重复泡茶回复
• 删除骚话 - 删除指定骚话
• 骚话列表 - 查看所有骚话
• 骚话统计 - 骚话系统统计

💡💡💡💡💡💡💡💡 使用 '帮助 命令名' 查看详细说明
例如：帮助 泡茶
            """.strip()
            await help_cmd.finish(help_text)
        else:
            help_text = f"""
🍵🍵 泡茶机器人使用帮助 🍵🍵

🎯 命令使用说明：
- 支持带 / 符号的命令：/泡茶、/帮助 等
- 也支持无符号命令：泡茶、帮助 等
- 两种方式都可以使用，按您习惯来！

【基础命令】
• 泡茶、喝水、sign - 每日泡茶签到，获得好感度
• 泡茶表、泡茶查询、sign_info - 查看个人泡茶信息  
• 等级、等级表 - 查看好感度等级对应表

【用户管理命令】
• 映射用户 <适配器ID> <QQ号> - 绑定用户映射
• 用户列表、绑定列表 - 查看所有绑定用户
• 搜索用户 <QQ号或适配器ID> - 搜索特定用户
• 删除用户 <QQ号或适配器ID> - 删除用户映射
• 清除映射 - 清除所有用户映射

【图片管理命令】
• 上传图片、添加图片 - 上传图片到图片库
• 删除图片、移除图片 - 删除指定图片
• 图片统计、图库统计 - 查看图片库信息

【骚话系统命令】
• 添加骚话 <内容> - 添加重复泡茶回复
• 删除骚话 <序号> - 删除指定骚话
• 骚话列表 - 查看所有骚话
• 骚话统计 - 骚话系统统计

💡 使用提示：
- 现在可以不用必须加 / 符号了！
*如果是官方适配器，建议使用带/的命令*
- 查看具体命令帮助：帮助 泡茶

🎯 快速开始：
1. 首次使用先绑定：映射用户 适配器ID QQ号
2. 然后每天：泡茶
3. 查看进度：泡茶表  
4. 丰富图库：上传图片
5. 自定义回复：添加骚话

输入 '帮助 命令名' 查看详细说明！
            """.strip()
            await help_cmd.finish(help_text)
            
    except Exception as e:
        error_help = """
第一次使用请使用"映射用户 原id qq号"命令绑定真实QQ号，方便管理！
        """.strip()
        await help_cmd.finish(error_help)

# 等级表命令
grade = on_command('sign', aliases={
    '/等级', '/等级表', '等级', '等级表', '段位', '等级列表'
})

@grade.handle()
async def re(bot: Bot, event: MessageEvent):
    msg = '\n'.join([f'{k}:{v}' for k, v in level_map.items()])
    msgs = '\n这是当前的等级列表：\n'
    await grade.send(msgs + msg)

# 签到指令
sign = on_command('sign', aliases={
    '/泡茶', '/喝水', '泡茶', '喝水', '签到', '打卡', '喝茶', '沏沏沏沏沏沏沏沏茶'
})
@sign.handle()
async def _(bot: Bot, event: MessageEvent):
    # 获取用户ID
    try:
        adapter_user_id = event.get_user_id()
        logger.info(f"签到请求 - 适配器用户ID: {adapter_user_id}")
    except ArgumentError:
        logger.error("事件对象缺少 get_user_id 方法")
        await sign.finish("❌❌ 系统错误：无法识别用户身份")
        return
    except Exception as e:
        logger.error(f"获取用户ID时出错: {e}", exc_info=True)
        await sign.finish("❌❌ 系统暂时繁忙，请稍后重试")
        return
    
    # 转换为真实QQ号
    real_user_id = get_real_user_id(adapter_user_id)
    logger.info(f"用户ID转换: {adapter_user_id} -> {real_user_id}")
    logger.info(f"当前用户映射状态: {user_id_mapping}")
    
    # 获取配置和路径
    config, _, image_path, _ = get_configs()
    sign_config_path, _, _, _ = init_paths()
    
    section_name = 'User-' + str(real_user_id)
    sign_time = datetime.now().strftime("%Y-%m-%d")
    
    # 本地图片处理
    image_segment = None
    if image_path.exists():
        try:
            image_files = [f for f in os.listdir(image_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            if image_files:
                image_file = random.choice(image_files)
                image_file_path = image_path / image_file
                with open(image_file_path, 'rb') as f:
                    image_data = BytesIO(f.read())
                image_segment = MessageSegment.file_image(image_data)
        except Exception as e:
            print(f"图片加载失败: {e}")
    # 在签到函数中加强日期验证
    def is_same_day(date1_str, date2_str):
        """检查两个日期字符串是否为同一天"""
        try:
            date1 = datetime.strptime(date1_str, "%Y-%m-%d")
            date2 = datetime.strptime(date2_str, "%Y-%m-%d")
            return date1.date() == date2.date()
        except:
            return False
    # 在签到逻辑中使用
    if config.has_section(section_name):
        sign_time_last = config.get(section_name, 'LastSignDate', fallback='')
        if is_same_day(sign_time_last, sign_time):
            # 拒绝签到
            chat_line = get_random_chat_line()
            if image_segment:
                await sign.finish(image_segment + chat_line)
            else:
                await sign.finish(chat_line)
            return  # 添加return确保函数结束
        
        # 修复：添加日期有效性检查
        try:
            last_date = datetime.strptime(sign_time_last, "%Y-%m-%d")
            current_date = datetime.strptime(sign_time, "%Y-%m-%d")
            
            # 如果上次签到日期大于当前日期（系统时间异常）
            if last_date > current_date:
                logger.warning(f"用户 {real_user_id} 系统时间异常，上次签到 {sign_time_last} 大于当前 {sign_time}")
                # 可以选择拒绝签到或允许签到，这里选择允许但记录警告
        except ValueError:
            # 日期格式错误，视为无效记录，允许签到
            logger.warning(f"用户 {real_user_id} 的签到日期格式错误: {sign_time_last}")
    
    # 执行签到逻辑（新用户或新的一天）
    if not config.has_section(section_name):
        config.add_section(section_name)
        config.set(section_name, 'SignCount', '1')
        config.set(section_name, 'Coins', '10')
        config.set(section_name, 'LastSignDate', sign_time)
        
        mention_id = format_adapter_id_for_mention(adapter_user_id)
        message = f'泡茶成功！\n你已泡茶1次，当前好感度为10，当前段位为1段\n距离下一等级还需要40好感度\n原id为{mention_id}\n如果是第一次使用请使用映射用户命令绑定真实QQ号'
        
        if image_segment:
            await sign.send(image_segment + message)
        else:
            await sign.send(message)
    else:
        # 更新现有用户签到信息
        config.set(section_name, 'LastSignDate', sign_time)
        sign_count = config.getint(section_name, 'SignCount', fallback=0) + 1
        coins = config.getint(section_name, 'Coins', fallback=0)
        previous_coins = coins
        coins += random.randint(1, 30)
        new_coins = coins - previous_coins
        config.set(section_name, 'SignCount', str(sign_count))
        config.set(section_name, 'Coins', str(coins))
        
        def get_user_level(coins):
            for level, coin in reversed(level_map.items()):
                if coins >= coin:
                    return level
            return '1段'
        
        level = get_user_level(coins)
        
        def get_coins_to_next_level(coins):
            for level_name, coin_req in level_map.items():
                if coins < coin_req:
                    return level_name, coin_req - coins
            return '最高等级', 0
        
        next_level, coins_needed = get_coins_to_next_level(coins)
        
        mention_id = format_adapter_id_for_mention(adapter_user_id)
        messages = f'泡茶成功！尊敬的指挥官你已泡了{sign_count}次茶\n当前获得{new_coins}好感度\n总好感度为{coins}\n当前泡茶时间为{sign_time}\n当前段位为{level}\n距离下一等级{next_level}还需要{coins_needed}好感度\n原id为{mention_id}\n如果是第一次使用请使用映射用户命令绑定真实QQ号'
        
        if image_segment:
            await sign.finish(image_segment + messages)
        else:
            await sign.finish(messages)
    
    # 保存配置
    with open(sign_config_path, 'w', encoding='utf-8') as f:
        config.write(f)

# 泡茶查询命令
sign_info = on_command('sign_info', aliases={
    '/泡茶表', '/泡茶查询', '泡茶表', '泡茶查询', '我的泡茶', '查询泡茶', '签到记录', '泡茶信息'
})

@sign_info.handle()
async def _(bot: Bot, event: MessageEvent):
    try:
        adapter_user_id = event.get_user_id()
    except Exception as e:
        await sign_info.finish("无法获取用户ID")
    
    real_user_id = get_real_user_id(adapter_user_id)
    
    config, _, _, _ = get_configs()
    section_name = 'User-' + str(real_user_id)
    
    if config.has_section(section_name):
        sign_time_last = config.get(section_name, 'LastSignDate', fallback='')
        sign_count = config.getint(section_name, 'SignCount')
        coins = config.getint(section_name, 'Coins')
        
        def get_user_level(coins):
            for level, coin in reversed(level_map.items()):
                if coins >= coin:
                    return level
            return '1段'
        
        level = get_user_level(coins)
        
        def get_coins_to_next_level(coins):
            for level_name, coin_req in level_map.items():
                if coins < coin_req:
                    return level_name, coin_req - coins
            return '最高等级', 0
        
        next_level, coins_needed = get_coins_to_next_level(coins)
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f'http://q.qlogo.cn/headimg_dl?dst_uin={real_user_id}&spec=640&img_type=jpg', timeout=10.0)
                if response.status_code == 200:
                    avatar_image = MessageSegment.file_image(BytesIO(response.content))
                else:
                    avatar_image = None
        except Exception as e:
            print(f"头像获取失败: {e}")
            avatar_image = None
        
        mention_id = format_adapter_id_for_mention(adapter_user_id)
        msgs = f'尊敬的指挥官\n你的泡茶次数为{sign_count}\n好感度为{coins}\n上次泡茶时间为{sign_time_last}\n现段位为{level}\n距离下一个等级{next_level}还需要{coins_needed}好感度\n原id为{mention_id}\n真实QQ号为{real_user_id}'
        
        if avatar_image:
            await sign_info.finish(avatar_image + msgs)
        else:
            await sign_info.finish(msgs)
    else:
        mention_id = format_adapter_id_for_mention(adapter_user_id)
        msgs = f'尊敬的指挥官你还未加入我们哦！\n请在第一次泡茶后把原id绑定为真实qq，以便查询泡茶信息'
        await sign_info.send(msgs)

# 用户映射命令
user_mapping = on_command('map_user', aliases={
    '/映射用户', '/绑定用户', '映射用户', '绑定用户', '用户映射', '绑定账号'
})

@user_mapping.handle()
async def map_user_handler(bot: Bot, event: MessageEvent):
    try:
        raw_message = str(event.get_message()).strip()
        logger.info(f"收到映射用户命令: {raw_message}")
        
        command_prefixes = ['/映射用户', '/绑定用户', '映射用户', '绑定用户']
        for prefix in command_prefixes:
            if raw_message.startswith(prefix):
                raw_message = raw_message[len(prefix):].strip()
                break
        
        if not raw_message:
            # 显示当前映射
            logger.info("用户请求查看当前映射")
            if user_id_mapping:
                mapping_list = "\n".join([f"{k} -> {v}" for k, v in user_id_mapping.items()])
                await user_mapping.send(f"当前用户映射:\n{mapping_list}")
                logger.info(f"向用户显示了 {len(user_id_mapping)} 个映射")
            else:
                await user_mapping.send("当前没有用户映射")
                logger.warning("用户映射为空")
            return
        
        parts = raw_message.split()
        
        if len(parts) >= 2:
            adapter_id = parts[0]
            real_qq = parts[1]
            
            adapter_id = adapter_id.replace('<@', '').replace('>', '')
            
            if not real_qq.isdigit() or len(real_qq) < 5:
                await user_mapping.send("QQ号格式不正确")
                return
            
            # 记录映射变更
            old_qq = user_id_mapping.get(adapter_id)
            user_id_mapping[adapter_id] = real_qq
            
            if save_user_mapping():
                logger.info(f"用户映射更新成功: {adapter_id} -> {real_qq} (旧映射: {old_qq})")
                
                # 迁移原有数据到新的QQ号
                if old_qq and old_qq != real_qq:
                    migrate_user_data(adapter_id, real_qq)
                
                await user_mapping.send(f"✅ 映射更新成功: {adapter_id} -> {real_qq}\n已迁移原有签到数据")
            else:
                logger.error(f"保存用户映射失败: {adapter_id} -> {real_qq}")
                await user_mapping.send("❌ 映射更新失败，请检查日志")
                
        else:
            await user_mapping.send("参数格式错误，正确格式：映射用户 适配器ID 真实QQ号\n例如：映射用户 7084F51C2C820B6E97CD40B820A0A166 2529464880")
            
    except Exception as e:
        logger.error(f"映射用户时出错: {e}", exc_info=True)
        await user_mapping.send(f"映射用户时出错: {str(e)}")

# 清除映射命令
clear_mapping = on_command('clear_map', aliases={
    '/清除映射', '清除映射', '清空映射', '重置映射'
})

@clear_mapping.handle()
async def clear_map_handler(bot: Bot, event: MessageEvent):
    try:
        user_id_mapping.clear()
        save_user_mapping()
        await clear_mapping.send("已清除所有用户映射")
    except Exception as e:
        await clear_mapping.send(f"清除映射时出错: {str(e)}")

# 用户列表命令
user_list = on_command('user_list', aliases={
    '/用户列表', '/绑定列表', '/查看用户', '用户列表', '绑定列表', '查看用户', '用户管理', '列表用户'
})

@user_list.handle()
async def user_list_handler(bot: Bot, event: MessageEvent):
    try:
        if not user_id_mapping:
            await user_list.send("当前没有绑定任何用户")
            return
        
        config, _, _, _ = get_configs()
        
        user_info_list = []
        total_users = len(user_id_mapping)
        
        user_info_list.append(f"📋 绑定用户列表 (共{total_users}个用户)")
        user_info_list.append("=" * 40)
        
        sorted_users = sorted(user_id_mapping.items(), key=lambda x: x[1])
        
        for i, (adapter_id, qq_number) in enumerate(sorted_users, 1):
            section_name = 'User-' + str(qq_number)
            if config.has_section(section_name):
                sign_count = config.getint(section_name, 'SignCount', fallback=0)
                coins = config.getint(section_name, 'Coins', fallback=0)
                last_sign = config.get(section_name, 'LastSignDate', fallback='从未签到')
                user_info = f"{i}. QQ: {qq_number} | 签到: {sign_count}次 | 好感度: {coins} | 最后签到: {last_sign}"
            else:
                user_info = f"{i}. QQ: {qq_number} | 状态: 未签到"
            
            user_info_list.append(user_info)
        
        if len(user_info_list) > 20:
            page_size = 20
            total_pages = (len(user_info_list) + page_size - 1) // page_size
            
            args = str(event.get_message()).strip()
            page = 1
            for prefix in ['/用户列表', '/绑定列表', '/查看用户', '用户列表', '绑定列表', '查看用户']:
                if args.startswith(prefix):
                    args = args[len(prefix):].strip()
                    break
            
            if args.isdigit():
                page = min(max(1, int(args)), total_pages)
            
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(user_info_list))
            
            page_content = user_info_list[start_idx:end_idx]
            page_info = f"\n第 {page}/{total_pages} 页 (使用 '用户列表 页码' 查看其他页)"
            result = "\n".join(page_content) + page_info
        else:
            result = "\n".join(user_info_list)
        
        await user_list.send(result)
        
    except Exception as e:
        await user_list.send(f"显示用户列表时出错: {str(e)}")

# 搜索用户命令
search_user = on_command('search_user', aliases={
    '/搜索用户', '/查找用户', '搜索用户', '查找用户', '查找', '搜索'
})

@search_user.handle()
async def search_user_handler(bot: Bot, event: MessageEvent):
    try:
        args = str(event.get_message()).strip()
        for prefix in ['/搜索用户', '/查找用户', '搜索用户', '查找用户']:
            if args.startswith(prefix):
                args = args[len(prefix):].strip()
                break
        
        if not args:
            await search_user.send("请输入要搜索的QQ号或适配器ID\n例如：搜索用户 2529464880")
            return
        
        search_term = args
        config, _, _, _ = get_configs()
        
        found_users = []
        for adapter_id, qq_number in user_id_mapping.items():
            if search_term in qq_number or search_term in adapter_id:
                section_name = 'User-' + str(qq_number)
                if config.has_section(section_name):
                    sign_count = config.getint(section_name, 'SignCount', fallback=0)
                    coins = config.getint(section_name, 'Coins', fallback=0)
                    last_sign = config.get(section_name, 'LastSignDate', fallback='从未签到')
                    user_info = f"QQ: {qq_number} | 适配器ID: {adapter_id} | 签到: {sign_count}次 | 好感度: {coins} | 最后签到: {last_sign}"
                else:
                    user_info = f"QQ: {qq_number} | 适配器ID: {adapter_id} | 状态: 未签到"
                found_users.append(user_info)
        
        if found_users:
            result = f"找到 {len(found_users)} 个匹配的用户:\n" + "\n".join(found_users)
        else:
            result = f"未找到包含 '{search_term}' 的用户"
        
        await search_user.send(result)
        
    except Exception as e:
        await search_user.send(f"搜索用户时出错: {str(e)}")

# 删除用户命令
delete_user = on_command('delete_user', aliases={
    '/删除用户', '/移除用户', '删除用户', '移除用户', '移除', '删除'
})

@delete_user.handle()
async def delete_user_handler(bot: Bot, event: MessageEvent):
    try:
        args = str(event.get_message()).strip()
        for prefix in ['/删除用户', '/移除用户', '删除用户', '移除用户']:
            if args.startswith(prefix):
                args = args[len(prefix):].strip()
                break
        
        if not args:
            await delete_user.send("请输入要删除的QQ号或适配器ID\n例如：删除用户 2529464880")
            return
        
        delete_term = args
        
        to_delete = []
        for adapter_id, qq_number in user_id_mapping.items():
            if delete_term == qq_number or delete_term == adapter_id:
                to_delete.append((adapter_id, qq_number))
        
        if to_delete:
            for adapter_id, qq_number in to_delete:
                del user_id_mapping[adapter_id]
            
            save_user_mapping()
            deleted_info = "\n".join([f"适配器ID: {adapter_id} -> QQ: {qq_number}" for adapter_id, qq_number in to_delete])
            await delete_user.send(f"已删除用户映射:\n{deleted_info}")
        else:
            await delete_user.send(f"未找到匹配的用户: {delete_term}")
        
    except Exception as e:
        await delete_user.send(f"删除用户时出错: {str(e)}")

# 上传图片命令
upload_image = on_command('upload_image', aliases={
    '/上传图片', '/添加图片', '上传图片', '添加图片', '上传', '添加图片'
})

@upload_image.handle()
async def upload_image_handler(bot: Bot, event: MessageEvent):
    try:
        message = event.get_message()
        image_segments = []
        
        for segment in message:
            if segment.type == 'image':
                image_segments.append(segment)
        
        if not image_segments:
            await upload_image.finish("请回复一张图片来上传！\n使用示例：回复一张图片并发送 上传图片")
        
        _, _, image_path, _ = init_paths()
        
        success_count = 0
        for i, image_segment in enumerate(image_segments):
            try:
                image_url = image_segment.data.get('url', '') if hasattr(image_segment, 'data') else ''
                
                if not image_url:
                    continue
                
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url, timeout=30.0)
                    
                    if response.status_code == 200:
                        file_extension = '.jpg'
                        content_type = response.headers.get('content-type', '')
                        if 'png' in content_type:
                            file_extension = '.png'
                        elif 'gif' in content_type:
                            file_extension = '.gif'
                        elif 'jpeg' in content_type:
                            file_extension = '.jpeg'
                        
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        random_num = random.randint(1000, 9999)
                        filename = f"upload_{timestamp}_{random_num}{file_extension}"
                        filepath = image_path / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        success_count += 1
                        print(f"图片上传成功: {filename}")
                        
                    else:
                        print(f"图片下载失败，状态码: {response.status_code}")
                        
            except Exception as e:
                print(f"处理第{i+1}张图片时出错: {e}")
                continue
        
        if success_count > 0:
            image_files = [f for f in os.listdir(image_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            total_images = len(image_files)
            
            await upload_image.send(f"✅ 成功上传 {success_count} 张图片！\n📁 图片库现有 {total_images} 张图片")
        else:
            await upload_image.send("❌ 图片上传失败，请检查图片格式或稍后重试")
        
    except Exception as e:
        await upload_image.send(f"上传图片时出错: {str(e)}")

# 删除图片命令
delete_image = on_command('delete_image', aliases={
    '/删除图片', '/移除图片', '删除图片', '移除图片', '删图', '移除图片'
})

@delete_image.handle()
async def delete_image_handler(bot: Bot, event: MessageEvent):
    try:
        args = str(event.get_message()).strip()
        for prefix in ['/删除图片', '/移除图片', '删除图片', '移除图片']:
            if args.startswith(prefix):
                args = args[len(prefix):].strip()
                break
        
        if not args:
            await delete_image.send("请输入要删除的图片序号或文件名\n使用 '图片统计' 查看图片列表\n例如：删除图片 1 或 删除图片 upload_123.jpg")
            return
        
        _, _, image_path, _ = init_paths()
        
        if not image_path.exists():
            await delete_image.send("图片目录不存在")
            return
        
        image_files = [f for f in os.listdir(image_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        if not image_files:
            await delete_image.send("图片库中没有图片")
            return
        
        # 按序号删除
        if args.isdigit():
            index = int(args) - 1
            if 0 <= index < len(image_files):
                filename = image_files[index]
                filepath = image_path / filename
                filepath.unlink()
                await delete_image.send(f"✅ 已删除图片: {filename}")
            else:
                await delete_image.send(f"❌ 图片序号无效，请输入 1-{len(image_files)} 之间的数字")
        # 按文件名删除
        else:
            filename = args
            filepath = image_path / filename
            if filepath.exists() and filepath.is_file():
                filepath.unlink()
                await delete_image.send(f"✅ 已删除图片: {filename}")
            else:
                await delete_image.send(f"❌ 未找到图片: {filename}")
        
    except Exception as e:
        await delete_image.send(f"删除图片时出错: {str(e)}")

# 图片统计命令
image_stats = on_command('image_stats', aliases={
    '/图片统计', '/图库统计', '图片统计', '图库统计', '统计图片', '图库信息'
})

@image_stats.handle()
async def image_stats_handler(bot: Bot, event: MessageEvent):
    try:
        _, _, image_path, _ = init_paths()
        
        if not image_path.exists():
            await image_stats.send("图片目录不存在")
            return
        
        image_files = [f for f in os.listdir(image_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        total_images = len(image_files)
        
        if total_images == 0:
            await image_stats.send("图库中暂无图片\n使用 上传图片 命令添加图片")
            return
        
        ext_stats = {}
        for file in image_files:
            ext = os.path.splitext(file)[1].lower()
            ext_stats[ext] = ext_stats.get(ext, 0) + 1
        
        stats_text = f"📊 图片库统计信息\n"
        stats_text += f"📁 总图片数: {total_images} 张\n"
        stats_text += "📈 格式分布:\n"
        
        for ext, count in ext_stats.items():
            percentage = (count / total_images) * 100
            stats_text += f"  {ext}: {count}张 ({percentage:.1f}%)\n"
        
        stats_text += f"\n🆕 图片列表 (共{total_images}张):\n"
        
        image_files_with_time = []
        for file in image_files:
            filepath = image_path / file
            mtime = os.path.getmtime(filepath)
            image_files_with_time.append((file, mtime))
        
        image_files_with_time.sort(key=lambda x: x[1], reverse=True)
        
        for i, (file, mtime) in enumerate(image_files_with_time, 1):
            upload_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            stats_text += f"  {i}. {file} ({upload_time})\n"
            if i >= 20:  # 只显示前20个
                if total_images > 20:
                    stats_text += f"  ... 还有 {total_images - 20} 张图片未显示\n"
                break
        
        stats_text += f"\n💡 使用 '删除图片 序号' 删除指定图片"
        
        await image_stats.send(stats_text)
        
    except Exception as e:
        await image_stats.send(f"获取图片统计时出错: {str(e)}")

# 骚话系统命令
# 添加骚话命令
add_chat_line_cmd = on_command('add_chat_line', aliases={
    '/添加骚话', '/添加回复', '添加骚话', '添加回复', '新增骚话'
})

@add_chat_line_cmd.handle()
async def add_chat_line_handler(bot: Bot, event: MessageEvent):
    try:
        args = str(event.get_message()).strip()
        for prefix in ['/添加骚话', '/添加回复', '添加骚话', '添加回复']:
            if args.startswith(prefix):
                args = args[len(prefix):].strip()
                break
        
        if not args:
            await add_chat_line_cmd.send("请输入要添加的骚话内容\n例如：添加骚话 茶虽好，可不要贪杯哦~")
            return
        
        if add_chat_line(args):
            chat_lines = load_chat_lines()
            await add_chat_line_cmd.send(f"✅ 骚话添加成功！\n当前共有 {len(chat_lines)} 条骚话")
        else:
            await add_chat_line_cmd.send("❌ 骚话已存在，无需重复添加")
        
    except Exception as e:
        await add_chat_line_cmd.send(f"添加骚话时出错: {str(e)}")

# 删除骚话命令
delete_chat_line_cmd = on_command('delete_chat_line', aliases={
    '/删除骚话', '/移除骚话', '删除骚话', '移除骚话', '删骚话'
})

@delete_chat_line_cmd.handle()
async def delete_chat_line_handler(bot: Bot, event: MessageEvent):
    try:
        args = str(event.get_message()).strip()
        for prefix in ['/删除骚话', '/移除骚话', '删除骚话', '移除骚话']:
            if args.startswith(prefix):
                args = args[len(prefix):].strip()
                break
        
        if not args:
            await delete_chat_line_cmd.send("请输入要删除的骚话序号\n使用 '骚话列表' 查看序号\n例如：删除骚话 3")
            return
        
        if not args.isdigit():
            await delete_chat_line_cmd.send("请输入有效的数字序号")
            return
        
        index = int(args) - 1
        deleted_line = delete_chat_line(index)
        
        if deleted_line:
            chat_lines = load_chat_lines()
            await delete_chat_line_cmd.send(f"✅ 骚话删除成功！\n已删除: {deleted_line}\n剩余 {len(chat_lines)} 条骚话")
        else:
            await delete_chat_line_cmd.send("❌ 骚话序号无效")
        
    except Exception as e:
        await delete_chat_line_cmd.send(f"删除骚话时出错: {str(e)}")

# 骚话列表命令
chat_lines_list = on_command('chat_lines_list', aliases={
    '/骚话列表', '/回复列表', '骚话列表', '回复列表', '查看骚话', '骚话查看'
})

@chat_lines_list.handle()
async def chat_lines_list_handler(bot: Bot, event: MessageEvent):
    try:
        chat_lines = load_chat_lines()
        
        if not chat_lines:
            await chat_lines_list.send("当前没有骚话，使用 '添加骚话' 命令添加")
            return
        
        list_text = f"💬 骚话列表 (共{len(chat_lines)}条):\n"
        list_text += "=" * 40 + "\n"
        
        for i, line in enumerate(chat_lines, 1):
            list_text += f"{i}. {line}\n"
        
        list_text += f"\n💡 使用 '删除骚话 序号' 删除指定骚话"
        
        await chat_lines_list.send(list_text)
        
    except Exception as e:
        await chat_lines_list.send(f"获取骚话列表时出错: {str(e)}")

# 骚话统计命令
chat_lines_stats = on_command('chat_lines_stats', aliases={
    '/骚话统计', '/回复统计', '骚话统计', '回复统计', '统计骚话'
})

@chat_lines_stats.handle()
async def chat_lines_stats_handler(bot: Bot, event: MessageEvent):
    try:
        chat_lines = load_chat_lines()
        total_lines = len(chat_lines)
        
        stats_text = f"📊 骚话系统统计\n"
        stats_text += f"💬 总骚话数: {total_lines} 条\n"
        
        if total_lines > 0:
            # 计算平均长度
            avg_length = sum(len(line) for line in chat_lines) / total_lines
            stats_text += f"📏 平均长度: {avg_length:.1f} 字符\n"
            
            # 显示最近添加的几条
            stats_text += f"\n🆕 最近添加的骚话:\n"
            recent_lines = chat_lines[-5:] if total_lines > 5 else chat_lines
            for i, line in enumerate(recent_lines, 1):
                stats_text += f"  {total_lines - len(recent_lines) + i}. {line}\n"
        
        stats_text += f"\n💡 使用 '骚话列表' 查看完整列表"
        
        await chat_lines_stats.send(stats_text)
        
    except Exception as e:
        await chat_lines_stats.send(f"获取骚话统计时出错: {str(e)}")