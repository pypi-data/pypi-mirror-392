from nonebot import on_command
from ctypes import ArgumentError
from nonebot.adapters.qq import Bot, MessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from datetime import datetime
import random
import json
import os
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

__version__ = "1.1.0"

# 使用 NoneBot 的数据目录
def get_plugin_data_dir():
    """获取插件数据目录"""
    data_dir = Path.cwd() / "data" / "paocha"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

# 初始化路径
def init_paths():
    """初始化路径配置"""
    data_dir = get_plugin_data_dir()
    
    # JSON文件路径
    user_data_path = data_dir / 'user_data.json'  # 用户数据和映射数据
    chat_data_path = data_dir / 'chat_data.json'  # 骚话数据
    image_path = data_dir / 'images'
    
    # 确保目录存在
    image_path.mkdir(parents=True, exist_ok=True)
    
    return user_data_path, chat_data_path, image_path

# 等级映射表
level_map = {
    '1段': 50, '2段': 100, '3段': 150, '4段': 200, '5段': 250,
    '6段': 350, '7段': 450, '8段': 550, '9段': 650, '10段': 750,
    '11段': 900,'12段': 1050,'13段': 1200,'14段': 1350,'15段': 1500,
    '16段': 1700,'17段': 1900,'18段': 2100,'19段': 2300,'20段': 2500,
    '21段': 2750,'22段': 3000,'23段': 3250,'24段': 3500,'25段': 3750,
    '26段': 4050,'27段': 4350,'28段': 4650,'29段': 4950,'30段': 5550,
    '传奇1段': 6800,'传奇2段': 7800, '传奇3段': 8800, '传奇4段': 10800,
    '传奇5段': 12800,'传奇6段': 13800,'传奇7段': 14800,'传奇8段': 15800,
    '传奇9段': 16800,
}

