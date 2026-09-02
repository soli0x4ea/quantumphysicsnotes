# -*- coding: utf-8 -*-
"""CODATA 常数表加载器（P1 整改：脚本常数统一从 data/constants_*.json 读取）。

用法：
    from constants import C          # C['m_e'], C['h'], C['c'] ...
    from constants import load_raw   # 需要版本/出处等元数据时
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def load_raw(version='2018'):
    path = os.path.join(_HERE, '..', 'data', f'constants_{version}.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)


_RAW = load_raw('2018')
# 数值字典：键为常数表键名（c/h/hbar/e/kB/NA/m_e/m_p/...）
C = {k: v['value'] for k, v in _RAW['constants'].items()}
META = _RAW.get('meta', {})
