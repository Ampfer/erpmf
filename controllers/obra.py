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

#@auth.requires_membership('admin')
def atividades():

    gridAtividades = grid(Atividades,60,orderby=Atividades.atividade)

    if gridAtividades.create_form:
        redirect(URL('atividade'))
    elif gridAtividades.update_form:
        redirect(URL('atividade', args=request.args(-1)))

    return dict(gridAtividades=gridAtividades)

#@auth.requires_membership('admin')
def atividade():
    idAtividade = request.args(-1) or "0"

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
            tipo = 'Composição'
        else:
            item = Insumo[int(form.vars.insumo)].descricao
            tipo = 'Insumo'

        Atividades_Itens[int(form.vars.id)] = dict(item = item, tipo=tipo)

    def validarItem(form):
        if form.vars.insumo and form.vars.composicao:
            form.errors.insumo = 'Cadastre Composição ou Insumo'
        if not form.vars.insumo and not form.vars.composicao:
            form.errors.insumo = 'Cadastre pelo menos uma Composição ou Insumo'


    fields = [Atividades_Itens.tipo,Atividades_Itens.item,Atividades_Itens.quantidade,Atividades_Itens.valor]
    gridItens = grid((Atividades_Itens.atividade==idAtividade),args=[idAtividade],searchable=False,onvalidation=validarItem,
        oncreate = completar_item, onupdate = completar_item,fields=fields)

    return dict(gridItens=gridItens)

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
        formObra = SQLFORM(Obras,field_id='id',_id='obra')
        loadAtividade = ''
        btnExcluir = btnNovo = ''
    else:
        formObra = SQLFORM(Obras, idObras,_id='obra',field_id='id')

        loadAtividade = LOAD(c='obra', f='obra_atividades', content='Aguarde, carregando...',
                           target='obraatividades', ajax=True, args=idObras)

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

    rows  = db(Atividades.etapa == request.vars.etapa).select() 
    
    atividades = []
    for row in rows:
        atividades.append(dict(atividade = row.atividade, id = row.id))
    atividadeJson = json.dumps(atividades)

    jquery = "$('#atividade_atividade').find('option').remove();$.each(%s, function (i, d) {$('<option>').val(d.id).text(d.atividade).appendTo($('#atividade_atividade'));});" %(atividadeJson)
    return  jquery

#@auth.requires_membership('admin')
def obra_atividades():
    idObra = int(request.args(0)) 

    formAtividade = SQLFORM.factory(
        Field('etapa','integer',label='Etapa:',requires=IS_EMPTY_OR(IS_IN_DB(db,'etapas.id','%(etapa)s'))),
        Field('atividade','integer',label='Item:',requires=IS_IN_DB(db,'atividades.id','%(atividade)s (%(unidade)s)')),
        Field('quantidade','Decimal',label='Quantidade:',requires=[IS_DECIMAL_IN_RANGE(dot=','),notempty]),
        table_name='atividade',
        submit_button='Adicionar',
        )
    formAtividade.element(_name='etapa')['_onchange'] = "ajax('%s',['etapa'],':eval');" % URL('obra', 'buscar_atividade')
    
    if formAtividade.process().accepted:
        
        itens = db(Atividades_Itens.atividade == formAtividade.vars.atividade).select()
        etapa = Atividades[int(formAtividade.vars.atividade)]['etapa']
        
        for item in itens:
            print item
            Obras_Itens[0] = dict(obra=idObra,
                               atividade = (formAtividade.vars.atividade),
                               etapa = (etapa), 
                               composicao = (item.composicao), 
                               insumo=item.insumo,
                               quantidade = formAtividade.vars.quantidade
                               )
        response.flash = 'Item Adicionado'
    elif formAtividade.errors:
        response.flash = 'Erro no Formulário'

    etapas = db(Obras_Itens.obra == idObra).select(Obras_Itens.etapa,distinct=True, orderby=Obras_Itens.etapa)
    
    result = []
    for etapa in etapas:
        q = (Obras_Itens.obra == idObra) & (Obras_Itens.etapa==etapa.etapa)
        atividades = db(q).select()
        xatividades = []
        for atividade in atividades:
            q1 = (Obras_Itens.obra == idObra) & (Obras_Itens.etapa==etapa.etapa) & (Obras_Itens.atividade==atividade.atividade)
            itens =  db(q).select()
            xitens = []
            for row in itens:
                if row.composicao:
                    item = Composicao[int(row.composicao)].descricao
                else:
                    item = Insumo[int(row.insumo)].descricao
                xitens.append(dict(item=item))

            xatividades.append(dict(id=atividade.atividade, itens = xitens))
        
        result.append(dict(etapa=etapa.etapa,atividade=xatividades))
  
    c = 0
    linhas = []
    for etapa in result:
        c = c + 1
        linhas.append(dict(item = Etapas[int(etapa['etapa'])].etapa, c=c, p=0))
        p = c    
        for atividade in etapa['atividade']:
            c = c+1
            linhas.append(dict(item=Atividades[int(atividade['id'])].atividade,c=c, p=p))
            pp = c
            for item in atividade['itens']:
                c = c+1
                linhas.append(dict(item = item['item'],c=c,p=pp))


    return dict(formAtividade=formAtividade, result=result, linhas=linhas)
