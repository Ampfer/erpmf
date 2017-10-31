
Pagar = db.define_table('pagar',
	Field('fornecedor','reference fornecedores',label = 'Fornecedor:',ondelete = "SET NULL"),
	Field('documento','string',label='Documento:',length=30 ),
	Field('emissao','date', label='Data:'),
	Field('valor','decimal(7,2)',label='Valor:'),
	Field('condicao','reference condicao', label='Condição de Pagamento:',ondelete = "SET NULL")
	)
Pagar.fornecedor.requires = IS_IN_DB(db,"fornecedores.id",'%(nome)s',zero='Escolha um Fornecedor')
Pagar.valor.requires = IS_DECIMAL_IN_RANGE(dot=',')
Pagar.emissao.requires = data
Pagar.condicao.requires = IS_IN_DB(db,"condicao.id",'%(descricao)s',zero='Condição de Pagamento')

Pagar_parcelas = db.define_table('pagar_parcelas',
	Field('pagar','reference pagar'),
	Field('parcela','string',label='Parcela:',length=7),
	Field('vencimento','date',label = 'Vencimento:'),
	Field('valor','decimal(7,2)',label='Valor'),
	Field('portador','string',label='Portador:',length=30),
	Field('valorpago','decimal(7,2)',label='Valor Pago'),
	Field('dtpagamento','date',label='Data Pagamento'),
	Field('lote','integer'),
	Field.Virtual('valorpendente',lambda row: row.pagar_parcelas.valor - row.pagar_parcelas.valorpago,label='Pendente'),
	Field.Virtual('status',lambda row: "Pendente" if row.pagar_parcelas.dtpagamento == None else "Pago",label='Status'),
	)
#Pagar_parcelas.id.readable = Pagar_parcelas.id.writable = False
Pagar_parcelas.pagar.readable = Pagar_parcelas.pagar.writable = False
#Pagar_parcelas.pagar.represent = lambda id,row:db.pagar(row.pagar).documento
Pagar_parcelas.dtpagamento.writable = False
Pagar_parcelas.dtpagamento.requires = data
Pagar_parcelas.vencimento.requires = data
Pagar_parcelas.valor.requires = IS_DECIMAL_IN_RANGE(dot=',')
Pagar_parcelas.valorpago.requires = IS_DECIMAL_IN_RANGE(dot=',')
Pagar_parcelas.valorpago.writable = False
Pagar_parcelas.valorpago.default = 0
Pagar_parcelas.portador.requires = IS_IN_SET(["M&F","Cliente"],zero=None)
Pagar_parcelas.lote.readable = Pagar_parcelas.lote.writable = False
Pagar_parcelas.portador.default = 'M&F'

PagarInsumos = db.define_table('pagarInsumos',
							    Field('pagar','reference pagar'),
							    Field('insumo','reference insumos',label='Insumo'),
							    Field('unidade','string',length=4,label='Unidade'),
							    Field('quantidade','decimal(9,4)',label='Quantidade'),
							    Field('preco','decimal(7,2)',label='Preço'),
								Field('desconto','decimal(7,2)',label='Desconto'),
								Field.Virtual('total',lambda row: round((row.pagarInsumos.preco*row.pagarInsumos.quantidade)-row.pagarInsumos.desconto,2),label='Total'),
							    Field('etapa', 'reference etapas',label='Etapa'),
							    Field('obra', 'reference obras',label='Obra'),
							   )
PagarInsumos.id.readable = PagarInsumos.id.writable = False
PagarInsumos.pagar.readable = PagarInsumos.pagar.writable = False
PagarInsumos.quantidade.requires = [IS_DECIMAL_IN_RANGE(dot=','),notempty]
PagarInsumos.preco.requires = IS_DECIMAL_IN_RANGE(dot=',')
PagarInsumos.desconto.requires = IS_DECIMAL_IN_RANGE(dot=',')
PagarInsumos.etapa.requires = IS_EMPTY_OR(IS_IN_DB(db,"etapas.id",'%(etapa)s'))
PagarInsumos.obra.requires = IS_IN_DB(db,"obras.id",'%(nome)s')

Despesas = db.define_table('despesas',
	                        Field('pagar','reference pagar'),
	                        Field('descricao','string',label='Descrição:',length=60),
	                        Field('dtdespesa','date',label='Data da Despesa'),
	                        Field('valor','decimal(7,2)',label='Valor:'),
	                        Field('etapa','reference etapas',ondelete = "SET NULL"),
	                        Field('obra','reference obras',ondelete = "SET NULL")
	                      )
Despesas.id.readable = Despesas.id.writable = False
Despesas.pagar.readable = Despesas.pagar.writable = False
Despesas.valor.requires = IS_DECIMAL_IN_RANGE(dot=',')
Despesas.dtdespesa.requires = data
Despesas.etapa.requires = IS_EMPTY_OR(IS_IN_DB(db,"etapas.id",'%(etapa)s'))
Despesas.obra.requires = IS_IN_DB(db,"obras.id",'%(nome)s')

def totalCompra(row):
	try:
		insumos= db(ComprasInsumos.compra == int(row.compras.id)).select()
	except:
		insumos=[]
	valorCompra = 0
	for insumo in insumos:
		valorCompra += (insumo.quantidade * insumo.preco).quantize(Decimal('1.00'), rounding=ROUND_DOWN)
	return valorCompra

Compras = db.define_table('compras',
	Field('fornecedor','reference fornecedores',label = 'Fornecedor:'),
	Field('documento','string',label='Documento:',length=30 ),
	Field('emissao','date', label='Data:'),
	Field.Virtual('valor',lambda row: totalCompra(row), label='Valor:'),
	Field('condicao','reference condicao', label='Condição de Pagamento:'),
	Field('obra','reference obras', label='Obra:'),
	Field('tipo','string', label='Tipo:',length=30),
	Field('obs','text', label='Observação:'),
	)
Compras.fornecedor.requires = IS_IN_DB(db,"fornecedores.id",'%(nome)s',zero='Escolha um Fornecedor')
Compras.obra.requires = IS_EMPTY_OR(IS_IN_DB(db,"obras.id",'%(nome)s',zero=None))
Compras.emissao.requires = data
Compras.condicao.requires = IS_IN_DB(db,"condicao.id",'%(descricao)s',zero='Condição de Pagamento')
Compras.tipo.requires = IS_IN_SET(['Pedido','Orçamento'],zero=None)

ComprasInsumos = db.define_table('comprasInsumos',
	Field('compra','reference compras'),
	Field('insumo','reference insumos',label='Insumo'),
	Field('unidade','string',length=4,label='Unidade'),
	Field('quantidade','decimal(9,4)',label='Quantidade'),
	Field('preco','decimal(7,2)',label='Preço'),
	Field('desconto','decimal(7,2)',label='Desconto'),
	Field.Virtual('total',lambda row: round((row.comprasInsumos.preco*row.comprasInsumos.quantidade)-row.comprasInsumos.desconto,2),label='Total'),
    )
ComprasInsumos.id.readable = ComprasInsumos.id.writable = False
ComprasInsumos.compra.readable = ComprasInsumos.compra.writable = False
ComprasInsumos.quantidade.requires = [IS_DECIMAL_IN_RANGE(dot=','),notempty]
ComprasInsumos.preco.requires = IS_DECIMAL_IN_RANGE(dot=',')
ComprasInsumos.desconto.requires = IS_DECIMAL_IN_RANGE(dot=',')
