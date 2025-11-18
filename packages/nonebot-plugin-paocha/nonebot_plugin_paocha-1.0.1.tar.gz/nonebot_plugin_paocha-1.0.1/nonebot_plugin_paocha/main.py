from ctypes import ArgumentError
from nonebot import on_command
from nonebot.adapters.qq import Bot, MessageEvent, MessageSegment
from datetime import datetime
import random
import os
import logging
import configparser
from pathlib import Path
from io import BytesIO
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="泡茶签到插件",
    description="茶饮签到系统，包含等级管理和图片上传功能",
    usage="使用 '泡茶' 命令开始使用",
    type="application",
    homepage="https://github.com/mmxd12/nonebot-plugin-paocha",
    supported_adapters={"nonebot.adapters.qq"},
)

# 使用插件数据目录（推荐方式）
PLUGIN_DIR = Path(__file__).parent
DATA_DIR = PLUGIN_DIR / "data"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)

# 配置文件路径 - 放在data目录下
SIGN_CONFIG_PATH = DATA_DIR / 'sign.ini'
DATA_CONFIG_PATH = DATA_DIR / 'data.ini'
IMAGE_PATH = DATA_DIR / 'images'

# 确保images目录存在
IMAGE_PATH.mkdir(parents=True, exist_ok=True)

# 初始化配置文件
config = configparser.ConfigParser()
data_config = configparser.ConfigParser()

# 如果配置文件不存在，创建它们
if not SIGN_CONFIG_PATH.exists():
    with open(SIGN_CONFIG_PATH, 'w', encoding='utf-8') as f:
        config.write(f)
else:
    config.read(SIGN_CONFIG_PATH, encoding='utf-8')

if not DATA_CONFIG_PATH.exists():
    with open(DATA_CONFIG_PATH, 'w', encoding='utf-8') as f:
        data_config.write(f)
else:
    data_config.read(DATA_CONFIG_PATH, encoding='utf-8')


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

def save_user_mapping():
    """保存用户映射到data.ini（data目录）"""
    if not data_config.has_section('UserMapping'):
        data_config.add_section('UserMapping')
    
    # 清空现有的映射
    if data_config.has_section('UserMapping'):
        for key in list(data_config['UserMapping'].keys()):
            data_config.remove_option('UserMapping', key)
    
    # 保存新的映射
    for adapter_id, qq_number in user_id_mapping.items():
        data_config.set('UserMapping', adapter_id, qq_number)
    
    # 保存到data目录的data.ini文件
    with open(DATA_CONFIG_PATH, 'w', encoding='utf-8') as f:
        data_config.write(f)

def load_user_mapping():
    """从data.ini（data目录）加载用户映射"""
    if DATA_CONFIG_PATH.exists():
        data_config.read(DATA_CONFIG_PATH, encoding='utf-8')
        if data_config.has_section('UserMapping'):
            user_id_mapping.clear()
            for adapter_id, qq_number in data_config.items('UserMapping'):
                user_id_mapping[adapter_id] = qq_number
            return True
    return False

# 启动时加载用户映射
user_id_mapping = {}
load_user_mapping()

# 如果没有加载到数据，使用默认映射
if not user_id_mapping:
    user_id_mapping = {
        '7084F51C2C820B6E97CD40B820A0A166': '2529464880',
    }
    save_user_mapping()  # 保存默认映射

def get_real_user_id(adapter_user_id: str) -> str:
    """将适配器的用户ID转换为真实QQ号"""
    # 去掉<@和>符号，只保留中间文字
    clean_adapter_id = adapter_user_id.replace('<@', '').replace('>', '')
    # 如果适配器用户ID在映射表中，返回映射的QQ号，否则返回原ID
    return user_id_mapping.get(clean_adapter_id, adapter_user_id)

def format_adapter_id_for_mention(adapter_id: str) -> str:
    """将适配器ID格式化为@的格式"""
    # 如果已经是<@格式，直接返回
    if adapter_id.startswith('<@') and adapter_id.endswith('>'):
        return adapter_id
    # 否则添加<@和>
    return f'<@{adapter_id}>'

