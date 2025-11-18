import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

from mestDS.mestDS import mestDS

mestds_1 = mestDS("dsl_v3/dgp_test.yaml")
sims = mestds_1.simulate()
mestds_1.to_csvs("datasets")


mestds_2 = mestDS()
mestds_2.evaluate("datasets")
