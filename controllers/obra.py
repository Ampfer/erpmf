# -*- coding: utf-8 -*-

def etapas():
    fields=[Etapas.item, Etapas.etapa]
    form_etapa = grid(Etapas,50,fields=fields,orderby=Etapas.item)
    if request.args(-2) == 'new':
           redirect(URL('etapa'))
    elif request.args(-3) == 'edit':
       idEtapa = request.args(-1)
       redirect(URL('etapa', args=idEtapa))

    return dict(form_etapa=form_etapa)

#@auth.requires_membership('admin')
def etapa():
    idEtapa = request.args(0) or "0"
    btnVoltar = voltar('etapas')

    if idEtapa == "0":
        formEtapa = SQLFORM(Etapas,field_id='id',_id='formEtapa')
        loadAtividade = '' 
        btnExcluir = btnNovo = ''
    else:
        formEtapa = SQLFORM(Etapas, idEtapa,_id='formEtapa',field_id='id')

        loadAtividade = LOAD(c='obra', f='etapa_atividades', content='Aguarde, carregando...',
                           target='etapaatividades', ajax=True, args=idEtapa)
                      
        btnExcluir = excluir("#")
        btnNovo = novo("etapa")

    if formEtapa.process().accepted:
        response.flash = 'Etapa Salva com Sucesso!'
        redirect(URL('etapa', args=formEtapa.vars.id))

    elif formEtapa.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formEtapa=formEtapa,loadAtividade=loadAtividade,btnNovo=btnNovo,btnVoltar=btnVoltar,btnExcluir=btnExcluir)

#@auth.requires_membership('admin')
def etapa_atividades():
    idEtapa = int(request.args(0))
    Etapa_Atividades.etapa.readable = Etapa_Atividades.etapa.writable = False
    Etapa_Atividades.etapa.default = idEtapa


    fields = [Etapa_Atividades.atividade]
    gridAtividades = grid((Etapa_Atividades.etapa==idEtapa),args=[idEtapa],searchable=False,fields=fields,alt='300px')
    
    btnExcluir = excluir("#") if gridAtividades.update_form else ''
    btnVoltar = voltar1('etapaatividades')
    
    return dict(gridAtividades=gridAtividades, btnExcluir=btnExcluir,btnVoltar=btnVoltar)

#@auth.requires_membership('admin')def demandas():
def demandas():
    formDemandas = grid((Demandas),
                              formname="listaDemandas",deletable=False )

    if request.args(-2) == 'new':
       redirect(URL('demanda'))
    elif request.args(-3) == 'edit':
       idDemanda = request.args(-1)
       redirect(URL('demanda', args=idDemanda ))

    return dict(formDemandas = formDemandas)

#@auth.requires_membership('admin')
def demanda():
    idDemanda = request.args(0) or "0"
    btnVoltar = voltar('demandas')

    if idDemanda == "0":
        formDemanda = SQLFORM(Demandas,field_id='id',_id='formDemanda')
        formDespesas = formInsumos = formAbc = formAtividades ='' 
        btnExcluir = btnNovo = ''
    else:
        formDemanda = SQLFORM(Demandas, idDemanda,_id='formDemanda',field_id='id')

        formAtividades = LOAD(c='obra', f='demandaAtividades', content='Aguarde, carregando...',
                           target='demandaatividades', ajax=True, args=idDemanda)

        formDespesas = LOAD(c='obra', f='demandaDespesas', content='Aguarde, carregando...',
                           target='demandaDespesas', ajax=True, args=idDemanda)
                      
        btnExcluir = excluir("#")
        btnNovo = novo("demanda")

    if formDemanda.process().accepted:
        response.flash = 'Demanda Salva com Sucesso!'
        redirect(URL('demanda', args=formDemanda.vars.id))

    elif formDemanda.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formDemanda=formDemanda,formDespesas=formDespesas,formAtividades=formAtividades,btnNovo=btnNovo,btnVoltar=btnVoltar,btnExcluir=btnExcluir)