# 使用帮助命令 - 支持多种触发方式
help_cmd = on_command('help', aliases={
    '/帮助', '/help', '/使用帮助', '/命令帮助', '/泡茶帮助',  # 带斜杠
    '帮助', 'help', '使用帮助', '命令帮助', '泡茶帮助',        # 无符号
    '？', '?', '帮助菜单', '功能列表'                           # 更多友好方式
})

# 配置日志
logger = logging.getLogger("nonebot_plugin_paocha")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / "paocha.log", encoding='utf-8'),
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
        
        # 定义所有可能的命令前缀（包括无前缀）
        command_prefixes = [
            '/帮助', '/help', '/使用帮助', '/命令帮助', '/泡茶帮助',
            '帮助', 'help', '使用帮助', '命令帮助', '泡茶帮助',
            '？', '?', '帮助菜单', '功能列表'
        ]
        
        # 按长度排序，优先匹配长前缀
        command_prefixes.sort(key=len, reverse=True)
        
        # 移除命令前缀
        matched_prefix = ""
        for prefix in command_prefixes:
            if raw_message.startswith(prefix):
                raw_message = raw_message[len(prefix):].strip()
                matched_prefix = prefix
                break
        
        # 定义详细命令帮助
        command_helps = {
            '泡茶': """
🍵🍵 泡茶命令帮助 🍵🍵🍵

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
📊📊 泡茶查询命令帮助 📊📊

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
📈📈 等级表命令帮助 📈📈

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
🔗🔗 用户映射命令帮助 🔗🔗

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
👥👥 用户列表命令帮助 👥👥

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
            """
        }
        
        # 如果有具体命令请求，显示详细帮助
        if raw_message:
            # 处理命令参数
            clean_command = raw_message.strip()
            
            for cmd, detailed_help in command_helps.items():
                if clean_command in cmd or cmd in clean_command:
                    await help_cmd.finish(detailed_help.strip())
            
            # 如果没有找到具体命令，显示通用帮助
            help_text = f"""
❓❓ 未找到命令 '{raw_message}' 的详细帮助

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

💡💡 使用 '帮助 命令名' 查看详细说明
例如：帮助 泡茶
            """.strip()
            await help_cmd.finish(help_text)
        else:
            # 显示完整帮助信息
            help_text = f"""
🍵🍵 泡茶机器人使用帮助 🍵🍵🍵

🎯🎯 命令使用说明：
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

💡💡 使用提示：
- 现在可以不用必须加 / 符号了！
*如果是官方适配器，建议使用带/的命令*
- 查看具体命令帮助：帮助 泡茶

🎯🎯 快速开始：
1. 首次使用先绑定：映射用户 适配器ID QQ号
2. 然后每天：泡茶
3. 查看进度：泡茶表  
4. 丰富图库：上传图片

输入 '帮助 命令名' 查看详细说明！
            """.strip()
            await help_cmd.finish(help_text)
            
    except Exception as e:
        # 简化错误提示，不显示具体路径
        error_help = """
🍵🍵 泡茶机器人使用帮助-简易版

基本命令：
• 泡茶 - 每日签到
• 泡茶表 - 查看信息  
• 等级表 - 查看等级
• 映射用户 - 绑定用户
• 上传图片 - 上传图片

💡💡 提示：命令可带/也可不带，按您习惯使用！
*如果是官方适配器，建议使用带/的命令！！！*
        """.strip()
        await help_cmd.finish(error_help)

# 等级表命令 - 支持无符号触发
grade = on_command('sign', aliases={
    '/等级', '/等级表',    # 带斜杠
    '等级', '等级表',      # 无符号
    '段位', '等级列表'     # 更多友好名称
})


@grade.handle()
async def re(bot: Bot, event: MessageEvent):
    msg = '\n'.join([f'{k}:{v}' for k, v in level_map.items()])
    msgs = '\n这是当前的等级列表：\n'
    await grade.send(msgs + msg)

# 签到指令 - 支持无符号触发
sign = on_command('sign', aliases={
    '/泡茶', '/喝水',      # 带斜杠  
    '泡茶', '喝水',        # 无符号
    '签到', '打卡',        # 更多友好名称
    '喝茶', '沏沏茶'         # 同义词
})


