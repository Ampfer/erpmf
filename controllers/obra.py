# -*- coding: utf-8 -*-

def etapas():
    form_etapa = grid(Etapas,50)
    return locals()

def insumos():

    fields = [Insumo.id,Insumo.codigo,Insumo.descricao,Insumo.unidade,Insumo.tipo,Insumo.preco]
    formInsumos = grid(Insumo,60,fields=fields,orderby=Insumo.descricao)

    if formInsumos.create_form:
        redirect(URL('insumoCadastro'))
    elif formInsumos.update_form:
        redirect(URL('insumoCadastro', args=request.args(-1)))

    return dict(grid=formInsumos)

def insumoCadastro():

    id_insumo = request.args(0) or "0"

    def completarCodigo(idInsumo,tipo):
        sigla = db(TipoInsumo.descricao==tipo).select().first().sigla
        codigo = sigla + '{:05d}'.format(int(idInsumo))
        try:
            db.insumos[idInsumo] = dict(codigo=codigo)
            return True
        except:
            return False

    btnVoltar = voltar('insumos')

    if session.tipo:
        Insumo.tipo.default = session.tipo
    if session.unidade:
        Insumo.unidade.default = session.unidade

    if id_insumo == "0":
        formInsumo = SQLFORM(Insumo, field_id='id', _id='form_insumo')
        btnExcluir = btnNovo = ''
        formFornecedor = formHistorico = ''
    else:
        formInsumo = SQLFORM(Insumo, id_insumo, _id='form_insumo', field_id='id')

        formFornecedor = LOAD(c='obra', f='insumoFornecedor', content='Aguarde, carregando...',
                        target='insumoFornecedor', ajax=True, args=id_insumo)

        formHistorico = LOAD(c='obra', f='insumoHistorico', content='Aguarde, carregando...',
                              target='insumoHistorico', ajax=True, args=id_insumo)

        btnExcluir = excluir("#")
        btnNovo = novo("insumoCadastro")

    if formInsumo.process().accepted and completarCodigo(formInsumo.vars.id,formInsumo.vars.tipo):
        response.flash = 'Insumo Salvo com Sucesso!'
        session.tipo = formInsumo.vars.tipo
        session.unidade = formInsumo.vars.unidade

        redirect(URL('insumoCadastro', args=formInsumo.vars.id))

    elif formInsumo.errors:
        response.flash = 'Erro no Formulário Principal!'

    return locals()

def insumoFornecedor():
    id_insumo = int(request.args(0))
    Custo.fornecedor.readable = Custo.fornecedor.writable = True
    Custo.insumo.default = id_insumo
    Custo.embalagem.default = 1

    def validarInsumo(form,insumo_id=id_insumo):
        fornecedor_id = form.vars.fornecedor
        if db((db.custos.fornecedor == fornecedor_id) & (db.custos.insumo==insumo_id)).count():
            if 'new' in request.args:
                form.errors.fornecedor = 'Fornecedor já Cadastrado para este Insumo'

    formInsumoFornecedor = SQLFORM.grid((Custo.insumo==id_insumo),csv=False,user_signature=False
                             ,maxtextlength=50,details=False,args=[id_insumo],onvalidation=validarInsumo)

    btnVoltar = voltar1('insumoFornecedor')

    if formInsumoFornecedor.update_form:
        btnExcluir = excluir("#")
    else:
        btnExcluir = ''

    return locals()

def insumoHistorico():
    id_insumo = int(request.args(0))
    query = (PagarInsumos.insumo==id_insumo)&(PagarInsumos.pagar==Pagar.id)
    fields= [Pagar.emissao,PagarInsumos.insumo,PagarInsumos.unidade,PagarInsumos.quantidade,
             PagarInsumos.preco,Pagar.fornecedor]
    formInsumoHistorico = SQLFORM.grid(query,csv=False,user_signature=False,orderby=~Pagar.emissao,
                             maxtextlength=50,details=False,args=[id_insumo],fields=fields,
                             create=False,editable=False,deletable = False,searchable=False)
    return locals()

def composicao():

    fields = [Composicao.id, Composicao.descricao, Composicao.unidade, Composicao.maodeobra, Composicao.valor]
    formComposicao = grid(Composicao,60,fields=fields,orderby=Composicao.descricao)

    if formComposicao.create_form:
        redirect(URL('composicaoCadastro'))
    elif formComposicao.update_form:
        redirect(URL('composicaoCadastro', args=request.args(-1)))

    return locals()

