"""
TeleBot Wizard - Command Line Interface
Bu modul CLI orqali wizard kutubxonasini ishlatish uchun mo'ljallangan.
Author: Yoqubov Javohir
Version: 1.0.0
"""

import argparse
import json
import sys
from pathlib import Path

from . import BotWizard, __version__
from .exceptions import WizardError


def create_bot_command(args):
    try:
        if not args.token:
            print("❌ Bot tokeni berilmagan!")
            return 1
            
        if ':' not in args.token:
            print("❌ Token format noto'g'ri! To'g'ri format: 1234567890:ABCdef...")
            return 1
        
        w = BotWizard(args.token)
        
        if args.test and not w.test_connection():
            print("❌ Bot tokeni noto'g'ri!")
            return 1
        
        if not args.skip_main_menu:
            w.menu("Asosiy")
            w.button("Salom", reply="Botga xush kelibsiz!")
            w.button("Info", reply="TeleBot Wizard yordamida qurilgan!")
        
        if args.buttons:
            for button_spec in args.buttons:
                parts = button_spec.split(':')
                if len(parts) == 2:
                    name, reply = parts
                    w.button(name, reply=reply)
                elif len(parts) == 3:
                    name, mode, content = parts
                    if mode == 'reply':
                        w.button(name, reply=content)
                    elif mode == 'run':
                        w.button(name, run=content)
        
        output_file = args.output or "bot.py"
        w.generate(output_file)
        
        print(f"✅ Bot '{output_file}' fayliga muvaffaqiyatli yaratildi!")
        
        if args.verbose:
            print("\n📊 Bot konfiguratsiyasi:")
            print(w.get_menus_summary())
        
        return 0
        
    except Exception as e:
        print(f"❌ Xatolik: {str(e)}")
        return 1


def validate_config_command(args):
    try:
        config_file = Path(args.config)
        if not config_file.exists():
            print(f"❌ Konfiguratsiya fayli topilmadi: {config_file}")
            return 1
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("🔍 Konfiguratsiya tekshirilmoqda...")
        
        if 'token' not in config:
            print("❌ Token topilmadi!")
            return 1
        
        if 'menus' not in config:
            print("❌ Menus topilmadi!")
            return 1
        
        total_buttons = sum(len(buttons) for buttons in config['menus'].values())
        print(f"✅ Topilgan menular: {len(config['menus'])}")
        print(f"✅ Jami tugmalar: {total_buttons}")
        
        if args.test_token:
            token = config['token']
            if token.endswith('...'):
                print("⚠️ Token qisqartirilgan. To'liq token kerak test uchun.")
                return 1
            
            w = BotWizard(token)
            if w.test_connection():
                print("✅ Bot tokeni to'g'ri!")
            else:
                print("❌ Bot tokeni noto'g'ri!")
                return 1
        
        print("🎉 Konfiguratsiya to'g'ri!")
        return 0
        
    except json.JSONDecodeError:
        print("❌ JSON format noto'g'ri!")
        return 1
    except Exception as e:
        print(f"❌ Xatolik: {str(e)}")
        return 1


def export_config_command(args):
    try:
        if not args.token:
            print("❌ Bot tokeni berilmagan!")
            return 1
        
        w = BotWizard(args.token)
        
        w.menu("Asosiy")
        w.button("Salom", reply="Xush kelibsiz!")
        w.button("Info", reply="Bot haqida ma'lumot")
        
        output_file = args.output or "bot_config.json"
        w.export_config(output_file)
        
        print(f"✅ Konfiguratsiya '{output_file}' fayliga eksport qilindi!")
        return 0
        
    except Exception as e:
        print(f"❌ Xatolik: {str(e)}")
        return 1


def info_command(args):
    print(f"TeleBot Wizard v{__version__}")
    print("Zero-Code Telegram Bot Builder for TeleBot")
    print()
    print("Havola: https://t.me/UzMaxBoy")
    print("Email: rakuzenuz@gmail.com")
    print()
    print("Foydalanish misoli:")
    print("  telebot-wizard create --token YOUR_TOKEN")
    print("  telebot-wizard validate --config config.json")
    print("  telebot-wizard export --token YOUR_TOKEN")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="telebot-wizard",
        description="TeleBot uchun Zero-Code Bot Builder",
        epilog="Batafsil ma'lumot: https://t.me/RaKUZEN_UZ"
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'telebot-wizard {__version__}'
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        help='Mavjud buyruqlar',
        metavar='COMMAND'
    )
    
    create_parser = subparsers.add_parser(
        'create',
        help='Yangi bot yaratish'
    )
    create_parser.add_argument(
        'token',
        help='Telegram bot tokeni'
    )
    create_parser.add_argument(
        '--output', '-o',
        help='Chiqish fayl nomi (default: bot.py)'
    )
    create_parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Bot tokenini tekshirish'
    )
    create_parser.add_argument(
        '--button', '-b',
        action='append',
        help='Tugma qo\'shish (format: name:reply yoki name:run:code)',
        dest='buttons'
    )
    create_parser.add_argument(
        '--skip-main-menu',
        action='store_true',
        help='Asosiy menuni yaratmaslik'
    )
    create_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Batafsil chiqish'
    )
    create_parser.set_defaults(func=create_bot_command)
    
    validate_parser = subparsers.add_parser(
        'validate',
        help='Konfiguratsiyani tekshirish'
    )
    validate_parser.add_argument(
        'config',
        help='Konfiguratsiya fayl yo\'li'
    )
    validate_parser.add_argument(
        '--test-token',
        action='store_true',
        help='Token ni test qilish'
    )
    validate_parser.set_defaults(func=validate_config_command)
    
    export_parser = subparsers.add_parser(
        'export',
        help='Namuna konfiguratsiyani eksport qilish'
    )
    export_parser.add_argument(
        'token',
        help='Telegram bot tokeni'
    )
    export_parser.add_argument(
        '--output', '-o',
        help='Chiqish fayl nomi (default: bot_config.json)'
    )
    export_parser.set_defaults(func=export_config_command)
    
    info_parser = subparsers.add_parser(
        'info',
        help='Paket haqida ma\'lumot'
    )
    info_parser.set_defaults(func=info_command)
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())