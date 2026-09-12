"""
运河四季·Turtle 美食绘卷 - 城市模块
"""

from .beijing import Beijing
from .tianjin import Tianjin
from .yangzhou import Yangzhou
from .suzhou import Suzhou
from .hangzhou import Hangzhou

CITIES = {
    '北京': Beijing,
    '天津': Tianjin,
    '扬州': Yangzhou,
    '苏州': Suzhou,
    '杭州': Hangzhou,
}

__all__ = ['Beijing', 'Tianjin', 'Yangzhou', 'Suzhou', 'Hangzhou', 'CITIES']
