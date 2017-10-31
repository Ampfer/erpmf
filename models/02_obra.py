# -*- coding: utf-8 -*-
Tempo = ('Sol','Nublado','Chuva')
from decimal import *

Etapas = db.define_table('etapas',
	Field('etapa','string',label='Descrição:',length=30),
    Field('item','string',label='Item:',length=02),
	format='%(etapa)s'
	)
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

def valorComposicao(row):
    insumos = db(Composicao_Insumos.composicao == row.composicao.id).select()
    valor_Composicao = 0
    for insumo in insumos:
        valor_Composicao += (insumo.quantidade * insumo.preco).quantize(Decimal('1.00'), rounding=ROUND_DOWN)
    return valor_Composicao

def valorMaoObra(row):
    insumos = db(Composicao_Insumos.composicao == row.composicao.id).select()
    valorMO = 0
    for insumo in insumos:
        tipo = Insumo[insumo.insumo].tipo
        if tipo == 'MÃO DE OBRA':
            valorMO += (insumo.quantidade * insumo.preco).quantize(Decimal('1.00'), rounding=ROUND_DOWN)
    return valorMO

Composicao = db.define_table('composicao',
                             Field('descricao', 'string', label='Descrição:', length=100),
                             Field('unidade', 'string', label='Unidade:', length=04),
                             Field('empreita', 'decimal(7,2)', label='Empreita:'),
                             Field.Virtual('maodeobra',lambda row:valorMaoObra(row), label='M.O.'),
                             Field.Virtual('valor',lambda row:valorComposicao(row), label='Valor'),
                             format='%(descricao)s',
                             )
Composicao.unidade.requires = IS_IN_DB(db,"unidade.unidade",'%(unidade)s - %(descricao)s')
Composicao.descricao.requires = IS_UPPER()
Composicao.empreita.requires = IS_DECIMAL_IN_RANGE(dot=',')

Composicao_Insumos = db.define_table('composicao_insumos',
                                     Field('composicao', 'reference composicao'),
                                     Field('insumo','reference insumos', label='Insumo',),
                                     Field('quantidade','decimal(9,4)', label='Quantidade'),
                                     Field('unidade','string',label='Unidade',length=04),
                                     Field.Virtual('preco',lambda row:buscaInsumo(int(row.composicao_insumos.insumo))['preco'], label='Preço'),
                                     Field.Virtual('total',lambda row:(row.composicao_insumos.quantidade * row.composicao_insumos.preco).quantize(Decimal('1.00'), rounding=ROUND_DOWN) ,label='Total'),
                                     Field.Virtual('codigoInsumo',lambda row: db.insumos[row.composicao_insumos.insumo].codigo ,label='Código')
                                     )
Composicao_Insumos.composicao.readable = Composicao_Insumos.composicao.writable = False
Composicao_Insumos.quantidade.requires= [IS_DECIMAL_IN_RANGE(dot=','),notempty]

Obras = db.define_table('obras',
	Field('nome','string',label='Descrição:',length=60),
	Field('cliente','reference clientes'),
	Field('endereco','reference enderecos',ondelete = "SET NULL"),
	Field('tipo_contrato','string',label = "Tipo de Contrato:",length=30),
	format='%(nome)s'
	)
Obras.cliente.requires = IS_IN_DB(db,"clientes.id",'%(nome)s')
Obras.endereco.requires = IS_IN_DB(db,"enderecos.id",'%(endereco)s - %(bairro)s - %(cidade)s - %(estado)s ')
Obras.tipo_contrato.requires = IS_IN_SET(TipoContrato,zero='Escolha um Tipo de Contrato')

ObraFotos = db.define_table('obraFotos',
                            Field('obra','reference obras'),
                            Field('descricao','string',label='Descrição'),
                            Field('dataFoto','date',label='Data'),
                            Field('etapa','reference etapas',label='Etapa'),
                            Field('foto','upload',label='Foto')
                            )
ObraFotos.obra.readable = ObraFotos.obra.writable = False
ObraFotos.dataFoto.requires = data

Diario = db.define_table('diario',
                         Field('dtdiario', 'date', label='Data:'),
                         Field('tempo','string',label='Tempo'),
                         Field('obra', 'reference obras', label='Obra:'),
                         Field('pedreiro','integer', label='Pedreiro:',default=0),
                         Field('servente', 'integer', label='Servente:',default=0),
                         Field('pintor','integer', label='Pintor:',default=0),
                         Field('eletrecista','integer', label='Eletrecista:',default=0),
                         Field('encanador','integer', label='Encanador:',default=0),
                         Field('servicos','list:reference insumos', label='Serviços'),
                         Field('equipamentos','list:reference insumos', label='Equipamentos'),
                         Field('ocorrencia','text',label='Ocorrências:'),
                         )

