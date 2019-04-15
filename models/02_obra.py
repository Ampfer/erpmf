# -*- coding: utf-8 -*-

TipoDemanda = ('Construção','Reforma','Projeto','Cronograma', 'Estoque')
Tempo = ('Sol','Nublado','Chuva')
from decimal import *

Etapas = db.define_table('etapas',
    Field('etapa','string',label='Descrição:',length=30),
    Field('item','string',label='Item:',length=02),
    Field('tarefas','list:reference atividades', label='Tarefas:'),
    format='%(item)s - %(etapa)s'
    )
Etapas.etapa.requires = IS_UPPER()
Etapas.tarefas.requires = IS_IN_DB(db,"atividades.id",'%(atividade)s',multiple=True)

def buscaEtapa(id):
    if not id:
        raise HTTP(404, 'ID Etapa não encontrado')
    try:
        etapa = db(db.etapas.id == id).select().first()
    except ValueError:
        raise HTTP(404, 'Argumento Etapa inválido')
    if not etapa:
        raise HTTP(404, 'Etapa não encontrado')
    return etapa

Demandas = db.define_table('demandas',
    Field('codigo','string',label = "Código:",length=9),
    Field('descricao','string',label='Descrição:',length=60),
    Field('cliente','reference clientes'),
    Field('endereco','reference enderecos',ondelete = "SET NULL"),
    Field('tipo','string',label = "Tipo de Demanda:",length=30),
    format='%(descricao)s'
    )
Demandas.cliente.requires = IS_IN_DB(db,"clientes.id",'%(nome)s')
Demandas.endereco.requires = IS_EMPTY_OR(IS_IN_DB(db,"enderecos.id",'%(endereco)s - %(bairro)s - %(cidade)s - %(estado)s '))
Demandas.tipo.requires = IS_IN_SET(TipoDemanda,zero=None)

Demanda_Atividades = db.define_table('demanda_atividades',
    Field('demanda','reference demandas', label= 'Demanda:'),
    Field('etapa','reference etapas', label= 'Etapa:'),
    Field('descricao','string',label='Descrição:',length=60),
    )

def valorComposicao(id,tipo=[]):
    idComposicao = int(id)
    insumos = db(Composicao_Insumos.composicao == idComposicao).select()
    valor_Composicao = 0
    for insumo in insumos:
        tp = Insumo[int(insumo.insumo)].tipo
        if tipo == [] or tp in tipo:
            valor_Composicao += (insumo.quantidade * insumo.preco).quantize(Decimal('1.00'), rounding=ROUND_DOWN)
    return valor_Composicao

def valorMaoObra(id):
    idComposicao = int(id)
    insumos = db(Composicao_Insumos.composicao == idComposicao).select()
    valorMO = 0
    for insumo in insumos:
        tipo = Insumo[insumo.insumo].tipo
        if tipo == 'MÃO DE OBRA':
            valorMO += (insumo.quantidade * insumo.preco).quantize(Decimal('1.00'), rounding=ROUND_DOWN)
    return valorMO

Composicao = db.define_table('composicao',
     Field('descricao', 'string', label='Descrição:', length=100),
     Field('unidade', 'string', label='Unidade:', length=04),
     format='%(descricao)s',
     )
Composicao.unidade.requires = IS_IN_DB(db,"unidade.unidade",'%(unidade)s - %(descricao)s')
Composicao.descricao.requires = IS_UPPER()
#Composicao.empreita.requires = IS_DECIMAL_IN_RANGE(dot=',')

Composicao_Insumos = db.define_table('composicao_insumos',
     Field('composicao', 'reference composicao'),
     Field('insumo','reference insumos', label='Insumo',),
     Field('quantidade','decimal(9,4)', label='Quantidade'),
     Field('unidade','string',label='Unidade',length=04),
     Field.Virtual('preco',lambda row:buscaInsumo(int(row.composicao_insumos.insumo))['preco'], label='Preço'),
     Field.Virtual('total',lambda row:(row.composicao_insumos.quantidade * row.composicao_insumos.preco).quantize(Decimal('1.00'), rounding=ROUND_DOWN) ,label='Total'),
     )
Composicao_Insumos.composicao.readable = Composicao_Insumos.composicao.writable = False
Composicao_Insumos.quantidade.requires = [IS_DECIMAL_IN_RANGE(dot=','),notempty]

def totalOrcamento(orcamento):
    try:
        rows = db(OrcamentoComposicao.orcamento==int(orcamento.orcamentos.id)).select()
    except:
        rows = []
    total = 0
    for row in rows:
        total += row.total
    return total

def totalMaodeObra(orcamento):
    try:
        rows = db(OrcamentoComposicao.orcamento==int(orcamento.orcamentos.id)).select()
    except:
        rows = []
    totalmo = 0
    for row in rows:
        totalmo += row.totmaodeobra
    return totalmo

Orcamentos = db.define_table('orcamentos',
    Field('dtorcamento','date',label='Data:'),
    Field('descricao', 'string', label='Descrição:'),
    Field('cliente','reference clientes',label='Cliente:'),
    Field('observacao','text', label='Observação:'),
    Field.Virtual('total',lambda row: totalOrcamento(row), label='Total'),
    Field.Virtual('maodeobra',lambda row: totalMaodeObra(row), label='M.Obra')
    )

Orcamentos.dtorcamento.requires = data


