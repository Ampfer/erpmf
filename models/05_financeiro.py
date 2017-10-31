Conta = db.define_table('conta',
	Field('descricao','string',label='Descrição:',length=60),
	format='%(descricao)s'
	)
def totallote(row):
	query = db(Conta_corrente.lote == row.lote.id)
	total_pagamentos = query.select(Conta_corrente.vlpagamento.sum()).first()[Conta_corrente.vlpagamento.sum()] or 0
	return total_pagamentos

Lote = db.define_table('lote',
	Field('dtlote', 'date',label='Data'),
    Field('parcelas','list:integer'),
	Field('tipo','string',length=30),
	Field.Virtual('total',lambda row:totallote(row), label='Total')
	)
Lote.dtlote.requires = data
Lote.id.readable = Lote.id.writable = False
Lote.tipo.readable = Lote.tipo.writable = False
Lote.dtlote.readable = Lote.dtlote.writable = False
Lote.parcelas.readable = Lote.parcelas.writable =False

Conta_corrente = db.define_table('conta_corrente',
	Field('descricao','string',label='Descricão do Lançamento',length=60),
	Field('dtpagamento','date',label='Data'),
	Field('conta','reference conta',label= 'Conta'),
	Field('vlrecebimento','decimal(7,2)',label='Valor do Recebimento'),
	Field('vlpagamento','decimal(7,2)',label='Valor do Pagamento'),
	Field('lote','reference lote',ondelete='CASCADE'),
	Field('tipo','string',length=30)
	)
Conta_corrente.id.readable = Conta_corrente.id.writable = False
Conta_corrente.lote.writable = False
Conta_corrente.descricao.writable =  False
Conta_corrente.tipo.readable = Conta_corrente.tipo.writable = False
Conta_corrente.dtpagamento.requires = data
Conta_corrente.vlrecebimento.requires = IS_DECIMAL_IN_RANGE(dot=',')
Conta_corrente.vlpagamento.requires = IS_DECIMAL_IN_RANGE(dot=',')

Banco = db.define_table('banco',
						Field('codigo', 'string',label = 'Numero',length=3, unique = True),
						Field('nome','string',label = 'Banco',length=50),
						)

Cheques = db.define_table('cheques',
						  Field('banco','string',label='Banco',length=3),
						  Field('agencia','string',label='Agência',length=4),
						  Field('conta', 'string',label='Conta Corrente', length=20),
						  Field('cheque','string',label='Cheque N.', length=20),
						  Field('valor','decimal(7,2)',label='Valor'),
						  Field('dtcheque','date',label='Bom para'),
                          Field('nome','string',label='Nome',length=100),
						  Field('lotpag','integer'),
						  Field('lotrec','integer')
						  )
Cheques.banco.requires = IS_IN_DB(db,'banco.codigo','%(nome)s')
Cheques.id.readable = Cheques.id.writable = False
Cheques.lotpag.readable = Cheques.lotpag.writable = False
Cheques.lotrec.readable = Cheques.lotrec.writable = False
Cheques.dtcheque.requires = data
Cheques.valor.requires = IS_DECIMAL_IN_RANGE(dot=',')