#@auth.requires_membership('admin')
def demandaAtividades():
    idDemanda = int(request.args(0))
    Demanda_Atividades.demanda.default = idDemanda

    gridAtividades = grid(Demanda_Atividades.demanda==idDemanda,formname="atividades",
                 searchable = False,args=[idDemanda],)

    btnVoltar = voltar1('atividades')

    if gridAtividades.update_form:
      btnExcluir = excluir("#")
    else:
      btnExcluir = ''

    return dict(gridAtividades = gridAtividades)

#@auth.requires_membership('admin')
def demandaDespesas():

    idDemanda = int(request.args(0))

    from datetime import datetime

    try:
      today = db(Despesas.demanda == idDemanda).select(Despesas.dtdespesa, orderby = Despesas.dtdespesa).first()['dtdespesa'] 
    except:
      today = request.now

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

    rows = db(Despesas.demanda==idDemanda).select(Despesas.dtdespesa.with_alias('dtdespesa'),
                                             Despesas.pagar.with_alias('pagar'),
                                             Despesas.despesa.with_alias('despesa'),
                                             Despesas.valor.with_alias('valor'),
                                             orderby=Despesas.dtdespesa)

    Relatorio.truncate()
    acumulado = 0
    for r in rows:
        acumulado += r.valor
        Relatorio[0] = dict(datarel = r.dtdespesa,
                            descricao = Fornecedores(Pagar(r.pagar).fornecedor).nome,
                            conta = PlanoContas3(r.despesa).conta,
                            valor=r.valor,
                            total = acumulado)

    if query:
        demandadespesas = db(query).select(Relatorio.datarel,
                                                 Relatorio.descricao,
                                                 Relatorio.conta,
                                                 Relatorio.valor,
                                                 Relatorio.total,
                                                 orderby=Relatorio.datarel)


        despesas = SQLTABLE(demandadespesas, _id='demandadespesas',
                           _class='display',
                           _cellspacing="0",
                           _width="100%",
                           headers='labels',
                           truncate=100)
    else:
        despesas = ''

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
    Insumo.conta.default = 5
    Insumo.tipo.default = 'MATERIAL'

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

    Composicao.maodeobra = Field.Virtual('maodeobra',lambda row:valorMaoObra(row.composicao.id), label='M.O.')
    Composicao.valor = Field.Virtual('valor',lambda row:valorComposicao(row.composicao.id), label='Valor')

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
        vlComposicao = vlMaodeObra = 0
        composicao = 'Nova Composicão'
    else:
        formComposicao = SQLFORM(Composicao,id_composicao, field_id='id', _id='formComposicao')

        formInsumos = LOAD(c='obra', f='composicao_insumo', content='Aguarde, carregando...',
                        target='composicao_insumo', ajax=True, args=id_composicao)
        btnExcluir = excluir("#")
        btnNovo = novo("composicaoCadastro")
        valor = valorComposicao(id_composicao)
        maodeObra = valorMaoObra(id_composicao)
        vlComposicao = ("{0:.2f}".format(round(valor,2)))
        vlMaodeObra = ("{0:.2f}".format(round(maodeObra,2)))
        composicao = Composicao[id_composicao].descricao

    btnVoltar = voltar("composicao")

    if formComposicao.process().accepted:
        redirect(URL('composicaoCadastro',args=formComposicao.vars.id))

    return locals()

def composicaoInsumoTrigger():
    return "jQuery('#preco').html('%s');jQuery('#composicao_insumos_unidade').val('%s');"\
           %(Insumo[request.vars.insumo].preco,Insumo[request.vars.insumo].unidade)