def composicaoCadastro():
    id_composicao = request.args(-1) or "0"

    if id_composicao == "0":
        formComposicao = SQLFORM(Composicao, field_id='id', _id='formComposicao')
        formInsumos = btnExcluir = btnNovo = ''
        valorComposicao = valorMaodeObra = 0
        composicao = 'Nova Composicão'
    else:
        formComposicao = SQLFORM(Composicao,id_composicao, field_id='id', _id='formComposicao')

        formInsumos = LOAD(c='obra', f='composicao_insumo', content='Aguarde, carregando...',
                        target='composicao_insumo', ajax=True, args=id_composicao)
        btnExcluir = excluir("#")
        btnNovo = novo("composicaoCadastro")

        valorComposicao = ("{0:.2f}".format(round(Composicao[id_composicao].valor,2)))
        valorMaodeObra = ("{0:.2f}".format(round(Composicao[id_composicao].maodeobra,2)))
        composicao = Composicao[id_composicao].descricao

    btnVoltar = voltar("composicao")

    if formComposicao.process().accepted:
        redirect(URL('composicaoCadastro',args=formComposicao.vars.id))

    return locals()

def composicaoInsumoTrigger():
    return "jQuery('#preco').html('%s');jQuery('#composicao_insumos_unidade').val('%s');"\
           %(Insumo[request.vars.insumo].preco,Insumo[request.vars.insumo].unidade)

@auth.requires_membership('admin')
def composicao_insumo():
    id_composicao = int(request.args(0))
    Composicao_Insumos.composicao.default = id_composicao

    def validarInsumo(form,composicao_id=id_composicao):
        insumo_id = form.vars.insumo
        if db((db.composicao_insumos.insumo == insumo_id) & (db.composicao_insumos.composicao==composicao_id)).count():
            if 'new' in request.args:
                form.errors.insumo = 'Insumo já Cadastrado nessa Composição'

    Composicao_Insumos.insumo.requires = IS_IN_DB(db,'insumos.id','%(descricao)s')

    fields=[Composicao_Insumos.codigoInsumo,Composicao_Insumos.insumo,Composicao_Insumos.unidade,
            Composicao_Insumos.quantidade,Composicao_Insumos.preco,Composicao_Insumos.total]

    formComposicaoInsumos = SQLFORM.grid((Composicao_Insumos.composicao==id_composicao),
                        args=[id_composicao],csv=False,user_signature=False, searchable=False,details=False,
                        maxtextlength=50,onvalidation=validarInsumo,fields=fields,)

    if formComposicaoInsumos.create_form or formComposicaoInsumos.update_form:
        formComposicaoInsumos[1].element(_name='insumo')['_onchange'] = "ajax('%s', ['insumo'], ':eval');" % URL('obra', 'composicaoInsumoTrigger')
        formComposicaoInsumos[1].element(_name='unidade')['_readonly'] = "readonly"
        if formComposicaoInsumos.update_form:
            response.js = "ajax('%s', ['insumo'], ':eval');" % URL('obra', 'composicaoInsumoTrigger')

    return locals()

@auth.requires_membership('admin')
def obras():
    form_obras = SQLFORM.grid((Obras),
                              formname="lista_obras",csv=False,user_signature=False, details=False,
                              maxtextlength=50,deletable=False )

    form_obras = DIV(form_obras, _class="well")

    if request.args(-2) == 'new':
       redirect(URL('obra'))
    elif request.args(-3) == 'edit':
       id_obra = request.args(-1)
       redirect(URL('obra', args=id_obra ))

    return locals()

