# -*- coding: utf-8 -*-

notempty=IS_NOT_EMPTY(error_message='Campo Obrigatório')
TipoPessoa = ('Física','Juridica')
TipoEndereco = ('Faturamento','Obra')
TipoContrato = ('Administração','Preço Fechado','Própria')
Departamentos = ('Vendas','Compras','Financeiro')
Estados = {'SP':'São Paulo','RJ':'Rio de Janeiro','MG':'Minas Gerais','RS':'Rio Grande do Sul','SC':'Santa Catarina','PR':'Paraná'}
TipoInsumos = {'Material':'MT-Marerial','Mão de Obra':'MO-Mão de Obra','Equipamentos':'EQ-Equipamentos','Documentação':'DC-Documentação'}
'''
Cadastros = db.define_table('cadastros',
	Field('tipo','string',label='Tipo de Pessoa:',length=30),
	Field('cnpj_cpf','string',label='CNPJ/CPF:',length=20),
	Field('ie_rg','string',label='I.E./RG:',length=20),	
	Field('razao','string',label='Razão Social:',length=60),
	format='%(razao)s'
	)
Cadastros.id.label = 'Código'
Cadastros.tipo.default = "Física"
Cadastros.cnpj_cpf.requires=IS_EMPTY_OR(IS_CPF_OR_CNPJ())
Cadastros.tipo.requires = IS_IN_SET(TipoPessoa,zero=None)
#Cadastro.email.requires = IS_EMAIL(error_message='Digite um Email')
'''

Clientes = db.define_table('clientes',
	Field('nome','string',label='Nome Fantasia:',length=60),
	Field('razao','string',label='Razão Social:',length=60),
	Field('tipo','string',label='Tipo de Pessoa:',length=30),
	Field('cnpj_cpf','string',label='CNPJ/CPF:',length=20),
	Field('ie_rg','string',label='I.E./RG:',length=20),	
	format='%(nome)s'
	)
Clientes.id.label = 'Código'
Clientes.nome.requires = notempty
Clientes.tipo.default = "Física"
Clientes.cnpj_cpf.requires=IS_EMPTY_OR(IS_CPF_OR_CNPJ())
Clientes.tipo.requires = IS_IN_SET(TipoPessoa,zero=None)

Fornecedores = db.define_table('fornecedores',
	Field('nome','string',label='Nome Fantasia:',length=60),
	Field('razao','string',label='Razão Social:',length=60),
	Field('tipo','string',label='Tipo de Pessoa:',length=30),
	Field('cnpj_cpf','string',label='CNPJ/CPF:',length=20),
	Field('ie_rg','string',label='I.E./RG:',length=20),	
	format='%(nome)s'
	)
Fornecedores.id.label = 'Código'
Fornecedores.nome.requires = notempty
Fornecedores.tipo.default = "Física"
Fornecedores.cnpj_cpf.requires=IS_EMPTY_OR(IS_CPF_OR_CNPJ())
Fornecedores.tipo.requires = IS_IN_SET(TipoPessoa,zero=None)

Contatos = db.define_table('contatos',
	Field('departamento','string',label='Departamento',length=30),
	Field('nome','string',label='Nome:',length=60),
	Field('fone','string',label='Fone:',length=60),
	Field('celular','string',label='Celular:',length=60),
	Field('email','string',label='Email:',length=60),
	Field('cliente','reference clientes'),
	Field('fornecedor','reference fornecedores'),
	format='%(nome)s'
	) 
Contatos.departamento.requires = IS_IN_SET(Departamentos,zero=None)
Contatos.cliente.readable = Contatos.cliente.writable = False
Contatos.fornecedor.readable = Contatos.fornecedor.writable = False
Contatos.email.requires = IS_EMPTY_OR(IS_EMAIL(error_message='Digite um Email'))

Enderecos = db.define_table('enderecos',
	Field('tipo','string',label='Tipo de Endereço:',length=30),
	Field('endereco','string',label='Endereço:',length=60),
	Field('bairro','string',label='Bairro:',length=40),
	Field('cidade','string',label='Cidade:',length=40),
	Field('estado','string',label='Estado:',length=2),
	Field('cep','string',label='Cep:',length=9),
	Field('cliente','reference clientes'),
	Field('fornecedor','reference fornecedores'),
	format='%(endereco)s - %(bairro)s - %(cidade)s - %(estado)s'
	)
Enderecos.tipo.requires = IS_IN_SET(TipoEndereco,zero=None)
Enderecos.estado.requires = IS_IN_SET(Estados,zero=None)
Enderecos.estado.default = 'SP'
Enderecos.cliente.readable = Contatos.cliente.writable = False
Enderecos.fornecedor.readable = Contatos.fornecedor.writable = False

Condicao = db.define_table('condicao',
	Field('descricao','string',label='Descrição:',length=30),
	Field('dias','list:integer',label='Dias:'),
	format='%(descricao)s'
	)
Unidade = db.define_table('unidade',
	Field('unidade','string',label='Unidade:',length=4, unique=True),
	Field('descricao','string',label='Descrição:',length=30),
	format='%(unidade)s'
	)
Unidade.unidade.requires = [IS_NOT_EMPTY(),IS_LENGTH(4),IS_NOT_IN_DB(db,'unidade.unidade')]

TipoInsumo = db.define_table('tipoInsumo',
                             Field('descricao','string',label='Descrição', length = 30,unique=True),
                             Field('sigla','string',label='Sigla', length = 02,unique=True),
                             )
TipoInsumo.descricao.requires = notempty
TipoInsumo.sigla.requires = notempty

Insumo = db.define_table('insumos',
                         Field('descricao', 'string', label='Descrição:', length=100),
                         Field('codigo', 'string', label='Código:', length=07),
                         Field('unidade', 'string', label='Unidade:', length=04),
                         Field('tipo','string', label='Tipo:', length=30),
                         Field('preco','decimal(7,2)',label='Preço'),
                         Field('obs','string',label='Observação'),
                         format='%(descricao)s',
                         )
Insumo.unidade.requires = IS_IN_DB(db,"unidade.unidade",'%(unidade)s - %(descricao)s')
Insumo.tipo.requires = IS_IN_DB(db,"tipoInsumo.descricao")
Insumo.preco.requires = IS_DECIMAL_IN_RANGE(dot=',')
Insumo.descricao.requires = IS_UPPER()

def buscaInsumo(id):
    if not id:
        raise HTTP(404, 'ID insumo não encontrado')
    try:
        insumo = db(db.insumos.id == id).select().first()
    except ValueError:
        raise HTTP(404, 'Argumento INSUMO inválido')
    if not insumo:
        raise HTTP(404, 'Insumo não encontrado')
    return insumo

Custo = db.define_table('custos',
						Field('insumo','reference insumos',label='Insumo:'),
						Field('fornecedor','reference fornecedores',label='Fornecedor:'),
						Field('custo','decimal(7,2)',label='Custo:'),
						Field('unidade','string',label='Unidade:', length=04),
						Field('embalagem','integer',label='Embalagem:')
						)
Custo.fornecedor.readable = Custo.fornecedor.writable = False
Custo.insumo.readable = Custo.insumo.writable = False
Custo.unidade.requires = IS_IN_DB(db,'unidade.unidade',)
Custo.custo.requires = IS_DECIMAL_IN_RANGE(dot=',')