#@auth.requires_membership('admin')
def composicao_insumo():
    id_composicao = int(request.args(0))
    Composicao_Insumos.composicao.default = id_composicao

    def validarInsumo(form,composicao_id=id_composicao):
        insumo_id = form.vars.insumo
        if db((db.composicao_insumos.insumo == insumo_id) & (db.composicao_insumos.composicao==composicao_id)).count():
            if 'new' in request.args:
                form.errors.insumo = 'Insumo já Cadastrado nessa Composição'

    Composicao_Insumos.insumo.requires = IS_IN_DB(db,'insumos.id','%(descricao)s')

    fields=[Composicao_Insumos.insumo,Composicao_Insumos.unidade,
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

#@auth.requires_membership('admin')
def orcamentos():
    fields = [Orcamentos.dtorcamento,Orcamentos.descricao,Orcamentos.cliente,Orcamentos.total]
    gridOrcamentos = grid(Orcamentos,50,8,'400px',fields=fields,formname="orcamentos",orderby =~Orcamentos.dtorcamento)
    if request.args(-2) == 'new':
       redirect(URL('orcamento'))
    elif request.args(-3) == 'edit':
       redirect(URL('orcamento', args=request.args(-1) ))

    return locals()

#@auth.requires_membership('admin')
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

#@auth.requires_membership('admin')
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

    #OrcamentoComposicao.orcamento.default = idOrcamento

    fields = [OrcamentoComposicao.composicao,OrcamentoComposicao.etapa,OrcamentoComposicao.quantidade,
              OrcamentoComposicao.unidade,OrcamentoComposicao.maodeobra,
              OrcamentoComposicao.totmaodeobra]

    formOrcamentoMaodeObra = grid(OrcamentoComposicao.orcamento==idOrcamento,editable=False,create=False,searchable=False,
                                  args=[idOrcamento],fields=fields,deletable=False,orderby = OrcamentoComposicao.etapa)

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

def valor_atividade(idAtividade):
    itens = db(Atividades_Itens.atividade == idAtividade).select()
    total = 0
    for item in itens:
        if item.composicao:
            valor = round(float(valorComposicao(int(item.composicao)))*float(item.quantidade),2)
        else:
            valor = round(float(Insumo[int(item.insumo)].preco)*float(item.quantidade),2)
        total += valor
    return "{0:.2f}".format(total)
    
#@auth.requires_membership('admin')
def atividades():

    Atividades.valor = Field.Virtual('valor',lambda row:valor_atividade(int(row.atividades.id)), label='Valor')

    fields = [Atividades.atividade,Atividades.unidade, Atividades.valor]
    gridAtividades = grid(Atividades,70,fields=fields,orderby=[Atividades.etapa,Atividades.atividade])

    if gridAtividades.create_form:
        redirect(URL('atividade'))
    elif gridAtividades.update_form:
        redirect(URL('atividade', args=request.args(-1)))

    return dict(gridAtividades=gridAtividades)

#@auth.requires_membership('admin')
def atividade():
    idAtividade = request.args(-1) or "0"
    Atividades.etapa.writable = False

    if idAtividade == "0":
        formAtividade = SQLFORM(Atividades, field_id='id', _id='atividade')
        loadItens = btnExcluir = btnNovo = ''
    else:
        formAtividade = SQLFORM(Atividades,idAtividade, field_id='id', _id='atividade')

        loadItens = LOAD(c='obra', f='atividade_itens', content='Aguarde, carregando...',
                        target='atividadesitens', ajax=True, args=idAtividade)
        btnExcluir = excluir("#")
        btnNovo = novo("atividade")

    btnVoltar = voltar("atividades")

    if formAtividade.process().accepted:
        redirect(URL('atividade',args=formAtividade.vars.id))

    return dict(formAtividade=formAtividade,loadItens=loadItens, btnNovo=btnNovo,btnExcluir=btnExcluir,btnVoltar=btnVoltar)

#@auth.requires_membership('admin')
def atividade_itens():

    idAtividade = int(request.args(0))
    Atividades_Itens.atividade.default = idAtividade

    def completar_item(form):
        if form.vars.composicao:
            item = Composicao[int(form.vars.composicao)].descricao
            unidade = Composicao[int(form.vars.composicao)].unidade
            tipo = 'Composição'
        else:
            item = Insumo[int(form.vars.insumo)].descricao
            unidade = Insumo[int(form.vars.insumo)].unidade
            tipo = 'Insumo'

        Atividades_Itens[int(form.vars.id)] = dict(item = item, tipo=tipo,unidade=unidade)

    def validarItem(form):
        if form.vars.insumo and form.vars.composicao:
            form.errors.insumo = 'Cadastre Composição ou Insumo'
        if not form.vars.insumo and not form.vars.composicao:
            form.errors.insumo = 'Cadastre pelo menos uma Composição ou Insumo'


    fields = [Atividades_Itens.tipo,Atividades_Itens.item,Atividades_Itens.quantidade,Atividades_Itens.unidade,]
    gridItens = grid((Atividades_Itens.atividade==idAtividade),args=[idAtividade],searchable=False,onvalidation=validarItem,
        oncreate = completar_item, onupdate = completar_item,fields=fields,alt='300px')
    
    if gridItens.create_form or gridItens.update_form:
        gridItens[1].element(_name='composicao')['_onchange'] = "$('#atividades_itens_quantidade').focus();"
        gridItens[1].element(_name='insumo')['_onchange'] = "$('#atividades_itens_quantidade').focus();"
    

    btnExcluir = excluir("#") if gridItens.update_form else ''
    btnVoltar = voltar1('atividadesitens')
    
    return dict(gridItens=gridItens, btnExcluir=btnExcluir,btnVoltar=btnVoltar)

#@auth.requires_membership('admin')
def obras():
    gridObras = grid(Obras,50,8,'400px',formname="obras",orderby =~Obras.id)
    if request.args(-2) == 'new':
       redirect(URL('obra'))
    elif request.args(-3) == 'edit':
       redirect(URL('obra', args=request.args(-1) ))

    return locals()

def demandaTrigger():
    return "$('#obras_descricao').val('%s')" %(Demandas[int(request.vars.demanda)].descricao)

#@auth.requires_membership('admin')
def obra():
    idObras = request.args(0) or "0"

    btnVoltar = voltar('obras')

    if idObras == "0":
        Obras.bdi.default = 0
        formObra = SQLFORM(Obras,field_id='id',_id='obra')
        loadAtividade = loadOrcamento = loadInsumos = ''
        btnExcluir = btnNovo = ''
    else:
        formObra = SQLFORM(Obras, idObras,_id='obra',field_id='id')

        loadAtividade = LOAD(c='obra', f='obra_atividades', content='Aguarde, carregando...',
                           target='obraatividades', ajax=True, args=idObras)
        loadOrcamento = LOAD(c='obra', f='obra_orcamento',
                           target='obraorcamento', ajax=True, args=idObras)
        loadInsumos = LOAD(c='obra', f='obra_insumos',
                   target='obraoinsumos', ajax=True, args=idObras)

        btnExcluir = excluir('#')
        btnNovo = novo("obra")

    formObra.element(_name='demanda')['_onchange'] = "ajax('%s',['demanda'],':eval');" % URL('obra','demandaTrigger')

    if formObra.process().accepted:
        response.flash = 'Orçamento Salvo com Sucesso!'
        redirect(URL('obra', args=formObra.vars.id))

    elif formObra.errors:
        response.flash = 'Erro no Formulário Principal!'

    return locals()

def buscar_atividade():
    import json

    rows  = db(Etapa_Atividades.etapa == request.vars.etapa).select() 
    atividades = []
    for row in rows:
        atividade = Atividades[row.atividade]
        atv = '%s (%s)' %(atividade.atividade,atividade.unidade)
        atividades.append(dict(atividade = atv , id = atividade.id)) 
    atividadeJson = json.dumps(atividades)

    jquery = "$('#atividade_atividade').find('option').remove();$.each(%s, function (i, d) {$('<option>').val(d.id).text(d.atividade).appendTo($('#atividade_atividade'));});" %(atividadeJson)
    return  jquery

#@auth.requires_membership('admin')
def obra_atividades():
    idObra = int(request.args(0))

    formAtividade = SQLFORM.factory(
        Field('etapa','integer',label='Etapa:',requires=IS_EMPTY_OR(IS_IN_DB(db,'etapas.id','%(item)s - %(etapa)s'))),
        Field('atividade','integer',label='Item:',requires=IS_IN_DB(db,'atividades.id','%(atividade)s (%(unidade)s)')),
        Field('quantidade','decimal(7,2)',label='Quantidade:',requires=[IS_DECIMAL_IN_RANGE(dot=','),notempty]),
        table_name='atividade',
        submit_button='Adicionar',
        )
    formAtividade.element(_name='etapa')['_onchange'] = "ajax('%s',['etapa'],':eval');" % URL('obra', 'buscar_atividade')

    def valida_atividade(form):
        if db((Obras_Itens.obra == idObra)&(Obras_Itens.atividade==form.vars.atividade)).select().first():
            form.errors.atividade = 'Atividade já Cadastrada' 

    if formAtividade.process(onvalidation = valida_atividade).accepted:
        
        atualizar_item(idObra = idObra,
                       idEtapa = formAtividade.vars.etapa,
                       idAtividade=formAtividade.vars.atividade,
                       quantidade = formAtividade.vars.quantidade)

        response.flash = 'Item Adicionado'

    elif formAtividade.errors:
        response.flash = 'Erro no Formulário'

    Obras_Itens.valor = Field.Virtual('valor',lambda row: 0, label='Valor')
    itens = db(Obras_Itens.obra == idObra).select(orderby=[Obras_Itens.etapa, Obras_Itens.atividade])
    linhas = gerar_linhas(idObra,itens)

    return dict(formAtividade=formAtividade,linhas=linhas)

def atualizar_item(idObra,idEtapa,idAtividade,quantidade):

    itens = db(Atividades_Itens.atividade == idAtividade).select()
    #etapa = Atividades[int(idAtividade)]['etapa']
    
    for item in itens:
        Obras_Itens.update_or_insert((Obras_Itens.obra==idObra)&(Obras_Itens.etapa==idEtapa)&(Obras_Itens.atividade==idAtividade)&(Obras_Itens.composicao==item.composicao)&(Obras_Itens.insumo==item.insumo),
                           obra=idObra,
                           atividade = idAtividade,
                           etapa = idEtapa, 
                           composicao = item.composicao, 
                           insumo=item.insumo,
                           quantidade = quantidade,
                           indice = item.quantidade
                           )

def alterar_item():
    id  = request.post_vars.id
    print id
    valor = request.post_vars.valor
    if id.count("-") > 0:
        idObra,idEtapa,idAtividade = id.split('-')
        atualizar_item(idObra=idObra,idEtapa=idEtapa,idAtividade=idAtividade,quantidade=valor)
        response.js = "$('#obraatividades').get(0).reload()"
    else:
        qtde = float(Obras_Itens[int(id)].quantidade)
        indice = "%.2f" %(round(float(valor)/qtde,2))
        Obras_Itens[int(id)] = dict(indice=indice) 
    return 

def obra_orcamento():
    idObra = int(request.args(0))
    itens = db(Obras_Itens.obra == idObra).select(Obras_Itens.etapa,Obras_Itens.atividade, 
        orderby=[Obras_Itens.etapa, Obras_Itens.atividade],distinct=True)
    totalOrcamento = legenda = ''
    xitens = {}
    for item in itens:
        #chave = '%s-%s' %(int(item.etapa),int(item.atividade))
        chave = item.atividade
        atividade = '%s-%s-%s' %(Etapas[item.etapa].item,Etapas[item.etapa].etapa, Atividades[item.atividade].atividade)
        xitens.update({chave:atividade})

    form_pesq = SQLFORM.factory(     
        Field('atividade',label='Item:',requires=IS_IN_SET(xitens,multiple=True)),
        Field('tipo',label='Tipo de Insumo',requires = IS_IN_DB(db,db.tipoInsumo.descricao,multiple=True)),
        table_name='orcamento',
        submit_button='Gerar Orçamento',
        )

    linhas = []
    if form_pesq.process().accepted:
        tipos = form_pesq.vars.tipo
        if form_pesq.vars.atividade == []:
            q = (Obras_Itens.obra == idObra)
        else:
            q = (Obras_Itens.obra == idObra) & (Obras_Itens.atividade.belongs(form_pesq.vars.atividade))        
        
        Obras_Itens.valor = Field.Virtual('valor',
            lambda row: valorComposicao(row.obras_itens.composicao,tipos) if row.obras_itens.composicao else valor_insumo(row.obras_itens.insumo, tipos) , 
            label='Valor')
        
        itens = db(q).select(orderby=[Obras_Itens.etapa, Obras_Itens.atividade])
        linhas = gerar_linhas(idObra,itens)
        obra = Obras[idObra]
        bdi = 1 + obra.bdi/100
 
        totalOrcamento = 0
        for item in itens:
            valor = valorComposicao(item.composicao,tipos) if item.composicao else valor_insumo(item.insumo, tipos)
            totalOrcamento += round(float(item.quantidade) * float(item.indice) * float(valor) * float(bdi),2)

        if tipos == []:
            legenda = 'Total do Orçamento'
        else:
            tipo=''
            for tp in tipos:
                tipo += "-" + tp 
            legenda = "Total ( %s )" %(tipo)
     
    return dict(form_pesq=form_pesq, linhas=linhas,totalOrcamento=totalOrcamento,legenda=legenda)
    
def obra_insumos():
    idObra = int(request.args(0))
    itens = db(Obras_Itens.obra == idObra).select(Obras_Itens.etapa,Obras_Itens.atividade, 
        orderby=[Obras_Itens.etapa, Obras_Itens.atividade],distinct=True)
    xitens = {}
    for item in itens:
        chave = item.atividade
        atividade = '%s-%s-%s' %(Etapas[item.etapa].item,Etapas[item.etapa].etapa, Atividades[item.atividade].atividade)
        xitens.update({chave:atividade})

    form_pesq = SQLFORM.factory(     
        Field('atividade',label='Item:',requires=IS_IN_SET(xitens,multiple=True)),
        Field('tipo',label='Tipo de Insumo',requires = IS_IN_DB(db,db.tipoInsumo.descricao,multiple=True)),
        table_name='orcamento',
        submit_button='Buscar Insumos',
        )

    query = ''
    if form_pesq.process().accepted:
        tipos = form_pesq.vars.tipo
        if form_pesq.vars.atividade == []:
            query = (Obras_Itens.obra == idObra)
        else:
            query = (Obras_Itens.obra == idObra) & (Obras_Itens.atividade.belongs(form_pesq.vars.atividade))        
        
    
        Relatorio.truncate()
        rows = db(query).select(orderby=[Obras_Itens.etapa, Obras_Itens.atividade])
        
        for row in rows:

            qtde = round(float(row.quantidade)*float(row.indice),2)

            if row.insumo:
                tp = Insumo[int(row.insumo)].tipo
                if tipos == [] or tp in tipos:
                    insumo = db(Insumo.id == row.insumo).select().first()
                    sum = Relatorio.quantidade.sum()
                    qtdeAnt = db(Relatorio.codigo==insumo.codigo).select(sum).first()[sum] or 0

                    Relatorio.update_or_insert(Relatorio.codigo == insumo.codigo,
                                codigo = insumo.codigo,
                                descricao = insumo.descricao,
                                unidade = insumo.unidade,
                                quantidade = float(qtdeAnt)+float(qtde),
                                valor=insumo.preco,
                                )
            elif row.composicao:    
                rows2 = db(Composicao_Insumos.composicao==row.composicao).select()
                for row2 in rows2:
                    tp = Insumo[int(row2.insumo)].tipo
                    if tipos == [] or tp in tipos:
                        qtdeInsumo = round(float(row2.quantidade) * float(qtde),2)
                        insumo = db(Insumo.id == row2.insumo).select().first()

                        sum = Relatorio.quantidade.sum()
                        qtdeAnt = db(Relatorio.codigo==insumo.codigo).select(sum).first()[sum] or 0

                        Relatorio.update_or_insert(Relatorio.codigo == insumo.codigo,
                                    codigo = insumo.codigo,
                                    descricao = insumo.descricao,
                                    unidade = insumo.unidade,
                                    quantidade = float(qtdeAnt)+float(qtdeInsumo),
                                    valor=insumo.preco,
                                    total = round((float(qtdeAnt)+float(qtdeInsumo))*float(insumo.preco),2)
                                    )

    if query:
        sum = Relatorio.total.sum()
        totalInsumos = db(Relatorio.id > 0).select(sum).first()[sum]

        obraInsumos = db(Relatorio.id>0).select(Relatorio.codigo,
                                            Relatorio.descricao,
                                            Relatorio.unidade,
                                            Relatorio.quantidade,
                                            Relatorio.valor,
                                            Relatorio.total,
                                            orderby=Relatorio.descricao
                                            )

        insumos = SQLTABLE(obraInsumos,_id='insumos',
                                        _class='display',
                                        _cellspacing = "0",
                                        _width = "100%",                                       
                                        headers='labels',
                                        truncate = 100)
    else:
        insumos = ''
        totalInsumos = 0


    return dict(form_pesq=form_pesq,insumos=insumos)



def gerar_linhas(idObra,itens):
    linhas = []
    idEtapa=idAtividade=0 
    c = p = 0
    for item in itens:
        if item.etapa != idEtapa:
            etapa = True
            idEtapa = item.etapa
        if item.atividade != idAtividade:
            atividade = True
            idAtividade = item.atividade
        c += 1
        if etapa:
            linhas.append(dict(item = Etapas[int(item.etapa)].etapa, c=c, p=0,))
            etapa=False
            idEtapa = item.etapa
            p = c
            pp = c
            c += 1
        if atividade:
            q1 = (Obras_Itens.obra == idObra) & (Obras_Itens.atividade == item.atividade) 
            rows = db(q1).select()
            valor = 0
            for r in rows:
                valor += round(float(r.valor) * float(r.indice),2)


            linhas.append(dict(item=Atividades[int(item.atividade)].atividade,
                               qtde = "{0:.2f}".format(item.quantidade),
                               unidade = Atividades[int(item.atividade)].unidade,
                               valor = "{0:.2f}".format(valor),
                               total = "{0:.2f}".format(round(valor * float(item.quantidade),2)),
                               c=c, 
                               p=pp,
                               id = "%s-%s-%s" %(idObra,idEtapa,item.atividade),
                               css = 'text-align: right; color:#0000ff;pad;padding-right: 10px',
                               ))
            atividade = False
            idAtividade = item.atividade
            p = c
            c += 1

        if item.composicao:
            xItem = Composicao[int(item.composicao)].descricao
            unidade = Composicao[int(item.composicao)].unidade
        else:
            xItem = Insumo[int(item.insumo)].descricao
            unidade = Insumo[int(item.insumo)].unidade
        
        total = round(float(item.quantidade)*float(item.indice)*float(item.valor),2)
        linhas.append(dict(item = xItem,
                           id = item.id,
                           qtde = "{0:.2f}".format(round(float(item.quantidade) * float(item.indice),2)),
                           unidade=unidade,
                           valor = "{0:.2f}".format(item.valor),
                           total = "{0:.2f}".format(total),
                           c=c,
                           p=p,
                           css = 'text-align: right;padding-right: 10px',
                           ))
    return linhas


def atualizaretapa():
    atividades = db(Atividades.id>0).select()
    for atividade in atividades:
        Etapa_Atividades.update_or_insert((Etapa_Atividades.etapa == atividade.etapa) & (Etapa_Atividades.atividade == atividade.id),
                                         etapa = atividade.etapa,
                                         atividade = atividade.id   
                                         )
