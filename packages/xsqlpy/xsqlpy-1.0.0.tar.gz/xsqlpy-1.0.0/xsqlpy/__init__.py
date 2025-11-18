# 2025.11.15  a light version of yulk, no local data file
import requests,os,math,json,builtins,hashlib,duckdb,warnings,sys, traceback,fileinput,zlib,re  #duckdb only imported in this file
import pandas as pd
import marimo as mo
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
builtins.root	= os.path.dirname(os.path.abspath(__file__)) 
warnings.filterwarnings("ignore")
builtins.duckdb = duckdb
builtins.pd		= pd
builtins.json	= json
builtins.os		= os
builtins.requests = requests
builtins.px		= px
builtins.plt	= plt
builtins.alt	= alt
builtins.re		= re
builtins.mo		= mo
builtins.ui		= mo.ui  # ui.text
builtins.md		= mo.md
builtins.mpl	= mo.mpl 

loadfile	= lambda filename: ''.join(fileinput.input(files=(filename)))
sql			= lambda q: duckdb.execute(q).df()
parse		= lambda input, **kwargs:  requests.get(f"http://data.yulk.net/parse~{input}", params=kwargs).json()
			
for file in [file for _root, dirs, files in os.walk(f"{root}/pycode",topdown=False) for file in files if file.endswith(".py") and not file.startswith("_") ]:
	try:
		dic = {}
		compiled_code = compile( loadfile(f'{root}/pycode/{file}'), f'{root}/pycode/{file}', 'exec') 
		exec(compiled_code,dic)
		[setattr(builtins, k, obj) for k, obj in dic.items() if not k.startswith("_") and not '.' in k and callable(obj)] # latter will overwrite former
	except Exception as e:
		print (f">>load pycode ex: file={file}, \t|",  e, flush=True)
		exc_type, exc_value, exc_obj = sys.exc_info() 	
		traceback.print_tb(exc_obj)

for file in [file for _root, dirs, files in os.walk(f"{root}/ducksql",topdown=False) for file in files if file.endswith(".sql") and not file.startswith("_") ]:
	try:  
		if not file.startswith('yulk') or os.path.exists('/yulk'):  # yulk*.sql only run where /yulk folder exists 
			duckdb.execute(loadfile(f'{root}/ducksql/{file}'))
	except Exception as e:
		print (">>Failed to load ducksql:", file, e )
		exc_type, exc_value, exc_obj = sys.exc_info() 	
		traceback.print_tb(exc_obj)

for cp in ('en','cn','enl','cnl'):  
	duckdb.execute(f"create schema IF NOT EXISTS {cp}") # cnl.svo # first run, create scheme en/cn
	setattr(builtins, cp, type(cp, (object,), {'name': cp}) ) # make 'en' as a new class, to attach new attrs later , such en.pos

echo = lambda *args, **kwargs : {'function name': 'echo', 'args':args, 'kwargs':kwargs}
class dummy: # dummy('xxx').value -> xxx
    def __init__(self, value):
        self.value = value
builtins.dummy = dummy

[setattr(builtins, k, f) for k, f in globals().items() if not k.startswith("_") and not '.' in k and not hasattr(builtins,k) and callable(f) ]
if __name__ == "__main__": 	pass 
