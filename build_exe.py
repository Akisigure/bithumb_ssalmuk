"""
EXE Build Script for Windows
"""
import os
import subprocess
import sys

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def build_exe():
    """EXE 파일 빌드"""
    print("=" * 60)
    print("Bithumb Trading Bot - EXE Build")
    print("=" * 60)
    
    # PyInstaller 명령어
    command = [
        "pyinstaller",
        "--onefile",                    # 단일 exe 파일 생성
        "--console",                    # 콘솔 창 표시 (CLI 앱)
        "--name=빗썸거래",               # 출력 파일 이름
        "--icon=NONE",                  # 아이콘 (필요시 .ico 파일 경로)
        "--hidden-import=jwt",          # JWT 모듈 명시적 포함
        "--hidden-import=dotenv",       # dotenv 모듈 명시적 포함
        "--clean",                      # 이전 빌드 정리
        "main.py"                       # 메인 파일
    ]
    
    print("\nBuilding...")
    print(f"Command: {' '.join(command)}\n")
    
    try:
        result = subprocess.run(command, check=True)
        
        print("\n" + "=" * 60)
        print("Build Complete!")
        print("=" * 60)
        print("\nOutput: dist/빗썸거래.exe")
        print("\nUsage:")
        print("  1. Copy dist/빗썸거래.exe")
        print("  2. Double-click to run")
        print("  3. Enter API keys on first run")
        print("\nFeatures:")
        print("  - Single EXE file")
        print("  - No config files needed")
        print("  - Auto-save API keys to .env")
        
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\nPyInstaller not found.")
        print("Install: pip install pyinstaller")
        sys.exit(1)


if __name__ == "__main__":
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("Error: main.py not found.")
        print("Run this script from project root directory.")
        sys.exit(1)
    
    build_exe()

