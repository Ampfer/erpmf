# -*- coding: utf-8 -*-

def curva():

    form_pesq = SQLFORM.factory(
        Field('demanda','integer',requires=IS_EMPTY_OR(IS_IN_DB(db,'demandas.id','%(codigo)s - %(descricao)s',zero='TODAS')),label='Demanda'),
        Field('abc',requires=IS_IN_SET(['INSUMO','FORNECEDOR'], zero=None),label='Curva ABC'),
        Field('tipo',requires=IS_EMPTY_OR(IS_IN_DB(db,'tipoInsumo.descricao','%(descricao)s',zero='TODOS')),label='Tipo Insumo'),
        table_name='pesquisar',
        submit_button='Gerar',
        keepvalues = True,
        )

    if form_pesq.process().accepted:
        idDemanda = form_pesq.vars.demanda
        abc = form_pesq.vars.abc
        tipo = form_pesq.vars.tipo
        
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    return locals()

def gerar_abc():
    idDemanda = request.vars.demanda
    abc = request.vars.abc
    tipo = request.vars.tipo
    Relatorio.truncate()
    if abc == 'INSUMO':
        sum = PagarInsumos.quantidade.sum()
        sum1 = (PagarInsumos.quantidade * PagarInsumos.preco - PagarInsumos.desconto).sum()
        groupby=PagarInsumos.insumo
        query = (PagarInsumos.pagar == Pagar.id) & (PagarInsumos.insumo == Insumo.id)
        xdesc = 'Insumo[row.pagarInsumos.insumo].descricao'
        if idDemanda != '':
            query = query & (Pagar.demanda==idDemanda)
        if tipo != '':
            query = query & (Insumo.tipo==tipo)

    elif abc == 'FORNECEDOR':
        sum = Pagar.valor.sum()
        sum1 = Pagar.valor.sum()
        groupby = Pagar.fornecedor
        query = (Pagar.demanda==idDemanda) if idDemanda != '' else (Pagar.id > 0)
        xdesc = 'Fornecedores[row.pagar.fornecedor].nome'

    if query:
        total = db(query).select(sum1).first()[sum1] or 1
        rows = db(query).select(groupby,
                                sum.with_alias('Quantidade'),
                                sum1.with_alias('Valor'),
                                ((sum1/total)*100).with_alias('Porcentagem'),
                                groupby=groupby,orderby=~sum1)
        acumulado = 0
        tot = 0
        for row in rows:
            acumulado += row.Porcentagem
            tot += row.Valor
            descricao = eval(xdesc)
            Relatorio[0] = dict(descricao = descricao,
                                quantidade = row.Quantidade,
                                valor=row.Valor,
                                total = tot,
                                porcentagem = row.Porcentagem,
                                acumulado = acumulado)

        curva = db(Relatorio.id>0).select()
    else:
        curva = ''

    return dict(curva=curva)