@auth.requires_membership('admin')
def obra():
    id_obra = request.args(0) or "0"
    btnVoltar = voltar('obras')

    if id_obra == "0":
        form_obra = SQLFORM(Obras,field_id='id',_id='form_obra')
        formDespesas = formFotos = formInsumos = ''
        btnExcluir = btnNovo = ''
    else:
        form_obra = SQLFORM(Obras, id_obra,_id='form_obra',field_id='id')
        formDespesas = LOAD(c='obra', f='obraDespesas', content='Aguarde, carregando...',
                           target='obraDespesas', ajax=True, args=id_obra)
        formInsumos = LOAD(c='obra', f='obraInsumos', content='Aguarde, carregando...',
                           target='obraInsumos', ajax=True, args=id_obra)
        formAbc = LOAD(c='obra', f='obraAbc', content='Aguarde, carregando...',
                           target='obraAbc', ajax=True, args=id_obra)
        formFotos = LOAD(c='obra', f='obraFotos', content='Aguarde, carregando...',
                           target='obraFotos', ajax=True, args=id_obra)
        btnExcluir = excluir("#")
        btnNovo = novo("obra")

    if form_obra.process().accepted:
        response.flash = 'Obra Salva com Sucesso!'
        redirect(URL('obra', args=form_obra.vars.id))

    elif form_obra.errors:
        response.flash = 'Erro no Formulário Principal!'

    return locals()

@auth.requires_membership('admin')
def obraDespesas():

    id_obra = int(request.args(0))

    from datetime import datetime

    today = db(Despesas.obra == id_obra).select(Despesas.dtdespesa, orderby = Despesas.dtdespesa).first()['dtdespesa']

    inicial = datetime.strptime(request.vars.dtinicial,'%d/%m/%Y').date() if request.vars.dtinicial else today
    final = datetime.strptime(request.vars.dtfinal,'%d/%m/%Y').date() if request.vars.dtfinal else request.now

    query = []

    form_pesq = SQLFORM.factory(
        Field('dtinicial','date',default=inicial,requires=data, label='Data Inicial'),
        Field('dtfinal','date',default=final,requires=data,label='Data Final'),
        table_name='insumopesquisar',
        submit_button='Gerar')

    if form_pesq.process().accepted:
        inicial = form_pesq.vars.dtinicial
        final = form_pesq.vars.dtfinal
        query = (Relatorio.datarel>=inicial) & (Relatorio.datarel<=final)
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    rows = db(Despesas.obra==id_obra).select(Despesas.dtdespesa.with_alias('dtdespesa'),
                                             Despesas.descricao.with_alias('descricao'),
                                             Despesas.etapa.with_alias('etapa'),
                                             Despesas.valor.with_alias('valor'),
                                             orderby=Despesas.dtdespesa)

    Relatorio.truncate()
    acumulado = 0
    for r in rows:
        acumulado += r.valor
        Relatorio[0] = dict(datarel = r.dtdespesa,
                            descricao = r.descricao,
                            etapa = Etapas(r.etapa).etapa,
                            valor=r.valor,
                            total = acumulado)

    if query:
        obradespesas = db(query).select(Relatorio.datarel,
                                                 Relatorio.descricao,
                                                 Relatorio.etapa,
                                                 Relatorio.valor,
                                                 Relatorio.total,
                                                 orderby=Relatorio.datarel)


        despesas = SQLTABLE(obradespesas, _id='obradespesas',
                           _class='display',
                           _cellspacing="0",
                           _width="100%",
                           headers='labels',
                           truncate=100)
    else:
        despesas = ''


    return locals()