OrcamentoComposicao = db.define_table('orcamentoComposicao',
    Field('orcamento','reference orcamentos', label='Orçamento:'),
    Field('etapa', 'reference etapas', label='Etapas:'),
    Field('composicao','reference composicao', label='Composição:'),
    Field('item','string',label='Item:',length=10),
    Field('quantidade','decimal(7,2)', label='Quantidade:'),
    Field('unidade','string',label='UN:',length=04),
    #Field('empreita','decimal(7,2)',label='Empreita:'),
    Field.Virtual('valor',
            lambda row:valorComposicao(row.orcamentoComposicao.composicao), label='Valor:'),
    Field.Virtual('maodeobra',
            lambda row:valorMaoObra(row.orcamentoComposicao.composicao), label='M.Obra:'),                                      
    Field.Virtual('total', lambda row: (row.orcamentoComposicao.quantidade * row.orcamentoComposicao.valor).quantize(
            Decimal('1.00'), rounding=ROUND_DOWN), label='Total:'),
    Field.Virtual('totmaodeobra', lambda row: (row.orcamentoComposicao.quantidade * row.orcamentoComposicao.maodeobra).quantize(Decimal('1.00'), rounding=ROUND_DOWN), label='Total MO:')
    )
OrcamentoComposicao.orcamento.readable = OrcamentoComposicao.orcamento.writable = False
OrcamentoComposicao.quantidade.requires = [IS_DECIMAL_IN_RANGE(dot=','),notempty]
#OrcamentoComposicao.empreita.requires = IS_DECIMAL_IN_RANGE(dot=',')

OrcamentoInsumos = db.define_table('orcamentoInsumos',
     Field('composicao', 'reference orcamentoComposicao'),
     Field('orcamento','integer'),
     Field('insumo','reference insumos', label='Insumo'),
     Field('quantidade','decimal(9,4)', label='Quantidade'),
     Field('unidade','string',label='Unidade', length=04),
     Field('preco','decimal(7,2)', label='Preço'),
     Field.Virtual('total',lambda row:(row.orcamentoInsumos.quantidade * row.orcamentoInsumos.preco).quantize(Decimal('1.00'), rounding=ROUND_DOWN) ,label='Total'),
     Field.Virtual('codigo',lambda row: Insumo[row.orcamentoInsumos.insumo].codigo ,label='Código')
     )
OrcamentoInsumos.composicao.readable = Composicao_Insumos.composicao.writable = False
OrcamentoInsumos.quantidade.requires = [IS_DECIMAL_IN_RANGE(dot=','),notempty]
OrcamentoInsumos.preco.requires = IS_DECIMAL_IN_RANGE(dot=',')

def valor_item(idItem):
    item = Atividades_Itens[int(idItem)]
    if item.composicao:
        valor = round(valorComposicao(int(item.composicao))* float(item.quantidade),2)
    elif item.insumo:
        valor = round(Insumo[int(item.insumo)].preco * float(item.quantidade),2)
    return valor.quantize(Decimal('1.00'), rounding=ROUND_DOWN)    

def valor_atividade(idAtividade):
    itens = db(Atividades_Itens.atividade==idAtividade).select()
    valor = 0
    for item in itens:
        valor += valor_item(item(item.atividade))
    return valor.quantize(Decimal('1.00'), rounding=ROUND_DOWN)

Atividades = db.define_table('atividades',
    Field('atividade','string',label='Descrição:',length=100),
    Field('etapa','reference etapas', label='Etapa:'),
    Field('unidade', 'string', label='Unidade:', length=04),
    format = '%(atividade)s'
    )
Atividades.unidade.requires = IS_IN_DB(db,"unidade.unidade",'%(unidade)s')
Atividades.atividade.requires = IS_UPPER()

Atividades_Itens = db.define_table('atividades_itens',
    Field('atividade','reference atividades',label='Atividade'),
    Field('tipo','string',label='Tipo:'),
    Field('item','string',label='Item:'),
    Field('composicao','integer', label='Composição'),
    Field('unidade', 'string', label='Unidade:', length=04),
    Field('insumo','integer',label='Insumos:'),
    Field('quantidade', 'decimal(9,4)',label='Quantidade:'),
    )
Atividades_Itens.quantidade.requires = [IS_DECIMAL_IN_RANGE(dot=','),notempty]
Atividades_Itens.atividade.readable = Atividades_Itens.atividade.writable = False
Atividades_Itens.composicao.requires = IS_EMPTY_OR(IS_IN_DB(db,"composicao.id",'%(descricao)s (%(unidade)s)'))
Atividades_Itens.insumo.requires = IS_EMPTY_OR(IS_IN_DB(db,"insumos.id",'%(descricao)s (%(unidade)s)'))

Etapa_Atividades = db.define_table('etapas_atividades',
    Field('etapa','reference etapas'),
    Field('atividade','reference atividades')
    )

Obras = db.define_table('obras',
    Field('demanda','integer',label='Demanda:'),
    Field('descricao', 'string', label='Descrição:'),
    Field('bdi','decimal(7,2)', label='Bdi:')
    )
Obras.demanda.requires = IS_EMPTY_OR(IS_IN_DB(db,"demandas.id",'%(codigo)s'))
Obras.bdi.requires = [IS_DECIMAL_IN_RANGE(dot=','),notempty]

Obras_Itens = db.define_table('obras_itens',
    Field('obra','reference obras', label='Obra:'),
    Field('atividade','integer',label='Atividade:'),
    Field('etapa', 'integer', label='Etapas:'),
    Field('composicao','integer', label='Composição:'),
    Field('insumo','integer', label='Insumo:'),
    Field('quantidade','decimal(7,2)', label='Quantidade:'),
    Field('indice', 'decimal(9,4)',label='Indice:'),
    )


Obras_Itens.obra.readable = Obras_Itens.obra.writable = False
Obras_Itens.quantidade.requires = [IS_DECIMAL_IN_RANGE(dot=','),notempty]
Obras_Itens.indice.requires = [IS_DECIMAL_IN_RANGE(dot=','),notempty]
Obras_Itens.atividade.represent = lambda value,row: db.atividades[value]