@sign.handle()
async def _(bot: Bot, event: MessageEvent):
    # 获取用户ID
    try:
        adapter_user_id = event.get_user_id()
    except ArgumentError:
        logger.error("事件对象缺少 get_user_id 方法")
        await sign.finish("❌ 系统错误：无法识别用户身份")
    except Exception as e:
        logger.error(f"获取用户ID时出错: {e}", exc_info=True)
        await sign.finish("❌ 系统暂时繁忙，请稍后重试")
    
    # 转换为真实QQ号
    real_user_id = get_real_user_id(adapter_user_id)
    logger.debug(f"用户ID: {adapter_user_id}, 真实QQ号: {real_user_id}")
    
    section_name = 'User-' + str(real_user_id)
    sign_time = datetime.now().strftime("%Y-%m-%d")
    
    # 本地图片处理
    image_segment = None
    if IMAGE_PATH.exists():
        try:
            image_files = [f for f in os.listdir(IMAGE_PATH) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            if image_files:
                image_file = random.choice(image_files)
                image_path = IMAGE_PATH / image_file
                with open(image_path, 'rb') as f:
                    image_data = BytesIO(f.read())
                image_segment = MessageSegment.file_image(image_data)
        except FileNotFoundError:
            logging.warning("图片目录不存在，跳过图片加载")
            image_segment = None
        except PermissionError:
            logging.error("没有权限访问图片目录")
            image_segment = None
        except Exception as e:
            logger.error(f"图片加载失败: {e}")
            image_segment = None
    
    # 检查是否已经签到过
    if config.has_section(section_name):
        sign_time_last = config.get(section_name, 'LastSignDate', fallback='')

        if sign_time_last == sign_time:
            message = '你今天已经泡过茶了，可不能贪杯哦！'
            if image_segment:
                await sign.finish(image_segment + message)
            else:
                await sign.finish(message)
        else:
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
    else:
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
    
    # 保存到data目录的sign.ini文件
    with open(SIGN_CONFIG_PATH, 'w', encoding='utf-8') as f:
        config.write(f)

# 泡茶查询命令 - 支持无符号触发
sign_info = on_command('sign_info', aliases={
    '/泡茶表', '/泡茶查询',    # 带斜杠
    '泡茶表', '泡茶查询',      # 无符号  
    '我的泡茶', '查询泡茶',    # 更多友好名称
    '签到记录', '泡茶信息'      # 同义词
})


@sign_info.handle()
async def _(bot: Bot, event: MessageEvent):
    # 获取用户ID
    try:
        adapter_user_id = event.get_user_id()
    except Exception as e:
        await sign_info.finish("无法获取用户ID")
    
    # 转换为真实QQ号
    real_user_id = get_real_user_id(adapter_user_id)
    
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
        
        # 获取用户头像图片
        try:
            import httpx
            # 使用真实QQ号获取头像
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

# 用户映射命令 - 支持无符号触发
user_mapping = on_command('map_user', aliases={
    '/映射用户', '/绑定用户',    # 带斜杠
    '映射用户', '绑定用户',      # 无符号
    '用户映射', '绑定账号'       # 更多友好名称
})


@user_mapping.handle()
async def map_user_handler(bot: Bot, event: MessageEvent):
    """映射用户ID命令"""
    try:
        # 获取原始消息
        raw_message = str(event.get_message()).strip()
        
        # 移除命令前缀（包括无符号的）
        command_prefixes = ['/映射用户', '/绑定用户', '映射用户', '绑定用户']
        for prefix in command_prefixes:
            if raw_message.startswith(prefix):
                raw_message = raw_message[len(prefix):].strip()
                break
        
        # 如果没有参数，显示当前映射
        if not raw_message:
            if user_id_mapping:
                mapping_list = "\n".join([f"{k} -> {v}" for k, v in user_id_mapping.items()])
                await user_mapping.send(f"当前用户映射:\n{mapping_list}")
            else:
                await user_mapping.send("当前没有用户映射")
            return
        
        # 解析参数格式：适配器ID 真实QQ号
        parts = raw_message.split()
        
        if len(parts) >= 2:
            adapter_id = parts[0]
            real_qq = parts[1]
            
            # 去掉参数中可能存在的<@和>符号
            adapter_id = adapter_id.replace('<@', '').replace('>', '')
            
            # 验证QQ号格式
            if not real_qq.isdigit() or len(real_qq) < 5:
                await user_mapping.send("QQ号格式不正确")
                return
            
            # 更新映射
            user_id_mapping[adapter_id] = real_qq
            save_user_mapping()
            await user_mapping.send(f"映射更新成功: {adapter_id} -> {real_qq}")
        else:
            await user_mapping.send("参数格式错误，正确格式：映射用户 适配器ID 真实QQ号\n例如：映射用户 7084F51C2C820B6E97CD40B820A0A166 2529464880")
            
    except Exception as e:
        await user_mapping.send(f"映射用户时出错: {str(e)}")

# 清除映射命令 - 支持无符号触发
clear_mapping = on_command('clear_map', aliases={
    '/清除映射',        # 带斜杠
    '清除映射',        # 无符号
    '清空映射',        # 同义词
    '重置映射'         # 更多友好名称
})


@clear_mapping.handle()
async def clear_map_handler(bot: Bot, event: MessageEvent):
    """清除用户映射命令"""
    try:
        user_id_mapping.clear()
        save_user_mapping()
        await clear_mapping.send("已清除所有用户映射")
    except Exception as e:
        await clear_mapping.send(f"清除映射时出错: {str(e)}")

# 用户列表命令 - 支持无符号触发
user_list = on_command('user_list', aliases={
    '/用户列表', '/绑定列表', '/查看用户',    # 带斜杠
    '用户列表', '绑定列表', '查看用户',        # 无符号
    '用户管理', '列表用户'                    # 更多友好名称
})


@user_list.handle()
async def user_list_handler(bot: Bot, event: MessageEvent):
    """显示绑定用户列表命令"""
    try:
        if not user_id_mapping:
            await user_list.send("当前没有绑定任何用户")
            return
        
        # 创建用户列表信息
        user_info_list = []
        total_users = len(user_id_mapping)
        
        user_info_list.append(f"📋📋 绑定用户列表 (共{total_users}个用户)")
        user_info_list.append("=" * 40)
        
        # 按QQ号排序显示
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
        
        # 分页显示
        if len(user_info_list) > 20:
            page_size = 20
            total_pages = (len(user_info_list) + page_size - 1) // page_size
            
            # 获取页码参数
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

# 搜索用户命令 - 支持无符号触发
search_user = on_command('search_user', aliases={
    '/搜索用户', '/查找用户',    # 带斜杠
    '搜索用户', '查找用户',      # 无符号
    '查找', '搜索'              # 简写
})


@search_user.handle()
async def search_user_handler(bot: Bot, event: MessageEvent):
    """搜索用户命令"""
    try:
        # 获取搜索关键词
        args = str(event.get_message()).strip()
        for prefix in ['/搜索用户', '/查找用户', '搜索用户', '查找用户']:
            if args.startswith(prefix):
                args = args[len(prefix):].strip()
                break
        
        if not args:
            await search_user.send("请输入要搜索的QQ号或适配器ID\n例如：搜索用户 2529464880")
            return
        
        search_term = args
        
        # 搜索用户
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

# 删除用户命令 - 支持无符号触发
delete_user = on_command('delete_user', aliases={
    '/删除用户', '/移除用户',    # 带斜杠
    '删除用户', '移除用户',      # 无符号
    '移除', '删除'              # 简写
})


@delete_user.handle()
async def delete_user_handler(bot: Bot, event: MessageEvent):
    """删除用户映射命令"""
    try:
        # 获取要删除的QQ号或适配器ID
        args = str(event.get_message()).strip()
        for prefix in ['/删除用户', '/移除用户', '删除用户', '移除用户']:
            if args.startswith(prefix):
                args = args[len(prefix):].strip()
                break
        
        if not args:
            await delete_user.send("请输入要删除的QQ号或适配器ID\n例如：删除用户 2529464880")
            return
        
        delete_term = args
        
        # 查找要删除的用户
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

# 上传图片命令 - 支持无符号触发
upload_image = on_command('upload_image', aliases={
    '/上传图片', '/添加图片',    # 带斜杠
    '上传图片', '添加图片',      # 无符号
    '上传', '添加图片'          # 简写
})


@upload_image.handle()
async def upload_image_handler(bot: Bot, event: MessageEvent):
    """上传图片到images文件夹命令"""
    try:
        # 检查消息是否包含图片
        message = event.get_message()
        image_segments = []
        
        # 提取消息中的所有图片
        for segment in message:
            if segment.type == 'image':
                image_segments.append(segment)
        
        if not image_segments:
            await upload_image.finish("请回复一张图片来上传！\n使用示例：回复一张图片并发送 上传图片")
        
        # 处理每张图片
        success_count = 0
        for i, image_segment in enumerate(image_segments):
            try:
                # 获取图片URL并下载
                image_url = image_segment.data.get('url', '') if hasattr(image_segment, 'data') else ''
                
                if not image_url:
                    continue
                
                # 下载图片
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url, timeout=30.0)
                    
                    if response.status_code == 200:
                        # 生成唯一文件名
                        file_extension = '.jpg'  # 默认扩展名
                        content_type = response.headers.get('content-type', '')
                        if 'png' in content_type:
                            file_extension = '.png'
                        elif 'gif' in content_type:
                            file_extension = '.gif'
                        elif 'jpeg' in content_type:
                            file_extension = '.jpeg'
                        
                        # 使用时间戳和随机数生成唯一文件名
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        random_num = random.randint(1000, 9999)
                        filename = f"upload_{timestamp}_{random_num}{file_extension}"
                        filepath = IMAGE_PATH / filename
                        
                        # 保存图片
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
            # 统计当前图片总数
            image_files = [f for f in os.listdir(IMAGE_PATH) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            total_images = len(image_files)
            
            await upload_image.send(f"✅ 成功上传 {success_count} 张图片！\n📁📁 图片库现有 {total_images} 张图片")
        else:
            await upload_image.send("❌❌ 图片上传失败，请检查图片格式或稍后重试")
        
    except Exception as e:
        await upload_image.send(f"上传图片时出错: {str(e)}")

# 图片统计命令 - 支持无符号触发
image_stats = on_command('image_stats', aliases={
    '/图片统计', '/图库统计',    # 带斜杠
    '图片统计', '图库统计',      # 无符号
    '统计图片', '图库信息'       # 更多友好名称
})


@image_stats.handle()
async def image_stats_handler(bot: Bot, event: MessageEvent):
    """显示图片库统计信息"""
    try:
        if not IMAGE_PATH.exists():
            await image_stats.send("图片目录不存在")
            return
        
        image_files = [f for f in os.listdir(IMAGE_PATH) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        total_images = len(image_files)
        
        if total_images == 0:
            await image_stats.send("图库中暂无图片\n使用 上传图片 命令添加图片")
            return
        
        # 按扩展名统计
        ext_stats = {}
        for file in image_files:
            ext = os.path.splitext(file)[1].lower()
            ext_stats[ext] = ext_stats.get(ext, 0) + 1
        
        stats_text = f"📊📊 图片库统计信息\n"
        stats_text += f"📁📁 总图片数: {total_images} 张\n"
        stats_text += "📈📈 格式分布:\n"
        
        for ext, count in ext_stats.items():
            percentage = (count / total_images) * 100
            stats_text += f"  {ext}: {count}张 ({percentage:.1f}%)\n"
        
        # 显示最近上传的5张图片
        stats_text += f"\n🆕🆕🆕 最近上传的5张图片:\n"
        
        # 按修改时间排序
        image_files_with_time = []
        for file in image_files:
            filepath = IMAGE_PATH / file
            mtime = os.path.getmtime(filepath)
            image_files_with_time.append((file, mtime))
        
        # 按时间倒序排列
        image_files_with_time.sort(key=lambda x: x[1], reverse=True)
        recent_files = image_files_with_time[:5]
        
        for i, (file, mtime) in enumerate(recent_files, 1):
            upload_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            stats_text += f"  {i}. {file} ({upload_time})\n"
        
        await image_stats.send(stats_text)
        
    except Exception as e:
        await image_stats.send(f"获取图片统计时出错: {str(e)}")