@auth.requires_membership('admin')
def obraInsumos():

    id_obra = int(request.args(0))
    q = (PagarInsumos.obra==id_obra) & (Pagar.id==PagarInsumos.pagar)
    id_pagar = int(db(q).select(PagarInsumos.pagar, orderby=Pagar.emissao).first()['pagar'])

    from datetime import datetime

    today = Pagar[id_pagar].emissao

    inicial = datetime.strptime(request.vars.dtinicial,'%d/%m/%Y').date() if request.vars.dtinicial else today
    final = datetime.strptime(request.vars.dtfinal,'%d/%m/%Y').date() if request.vars.dtfinal else request.now

    query = []

    form_pesq = SQLFORM.factory(
        Field('dtinicial','date',default=inicial,requires=data, label='Data Inicial'),
        Field('dtfinal','date',default=final,requires=data,label='Data Final'),
        table_name='insumopesquisar',
        submit_button='Gerar')

    if form_pesq.process().accepted:
        inicial = form_pesq.vars.dtinicial
        final = form_pesq.vars.dtfinal
        query = (Relatorio.datarel>=inicial) & (Relatorio.datarel<=final)
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'


    rows = db(PagarInsumos.obra==id_obra).select(PagarInsumos.insumo.with_alias('insumo'),
                                                 PagarInsumos.unidade.with_alias('un'),
                                                 PagarInsumos.quantidade.with_alias('qtde'),
                                                 PagarInsumos.preco.with_alias('preco'),
                                                 PagarInsumos.desconto.with_alias('desconto'),
                                                 PagarInsumos.pagar.with_alias('pagar'))

    Relatorio.truncate()
    for r in rows:
        total = round(r.qtde*r.preco-r.desconto,2)

        Relatorio[0] = dict(descricao = Insumo[r.insumo].descricao,
                            quantidade = r.qtde,
                            valor=r.preco,
                            total = total,
                            codigo = Insumo[r.insumo].codigo,
                            unidade = r.un,
                            datarel = Pagar[r.pagar].emissao )

    if query:
        obraInsumos = db(query).select(Relatorio.datarel,
                                                Relatorio.codigo,
                                                Relatorio.descricao,
                                                Relatorio.unidade,
                                                Relatorio.quantidade,
                                                Relatorio.valor,
                                                Relatorio.total,orderby=Relatorio.datarel)


        insumos = SQLTABLE(obraInsumos,_id='obrainsumos',
                                        _class='display',
                                        _cellspacing = "0",
                                        _width = "100%",
                                        headers='labels',
                                        truncate = 100)
    else:
        insumos = ''

    return dict(insumos=insumos,form_pesq=form_pesq)

@auth.requires_membership('admin')
def obraAbc():
    id_obra = int(request.args(0))
    abc = request.vars.abc if request.vars.abc else ''
    tipo = request.vars.tipo if request.vars.tipo else None
    query = []

    form_pesq = SQLFORM.factory(
        Field('abc', default=abc, requires=IS_IN_SET(['INSUMO','ETAPA','FORNECEDOR'], zero=None),label='Curva ABC'),
        Field('tipo',default=tipo, requires=IS_EMPTY_OR(IS_IN_DB(db,'tipoInsumo.descricao','%(descricao)s',zero='TODOS')),label='Tipo Insumo'),
        table_name='pesquisar',
        submit_button='Gerar',
        )

    if form_pesq.process().accepted:
        abc = form_pesq.vars.abc
        tipo = form_pesq.vars.tipo
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    Relatorio.truncate()
    if abc == 'INSUMO' or abc == 'ETAPA':
        sum = PagarInsumos.quantidade.sum()
        sum1 = (PagarInsumos.quantidade * PagarInsumos.preco - PagarInsumos.desconto).sum()
        if abc == 'INSUMO':
            groupby=PagarInsumos.insumo
            query = (PagarInsumos.obra == id_obra) & (PagarInsumos.insumo == Insumo.id)
            xdesc = 'Insumo[row.pagarInsumos.insumo].descricao'
            if tipo != None:
                query = query & (Insumo.tipo==tipo)
        else:
            groupby = PagarInsumos.etapa
            query = (PagarInsumos.obra == id_obra)
            xdesc = 'Etapas[row.pagarInsumos.etapa].etapa'
    elif abc == 'FORNECEDOR':
        sum = Despesas.valor.sum()
        sum1 = Despesas.valor.sum()
        query = (Despesas.obra == id_obra) & (Despesas.pagar == Pagar.id)
        groupby = Pagar.fornecedor
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

        curvaabc = db(Relatorio.id>0).select()
    else:
        curvaabc = ''

    return locals()

@auth.requires_membership('admin')
def obraFotos():
    id_obra = int(request.args(0))
    ObraFotos.obra.default = id_obra
    formObraFoto = SQLFORM.grid(ObraFotos.obra==id_obra,args=[id_obra],
                               details=False, csv=False, user_signature=False, maxtextlength=50,
                               )
    return locals()

@auth.requires_membership('admin')
def diarios():

    btnVoltar = A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning", _title="Voltar...",
                  _href=URL(c="obra", f="diarios"))
    btnExcluir = A(SPAN(_class="glyphicon glyphicon-trash"), ' Excluir ', _class="btn btn-danger", _title="Excluir...",
                   _href="#")

    Fields = [Diario.dtdiario,Diario.obra,Diario.servicos,Diario.tempo]
    form_diario = SQLFORM.grid(Diario,
                details=False,csv=False,user_signature=False,maxtextlength=50,fields=Fields,
          )

    return locals()