Diario.obra.requires = IS_IN_DB(db,'obras.id','%(nome)s',zero='Escolha uma Obra')
Diario.servicos.requires = IS_IN_DB(db(db.insumos.tipo=='Mão de Obra'),'insumos.id','%(descricao)s', multiple=True)
Diario.equipamentos.requires = IS_IN_DB(db(db.insumos.tipo=='Equipamentos'),'insumos.id','%(descricao)s', multiple=True)
Diario.tempo.requires = IS_IN_SET(Tempo,zero=None)
Diario.dtdiario.requires = data

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
                            #Field.Virtual('maodeobra',lambda row: totalMaodeObra(row), label='M.O.')
                            )

Orcamentos.dtorcamento.requires = data

def totalComposicao(row):
    try:
        insumos = db(OrcamentoInsumos.composicao == int(row.orcamentoComposicao.id)).select()
    except:
        insumos=[]
    valor_Composicao = 0
    for insumo in insumos:
        valor_Composicao += (insumo.quantidade * insumo.preco).quantize(Decimal('1.00'), rounding=ROUND_DOWN)
    return valor_Composicao

OrcamentoComposicao = db.define_table('orcamentoComposicao',
                                      Field('orcamento','reference orcamentos', label='Orçamento:'),
                                      Field('etapa', 'reference etapas', label='Etapas:'),
                                      Field('composicao','reference composicao', label='Composição:'),
                                      Field('item','string',label='Item:',length=10),
                                      Field('quantidade','decimal(7,2)', label='Quantidade:'),
                                      Field('unidade','string',label='UN:',length=04),
                                      Field('empreita','decimal(7,2)',label='Empreita:'),
                                      Field.Virtual('valor',
                                                    lambda row:totalComposicao(row), label='Valor:'),
                                      Field.Virtual('total', lambda row: (row.orcamentoComposicao.quantidade * row.orcamentoComposicao.valor).quantize(
                                                    Decimal('1.00'), rounding=ROUND_DOWN), label='Total:'),

                                      )
OrcamentoComposicao.orcamento.readable = OrcamentoComposicao.orcamento.writable = False
OrcamentoComposicao.quantidade.requires = [IS_DECIMAL_IN_RANGE(dot=','),notempty]
OrcamentoComposicao.empreita.requires = IS_DECIMAL_IN_RANGE(dot=',')

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

Quantitativos = db.define_table('quantitativos',
                               Field('descricao','string',label='Descrição', length=60),
                              )

QuantitativoElementos = db.define_table('quantitativoElementos',
                                    Field('quantitativo','reference quantitativos'),
                                    Field('descricao','string',label='Descrição', length=30),
                                    Field('espessura', 'decimal(6,2)', label='Espessura'),
                                    Field('largura', 'decimal(6,2)', label='Altura/largura'),
                                    Field('comprimento', 'decimal(6,2)', label='Comprimento'),
                                    Field('nucleo','string',label='Núcleo'),
                                    Field('cima','list:string',label='Cima'),
                                    Field('baixo', 'list:string', label='Baixo'),
                                    Field('etapa','string', label='Etapa'),
                                   )
Nucleo = ['Cerâmico Estrutural','Tijolo Maciço','Bloco Concreto','Laje','Contrapiso']
Revestimento = ['Cerâmico','Porcelanato','Revestimento','Reboco','Massa Fina','Gesso Parede','Gesso Forro',
                'Regularização','Impermeabilizao',]
Etapa = ['Fundação','Supraestrutura','Cobertura','Área Externa']

QuantitativoElementos.quantitativo.readable = QuantitativoElementos.quantitativo.writable = False
QuantitativoElementos.espessura.requires = IS_DECIMAL_IN_RANGE(dot=',')
QuantitativoElementos.largura.requires = IS_DECIMAL_IN_RANGE(dot=',')
QuantitativoElementos.comprimento.requires = IS_DECIMAL_IN_RANGE(dot=',')
QuantitativoElementos.nucleo.requires = IS_IN_SET(Nucleo,zero=None,)
QuantitativoElementos.cima.requires = IS_IN_SET(Revestimento,zero=None, multiple=True)
QuantitativoElementos.baixo.requires = IS_IN_SET(Revestimento,zero=None, multiple=True)
QuantitativoElementos.etapa.requires = IS_IN_SET(Etapa,zero=None,)

QuantitativoResumo= db.define_table('quantitativoResumo',
                                    Field('quantitativo','reference quantitativos'),
                                    Field('etapa', 'string', label='Etapa',length=30),
                                    Field('servico', 'string', label='Serviço', length=30),
                                    Field('quantidade', 'decimal(7,2)', label='Quantidade'),
                                    )
QuantitativoResumo.quantitativo.readable = QuantitativoResumo.quantitativo.writable = False
QuantitativoResumo.quantidade.requires = IS_DECIMAL_IN_RANGE(dot=',')


