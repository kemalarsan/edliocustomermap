import os
os.chdir('/Users/aliarsan/edliocustomermap/')

# Read and execute the merge script
with open('direct_merge_execution.py', 'r') as f:
    code = f.read()

exec(code)