# 用户数据管理
class UserDataManager:
    def __init__(self):
        self.user_data_path, self.chat_data_path, self.image_path = init_paths()
        self.user_data = self.load_user_data()
        self.chat_data = self.load_chat_data()
    
    def load_user_data(self):
        """加载用户数据"""
        if self.user_data_path.exists():
            try:
                with open(self.user_data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 确保数据结构完整
                    if 'user_mapping' not in data:
                        data['user_mapping'] = {}
                    if 'user_info' not in data:
                        data['user_info'] = {}
                    return data
            except Exception:
                # 如果文件损坏，创建默认结构
                pass
        
        # 默认数据结构
        default_data = {
            'user_mapping': {
                '7084F51C2C820B6E97CD40B820A0A166': '2529464880',
            },
            'user_info': {}
        }
        self.save_user_data(default_data)
        return default_data
    
    def load_chat_data(self):
        """加载骚话数据"""
        if self.chat_data_path.exists():
            try:
                with open(self.chat_data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 确保数据结构完整
                    if 'chat_lines' not in data:
                        data['chat_lines'] = ["你今天已经泡过茶了，可不能贪杯哦！"]
                    return data
            except Exception:
                # 如果文件损坏，创建默认结构
                pass
        
        # 默认骚话数据
        default_data = {
            'chat_lines': ["你今天已经泡过茶了，可不能贪杯哦！"]
        }
        self.save_chat_data(default_data)
        return default_data
    
    def save_user_data(self, data=None):
        """保存用户数据"""
        if data is None:
            data = self.user_data
        with open(self.user_data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_chat_data(self, data=None):
        """保存骚话数据"""
        if data is None:
            data = self.chat_data
        with open(self.chat_data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_real_user_id(self, adapter_user_id: str) -> str:
        """将适配器的用户ID转换为真实QQ号"""
        clean_adapter_id = adapter_user_id.replace('<@', '').replace('>', '')
        return self.user_data['user_mapping'].get(clean_adapter_id, adapter_user_id)
    
    def add_user_mapping(self, adapter_id: str, real_qq: str):
        """添加用户映射"""
        clean_adapter_id = adapter_id.replace('<@', '').replace('>', '')
        self.user_data['user_mapping'][clean_adapter_id] = real_qq
        self.save_user_data()
    
    def migrate_user_data(self, adapter_id: str, real_qq: str):
        """将适配器ID的用户数据迁移到真实QQ号"""
        try:
            clean_adapter_id = adapter_id.replace('<@', '').replace('>', '')
            old_section = f'User-{clean_adapter_id}'
            new_section = f'User-{real_qq}'
            
            # 如果旧数据存在
            if old_section in self.user_data['user_info']:
                old_data = self.user_data['user_info'][old_section]
                
                # 如果新数据不存在，直接迁移
                if new_section not in self.user_data['user_info']:
                    self.user_data['user_info'][new_section] = old_data
                else:
                    # 合并数据
                    new_data = self.user_data['user_info'][new_section]
                    
                    # 合并签到次数和好感度（取较大值）
                    merged_sign_count = max(
                        old_data.get('SignCount', 0), 
                        new_data.get('SignCount', 0)
                    )
                    merged_coins = max(
                        old_data.get('Coins', 0), 
                        new_data.get('Coins', 0)
                    )
                    
                    # 比较日期，取较晚的日期
                    old_last_sign = old_data.get('LastSignDate', '')
                    new_last_sign = new_data.get('LastSignDate', '')
                    
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
                    self.user_data['user_info'][new_section].update({
                        'SignCount': merged_sign_count,
                        'Coins': merged_coins,
                        'LastSignDate': merged_last_sign
                    })
                
                # 删除旧数据
                del self.user_data['user_info'][old_section]
                self.save_user_data()
                
                print(f"成功迁移用户数据: {adapter_id} -> {real_qq}")
                
        except Exception as e:
            print(f"迁移用户数据时出错: {e}")
    
    def get_user_info(self, real_user_id: str):
        """获取用户信息"""
        section_name = f'User-{real_user_id}'
        return self.user_data['user_info'].get(section_name, {})
    
    def update_user_info(self, real_user_id: str, user_info: dict):
        """更新用户信息"""
        section_name = f'User-{real_user_id}'
        self.user_data['user_info'][section_name] = user_info
        self.save_user_data()
    
    def get_all_users(self):
        """获取所有用户信息"""
        return self.user_data['user_info']
    
    def get_user_mapping(self):
        """获取用户映射"""
        return self.user_data['user_mapping']
    
    def clear_user_mapping(self):
        """清空用户映射"""
        self.user_data['user_mapping'] = {}
        self.save_user_data()
    
    def delete_user(self, identifier: str):
        """删除用户"""
        # 尝试通过QQ号删除
        for section_name in list(self.user_data['user_info'].keys()):
            if section_name == f'User-{identifier}':
                del self.user_data['user_info'][section_name]
                self.save_user_data()
                return True
        
        # 尝试通过适配器ID删除映射
        for adapter_id, qq_number in list(self.user_data['user_mapping'].items()):
            if identifier == adapter_id or identifier == qq_number:
                del self.user_data['user_mapping'][adapter_id]
                self.save_user_data()
                return True
        
        return False

# 骚话系统管理
class ChatDataManager:
    def __init__(self, user_data_manager):
        self.user_data_manager = user_data_manager
    
    def load_chat_lines(self):
        """加载骚话列表"""
        return self.user_data_manager.chat_data.get('chat_lines', [])
    
    def save_chat_lines(self, chat_lines):
        """保存骚话列表"""
        self.user_data_manager.chat_data['chat_lines'] = chat_lines
        self.user_data_manager.save_chat_data()
    
    def add_chat_line(self, line):
        """添加一条骚话"""
        chat_lines = self.load_chat_lines()
        if line not in chat_lines:
            chat_lines.append(line)
            self.save_chat_lines(chat_lines)
            return True
        return False
    
    def delete_chat_line(self, index):
        """删除指定索引的骚话"""
        chat_lines = self.load_chat_lines()
        if 0 <= index < len(chat_lines):
            deleted_line = chat_lines.pop(index)
            self.save_chat_lines(chat_lines)
            return deleted_line
        return None
    
    def get_random_chat_line(self):
        """随机获取一条骚话"""
        chat_lines = self.load_chat_lines()
        if chat_lines:
            return random.choice(chat_lines)
        return "你今天已经泡过茶了，可不能贪杯哦！"

# 初始化数据管理器
data_manager = UserDataManager()
chat_manager = ChatDataManager(data_manager)

def format_adapter_id_for_mention(adapter_id: str) -> str:
    """将适配器ID格式化为@的格式"""
    if adapter_id.startswith('<@') and adapter_id.endswith('>'):
        return adapter_id
    return f'<@{adapter_id}>'

def is_same_day(date1_str, date2_str):
    """检查两个日期字符串是否为同一天"""
    try:
        date1 = datetime.strptime(date1_str, "%Y-%m-%d")
        date2 = datetime.strptime(date2_str, "%Y-%m-%d")
        return date1.date() == date2.date()
    except:
        return False

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
        help_text = """
🍵🍵 泡茶机器人使用帮助 🍵🍵🍵

主要命令：
• 泡茶/签到 - 每日泡茶签到
• 泡茶表 - 查看个人泡茶记录
• 等级表 - 查看等级要求
• 映射用户 [适配器ID] [QQ号]
• 用户列表 - 查看所有用户
• 上传图片 - 上传签到图片
• 图片统计 - 查看图片库
• 骚话列表 - 查看所有骚话
• 添加骚话 [内容] - 添加新骚话

第一次泡茶请使用"映射用户 原id qq号"命令绑定真实QQ号！
        """.strip()
        await help_cmd.finish(help_text)
    except Exception as e:
        error_help = """
其他命令：
• 清除映射 - 清空所有用户映射
• 搜索用户 [QQ号/适配器ID] - 搜索绑定用户
• 删除用户 [QQ号/适配器ID] - 删除绑定用户
• 删除图片 [序号/文件名] - 删除图库中的图片
• 删除骚话 [序号] - 删除指定骚话
• 泡茶帮助 - 显示帮助信息
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
    '/泡茶', '/喝水', '泡茶', '喝水', '签到', '打卡', '喝茶', '沏沏茶'
})

@sign.handle()
async def _(bot: Bot, event: MessageEvent):
    # 获取用户ID
    try:
        adapter_user_id = event.get_user_id()
    except ArgumentError:
        await sign.finish("❌❌ 系统错误：无法识别用户身份")
    except Exception as e:
        await sign.finish("❌❌ 系统暂时繁忙，请稍后重试")
    
    # 转换为真实QQ号
    real_user_id = data_manager.get_real_user_id(adapter_user_id)
    
    # 本地图片处理
    image_segment = None
    image_path = data_manager.image_path
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
    
    sign_time = datetime.now().strftime("%Y-%m-%d")
    user_info = data_manager.get_user_info(real_user_id)
    
    # 检查是否已经签到
    if user_info and 'LastSignDate' in user_info:
        sign_time_last = user_info['LastSignDate']
        if is_same_day(sign_time_last, sign_time):
            # 拒绝签到
            chat_line = chat_manager.get_random_chat_line()
            if image_segment:
                await sign.finish(image_segment + chat_line)
            else:
                await sign.finish(chat_line)
            return
    
    # 执行签到逻辑（新用户或新的一天）
    if not user_info:
        # 新用户
        new_user_info = {
            'SignCount': 1,
            'Coins': 10,
            'LastSignDate': sign_time
        }
        data_manager.update_user_info(real_user_id, new_user_info)
        
        mention_id = format_adapter_id_for_mention(adapter_user_id)
        message = f'泡茶成功！\n你已泡茶1次，当前好感度为10，当前段位为1段\n距离下一等级还需要40好感度\n原id为{mention_id}\n如果是第一次泡茶请使用映射用户命令绑定真实QQ号'
        
        if image_segment:
            await sign.send(image_segment + message)
        else:
            await sign.send(message)
    else:
        # 更新现有用户签到信息
        sign_count = user_info.get('SignCount', 0) + 1
        coins = user_info.get('Coins', 0)
        previous_coins = coins
        coins += random.randint(1, 30)
        new_coins = coins - previous_coins
        
        updated_info = {
            'SignCount': sign_count,
            'Coins': coins,
            'LastSignDate': sign_time
        }
        data_manager.update_user_info(real_user_id, updated_info)
        
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
        messages = f'泡茶成功！尊敬的指挥官你已泡了{sign_count}次茶\n当前获得{new_coins}好感度\n总好感度为{coins}\n当前泡茶时间为{sign_time}\n当前段位为{level}\n距离下一等级{next_level}还需要{coins_needed}好感度\n原id为{mention_id}\n使用“泡茶帮助”查看更多指令'
        
        if image_segment:
            await sign.finish(image_segment + messages)
        else:
            await sign.finish(messages)

# 泡茶查询命令
sign_info = on_command('sign_info', aliases={
    '/泡茶表', '/泡茶查询', '泡茶表', '泡茶查询', '我的泡茶', '查询泡茶', '签到记录', '泡茶信息'
})

@sign_info.handle()
async def _(bot: Bot, event: MessageEvent):
    try:
        adapter_user_id = event.get_user_id()
    except Exception:
        await sign_info.finish("无法获取用户ID")
    
    real_user_id = data_manager.get_real_user_id(adapter_user_id)
    user_info = data_manager.get_user_info(real_user_id)
    
    if user_info:
        sign_time_last = user_info.get('LastSignDate', '')
        sign_count = user_info.get('SignCount', 0)
        coins = user_info.get('Coins', 0)
        
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
        
        # 获取头像
        avatar_image = None
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f'http://q.qlogo.cn/headimg_dl?dst_uin={real_user_id}&spec=640&img_type=jpg', timeout=10.0)
                if response.status_code == 200:
                    avatar_image = MessageSegment.file_image(BytesIO(response.content))
        except Exception:
            pass
        
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
            # 显示当前映射
            user_mapping_data = data_manager.get_user_mapping()
            if user_mapping_data:
                mapping_list = "\n".join([f"{k} -> {v}" for k, v in user_mapping_data.items()])
                await user_mapping.send(f"当前用户映射:\n{mapping_list}")
            else:
                await user_mapping.send("当前没有用户映射")
            return
        
        parts = raw_message.split()
        
        if len(parts) >= 2:
            adapter_id = parts[0]
            real_qq = parts[1]
            
            if not real_qq.isdigit() or len(real_qq) < 5:
                await user_mapping.send("QQ号格式不正确")
                return
            
            data_manager.add_user_mapping(adapter_id, real_qq)
            data_manager.migrate_user_data(adapter_id, real_qq)
            
            await user_mapping.send(f"映射更新成功: {adapter_id} -> {real_qq}\n已迁移原有签到数据")
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
        data_manager.clear_user_mapping()
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
        user_mapping_data = data_manager.get_user_mapping()
        all_users = data_manager.get_all_users()
        
        if not user_mapping_data:
            await user_list.send("当前没有绑定任何用户")
            return
        
        user_info_list = []
        total_users = len(user_mapping_data)
        
        user_info_list.append(f"📋📋 绑定用户列表 (共{total_users}个用户)")
        user_info_list.append("=" * 40)
        
        sorted_users = sorted(user_mapping_data.items(), key=lambda x: x[1])
        
        for i, (adapter_id, qq_number) in enumerate(sorted_users, 1):
            section_name = f'User-{qq_number}'
            if section_name in all_users:
                user_data = all_users[section_name]
                sign_count = user_data.get('SignCount', 0)
                coins = user_data.get('Coins', 0)
                last_sign = user_data.get('LastSignDate', '从未签到')
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
        user_mapping_data = data_manager.get_user_mapping()
        all_users = data_manager.get_all_users()
        
        found_users = []
        for adapter_id, qq_number in user_mapping_data.items():
            if search_term in qq_number or search_term in adapter_id:
                section_name = f'User-{qq_number}'
                if section_name in all_users:
                    user_data = all_users[section_name]
                    sign_count = user_data.get('SignCount', 0)
                    coins = user_data.get('Coins', 0)
                    last_sign = user_data.get('LastSignDate', '从未签到')
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
        
        if data_manager.delete_user(delete_term):
            await delete_user.send(f"已删除用户: {delete_term}")
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
        
        image_path = data_manager.image_path
        
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
            await upload_image.send("❌❌ 图片上传失败，请检查图片格式或稍后重试")
        
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
        
        image_path = data_manager.image_path
        
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
                await delete_image.send(f"❌❌ 图片序号无效，请输入 1-{len(image_files)} 之间的数字")
        # 按文件名删除
        else:
            filename = args
            filepath = image_path / filename
            if filepath.exists() and filepath.is_file():
                filepath.unlink()
                await delete_image.send(f"✅ 已删除图片: {filename}")
            else:
                await delete_image.send(f"❌❌ 未找到图片: {filename}")
        
    except Exception as e:
        await delete_image.send(f"删除图片时出错: {str(e)}")

# 图片统计命令
image_stats = on_command('image_stats', aliases={
    '/图片统计', '/图库统计', '图片统计', '图库统计', '统计图片', '图库信息'
})

@image_stats.handle()
async def image_stats_handler(bot: Bot, event: MessageEvent):
    try:
        image_path = data_manager.image_path
        
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
        
        if chat_manager.add_chat_line(args):
            chat_lines = chat_manager.load_chat_lines()
            await add_chat_line_cmd.send(f"✅ 骚话添加成功！\n当前共有 {len(chat_lines)} 条骚话")
        else:
            await add_chat_line_cmd.send("❌❌ 骚话已存在，无需重复添加")
        
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
        deleted_line = chat_manager.delete_chat_line(index)
        
        if deleted_line:
            chat_lines = chat_manager.load_chat_lines()
            await delete_chat_line_cmd.send(f"✅ 骚话删除成功！\n已删除: {deleted_line}\n剩余 {len(chat_lines)} 条骚话")
        else:
            await delete_chat_line_cmd.send("❌❌ 骚话序号无效")
        
    except Exception as e:
        await delete_chat_line_cmd.send(f"删除骚话时出错: {str(e)}")

# 骚话列表命令
chat_lines_list = on_command('chat_lines_list', aliases={
    '/骚话列表', '/回复列表', '骚话列表', '回复列表', '查看骚话', '骚话查看'
})

@chat_lines_list.handle()
async def chat_lines_list_handler(bot: Bot, event: MessageEvent):
    try:
        chat_lines = chat_manager.load_chat_lines()
        
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
        chat_lines = chat_manager.load_chat_lines()
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