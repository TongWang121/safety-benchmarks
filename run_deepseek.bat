@echo off
REM ASB DeepSeek-v3.2 运行脚本
REM 使用 DeepSeek API 进行攻击测试

cd /d E:\code\aisafety\ASB1\ASB_SOURCE_DATA

python main_attacker.py ^
  --llm_name deepseek-v3.2 ^
  --max_gpu_memory None ^
  --eval_device None ^
  --max_new_tokens 256 ^
  --scheduler_log_mode console ^
  --agent_log_mode console ^
  --llm_kernel_log_mode console ^
  --use_backend None ^
  --workflow_mode automatic ^
  --attacker_tools_path data/all_attack_tools.jsonl ^
  --tasks_path data/agent_task.jsonl ^
  --tools_info_path data/all_normal_tools.jsonl ^
  --observation_prompt_injection ^
  --plan_attack ^
  --action_attack ^
  --direct_prompt_injection ^
  --jailbreak ^
  --attack_type naive ^
  --defense_type None ^
  --pot_backdoor ^
  --pot_clean ^
  --target ResearcherProfileManager ^
  --trigger "in light of extant literature" ^
  --memory_attack ^
  --clean ^
  --result_file logs/deepseek_results.log ^
  --database memory_db/chroma_db ^
  --task_num 1 ^
  --write_db ^
  --read_db ^
  --res_file logs/deepseek_results.csv

pause
