
Pagar = db.define_table('pagar',
	Field('fornecedor','reference fornecedores',label = 'Fornecedor:',ondelete = "SET NULL"),
	Field('documento','string',label='Documento:',length=30 ),
	Field('demanda', 'reference demandas',label='Demanda'),
	Field('emissao','date', label='Data:'),
	Field('tipo','string',label='Tipo:',length=30 ),
	Field('remetente','reference remetente',label='Remetente:'),
	Field('valor','decimal(7,2)',label='Valor:'),
	Field('condicao','reference condicao', label='Condição de Pagamento:',ondelete = "SET NULL")
	)
Pagar.fornecedor.requires = IS_IN_DB(db,"fornecedores.id",'%(nome)s',zero='Escolha um Fornecedor')
Pagar.fornecedor.represent = lambda value,row: db.fornecedores[value].nome
Pagar.valor.requires = IS_DECIMAL_IN_RANGE(dot=',')
Pagar.emissao.requires = data
Pagar.tipo.requires = IS_IN_SET(['Compra','Transferência','Devolução'],zero=None)
Pagar.condicao.requires = IS_IN_DB(db,"condicao.id",'%(descricao)s',zero='Condição de Pagamento')
Pagar.remetente.requires = IS_EMPTY_OR(IS_IN_DB(db,"remetente.id",'%(nome)s',))
Pagar.demanda.requires = IS_EMPTY_OR(IS_IN_DB(db,"demandas.id",'%(descricao)s'))

Pagar_parcelas = db.define_table('pagar_parcelas',
	Field('pagar','reference pagar'),
	Field('parcela','string',label='Parcela:',length=7),
	Field('vencimento','date',label = 'Vencimento:'),
	Field('valor','decimal(7,2)',label='Valor'),
	Field('valorpago','decimal(7,2)',label='Valor Pago'),
	Field('dtpagamento','date',label='Pagamento'),
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
Pagar_parcelas.lote.readable = Pagar_parcelas.lote.writable = False

PagarInsumos = db.define_table('pagarInsumos',
							    Field('pagar','reference pagar'),
							    Field('insumo','reference insumos',label='Insumo'),
							    Field('unidade','string',length=4,label='Unidade'),
							    Field('quantidade','decimal(9,4)',label='Quantidade'),
							    Field('preco','decimal(7,2)',label='Preço'),
								Field('desconto','decimal(7,2)',label='Desconto'),
								Field('demanda', 'reference demandas',label='Demanda'),
								Field('conta','reference plano_contas3',ondelete = "SET NULL"),
								Field('etapa', 'reference etapas',label='Etapa'),
								Field.Virtual('total',lambda row: round((row.pagarInsumos.preco*row.pagarInsumos.quantidade)-row.pagarInsumos.desconto,2),label='Total'),
							   )
PagarInsumos.id.readable = PagarInsumos.id.writable = False
PagarInsumos.pagar.readable = PagarInsumos.pagar.writable = False
PagarInsumos.quantidade.requires = [IS_DECIMAL_IN_RANGE(dot=','),notempty]
PagarInsumos.preco.requires = IS_DECIMAL_IN_RANGE(dot=',')
PagarInsumos.desconto.requires = IS_DECIMAL_IN_RANGE(dot=',')
PagarInsumos.demanda.requires = IS_EMPTY_OR(IS_IN_DB(db,"demandas.id",'%(descricao)s'))
PagarInsumos.etapa.requires = IS_EMPTY_OR(IS_IN_DB(db,"etapas.id",'%(etapa)s'))

Despesas = db.define_table('despesas',
	                        Field('pagar','reference pagar'),	          
	                        Field('dtdespesa','date',label='Data da Despesa'),
	                        Field('valor','decimal(7,2)',label='Valor:'),
	                        Field('demanda','reference demandas',ondelete = "SET NULL"),
	                        Field('despesa','reference plano_contas3',ondelete = "SET NULL"),
	                      )
Despesas.id.readable = Despesas.id.writable = False
Despesas.pagar.readable = Despesas.pagar.writable = False
Despesas.valor.requires = IS_DECIMAL_IN_RANGE(dot=',')
Despesas.dtdespesa.requires = data
#Despesas.demanda.readable = Despesas.demanda.writable = False
#Despesas.demanda.requires = IS_IN_DB(db,"demandas.id",'%(descricao)s')
#Despesas.despesa.requires = IS_IN_DB(db(PlanoContas3.despesa == 'T'),"plano_contas3.id",'%(nivel2)s - %(conta)s')

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
	Field('condicao','reference condicao', label='Condição de Pagamento:'),
	Field('demanda','reference demandas', label='Demanda:'),
	Field('tipo','string', label='Tipo:',length=30),
	Field('obs','text', label='Observação:'),
	Field.Virtual('valor',lambda row: totalCompra(row), label='Valor:'),
	)
Compras.fornecedor.requires = IS_IN_DB(db,"fornecedores.id",'%(nome)s',zero='Escolha um Fornecedor')
Compras.demanda.requires = IS_EMPTY_OR(IS_IN_DB(db,"demandas.id",'%(descricao)s',zero=None))
Compras.emissao.requires = data
Compras.condicao.requires = IS_IN_DB(db,"condicao.id",'%(descricao)s',zero='Condição de Pagamento')
Compras.tipo.requires = IS_IN_SET(['Pedido','Orçamento'],zero=None)

ComprasInsumos = db.define_table('comprasInsumos',
	Field('compra','reference compras'),
	Field('insumo','reference insumos',label='Insumo'),
	Field('detalhe','string',length=50,label='Detalhe'),
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
ComprasInsumos.detalhe.requires = IS_UPPER()
