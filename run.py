"""
启动脚本 - 直接运行 python run.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from canal_delights.app import main

if __name__ == '__main__':
    main()