@auth.requires_membership('admin')
def orcamentos():
    fields = [Orcamentos.dtorcamento,Orcamentos.descricao,Orcamentos.cliente,Orcamentos.total]
    gridOrcamentos = grid(Orcamentos,50,8,'400px',fields=fields,formname="orcamentos",orderby =~Orcamentos.dtorcamento)
    if request.args(-2) == 'new':
       redirect(URL('orcamento'))
    elif request.args(-3) == 'edit':
       redirect(URL('orcamento', args=request.args(-1) ))

    return locals()

@auth.requires_membership('admin')
def orcamento():
    idOrcamento = request.args(0) or "0"

    btnVoltar = voltar('orcamentos')

    if idOrcamento == "0":
        formOrcamento = SQLFORM(Orcamentos,field_id='id',_id='orcamento')
        formComposicao = formInsumos = formMaodeObra = formInsumoRelacao = ''
        btnExcluir = btnNovo = ''
    else:
        formOrcamento = SQLFORM(Orcamentos, idOrcamento,_id='orcamento',field_id='id')

        formComposicao = LOAD(c='obra', f='orcamentoComposicao', content='Aguarde, carregando...',
                           target='orcamentocomposicao', ajax=True, args=idOrcamento)
        formMaodeObra = LOAD(c='obra', f='orcamentoMaodeObra', content='Aguarde, carregando...',
                           target='orcamentomaodeobra', ajax=True, args=idOrcamento)
        formInsumoRelacao = LOAD(c='obra', f='insumosOrcamento', content='Aguarde, carregando...',
                           target='insumosorcamento', ajax=True, args=idOrcamento)

        btnExcluir = excluir('#')
        btnNovo = novo("orcamento")

    if formOrcamento.process().accepted:
        response.flash = 'Orçamento Salvo com Sucesso!'
        redirect(URL('orcamento', args=formOrcamento.vars.id))

    elif formOrcamento.errors:
        response.flash = 'Erro no Formulário Principal!'

    return locals()

def composicaoTrigger():
    idcomposicao = request.vars.composicao[0]
    return "jQuery('#orcamentoComposicao_unidade').val('%s')" % (Composicao[idcomposicao].unidade)

def etapaTrigger():
    idEtapa = request.vars.etapa[0]
    idOrcamento = session.idOrcamento
    query = (OrcamentoComposicao.etapa == idEtapa) & (OrcamentoComposicao.orcamento == idOrcamento)
    cont = db(query).count() or 0
    item = Etapas[idEtapa].item + '.' + '{:02d}'.format(cont+1)
    return "jQuery('#orcamentoComposicao_item').val('%s');"  % (item)

@auth.requires_membership('admin')
def orcamentoComposicao():
    idOrcamento = int(request.args(0))
    session.idOrcamento = idOrcamento

    OrcamentoComposicao.orcamento.default = idOrcamento
    
    fields = [OrcamentoComposicao.item,OrcamentoComposicao.composicao,OrcamentoComposicao.etapa,OrcamentoComposicao.quantidade,
              OrcamentoComposicao.unidade,OrcamentoComposicao.valor, OrcamentoComposicao.total,]

    formOrcamentoComposicao = grid(OrcamentoComposicao.orcamento==idOrcamento,
                                           searchable=False,args=[idOrcamento],
                                           fields=fields,orderby=OrcamentoComposicao.item)

    if formOrcamentoComposicao.create_form or formOrcamentoComposicao.update_form:
        formOrcamentoComposicao[1].element(_name='composicao')['_onchange'] = "ajax('%s',['composicao'],':eval');" % URL('obra', 'composicaoTrigger')
        formOrcamentoComposicao[1].element(_name='etapa')['_onchange'] = "ajax('%s',['etapa'],':eval');" % URL('obra', 'etapaTrigger')
        formOrcamentoComposicao[1].element(_name='unidade')['_readonly'] = "readonly"
    total = Orcamentos[idOrcamento].total or 0

    return dict(formOrcamentoComposicao = formOrcamentoComposicao, total=total)


def insumoTrigger():
    return "jQuery('#orcamentoInsumos_preco').val('%s');jQuery('#orcamentoInsumos_unidade').val('%s');"\
           %(Insumo[request.vars.insumo].preco,Insumo[request.vars.insumo].unidade)

