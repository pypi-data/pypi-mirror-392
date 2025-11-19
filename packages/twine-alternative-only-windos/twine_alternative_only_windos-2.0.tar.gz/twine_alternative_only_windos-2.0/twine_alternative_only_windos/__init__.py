import os
import sys
import argparse
import subprocess
from pathlib import Path

def create_deploy_script(project_path, token):
    """
    Создает BAT-файл для развертывания на PyPI
    """
    project_path = os.path.abspath(project_path)
    
    # Проверяем необходимые файлы
    required_files = ['setup.py', 'setup.cfg']
    for file in required_files:
        if not os.path.exists(os.path.join(project_path, file)):
            print(f"❌ Ошибка: {file} не найден в {project_path}")
            return False
    
    # Ищем папку с кодом (папка с __init__.py)
    code_dir = None
    for item in os.listdir(project_path):
        item_path = os.path.join(project_path, item)
        if os.path.isdir(item_path):
            # Проверяем, есть ли внутри Python файлы
            py_files = [f for f in os.listdir(item_path) if f.endswith('.py')]
            if py_files:
                code_dir = item
                break
    
    if not code_dir:
        print("❌ Ошибка: Не найдена папка с Python кодом")
        return False
    
    # Создаем BAT файл для развертывания
    bat_content = f'''@echo off
chcp 65001 >nul
echo 🚀 Начинаем развертывание проекта...

cd /d "{project_path}"

echo 📦 Проверяем установку необходимых инструментов...
python -m pip install --upgrade pip
python -m pip install --upgrade build twine

echo 🔨 Собираем пакет...
python -m build

echo 📤 Загружаем на PyPI...
python -m twine upload --repository pypi dist/* --username __token__ --password {token}

echo.
echo ✅ Развертывание завершено!
echo.
echo 🎯 Теперь ваш пакет можно установить через pip:
echo pip install {code_dir}
pause
'''
    
    bat_path = os.path.join(project_path, "deploy_to_pypi.bat")
    
    try:
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(bat_content)
        
        print(f"✅ Файл развертывания создан: {bat_path}")
        print(f"📁 Проект: {project_path}")
        print(f"🔑 Токен: {token}")
        print(f"📦 Папка с кодом: {code_dir}")
        print(f"\n🎯 После запуска BAT-файла установите пакет командой:")
        print(f"   pip install {code_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании файла: {e}")
        return False

def deploy_now(project_path, token):
    """
    Немедленное развертывание (без создания BAT файла)
    """
    project_path = os.path.abspath(project_path)
    
    try:
        print("🚀 Немедленное развертывание...")
        
        # Проверяем необходимые файлы
        required_files = ['setup.py', 'setup.cfg']
        for file in required_files:
            if not os.path.exists(os.path.join(project_path, file)):
                print(f"❌ Ошибка: {file} не найден")
                return False
        
        # Определяем имя пакета из setup.cfg или папки
        package_name = None
        for item in os.listdir(project_path):
            if os.path.isdir(os.path.join(project_path, item)) and any(f.endswith('.py') for f in os.listdir(os.path.join(project_path, item))):
                package_name = item
                break
        
        if not package_name:
            print("❌ Не удалось определить имя пакета")
            return False
        
        # Устанавливаем/обновляем инструменты
        print("📦 Устанавливаем инструменты...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "build", "twine"], 
                      check=True, capture_output=True)
        
        # Очищаем предыдущие сборки
        dist_dir = os.path.join(project_path, "dist")
        if os.path.exists(dist_dir):
            import shutil
            shutil.rmtree(dist_dir)
        
        # Собираем пакет
        print("🔨 Собираем пакет...")
        subprocess.run([sys.executable, "-m", "build", project_path], check=True, cwd=project_path)
        
        # Загружаем на PyPI
        print("📤 Загружаем на PyPI...")
        result = subprocess.run([
            sys.executable, "-m", "twine", "upload", 
            "--repository", "pypi", 
            "dist/*",
            "--username", "__token__",
            "--password", token
        ], check=True, capture_output=True, text=True, cwd=project_path)
        
        print("✅ Пакет успешно загружен на PyPI!")
        print(f"📦 Имя пакета: {package_name}")
        print(f"\n🎯 Теперь установите пакет командой:")
        print(f"   pip install {package_name}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при развертывании: {e}")
        if e.stderr:
            print(f"Детали: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_package_installed(package_name):
    """
    Проверяет, установлен ли пакет
    """
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", package_name], 
                      check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def install_package(package_name):
    """
    Устанавливает пакет через pip
    """
    try:
        print(f"📦 Устанавливаем пакет {package_name}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                              check=True, capture_output=True, text=True)
        print(f"✅ Пакет {package_name} успешно установлен!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке: {e}")
        if e.stderr:
            print(f"Детали: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Менеджер развертывания Python пакетов на PyPI")
    parser.add_argument("project_path", help="Путь к папке проекта")
    parser.add_argument("token", help="Токен PyPI")
    parser.add_argument("--deploy-now", action="store_true", 
                       help="Немедленно развернуть (без создания BAT файла)")
    parser.add_argument("--install", action="store_true",
                       help="Установить пакет после развертывания")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.project_path):
        print(f"❌ Ошибка: Путь {args.project_path} не существует")
        sys.exit(1)
    
    # Определяем имя пакета
    package_name = None
    for item in os.listdir(args.project_path):
        item_path = os.path.join(args.project_path, item)
        if os.path.isdir(item_path) and any(f.endswith('.py') for f in os.listdir(item_path)):
            package_name = item
            break
    
    if not package_name:
        print("❌ Не удалось определить имя пакета")
        sys.exit(1)
    
    if args.deploy_now:
        # Немедленное развертывание
        success = deploy_now(args.project_path, args.token)
        if success and args.install:
            # Ждем немного чтобы PyPI обновился
            import time
            print("⏳ Ждем обновления PyPI...")
            time.sleep(10)
            install_package(package_name)
        sys.exit(0 if success else 1)
    else:
        # Создание BAT файла для будущего развертывания
        success = create_deploy_script(args.project_path, args.token)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование:")
        print("  Создать BAT файл для развертывания:")
        print("  python pypi_deployer.py <путь_к_проекту> <токен_pypi>")
        print("")
        print("  Немедленное развертывание:")
        print("  python pypi_deployer.py <путь_к_проекту> <токен_pypi> --deploy-now")
        print("")
        print("  Развернуть и установить:")
        print("  python pypi_deployer.py <путь_к_проекту> <токен_pypi> --deploy-now --install")
        print("")
        print("Пример:")
        print('  python pypi_deployer.py "C:\\MyProject" "pypi-токен" --deploy-now --install')
        sys.exit(1)
    
    main()