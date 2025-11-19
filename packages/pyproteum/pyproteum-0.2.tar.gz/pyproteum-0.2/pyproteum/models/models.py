from peewee import *
from datetime import datetime
from playhouse.migrate import *

db = Proxy()

class BaseModel(Model):
	class Meta:
		database = db

class Session(BaseModel):
	filename = CharField(unique=True)
	type = CharField()
	criado = DateTimeField(default=datetime.now)

class TestCase(BaseModel):
	filename = CharField(unique=True)
	criado = DateTimeField(default=datetime.now)


class Mutant(BaseModel):
	source = ForeignKeyField(Session, backref='mutants')
	operator = CharField()
	function = CharField()
	func_lineno = IntegerField()
	func_end_lineno = IntegerField()
	lineno = IntegerField()
	col_offset = IntegerField()
	end_lineno = IntegerField()
	end_col_offset = IntegerField()
	seq_number = IntegerField()
	ast = BlobField()
	status = CharField(default='live')
	criado = DateTimeField(default=datetime.now)

	class Meta:
		indexes = (
			(('source', 'lineno', 'col_offset','operator','seq_number'), True),  # combinação única
		)

	def __str__(self):
		s = f'Source: {self.source.filename}\n'
		s += f'Operator: {self.operator}\n'
		s += f'Func Lineno: {self.func_lineno}\n'
		s += f'Func End Lineno: {self.func_end_lineno}\n'
		s += f'Lineno: {self.lineno}\n'
		s += f'End Lineno: {self.end_lineno}\n'
		return s

class Execution(BaseModel):
	mutant =  ForeignKeyField(Mutant, backref='executed')		
	criado = DateTimeField(default=datetime.now)
	execucao = TextField(default='')

def criar_modelo(nome_modelo, campos):
	class Meta:
		database = db

	atributos = dict(campos)
	atributos['Meta'] = Meta
	return type(nome_modelo, (Model,), atributos)

#uso: 
# campos = {
#	 'titulo': CharField(),
#	 'ano': IntegerField(),
#	 'autor': CharField(),
# }

# Livro = criar_modelo('Livro', campos, db)
# db.create_tables([Livro])
# Livro.create(titulo='Dom Casmurro', ano=1899, autor='Machado de Assis')
#db.drop_tables([Model1, Model2])

def get_table_model(table_name):
	colunas = db.get_columns(table_name)
	atributos = {
		'_meta': type('Meta', (), {'database': db, 'table_name': table_name})
	}
	for col in colunas:
		atributos[col.name] = Field()
	return type(table_name, (BaseModel,), atributos)

# Livro = get_table_model('Livro')