def orcamentoMaodeObra():
    
    idOrcamento = int(request.args(0))

    OrcamentoComposicao.orcamento.default = idOrcamento

    fields = [OrcamentoComposicao.composicao,OrcamentoComposicao.etapa,OrcamentoComposicao.quantidade,
              OrcamentoComposicao.unidade,OrcamentoComposicao.maodeobra,
              OrcamentoComposicao.totmaodeobra]

    formOrcamentoMaodeObra = grid(OrcamentoComposicao.orcamento==idOrcamento,editable=False,create=False,searchable=False,
                                  args=[idOrcamento],fields=fields,deletable=False,orderby = OrcamentoComposicao.etapa)

    if  formOrcamentoMaodeObra.update_form:
        formOrcamentoMaodeObra[1].element(_name='unidade')['_readonly'] = "readonly"

    totalMaodeObra = Orcamentos[idOrcamento].maodeobra or 0

    return dict(formOrcamentoMaodeObra=formOrcamentoMaodeObra, totalMaodeObra = totalMaodeObra)


def insumosOrcamento():

    idOrcamento = int(request.args(0))

    etapa = request.vars.etapa if request.vars.etapa else '0'
    composicao = request.vars.composicao if request.vars.composicao else '0'

    rowsEtapa = db(OrcamentoComposicao.orcamento == idOrcamento).select(OrcamentoComposicao.etapa, distinct=True)
    etapaSet = dict([(row.etapa,Etapas[row.etapa].etapa) for row in rowsEtapa])
    etapaSet[0] = 'Todos'
    rowsComposicao = db(OrcamentoComposicao.orcamento == idOrcamento).select(OrcamentoComposicao.composicao, distinct=True)
    composicaoSet = dict([(row.composicao,Composicao[row.composicao].descricao) for row in rowsComposicao])
    composicaoSet[0] = 'Todos'

    form_pesq = SQLFORM.factory(
        Field('etapa', default=etapa, requires=IS_IN_SET(etapaSet, zero=None)),
        Field('composicao', default=composicao, requires=IS_IN_SET(composicaoSet, zero=None)),
        table_name='pesquisar',
        submit_button='Gerar',
    )

    if form_pesq.process().accepted:
        etapa = form_pesq.vars.etapa
        composicao = form_pesq.vars.composicao
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    query = (OrcamentoComposicao.orcamento == idOrcamento)
    query = query & (OrcamentoComposicao.etapa == etapa) if etapa != '0' else query
    query = query & (OrcamentoComposicao.composicao == composicao) if composicao != '0' else query

    Relatorio.truncate()
        
    rows1 = db(query).select()
    for r1 in rows1:
        qtComposicao = r1.quantidade
        rows2 = db(Composicao_Insumos.composicao==r1.composicao).select()
        for r2 in rows2:
            qtde = (r2.quantidade * qtComposicao).quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)
            insumo = db(Insumo.id == r2.insumo).select().first()
            sum1 = Relatorio.quantidade.sum()
            qtAnt = db(Relatorio.codigo == insumo.codigo).select(sum1).first()[sum1] or 0

            Relatorio.update_or_insert(Relatorio.codigo == insumo.codigo,
                        codigo = insumo.codigo,
                        descricao = insumo.descricao,
                        unidade = insumo.unidade,
                        quantidade = (qtAnt + qtde),
                        valor=insumo.preco,
                        #total = total,
                        )

    if query:
        sum2 = Relatorio.total.sum()
        totalInsumos = db(Relatorio.id > 0).select(sum2).first()[sum2]

        orcamentoInsumos = db(Relatorio.id>0).select(Relatorio.codigo,
                                            Relatorio.descricao,
                                            Relatorio.unidade,
                                            Relatorio.quantidade,
                                            Relatorio.valor,
                                            Relatorio.total,
                                            orderby=Relatorio.descricao
                                            )


        insumos = SQLTABLE(orcamentoInsumos,_id='insumosOrcamento',
                                        _class='display',
                                        _cellspacing = "0",
                                        _width = "100%",
                                        headers='labels',
                                        truncate = 100)
    else:
        insumos = ''
        totalInsumos = 0

    return locals()

