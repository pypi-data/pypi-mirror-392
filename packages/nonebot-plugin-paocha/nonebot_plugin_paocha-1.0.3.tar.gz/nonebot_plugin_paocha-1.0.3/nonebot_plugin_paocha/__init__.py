from nonebot import on_command, get_driver
from nonebot.adapters.qq import Bot, MessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from datetime import datetime
import random
import os
import base64
import configparser
from pathlib import Path
from io import BytesIO

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="泡茶签到插件",
    description="茶饮签到系统，包含等级管理和图片上传功能",
    usage="使用 '泡茶' 命令开始使用",
    type="application",
    homepage="https://github.com/mmxd12/nonebot-plugin-paocha",
    supported_adapters={"nonebot.adapters.qq"},
)

__version__ = "1.0.2"

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
    
    # 确保目录存在
    image_path.mkdir(parents=True, exist_ok=True)
    
    return sign_config_path, data_config_path, image_path

# 延迟初始化配置
def get_configs():
    """获取配置对象"""
    sign_config_path, data_config_path, image_path = init_paths()
    
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
    
    return config, data_config, image_path

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
    data_config, _, _ = get_configs()
    if not data_config.has_section('UserMapping'):
        data_config.add_section('UserMapping')
    
    # 清空现有的映射
    if data_config.has_section('UserMapping'):
        for key in list(data_config['UserMapping'].keys()):
            data_config.remove_option('UserMapping', key)
    
    # 保存新的映射
    for adapter_id, qq_number in user_id_mapping.items():
        data_config.set('UserMapping', adapter_id, qq_number)
    
    # 保存到数据目录的data.ini文件
    _, data_config_path, _ = init_paths()
    with open(data_config_path, 'w', encoding='utf-8') as f:
        data_config.write(f)

def load_user_mapping():
    """从data.ini加载用户映射"""
    _, data_config_path, _ = init_paths()
    data_config, _, _ = get_configs()
    
    if data_config_path.exists():
        data_config.read(data_config_path, encoding='utf-8')
        if data_config.has_section('UserMapping'):
            user_id_mapping.clear()
            for adapter_id, qq_number in data_config.items('UserMapping'):
                user_id_mapping[adapter_id] = qq_number
            return True
    return False

# 启动时加载用户映射
def init_plugin():
    """插件初始化"""
    load_user_mapping()
    
    # 如果没有加载到数据，使用默认映射
    if not user_id_mapping:
        user_id_mapping.update({
            '7084F51C2C820B6E97CD40B820A0A166': '2529464880',
        })
        save_user_mapping()  # 保存默认映射

# 在插件加载时初始化
init_plugin()

def get_real_user_id(adapter_user_id: str) -> str:
    """将适配器的用户ID转换为真实QQ号"""
    clean_adapter_id = adapter_user_id.replace('<@', '').replace('>', '')
    return user_id_mapping.get(clean_adapter_id, adapter_user_id)

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

@help_cmd.handle()
async def help_handler(bot: Bot, event: MessageEvent):
    """显示使用帮助"""
    try:
        raw_message = str(event.get_message()).strip()
        
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
            '泡茶': "泡茶命令帮助内容...",
            '泡茶表': "泡茶查询命令帮助内容...",
            # ... 其他帮助内容保持不变
        }
        
        if raw_message:
            clean_command = raw_message.strip()
            
            for cmd, detailed_help in command_helps.items():
                if clean_command in cmd or cmd in clean_command:
                    await help_cmd.finish(detailed_help.strip())
            
            help_text = f"未找到命令 '{raw_message}' 的详细帮助..."
            await help_cmd.finish(help_text)
        else:
            help_text = "泡茶机器人使用帮助..."
            await help_cmd.finish(help_text)
            
    except Exception as e:
        error_help = "泡茶机器人使用帮助-简易版..."
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
    '/泡茶', '/喝水', '泡茶', '喝水', '签到', '打卡', '喝茶', '沏沏茶'
})

@sign.handle()
async def _(bot: Bot, event: MessageEvent):
    try:
        adapter_user_id = event.get_user_id()
    except Exception as e:
        await sign.finish("无法获取用户ID")
    
    real_user_id = get_real_user_id(adapter_user_id)
    
    # 获取配置和路径
    config, _, image_path = get_configs()
    sign_config_path, _, _ = init_paths()
    
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
    
    config, _, _ = get_configs()
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
        
        command_prefixes = ['/映射用户', '/绑定用户', '映射用户', '绑定用户']
        for prefix in command_prefixes:
            if raw_message.startswith(prefix):
                raw_message = raw_message[len(prefix):].strip()
                break
        
        if not raw_message:
            if user_id_mapping:
                mapping_list = "\n".join([f"{k} -> {v}" for k, v in user_id_mapping.items()])
                await user_mapping.send(f"当前用户映射:\n{mapping_list}")
            else:
                await user_mapping.send("当前没有用户映射")
            return
        
        parts = raw_message.split()
        
        if len(parts) >= 2:
            adapter_id = parts[0]
            real_qq = parts[1]
            
            adapter_id = adapter_id.replace('<@', '').replace('>', '')
            
            if not real_qq.isdigit() or len(real_qq) < 5:
                await user_mapping.send("QQ号格式不正确")
                return
            
            user_id_mapping[adapter_id] = real_qq
            save_user_mapping()
            await user_mapping.send(f"映射更新成功: {adapter_id} -> {real_qq}")
        else:
            await user_mapping.send("参数格式错误，正确格式：映射用户 适配器ID 真实QQ号\n例如：映射用户 7084F51C2C820B6E97CD40B820A0A166 2529464880")
            
    except Exception as e:
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
        
        config, _, _ = get_configs()
        
        user_info_list = []
        total_users = len(user_id_mapping)
        
        user_info_list.append(f"📋📋 绑定用户列表 (共{total_users}个用户)")
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
        config, _, _ = get_configs()
        
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
        
        _, _, image_path = init_paths()
        
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
            
            await upload_image.send(f"✅ 成功上传 {success_count} 张图片！\n📁📁 图片库现有 {total_images} 张图片")
        else:
            await upload_image.send("❌❌ 图片上传失败，请检查图片格式或稍后重试")
        
    except Exception as e:
        await upload_image.send(f"上传图片时出错: {str(e)}")

# 图片统计命令
image_stats = on_command('image_stats', aliases={
    '/图片统计', '/图库统计', '图片统计', '图库统计', '统计图片', '图库信息'
})

@image_stats.handle()
async def image_stats_handler(bot: Bot, event: MessageEvent):
    try:
        _, _, image_path = init_paths()
        
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
        
        stats_text = f"📊📊 图片库统计信息\n"
        stats_text += f"📁📁 总图片数: {total_images} 张\n"
        stats_text += "📈📈 格式分布:\n"
        
        for ext, count in ext_stats.items():
            percentage = (count / total_images) * 100
            stats_text += f"  {ext}: {count}张 ({percentage:.1f}%)\n"
        
        stats_text += f"\n🆕🆕🆕 最近上传的5张图片:\n"
        
        image_files_with_time = []
        for file in image_files:
            filepath = image_path / file
            mtime = os.path.getmtime(filepath)
            image_files_with_time.append((file, mtime))
        
        image_files_with_time.sort(key=lambda x: x[1], reverse=True)
        recent_files = image_files_with_time[:5]
        
        for i, (file, mtime) in enumerate(recent_files, 1):
            upload_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            stats_text += f"  {i}. {file} ({upload_time})\n"
        
        await image_stats.send(stats_text)
        
    except Exception as e:
        await image_stats.send(f"获取图片统计时出错: {str(e)}")