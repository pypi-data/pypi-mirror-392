
import json

class ExecutionReg:

	def __init__(self, init_str=None):
		if init_str == None:
			self.registro = {}
		else:
			self.registro = json.loads(init_str)

	def update(self, lista_campos):
		new_reg = {}
		for k,v in self.registro.items():
			if k in lista_campos:
				new_reg[k] = v 


		for k in lista_campos:
			if k not in new_reg:
				new_reg[k] = 'No exec'

		self.registro = new_reg


	def __str__(self):
		return json.dumps(self.registro)

	