'''
    #sum = (OrcamentoComposicao.quantidade*Composicao_Insumos.quantidade).sum()
    query = (Insumo.id == Composicao_Insumos.insumo) & (Composicao_Insumos.composicao == OrcamentoComposicao.composicao) & (OrcamentoComposicao.orcamento == idOrcamento)
    query = query & (OrcamentoComposicao.etapa == etapa) if etapa != '0' else query
    query = query & (OrcamentoComposicao.composicao == composicao) if composicao != '0' else query
    rows = db(query).select(Insumo.id.with_alias('insumo'),
                            Insumo.descricao.with_alias('descricao'),
                            Insumo.unidade.with_alias('unidade'),
                            Insumo.preco.with_alias('preco'),
                            Insumo.codigo.with_alias('codigo'),
                            OrcamentoComposicao.quantidade.with_alias('qtComposicao'),
                            Composicao_Insumos.quantidade.with_alias('qtInsumos')
                            )

    Relatorio.truncate()

    for r in rows:

        qtde = r.qtComposicao*r.qtInsumos
        
        Relatorio.update_or_insert(Relatorio.codigo == r.codigo,
                            codigo = r.codigo,
                            descricao = r.descricao,
                            unidade = r.unidade,
                            quantidade =+ qtde,
                            valor=r.preco,
                            #total = total,
                                                        
                            )
                                   
        Relatorio[0] = dict(codigo = codigo,
                            descricao = r.descricao,
                            unidade = r.unidade,
                            quantidade = quantidade + qtde,
                            valor=r.preco,
                            #total = total,
                            
                            #datarel = Pagar[r.pagar].emissao 
                            )
        '''






@auth.requires_membership('admin')
def quantitativos():
    gridQuantitativo = SQLFORM.grid(Quantitativos,
                                  formname="quantitativos",csv=False,user_signature=False,details=False,maxtextlength=50 )
    if request.args(-2) == 'new':
       redirect(URL('quantitativo'))
    elif request.args(-3) == 'edit':
       redirect(URL('quantitativo', args=request.args(-1) ))

    return locals()
@auth.requires_membership('admin')
def quantitativo():
    idQuantitativo = request.args(0) or "0"

    btnVoltar = voltar('quantitativos')

    if idQuantitativo == "0":
        formQuantitativo = SQLFORM(Quantitativos,field_id='id',_id='quantitativo')
        formElementos = formResumo = ''
        btnExcluir = btnNovo = ''
    else:
        formQuantitativo = SQLFORM(Quantitativos, idQuantitativo,_id='quantitativo',field_id='id')

        formElementos = LOAD(c='obra', f='quantitativoElementos', content='Aguarde, carregando...',
                           target='quantitativoelementos', ajax=True, args=idQuantitativo)
        formResumo = LOAD(c='obra', f='quantitativoResumo', content='Aguarde, carregando...',
                           target='quantitativoresumo', ajax=True, args=idQuantitativo)

        btnExcluir = excluir('#')
        btnNovo = novo("quantitativo")

    if formQuantitativo.process().accepted:
        response.flash = 'Orçamento Salvo com Sucesso!'
        redirect(URL('quantitativo', args=formQuantitativo.vars.id))

    elif formQuantitativo.errors:
        response.flash = 'Erro no Formulário Principal!'

    return locals()

def adcionaResumo(form):

    QuantitativoResumo[0] = dict(quantitativo = int(form.vars.id),
                                 etapa = form.vars.etapa,
                                 servico = form.vars.nucleo,
                                 quantidade = round(float(form.vars.largura)*float(form.vars.comprimento),2)
                                )
    return locals()

@auth.requires_membership('admin')
def quantitativoElementos():
    idQuantitativo = int(request.args(0))

    QuantitativoElementos.quantitativo.default = idQuantitativo

    formQ = SQLFORM.grid(QuantitativoElementos.quantitativo==idQuantitativo,details=False,
                                           csv=False, user_signature=False,maxtextlength=50,
                                           searchable=False,args=[idQuantitativo],)

    return locals()

@auth.requires_membership('admin')
def quantitativoResumo():
    idQuantitativo = int(request.args(0))

    QuantitativoResumo.quantitativo.default = idQuantitativo

    formR = SQLFORM.grid(QuantitativoResumo.quantitativo==idQuantitativo,details=False,csv=False,
                        user_signature=False,maxtextlength=50,searchable=False,args=[idQuantitativo],
                        create=False,editable=False)
    locals()