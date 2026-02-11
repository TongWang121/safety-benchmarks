#!/usr/bin/env python3
"""从日志文件中提取防御策略测试结果"""
import zipfile
import json
from pathlib import Path

log_dir = Path(r'E:\code\aisafety\ASB1\logs\defenses')
log_files = sorted(log_dir.glob('*.eval'))

def extract_scores(log_path):
    with zipfile.ZipFile(log_path, 'r') as z:
        with z.open('header.json') as f:
            header = json.load(f)
            results = header.get('results', {})
            scores = results.get('scores', [])
            asr_val, tsr_val, rr_val = None, None, None
            for score in scores:
                metrics = score.get('metrics', {})
                for metric_name, metric_data in metrics.items():
                    if 'asr' in metric_name.lower():
                        asr_val = metric_data.get('value')
                    elif 'tsr' in metric_name.lower():
                        tsr_val = metric_data.get('value')
                    elif 'rr' in metric_name.lower():
                        rr_val = metric_data.get('value')
            return asr_val, tsr_val, rr_val

# 防御策略顺序（按文件创建时间）
defense_names = [
    'delimiters_defense',
    'instructional_prevention',
    'direct_paraphrase_defense',
    'dynamic_prompt_rewriting',
    'ob_sandwich_defense',
    'pot_paraphrase_defense',
    'pot_shuffling_defense'
]

print('=' * 70)
print(' 七种防御策略测试结果汇总')
print('=' * 70)
print(f"{'防御策略':<35} {'ASR':<10} {'TSR':<10} {'RR':<10}")
print('-' * 70)

for i, (log_file, name) in enumerate(zip(log_files[:7], defense_names)):
    asr, tsr, rr = extract_scores(log_file)
    asr_str = f'{asr:.3f}' if asr is not None else 'N/A'
    tsr_str = f'{tsr:.3f}' if tsr is not None else 'N/A'
    rr_str = f'{rr:.3f}' if rr is not None else 'N/A'
    print(f'{name:<35} {asr_str:<10} {tsr_str:<10} {rr_str:<10}')

print('=' * 70)
print(f'\n所有日志已保存到: {log_dir}')
