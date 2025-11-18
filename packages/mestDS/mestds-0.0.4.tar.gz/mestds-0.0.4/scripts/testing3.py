import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

from mestDS.mestDS import mestDS

# all_sim_suites = mestDS("dsl/simplistic_sim.yaml")
weekly = mestDS("dsl/6_weekly_model_eval..yaml")
weekly.evaluate()

monthly = mestDS("dsl/7_monthly_model_eval..yaml")
monthly.evaluate()
