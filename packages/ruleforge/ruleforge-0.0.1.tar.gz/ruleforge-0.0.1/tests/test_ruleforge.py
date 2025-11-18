import pandas as pd
from ruleforge import RuleForger

def test_basic_load_and_validate(tmp_path):
    df = pd.read_csv("/home/akash/projects/ruleforge/datasets/spaceship-titanic/train.csv")
    path = "/home/akash/projects/ruleforge/tests/config.json"
    rf = RuleForger(df)
    rf.load_from_config(path)
    rf.validate()  
