from pyproteum.moperators.orrn import Orrn
from pyproteum.moperators.ssdl import Ssdl
from pyproteum.moperators.oaan import Oaan
from pyproteum.moperators.oaaa import Oaaa
from pyproteum.moperators.sbrc import Sbrc
from pyproteum.moperators.scrb import Scrb
from pyproteum.moperators.crcr import Crcr
from pyproteum.moperators.cccr import Cccr
from pyproteum.moperators.ccsr import Ccsr
from pyproteum.moperators.oodl import Oodl
from pyproteum.moperators.oeap import Oeap
from pyproteum.moperators.oeap import Oepa


def get_descr(name):
    for r in operator_list:
        if r['name'] == name:
            return r['descr']
    return None

operator_list = [
	{'class': Cccr, 
    'descr':'Cosntant by Constant Replacement',
	'name' : 'cccr',
    'max': 1 },

	{'class': Ccsr, 
    'descr':'Constant by scalar Replacement',
	'name' : 'ccsr',
    'max': 0},
    
	{'class': Crcr, 
    'descr':'Required Constant Replacement',
	'name' : 'crcr',
    'max' : 0 },
    
	{'class':Oaaa,
	'descr': 'Replace arithmetic assigment operator by other arithmetic assigment operator',
	'name':'oaaa', 
    'max' : 5 },

	{'class':Oaan,
	'descr': 'Replace arithmetic operator by other arithmetic operator',
	'name':'oaan', 
    'max' : 5},

	{'class':Oeap,
	'descr': 'Replace augmented assignment by plain assignment',
	'name':'oeap', 
    'max' : 0},
    
	# {'class':Oepa,
	# 'descr': 'Replace plain assignment by augmented assignment',
	# 'name':'oepa',
    # 'max' : 0},
    
	{'class':Oodl,
	'descr': 'Operator deletion',
	'name':'oodl', 
    'max' : 0},

	{'class': Orrn, 
    'descr':'Replace relational operator (< > <= >= == !=) by other relational operator',
	'name' : 'orrn', 
    'max' : 0},

	{'class':Sbrc,
	'descr': 'Replace each break statement by a continue statement',
	'name':'sbrc',
    'max' : 0},

	{'class':Scrb,
	'descr': 'Replace each continue statement by a break statement',
	'name':'scrb', 
    'max' : 0},

	{'class':Ssdl,
	'descr': 'Replace each statement by a pass statement',
	'name':'ssdl', 
    'max' : 0},
	]

