"""
TeleBot Wizard - Zero-Code Bot Builder
Bu kutubxona orqali foydalanuvchilar hech qanday kod yozmasdan
pyTelegramBotAPI yordamida professional Telegram botlar yarata olishadi.
Author: Yoqubov Javohir
Version: 1.0.0
Python: 3.8+
"""

import os
from typing import List, Dict, Optional, Union
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from .exceptions import WizardError, ConfigurationError, GenerationError

class BotWizard:
    
    def __init__(self, token: str):
       
        if not token or not isinstance(token, str):
            raise ValueError("Bot tokeni berilishi shart!")
            
        self.token = token
        self.bot = None
        self.menus: Dict[str, List[Dict]] = {}
        self.current_menu: Optional[str] = None
        self.menu_order: List[str] = []
        self.generated_functions: List[str] = []
        self._validate_token()
        
    def _validate_token(self) -> None:
        
        if ':' not in self.token:
            raise ConfigurationError("Token format noto'g'ri! To'g'ri format: 1234567890:ABCdef...")
            
        parts = self.token.split(':')
        if len(parts) != 2 or not parts[0].isdigit():
            raise ConfigurationError("Token format noto'g'ri!")
            
    def menu(self, name: str) -> 'BotWizard':
        
        if not name or not isinstance(name, str):
            raise ValueError("Menu nomi berilishi shart!")
            
        if name in self.menus:
            raise WizardError(f"Menu '{name}' allaqachon mavjud!")
            
        self.menus[name] = []
        self.menu_order.append(name)
        self.current_menu = name
        return self
        
    def button(self, name: str, reply: str = None, run: str = None) -> 'BotWizard':
        
        if not name or not isinstance(name, str):
            raise ValueError("Tugma nomi berilishi shart!")
            
        if not self.current_menu:
            raise WizardError("Avval menu() metodini chaqiring!")
            
        if reply is None and run is None:
            raise ValueError("Kamida reply yoki run parametri berilishi shart!")
            
        if reply is not None and run is not None:
            raise ValueError("Faqat bitta rejim (reply yoki run) tanlanishi mumkin!")
            
        for existing_button in self.menus[self.current_menu]:
            if existing_button['name'] == name:
                raise WizardError(f"Tugma '{name}' allaqachon mavjud!")
                
        button_data = {
            'name': name,
            'reply': reply,
            'run': run
        }
        
        self.menus[self.current_menu].append(button_data)
        return self
        
    def generate(self, filename: str, include_comments: bool = True) -> None:
      
        if not self.token:
            raise ValueError("Bot tokeni berilmagan!")
            
        if not self.menus:
            raise ValueError("Kamida bitta menu yaratilishi shart!")
            
        generated_code = self._build_bot_code(include_comments)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(generated_code)
            print(f"✅ Bot kodi '{filename}' fayliga muvaffaqiyatli yozildi!")
        except Exception as e:
            raise GenerationError(f"Faylni yaratishda xatolik: {str(e)}")
            
    def _build_bot_code(self, include_comments: bool = True) -> str:
        code_lines = []
        
        if include_comments:
            code_lines.extend([
                "\"\"\"",
                f"Auto-generated bot kodi - {self.token[:10]}...",
                f"TeleBot Wizard v{__version__} tomonidan yaratilgan",
                f"Yaratilgan sana: {self._get_timestamp()}",
                "\"\"\"",
                "",
            ])
            
        code_lines.extend([
            "import telebot",
            "from telebot.types import ReplyKeyboardMarkup, KeyboardButton",
            "",
            f"bot = telebot.TeleBot('{self.token}')",
            "",
            "# Auto-generated nadar va tugmalar",
            "menus = {}"
        ])
        
        for menu_name in self.menu_order:
            buttons = self.menus[menu_name]
            code_lines.append(f"menus['{menu_name}'] = {{}}")
            
            for button in buttons:
                name = button['name']
                if button['reply']:
                    escaped_reply = button['reply'].replace("'", "\\'")
                    code_lines.append(f"menus['{menu_name}']['{name}'] = '{escaped_reply}'")
                elif button['run']:
                    # Run rejimi uchun kodni escape qilish
                    escaped_code = button['run'].replace("'", "\\'")
                    code_lines.append(f"menus['{menu_name}']['{name}'] = 'RUN:{escaped_code}'")
                    
        code_lines.append("")
        
        code_lines.extend([
            "def create_keyboard(menu_name):",
            "    \"\"\"Menuga mos keyboard yaratish.\"\"\"",
            "    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)",
            "    if menu_name in menus:",
            "        for button_name in menus[menu_name].keys():",
            "            markup.add(KeyboardButton(button_name))",
            "    return markup",
            ""
        ])
        
        code_lines.extend([
            "@bot.message_handler(commands=['start', 'help'])",
            "def start_handler(message):",
            "    \"\"\"Start komandasi uchun handler.\"\"\"",
            "    bot.reply_to(message, 'Salom! Botni ishlatish uchun tugmalarni bosing:', ",
            "                reply_markup=create_keyboard('{}'))".format(self.menu_order[0] if self.menu_order else 'Asosiy'),
            ""
        ])
        
        for menu_name in self.menu_order:
            func_name = self._safe_function_name(menu_name)
            code_lines.extend([
                f"@bot.message_handler(func=lambda m: m.text == '{menu_name}')",
                f"def menu_{func_name}(message):",
                f"    \"\"\"{menu_name} menu handler.\"\"\"",
                f"    bot.send_message(message.chat.id, '{menu_name} menyu:', ",
                f"                reply_markup=create_keyboard('{menu_name}'))",
                ""
            ])
        
        all_buttons = []
        for menu_name in self.menu_order:
            for button in self.menus[menu_name]:
                all_buttons.append(button)
                
        for button in all_buttons:
            name = button['name']
            reply = button['reply']
            run = button['run']
            func_name = self._safe_function_name(name)
            
            if reply:
                escaped_reply = reply.replace("'", "\\'")
                code_lines.extend([
                    f"@bot.message_handler(func=lambda m: m.text == '{name}')",
                    f"def button_{func_name}(message):",
                    f"    \"\"\"{name} tugma handler.\"\"\"",
                    f"    bot.reply_to(message, '{escaped_reply}')",
                    ""
                ])
            elif run:
                code_lines.extend([
                    f"@bot.message_handler(func=lambda m: m.text == '{name}')",
                    f"def button_{func_name}(message):",
                    f"    \"\"\"{name} tugma handler (run rejimi).\"\"\"",
                    "    try:",
                    f"        code = '''{run.replace('return ', '')}'''",
                    "        result = eval(code)",
                    f"        bot.reply_to(message, str(result))",
                    "    except Exception as e:",
                    "        bot.reply_to(message, f'Xatolik: {str(e)}')",
                    ""
                ])
        
        code_lines.extend([
            "if __name__ == '__main__':",
            "    print('🤖 Bot ishga tushmoqda...')",
            "    bot.infinity_polling(timeout=10, long_polling_timeout=5)",
            ""
        ])
        
        return "\n".join(code_lines)
        
    def _safe_function_name(self, name: str) -> str:
        safe_name = name.replace(' ', '_').lower()
        
        if safe_name and safe_name[0].isdigit():
            safe_name = 'btn_' + safe_name
            
        import re
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', safe_name)
        
        if not safe_name:
            safe_name = 'func_' + str(hash(name))
            
        return safe_name
        
    def _get_timestamp(self) -> str:
       
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def test_connection(self) -> bool:
       
        try:
            self.bot = TeleBot(self.token)
            bot_info = self.bot.get_me()
            print(f"✅ Bot ulanishi muvaffaqiyatli! Bot: @{bot_info.username}")
            return True
        except Exception as e:
            print(f"❌ Bot ulanish xatoligi: {str(e)}")
            return False
            
    def get_menus_summary(self) -> str:
       
        summary = f"BotWizard konfiguratsiyasi:\n"
        summary += f"Token: {self.token[:10]}...\n"
        summary += f"Menus: {len(self.menus)}\n"
        summary += f"Jami tugmalar: {sum(len(buttons) for buttons in self.menus.values())}\n"
        
        for menu_name in self.menu_order:
            buttons = self.menus[menu_name]
            summary += f"  - {menu_name}: {len(buttons)} tugma\n"
            
        return summary
        
    def get_button_count(self) -> int:
     
        return sum(len(buttons) for buttons in self.menus.values())
        
    def export_config(self, filename: str) -> None:
       
        import json
        
        config = {
            'token': self.token[:10] + '...',  # Token xavfsizligi uchun
            'menus': {},
            'menu_order': self.menu_order,
            'export_timestamp': self._get_timestamp(),
            'version': '1.0.0'
        }
        
        for menu_name in self.menu_order:
            config['menus'][menu_name] = self.menus[menu_name]
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Konfiguratsiya '{filename}' fayliga eksport qilindi!")
        
    def validate_configuration(self) -> Dict[str, bool]:
      
        results = {
            'token_valid': bool(self.token),
            'menus_exist': bool(self.menus),
            'menu_order_correct': len(self.menu_order) == len(self.menus),
            'no_empty_menus': all(len(buttons) > 0 for buttons in self.menus.values())
        }
        
        return results


__version__ = "1.0.0"
__author__ = "Joqubov Javohir"