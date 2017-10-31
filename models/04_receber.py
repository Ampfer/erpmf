Receber = db.define_table('receber',
	Field('cliente','reference clientes',label = 'Cliente:',ondelete = "SET NULL"),
	Field('documento','string',label='Documento:',length=30),
	Field('emissao','date', label='Data:'),
	Field('valor','decimal(7,2)',label='Valor:'),
	Field('condicao','reference condicao', label='Condição de Pagamento:',ondelete = "SET NULL")
	)
Receber.cliente.requires = IS_IN_DB(db,"clientes.id",'%(nome)s',zero='Escolha um Cliente')
Receber.valor.requires = IS_DECIMAL_IN_RANGE(dot=',')
Receber.emissao.requires = data
Receber.condicao.requires = IS_IN_DB(db,"condicao.id",'%(descricao)s',zero='Condição de Pagamento')

Receber_parcelas = db.define_table('receber_parcelas',
	Field('receber','reference receber'),
	Field('parcela','string',label='Parcela:',length=7),
	Field('vencimento','date',label = 'Vencimento:'),
	Field('valor','decimal(7,2)',label='Valor'),
	Field('valorpago','decimal(7,2)',label='Valor Pago'),
	Field('dtpagamento','date',label='Data Pagamento'),
	Field('lote','integer'),
	Field.Virtual('valorpendente',lambda row: row.receber_parcelas.valor - row.receber_parcelas.valorpago,label='Pendente'),
	Field.Virtual('status',lambda row: "Pendente" if row.receber_parcelas.dtpagamento == None else "Pago",label='Status'),
	)
Receber_parcelas.receber.readable = Receber_parcelas.receber.writable = False
Receber_parcelas.dtpagamento.writable = False
Receber_parcelas.dtpagamento.requires = data
Receber_parcelas.vencimento.requires = data
Receber_parcelas.valor.requires = IS_DECIMAL_IN_RANGE(dot=',')
Receber_parcelas.valorpago.requires = IS_DECIMAL_IN_RANGE(dot=',')
Receber_parcelas.valorpago.writable = False
Receber_parcelas.valorpago.default = 0
Receber_parcelas.lote.default = 0
Receber_parcelas.lote.readable = Receber_parcelas.lote.writable = False

Receitas = db.define_table('receitas',
	Field('receber','reference receber'),
	Field('descricao','string',label='Descrição:',length=60),
	Field('dtreceita','date',label='Data da Receita'),
	Field('valor','decimal(7,2)',label='Valor:'),
	Field('tipo','string',label='Tipo de Receita',length=30),
	Field('obra','reference obras',ondelete = "SET NULL")
	)
Receitas.id.readable = Receitas.id.writable = False
Receitas.receber.readable = Receitas.receber.writable = False
Receitas.valor.requires = IS_DECIMAL_IN_RANGE(dot=',')
Receitas.dtreceita.requires = data
Receitas.tipo.requires = IS_IN_SET(['Receita','Reembolso'])
Receitas.obra.requires = IS_IN_DB(db,"obras.id",'%(nome)s')