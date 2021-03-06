# -*- coding: utf-8 -*-
#@auth.requires_membership('admin')
def atualizarDemanda():
    insumos = db(PagarInsumos.id > 0).select()
    for insumo in insumos:
        demanda = Pagar[insumo.pagar].demanda
        PagarInsumos[insumo.id] = dict(demanda=demanda)

def entrada_lista():
    fields = (Pagar.emissao ,Pagar.documento,Pagar.fornecedor, Pagar.demanda, Pagar.valor)
    grid_pagar = grid(Pagar,formname="lista_pagar",fields=fields,orderby=~Pagar.emissao)

    if request.args(-2) == 'new':
       redirect(URL('entrada'))
    elif request.args(-3) == 'edit':
       idd = request.args(-1)
       redirect(URL('entrada', args=idd ))

    return locals()

#@auth.requires_membership('admin')
def pesquisarFornecedor():
    fields = [Fornecedores.id,Fornecedores.nome]
    links=[dict(header='Selecionar',
                body=lambda row: A(TAG.button(I(_class='glyphicon glyphicon-edit')),
               _href='#', _onclick="selecionar(%s);" %row.id))]

    pesq = SQLFORM.grid(Fornecedores,csv=False,details=False,maxtextlength=50,fields=fields,orderby=Fornecedores.nome,
                        paginate=5,create=False,editable=False,deletable=False,links=links)

    return locals()

#@auth.requires_membership('admin')
def entrada():
    id_pagar = request.args(0) or "0"

    if id_pagar == "0":
        Pagar.emissao.default= request.now.date()
        form_pagar = SQLFORM(Pagar,field_id='id',_id='form_pagar')
        form_parcelas = form_despesas = form_insumos = " Primeiro Cadastre um Contas a Pagar"
        btnExcluir = btnNovo = ''
        
    else:
        form_pagar = SQLFORM(Pagar,id_pagar,_id='form_form_pagar' ,field_id='id')

        form_insumos = LOAD(c='pagar', f='pagarInsumos', args=[id_pagar],
                     content='Aguarde, carregando...', target='pagarinsumos', ajax=True)

        form_parcelas = LOAD(c='pagar',f='pagar_parcelas',args=[id_pagar],
                     content='Aguarde, carregando...',target='parcelas',ajax=True)

        form_despesas = LOAD(c='pagar',f='pagar_despesas',args=[id_pagar],
                     content='Aguarde, carregando...',target='despesas',ajax=True)

        btnExcluir = excluir("#")
        btnNovo = novo("entrada")

    btnVoltar = voltar("entrada_lista")
    btnPesquisar = pesquisar('pagar','pesquisarFornecedor','Pesquisar Fornecedor')

    if form_pagar.process().accepted:
        response.flash = 'Salvo com sucesso!'
        session.valor = form_pagar.vars.valor
        redirect(URL('entrada', args=[form_pagar.vars.id]))
        session.valor = 0

    elif form_pagar.errors:
        response.flash = 'Erro no Formulário Principal!'
    return locals()

#@auth.requires_membership('admin')
def pesquisarInsumo():
    fields = [Insumo.codigo,Insumo.descricao,Insumo.unidade,Insumo.tipo,Insumo.preco]
    links=[dict(header='Selecionar',
                body=lambda row: A(TAG.button(I(_class='glyphicon glyphicon-edit')),
               _href='#', _onclick="selecionar(%s);" %row.id))]

    pesq = SQLFORM.grid(Insumo,csv=False,details=False,maxtextlength=50,fields=fields,orderby=Insumo.descricao,
                        paginate=5,create=False,editable=False,deletable=False,links=links)

    return locals()

def insumoTrigger():
    idFornecedor = Pagar(request.vars.id_pagar).fornecedor
    conta = Insumo[request.vars.insumo].conta
    query = (Custo.insumo==request.vars.insumo) & (Custo.fornecedor==idFornecedor)
    try:
        custo = db(query).select(Custo.custo,Custo.unidade).first()
        preco = float(custo.custo)
        unidade = custo.unidade
    except:
        preco=Insumo[request.vars.insumo].preco
        unidade = Insumo[request.vars.insumo].unidade

    return "jQuery('#pagarInsumos_preco').val('%s');" \
           "jQuery('#pagarInsumos_unidade').val('%s');" \
           "jQuery('#pagarInsumos_conta').val('%s');" \
           "jQuery('#pagarInsumos_quantidade').focus();" \
           % (preco,unidade,conta)

#@auth.requires_membership('admin')
def pagarInsumos():
    
    id_pagar = int(request.args(0))
    sum = (PagarInsumos.preco * PagarInsumos.quantidade - PagarInsumos.desconto).sum()
    total_insumos = float(db(PagarInsumos.pagar==id_pagar).select(sum).first()[sum] or 0)

    def atualizaTabelas(form,idpagar=id_pagar):
        session.etapa = form.vars.etapa
        session.demanda = form.vars.demanda
        idFornecedor = Pagar[int(idpagar)].fornecedor
        #### Atualiza Tabela Custo #####
        query = (Custo.insumo == form.vars.insumo) & (Custo.fornecedor == idFornecedor)
        Custo.update_or_insert(query,
                               unidade=form.vars.unidade,
                               custo=form.vars.preco,
                               insumo=form.vars.insumo,
                               embalagem =1,
                               fornecedor=idFornecedor,
                               )
        #### Atualiza Tabela Insumo (preco) #####
        max = Custo.custo.max()
        insumo = int(form.vars.insumo)
        query = Custo.insumo== insumo
        custo = float(db(query).select(max).first()[max] or 0)
        Insumo[insumo] = dict(preco=custo)

    PagarInsumos.pagar.default = 10
    PagarInsumos.pagar.default = id_pagar
    PagarInsumos.desconto.default = 0.00
    if session.etapa:
        PagarInsumos.etapa.default = session.etapa
    if session.demanda:
        PagarInsumos.demanda.default = session.demanda


    fields=[PagarInsumos.insumo,PagarInsumos.unidade,PagarInsumos.quantidade,PagarInsumos.preco,PagarInsumos.desconto,
            PagarInsumos.total,PagarInsumos.demanda]

    formInsumos = grid(PagarInsumos.pagar==id_pagar,alt='250px',
                               args=[id_pagar],formname = "pagarinsumos",
                               searchable = False, fields=fields,
                               deletable=True,onvalidation=atualizaTabelas,
                               )

    if formInsumos.create_form or formInsumos.update_form:
        formInsumos[1].element(_name='insumo')['_onchange'] = "ajax('%s', ['insumo'], ':eval');" % URL('pagar', 'insumoTrigger',vars=dict(id_pagar=id_pagar))
        formInsumos[1].element(_name='insumo')['_onblur']   = "ajax('%s', ['insumo'], ':eval');" % URL('pagar', 'insumoTrigger',vars=dict(id_pagar=id_pagar))

    btnVoltar = voltar1('pagarinsumos')
    btnPesquisar = pesquisar('pagar','pesquisarInsumo','Pesquisar Insumo')

    if formInsumos.update_form:
        btnExcluir = excluir("#")
    else:
        btnExcluir = ''

    return locals()

#@auth.requires_membership('admin')
def pagar_parcelas():
    id_pagar = int(request.args(0))

    old_valor = request.post_vars.valor or "0"

    pagar = db(Pagar.id==id_pagar).select(Pagar.valor,Pagar.condicao,Pagar.emissao,Pagar.tipo).first()
    pagar_valor = float(pagar[Pagar.valor])
    pagar_condicao = int(pagar[Pagar.condicao])
    pagar_emissao = pagar[Pagar.emissao]
    pagar_tipo = pagar[Pagar.tipo]
    rows = db(Pagar_parcelas.pagar==id_pagar).select(Pagar_parcelas.valor.sum()).first()
    total_parcela = float(rows[Pagar_parcelas.valor.sum()] or 0) 

    def atualiza_parcela():
        rows = db(Pagar_parcelas.pagar==id_pagar).select(orderby=Pagar_parcelas.vencimento)
        teste = []       
        for index,row in enumerate(rows):
            id_parc = int(row[Pagar_parcelas.id])
            parc = (str(index+1) + '/' + str(len(rows)))
            Pagar_parcelas[int(id_parc)] = dict(parcela=parc)
            teste.append(id_parc)
        
    def gera_parcela(id_pagar,pagar_valor,pagar_condicao,pagar_emissao):
        from datetime import timedelta
        condicao = db(Condicao.id ==  pagar_condicao ).select(Condicao.dias).first()[Condicao.dias]
        for index,dia in enumerate(condicao):
            parcela_valor = round(pagar_valor/len(condicao),2)
            #parcela_parcela = (str(index+1) + '/' + str(len(condicao)))
            parcela_parcela = '1'
            parcelas = dict(pagar = id_pagar,parcela=parcela_parcela,vencimento = pagar_emissao + timedelta(dia),valor=parcela_valor)
            Pagar_parcelas[0] = parcelas 

    if total_parcela == 0 and pagar_tipo != 'Transferência':
        gera_parcela(id_pagar,pagar_valor,pagar_condicao,pagar_emissao)
   
    Pagar_parcelas.pagar.default = id_pagar
    Pagar_parcelas.valor.default = pagar_valor - total_parcela
    Pagar_parcelas.valorpago.default = 0
    #Pagar_parcelas.parcela.writable = False
           
    atualiza_parcela()

    def validar(form,total_parcela=total_parcela,pagar_valor=pagar_valor):
        if request.args(-3) == 'edit':
            id_parcela = request.args(-1)
            old_valor = float(Pagar_parcelas(id_parcela).valor)
        else:
            old_valor = 0    
        if (total_parcela + float(form.vars.valor) - old_valor) > pagar_valor:
            form.errors.valor = "Soma das Parcelas é Maior que o Valor do Documento"
        elif (total_parcela + float(form.vars.valor) - old_valor) < pagar_valor:
            session.flash = 'Valor do Ducumento: %s Soma das Parcelas: %s ' %(pagar_valor,total_parcela) 

    def deletar_parcela(table,id):
        return atualiza_parcela()


    formParcelas = grid((Pagar_parcelas.pagar==id_pagar),alt='250px',
            formname="parcelas",searchable = False,args=[id_pagar],onvalidation=validar,
            ondelete = deletar_parcela,deletable=True,editargs= dict(deletable=True),
            orderby=Pagar_parcelas.vencimento,)

    btnVoltar = voltar1('parcelas')

    if formParcelas.update_form:
        btnExcluir = excluir("#")
    else:
        btnExcluir = ''

    return locals()

def geraDespesas():

    idPagar = int(request.args(0))
    pagar = Pagar(idPagar)
    
    try:
        rr = db(PagarInsumos.pagar == idPagar).select(orderby = PagarInsumos.insumo)

        for r in rr:
            
            #valorDespesa += round(float(r.quantidade)*float(r.preco),2) - float(r.desconto)
            
            valorDespesa = round(float(r.quantidade)*float(r.preco),2) - float(r.desconto)
            tipoInsumo = Insumo(int(r.insumo)).tipo
            conta = db(TipoInsumo.descricao == tipoInsumo).select().first()['conta']
            query = (Despesas.despesa == int(conta)) & (Despesas.demanda == int(r.demanda)) & (Despesas.pagar == int(idPagar))
            try:
                totalDespesas = float(db(query).select().first()['valor'])
            except :
                totalDespesas = 0
      
            Despesas.update_or_insert(query,
                                      pagar = idPagar,
                                      dtdespesa = pagar.emissao,                                  
                                      demanda=r.demanda,
                                      despesa=conta,
                                      valor = valorDespesa + totalDespesas
                                      )   
    except:
        pass
    session.demanda = ''
    response.js = "$('#despesas').get(0).reload()"

#@auth.requires_membership('admin')
def pagar_despesas():

    idPagar = int(request.args(0))
    pagar = Pagar(idPagar)
    Despesas.pagar.default = idPagar
    Despesas.dtdespesa.default = pagar.emissao
    Despesas.demanda.default = pagar.demanda

    if session.demanda:
        Despesas.demanda.default = session.demanda
    
    total_despesas = (db(Despesas.pagar==idPagar).select(Despesas.valor.sum()).first())[Despesas.valor.sum()] or 0
    Despesas.valor.default = float(pagar.valor) - float(total_despesas or 0)

   
    def validar(form,total_despesas=float(total_despesas or 0),pagar_valor=pagar.valor):
        
        session.demanda = form.vars.demanda
        if 'edit' in request.args:
            id_despesa = request.args(-1)
            old_valor = float(Despesas(id_despesa).valor)
        else:
            old_valor = 0  
        if round((total_despesas + float(form.vars.valor) - old_valor),2) > round(pagar_valor,2):
            form.errors.valor = "Soma das Despesas é Maior que o Valor do Documento" 
        elif round((total_despesas + float(form.vars.valor) - old_valor),2) < round(pagar_valor,2):
            session.flash = 'Valor do Ducumento: %s Soma das Despesas: %s ' %(pagar_valor,total_despesas) 

    fields = (Despesas.dtdespesa,Despesas.despesa, Despesas.demanda, Despesas.valor)
    formDespesas = grid(Despesas.pagar==idPagar,alt='250px',
        formname="despesas",searchable = False,args=[idPagar],fields=fields,onvalidation=validar)


    btnGerar = A(SPAN(_class="glyphicon glyphicon-cog"), ' Gerar ', _class="btn btn-default",_id='gerar',
             _onclick="if (confirm('Deseja Gerar Despesas ?')) ajax('%s', [], 'despesas');" %URL('pagar', 'geraDespesas', args=[idPagar,request.args(-1)]))

    formDespesas[0].insert(-1, btnGerar)

    btnVoltar = voltar1('despesas')

    if formDespesas.update_form:
        btnExcluir = excluir("#")
    else:
        btnExcluir = ''

    return locals()

#@auth.requires_membership('admin')
def pagamento_modal(ids):
    response.js = "show_modal('%s','teste');" % URL('pagar','pagamentos.load',vars=dict(ids=ids))
    return False

#@auth.requires_membership('admin')
def pagar_lista():
       
    form_pesq = SQLFORM.factory(
        Field('fornecedor','integer',label='Fornecedor:',requires=IS_IN_DB(db,'fornecedores.id','fornecedores.nome',zero='TODOS')),
        Field('status',label='Status',default = 'Pendente',requires=IS_IN_SET(['Todos','Pendente','Pago'],zero=None)),
        Field('dtinicial','date',label='Data Inicial:',requires=data,),
        Field('dtfinal','date',requires=data,label='Data Final',),
        Field('documento',label='Documento:'),
        table_name='pesquisar',
        submit_button='Filtrar',
        )  
    
    if form_pesq.process().accepted:
        pass       
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    return dict(form_pesq=form_pesq)

def gerar_pagar():
    from datetime import datetime

    idFornecedor = request.vars.fornecedor
    inicial = datetime.strptime(request.vars.dtinicial,'%d/%m/%Y').date() if request.vars.dtinicial != '' else ''
    final = datetime.strptime(request.vars.dtfinal,'%d/%m/%Y').date() if request.vars.dtfinal != '' else ''
    status = request.vars.status
    documento = request.vars.documento.split(',')
    

    query = (Pagar_parcelas.pagar == Pagar.id) & (Fornecedores.id == Pagar.fornecedor)
    if idFornecedor:
        query = query & (Pagar.fornecedor == idFornecedor)
    if inicial != '':
        query = query & (Pagar_parcelas.vencimento >= inicial)
    if final != '':
        query = query & (Pagar_parcelas.vencimento <= final)
    if status == 'Pendente':
        query = query & (Pagar_parcelas.dtpagamento == None)
    if status == 'Pago':
        query = query & (Pagar_parcelas.dtpagamento != None) 
    if documento != ['']:
        query = query & (Pagar.documento.contains(documento))

    total = db(query).select(Pagar_parcelas.valor.sum()).first()[Pagar_parcelas.valor.sum()] or 0
    total_pago = db(query).select(Pagar_parcelas.valorpago.sum()).first()[Pagar_parcelas.valorpago.sum()] or 0
    total_pendente = total - total_pago

    duplicatas = db(query).select(
                            Pagar_parcelas.id.with_alias('rowId'),
                            Fornecedores.nome.with_alias('fornecedor'),
                            Pagar.documento.with_alias('documento'),
                            Pagar_parcelas.parcela.with_alias('parcela'),
                            Pagar.emissao.with_alias('emissao'),
                            Pagar_parcelas.vencimento.with_alias('vencimento'),
                            Pagar_parcelas.dtpagamento.with_alias('pagamento'),
                            Pagar_parcelas.valor.with_alias('valor'),
                            (Pagar_parcelas.valor - Pagar_parcelas.valorpago).with_alias('pendente'),
                            orderby = Pagar_parcelas.vencimento
                            )

    return dict(duplicatas=duplicatas,total=total,total_pago=total_pago,total_pendente=total_pendente)

def buscadoc(ids,loteId=0):

    if loteId != 0:
        ids = Lote[loteId].parcelas

    dcto = db(Pagar_parcelas.id.belongs(ids)).select(db.pagar.documento, db.pagar_parcelas.parcela,
              left=db.pagar_parcelas.on(db.pagar.id == db.pagar_parcelas.pagar))

    doctos = []
    for x in dcto:
        doctos.append('(' + x.pagar.documento + '-' + x.pagar_parcelas.parcela + ') ')
    return doctos

#@auth.requires_membership('admin')
def lotes():
    Lote.id.readable = True
    Lote.dtlote.readable = True
    Lote.documentos = Field.Virtual('documentos',lambda row: buscadoc(row.lote.parcelas),label='Documentos')

    form = grid(Lote.tipo == "pagar",
        orderby=~Lote.dtlote,create=False,deletable=False,editable=False,
        searchable=False,formname="pagarLotes",
        links =[lambda row: A(SPAN(_class="glyphicon glyphicon-pencil"), _class="btn btn-default",
                                   _href=URL('pagar','pagar',vars=dict(id_lote=row.id,target='pagarLotes',url='pagar_lista'))),
                lambda row: A(SPAN(_class="glyphicon glyphicon-trash"),_id="lote_delete", _class="btn btn-default",
                                   _href=URL('pagar','lote_delete',vars=dict(id_lote=row.id,total=row.total,url='lotes')))
               ],
        )
    
    return dict(form=form)

#@auth.requires_membership('admin')
def lote_delete():
    url = request.vars.url
    id_lote = request.vars.id_lote

    parcelas = Lote[id_lote].parcelas
    
    del Lote[id_lote]
    db(Lote_parcelas.lote == id_lote).delete()
    db(Conta_corrente.lote == id_lote).delete()
    db(Cheques.lotpag==id_lote).delete()

    for parcela in parcelas:
        atualizaParcela(parcela,None)
    
    redirect(URL(url))

#@auth.requires_membership('admin')
def pagar():
    
    session.id_lote = request.vars.id_lote or 0
    try:
        int(session.id_lote)
    except ValueError:
        session.id_lote = 0

    btnVoltar = voltar('pagar_lista')  
    
    if session.id_lote ==0:
        ids=[]
        for row in request.vars:
            ids.append( request.vars[row])
        if ids == []:
            session.flash = 'Selecione pelo menos uma Parcela'
            redirect(URL(c="pagar",f="pagar_lista"))
        else:
            session.ids = ids
    else:
        session.ids = Lote[session.id_lote].parcelas

    form_parcelas = LOAD(c='pagar',f='mostrar_parcelas',
        content='Aguarde, carregando...',target='mostrar_parcelas',ajax=True,)

    form_pagamentos = LOAD(c='pagar',f='pagamentos_lista',
        content='Aguarde, carregando...',target='pagamentos_lista',ajax=True,)

    form_cheques = LOAD(c='pagar',f='pagamentosCheques',
        content='Aguarde, carregando...',target='pagamentosCheques',ajax=True,)

    return locals()
    
#@auth.requires_membership('admin')
def mostrar_parcelas():
        
    query = db(Pagar_parcelas.id.belongs(session.ids))

    sum = (Pagar_parcelas.valor - Pagar_parcelas.valorpago).sum()
    session.total_pagar = query.select(sum).first()[sum] or 0
    form = SQLFORM.grid(query,
        searchable = False,create=False,deletable = False,editable = False,details=False,
        csv=False,user_signature=False,
        )
    return locals()

#@auth.requires_membership('admin')
def pagamentos_delete():
    id = request.args(0)
    valoranterior = 0 - db(Conta_corrente.id == id).select(Conta_corrente.vlpagamento).first()[Conta_corrente.vlpagamento]
    datapg = None
    idLote = db(Conta_corrente.id==id).select(Conta_corrente.lote).first()['lote']
    del Conta_corrente[id]
    '''
    if db(Conta_corrente.lote==idLote).count() == 0:
        parcelas = Lote[idLote].parcelas
        #del Lote[idLote]
        db(Lote_parcelas.lote == idLote).delete()
        db(Cheques.lotpag==idLote).delete()
        for parcela in parcelas:
            atualizaParcela(parcela,None)    
        #redirect(URL('pagar',vars=dict(ids=session.ids)))
    else:
    '''        
    atualizaPagamentos(idLote)
    response.js = "$('#pagamentos_lista').get(0).reload()"
    #redirect(URL('pagar',vars=dict(ids=session.ids,id_lote=session.id_lote)))
    

#@auth.requires_membership('a#dmin')    
def pagamentos_lista():
    
    query = db(Conta_corrente.lote == session.id_lote)
    session.total_pagamentos = query.select(Conta_corrente.vlpagamento.sum()).first()[Conta_corrente.vlpagamento.sum()] or 0
    fields = [Conta_corrente.lote,Conta_corrente.conta, Conta_corrente.dtpagamento,
              Conta_corrente.vlpagamento,Conta_corrente.desconto,Conta_corrente.juros]
    form = SQLFORM.grid(Conta_corrente.lote==session.id_lote,
            formname="pagamentos",_class='web2py_grid',csv=False,maxtextlength=50,fields=fields,
            searchable = False,create=False,deletable=False,editable=False,details = False,
            links =[lambda row: A(SPAN(_class="glyphicon glyphicon-pencil"), _class="btn btn-default",_href='#',_onclick="show_modal('%s','Pagamentos');" % URL('pagar','pagamentos',args=[row.id])),
                    lambda row: A(SPAN(_class="glyphicon glyphicon-trash"), _class="btn btn-default",_id='excluir',_onclick="return confirm('Deseja Excluir esse Pagamento ?');"  ,callback=URL('pagar','pagamentos_delete',args=[row.id]))
                   ],
            )
    
    novo =A(SPAN(_class="glyphicon glyphicon-plus"), _class="btn btn-default", _id='novo')
    form[0].insert(-1,novo)

    return dict(form=form)


def pagamentos():

    id_pagamento = request.args(0) or "0"

    Conta_corrente.lote.readable = False
    Conta_corrente.vlrecebimento.readable = Conta_corrente.vlrecebimento.writable = False
    Conta_corrente.descricao.readable = Conta_corrente.descricao.writable = False
    Conta_corrente.vlrecebimento.default = 0
    Conta_corrente.desconto.default = 0
    Conta_corrente.juros.default = 0

    if id_pagamento == "0":
        Conta_corrente.dtpagamento.default= request.now.date()
        Conta_corrente.vlpagamento.default = session.total_pagar - session.total_pagamentos
        form_pagamentos = SQLFORM.factory(Lote,Conta_corrente,_id='form_pagamentos',field_id='id',table_name='pagamentos')

        if form_pagamentos.process().accepted:
            if session.id_lote == 0:
                session.id_lote = Lote.insert(dtlote = form_pagamentos.vars.dtpagamento,
                                              tipo = 'pagar',
                                              parcelas=session.ids)

            descricao = "PAG LT %s %s" %('{:0>4}'.format(session.id_lote),buscadoc(0,session.id_lote)[0])

            Conta_corrente.insert(dtpagamento = form_pagamentos.vars.dtpagamento,
                                  vlpagamento = form_pagamentos.vars.vlpagamento,
                                  desconto = form_pagamentos.vars.desconto,
                                  juros = form_pagamentos.vars.juros,
                                  tipo = 'pagar',
                                  lote=session.id_lote,
                                  conta= form_pagamentos.vars.conta,
                                  descricao=descricao)
            
            atualizaPagamentos(session.id_lote)

            response.flash='Pagamentos Salvo com Sucesso!'
            response.js = 'hide_modal(%s);' %("'pagamentos_lista'")
        elif form_pagamentos.errors:
            response.flash = 'Erro no Formulário...!' 
    else:
        valoranterior = db(Conta_corrente.id == id_pagamento).select(Conta_corrente.vlpagamento).first()[Conta_corrente.vlpagamento]

        form_pagamentos = SQLFORM(Conta_corrente,id_pagamento,submit_button='Alterar',_id='form_pagamentos',field_id='id')

        if form_pagamentos.process().accepted:
            atualizaPagamentos(session.id_lote)
            response.flash = 'Pagamento Alterado com Sucesso!'
            response.js = 'hide_modal(%s);' %("'pagamentos_lista'")

        elif form_pagamentos.errors:
            response.flash = 'Erro no Formulário...!'

    return dict(form_pagamentos=form_pagamentos)

def totalLote(idLote):
    query = (Conta_corrente.lote == idLote)
    sum = (Conta_corrente.vlpagamento + Conta_corrente.desconto - Conta_corrente.juros).sum()
    #sum = (Conta_corrente.vlpagamento).sum()
    try:
        total = round(float(db(query).select(sum).first()[sum]),2)
    except:
        total = 0
    return total


def atualizaPagamentos(idLote):

    ids = Lote[idLote].parcelas
    valorpago = totalLote(idLote)
    
    datapg = None 
    parcelas = db(Pagar_parcelas.id.belongs(ids)).select(Pagar_parcelas.id, Pagar_parcelas.valor,
                                                                 orderby=Pagar_parcelas.vencimento)
    # zerando pagamentos do Lote
    db(Lote_parcelas.lote == idLote).update(valpag=0)    

    for parcela in parcelas:
        idParcela = parcela.id
        valorpendente = float(parcela.valor) - valorPago(idParcela)
        
        valor = min(valorpago,valorpendente)

        
        query = (Lote_parcelas.lote == idLote) & (Lote_parcelas.parcela == idParcela)
        Lote_parcelas.update_or_insert(query,
            lote= idLote,
            parcela = idParcela,
            valpag =  valor,
            )
        
        valorpago = valorpago - valor       
        
        atualizaParcela(idParcela,idLote)


def valorPago(idParcela):
    query = (Lote_parcelas.parcela == idParcela) & (Lote.id==Lote_parcelas.lote) & (Lote.tipo=='pagar')
    sum = (Lote_parcelas.valpag).sum()
    try:
        valor = round(float(db(query).select(sum).first()[sum]),2)
    except:
        valor = 0
    return valor   

def atualizaParcela(idParcela,idLote):
    
    valor=valorPago(idParcela)
   
    Pagar_parcelas[idParcela] = dict(valorpago=valor)

    if idLote == None:
        Pagar_parcelas[idParcela] = dict(dtpagamento=None)
    
    if round(Pagar_parcelas[idParcela].valor,2) <= round(valor,2):
        datapg = db(Conta_corrente.lote == idLote).select(Conta_corrente.dtpagamento,orderby=~Conta_corrente.dtpagamento).first() or None
        Pagar_parcelas[idParcela] = dict(dtpagamento=datapg['dtpagamento'])


def atualizarcontaspagar():
    contas = db(Conta_corrente.id>0).select(orderby=Conta_corrente.dtpagamento)
    for conta in contas:
        if conta.tipo == 'pagar':
            try:
                atualizaPagamentos(conta.lote)
            except:
                print conta.lote

def excluirCheque():
    idCheque = request.args(0)
    Cheques[idCheque] = dict(lotpag=None)
    response.js = "$('#pagamentosCheques').get(0).reload()"

#@auth.requires_membership('admin')
def pagamentosCheques():

    sum = Cheques.valor.sum()
    total_cheques= db(Cheques.lotpag == session.id_lote).select(sum).first()[sum]

    links = [lambda row: A(SPAN(_class="glyphicon glyphicon-trash"), _class="btn btn-default", _id='excluirCheque',_onclick="return confirm('Deseja Excluir esse Cheque ?');",callback=URL('pagar', 'excluirCheque', args=[row.id]))]

    gridCheques = SQLFORM.grid(Cheques.lotpag==session.id_lote,searchable=False,create=False,details=False,deletable=False,editable=False,
                                 csv=False,maxtextlength=50,user_signature=False,links=links)

    form_pesq = SQLFORM.factory(
        Field('cheque',
        requires=IS_IN_DB(db(Cheques.lotpag == None),"cheques.id",'%(banco)s %(agencia)s %(conta)s N. %(cheque)s R$ %(valor)s %(nome)s'    ,zero='Selecione um Cheque')),
        table_name='pesquisar',
        submit_button='Salvar',)

    if form_pesq.process().accepted:
        Cheques[form_pesq.vars.cheque] = dict(lotpag=session.id_lote)
        redirect('#')
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    return locals()

#@auth.requires_membership('admin')   
def fornecedor_ficha():

    #session.fornecedor = None

    form_pesq = SQLFORM.factory(
        Field('fornecedor',default=request.vars.fornecedor or session.fornecedor,requires=IS_IN_DB(db,"fornecedores.id",'%(nome)s',zero='Selecione um Fornecedor')),
        table_name='pesquisar',
        submit_button='Selecionar',
        )  

    if form_pesq.process().accepted:
        session.fornecedor = form_pesq.vars.fornecedor
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    
    query = (Pagar_parcelas.pagar == Pagar.id) & (Pagar.fornecedor==session.fornecedor)
    '''
    lotes=[0]
    for row in db(query).select(Pagar_parcelas.lote):
        lotes.append(row.lote)
    '''
    total = db(query).select(Pagar_parcelas.valor.sum()).first()[Pagar_parcelas.valor.sum()] or 0
    total_pago = db(query).select(Pagar_parcelas.valorpago.sum()).first()[Pagar_parcelas.valorpago.sum()] or 0
    total_pendente = total - total_pago

    form_parcelas = ' '
    fields = [Pagar.documento,Pagar_parcelas.parcela,Pagar.emissao,Pagar_parcelas.vencimento,
              Pagar_parcelas.dtpagamento,Pagar_parcelas.valor,Pagar_parcelas.lote,Pagar_parcelas.valorpendente, Pagar_parcelas.status]
    
    if session.fornecedor:
        '''
        links = [lambda row: A(SPAN(_class="glyphicon glyphicon-share-alt"),' Pagar', _class="btn btn-default",_id='pagar',_title="Pagar Parcelas",
                                        _href=URL('pagar',vars=dict(id_lote = row.pagar_parcelas.lote,ids=row.pagar_parcelas.id,url="fornecedor_ficha")))]
        '''
        form_parcelas = grid(query,
            formname="fornecedor_parcelas",field_id = Pagar_parcelas.id,orderby=Pagar_parcelas.vencimento,fields=fields,
            deletable = False,editable = False,create=False,searchable=False)

    formPagamentos = LOAD(c='pagar',f='fornecedorPagamentos',target='fornecedorPagamentos',ajax=True,args=session.fornecedor)

    btnPesquisar = pesquisar('pagar', 'pesquisarFornecedor', 'Pesquisar Fornecedor')

    return locals()

#@auth.requires_membership('admin')
def fornecedorPagamentos():

    id_fornecedor = request.args(0)

    qparcelas = (Pagar_parcelas.pagar==Pagar.id) & (Pagar.fornecedor==id_fornecedor) 
    parcelas = db(qparcelas).select(Pagar_parcelas.id)
    lotes = []
    for parcela in parcelas:
        for lote in db(Lote.id>0).select():
            if parcela.id in lote.parcelas:
                lotes.append(lote.id)

    Conta_corrente.lote.readable = True
    Conta_corrente.descricao.readable = True
    fields = [Conta_corrente.dtpagamento,Conta_corrente.descricao,Conta_corrente.conta,Conta_corrente.vlpagamento,Conta_corrente.desconto,Conta_corrente.juros]

    qridPagamentos = grid(db(Conta_corrente.lote.belongs(lotes)),searchable=False,create=False,deletable=False,
        editable=False,fields=fields,groupby = Conta_corrente.lote, orderby = Conta_corrente.dtpagamento)
    return dict(qridPagamentos=qridPagamentos)

#@auth.requires_membership('admin')
def compras():
    fields = [Compras.emissao,Compras.documento,Compras.fornecedor,Compras.demanda, Compras.tipo,Compras.valor]
    gridCompras = grid(Compras,formname="compras",orderby=~Compras.emissao,fields=fields)

    if request.args(-2) == 'new':
        redirect(URL('compra'))
    elif request.args(-3) == 'edit':
        idd = request.args(-1)
        redirect(URL('compra', args=idd))

    return dict(gridCompras=gridCompras)

#@auth.requires_membership('admin')
def compra():
    id_compra = request.args(0) or "0"

    if id_compra == "0":
        Compras.emissao.default = request.now.date()
        mx = Compras.id.max()
        try:
            Compras.documento.default = '{:0>6}'.format(int(db(Compras.id>0).select(mx).first()[mx])+1)
        except:
            Compras.documento.default = 1
 
        formCompra = SQLFORM(Compras, field_id='id', _id='compra')
        formCompraInsumos = ''
        btnExcluir = btnNovo = ''

    else:
        formCompra = SQLFORM(Compras,id_compra, field_id='id', _id='compra')

        formCompraInsumos = LOAD(c='pagar', f='compraInsumos', args=[id_compra],
                            content='Aguarde, carregando...', target='comprainsumos', ajax=True)

        btnExcluir = excluir("#")
        btnNovo = novo("compra")

    formCompra.element(_name='documento')['_readonly'] = "readonly"
    btnVoltar = voltar("compras")
    btnPesquisar = pesquisar('pagar', 'pesquisarFornecedor', 'Pesquisar Fornecedor')

    btnEmail = email(id_compra)
    pdf_link = pdf("compraPdf",id_compra)

    formCompra.element('#compras_obs')['_rows']=3

    if formCompra.process().accepted:
        response.flash = 'Salvo com sucesso!'
        redirect(URL('compra', args=[formCompra.vars.id]))
    elif formCompra.errors:
        response.flash = 'Erro no Formulário Principal!'

    return locals()

def insumoTriggerCompra():
    idFornecedor = Compras(request.vars.id_compra).fornecedor
    query = (Custo.insumo==request.vars.insumo) & (Custo.fornecedor==idFornecedor)
    try:
        custo = db(query).select(Custo.custo,Custo.unidade).first()
        preco = float(custo.custo)
        unidade = custo.unidade
    except:
        preco=Insumo[request.vars.insumo].preco
        unidade = Insumo[request.vars.insumo].unidade

    return "jQuery('#comprasInsumos_preco').val('%s');" \
           "jQuery('#comprasInsumos_unidade').val('%s');" \
           "jQuery('#comprasInsumos_quantidade').focus();" \
           % (preco,unidade)

#@auth.requires_membership('admin')
def compraInsumos():
    id_compra = int(request.args(0))
    id_fornecedor = Compras(id_compra).fornecedor

    sum = (ComprasInsumos.quantidade*ComprasInsumos.preco - ComprasInsumos.desconto).sum()
    totalInsumos = float(db(ComprasInsumos.compra == id_compra).select(sum).first()[sum] or 0)

    query = (Insumo.id == Custo.insumo) & (Custo.fornecedor == id_fornecedor)

    ComprasInsumos.insumo.requires = IS_IN_DB(db(query),'insumos.id','%(descricao)s')
    ComprasInsumos.compra.default = id_compra
    ComprasInsumos.desconto.default = 0.00

    fields=[ComprasInsumos.insumo,ComprasInsumos.detalhe,ComprasInsumos.unidade,ComprasInsumos.quantidade,ComprasInsumos.preco,ComprasInsumos.desconto,
            ComprasInsumos.total]

    formInsumos = grid(ComprasInsumos.compra==id_compra,
                               args=[id_compra],formname = "comprainsumos",
                               searchable = False, fields=fields,
                               deletable=True,
                               )

    if formInsumos.create_form or formInsumos.update_form:
        formInsumos[1].element(_name='insumo')['_onchange'] = "ajax('%s', ['insumo'], ':eval');" % URL('pagar', 'insumoTriggerCompra',vars=dict(id_compra=id_compra))
        formInsumos[1].element(_name='insumo')['_onblur']   = "ajax('%s', ['insumo'], ':eval');" % URL('pagar', 'insumoTriggerCompra',vars=dict(id_compra=id_compra))
        formInsumos[1].element(_name='unidade')['_readonly'] = "readonly"
    btnVoltar = voltar1('comprainsumos')
    btnPesquisar = pesquisar('pagar','pesquisarInsumo','Pesquisar Insumo')

    if formInsumos.update_form:
        btnExcluir = excluir("#")
    else:
        btnExcluir = ''

    return locals()

def emailTrigger():
    return "jQuery('#email_email').val('%s');" %(request.vars.para)

#@auth.requires_membership('admin')
def enviarEmail():
    import os
    idCompra = request.vars.id_compra
    idFornecedor = Compras[idCompra].fornecedor
    query = (Contatos.fornecedor == idFornecedor)

    compraGeraPdf(idCompra)

    emaildefault=db(query&Contatos.departamento=='Vendas').select(Contatos.email).first()['email']
    Emails.email.default = emaildefault
    Emails.assunto.default = 'Pedido de Compra n. %s' %Compras[idCompra].documento

    anexo = 'Ped%s_%s.pdf' %('{:0>3}'.format(Compras[idCompra].fornecedor),Compras[idCompra].documento)
    pdf = os.path.join(request.folder, 'static', 'pdf', '%s') %(anexo)
    Emails.anexo.default = anexo
    Emails.anexo.writable = False

    form = SQLFORM.factory(Field('para', requires=IS_IN_DB(db(query),'contatos.email','%(nome)s - %(departamento)s - %(email)s',
                                 zero = 'Escolha um e-mail'),label='Para:',default=emaildefault),Emails,table_name='email',)

    form.element('#email_para')['_onchange'] = "ajax('%s', ['para'], ':eval');" % URL('pagar','emailTrigger')
    form.element(_type='submit')['_value'] = 'Enviar'

    if form.process().accepted:
        if mail:
            if mail.send(to=form.vars.email,
                         subject= form.vars.assunto,
                         message= form.vars.mensagem,
                         attachments = mail.Attachment(pdf)
                         ):

                response.flash = 'email enviado com sucesso...!'
                Emails[0] = dict(email = form.vars.email,
                                 assunto=form.vars.assunto,
                                 mensagem=form.vars.mensagem,
                                 )

                response.js = "$('#janela-modal').modal('hide')"

            else:
                response.flash = 'email NÃO enviado...!'
        else:
            response.flash = 'email não configurado corretamente....'

    elif form.errors:
        response.flash = 'erro no formulário.'
    return dict(form=form)

def compraPdf():
    id_pagar = request.vars.id_pagar
    pdf = compraGeraPdf(id_pagar)
    return pdf.output(dest='S')

def compraGeraPdf(id_compra):

    import os

    response.pedido = '%s n.%s' %(Compras[id_compra].tipo,Compras[id_compra].documento)
    response.dtpedido = "Data: %s" %(Compras[id_compra].emissao.strftime("%d/%m/%Y"))

    fornecedor = Compras[id_compra].fornecedor.nome
    condicao = '%s \n' %(Compras[id_compra].condicao.descricao)
    endereco = '%s - %s - %s - %s' %(Compras[id_compra].demanda.endereco.endereco,
                               Compras[id_compra].demanda.endereco.bairro,
                               Compras[id_compra].demanda.endereco.cidade,
                               Compras[id_compra].demanda.endereco.estado)

    demanda = Compras[id_compra].demanda.descricao
    
    obs = Compras[id_compra].obs
    insumos = db(ComprasInsumos.compra == id_compra).select()

    pdf = Report()
    li=30
    totalPedido = 0
    for r in insumos:
        if li > 24:
            li=0
            pdf.add_page()
            # Dados do Pedido
            pdf.set_font('Times', 'B', 8)
            pdf.cell(130, 8, "Fornecedor:".decode('UTF-8').encode('cp1252'), 0, 0, 'L',False)
            pdf.cell(60, 8, "Condição de Pagamento:".decode('UTF-8').encode('cp1252'), 0, 0, 'L',False)
            pdf.ln(5)
            pdf.set_font('Times', '', 10)
            pdf.cell(130, 8, fornecedor.decode('UTF-8').encode('cp1252'), 0, 0, 'L',False)
            pdf.cell(60, 8, condicao.decode('UTF-8').encode('cp1252'), 0, 0, 'L',False)
            pdf.ln(5)
            pdf.set_font('Times', 'B', 8)
            pdf.cell(130, 8, "Endereço:".decode('UTF-8').encode('cp1252'), 0, 0, 'L',False)
            pdf.cell(60, 8, "Obra:".decode('UTF-8').encode('cp1252'), 0, 0, 'L',False)
            pdf.ln(5)
            pdf.set_font('Times', '', 10)
            pdf.cell(130, 8, endereco.decode('UTF-8').encode('cp1252'), 0, 0, 'L',False)
            pdf.cell(60, 8, demanda.decode('UTF-8').encode('cp1252'), 0, 0, 'L',False)
            
            pdf.ln(9)
            pdf.set_font('Arial', 'B', 10)
            pdf.set_fill_color(192,192,192)
            pdf.cell(20, 8, "Código".decode('UTF-8').encode('cp1252'), 0, 0, 'C', True)
            pdf.cell(100, 8, "Descrição".decode('UTF-8').encode('cp1252'), 0, 0, 'C', True)
            #pdf.cell(20, 8, "Detalhe".decode('UTF-8').encode('cp1252'), 0, 0, 'C',True)
            pdf.cell(10, 8, "Un".decode('UTF-8').encode('cp1252'), 0, 0, 'C', True)
            pdf.cell(20, 8, "Qtde".decode('UTF-8').encode('cp1252'), 0, 0, 'C', True)
            pdf.cell(20, 8, "Preço".decode('UTF-8').encode('cp1252'), 0, 0, 'C', True)
            pdf.cell(20, 8, "Total".decode('UTF-8').encode('cp1252'), 0, 1, 'C', True)
            pdf.set_font('Times', '', 10)

        codigo = Insumo[int(r.insumo)].codigo
        descricao = "%s %s" %(r.insumo.descricao.decode('UTF-8').encode('cp1252'),r.detalhe.decode('UTF-8').encode('cp1252'))
        unidade = r.unidade.decode('UTF-8').encode('cp1252')
        qtde = str("%0.2f") %round(r.quantidade,2)
        preco = moeda(r.preco)
        total = moeda(round(r.quantidade*r.preco,2))
        pdf.cell(20, 8, codigo,0, 0, 'C')
        pdf.cell(100, 8, descricao[0:49], 0, 0, 'L')
        pdf.cell(10, 8, unidade, 0, 0, 'C')
        pdf.cell(20, 8, qtde, 0, 0, 'R')
        pdf.cell(20, 8, preco, 0, 0, 'R')
        pdf.cell(20, 8, total, 0, 1, 'R')

        totalPedido += round(r.quantidade*r.preco,2)
        li += 1

    pdf.set_font('Arial', 'B', 10)
    pdf.cell(170, 8, "Total do Pedido R$",0, 0, 'R', True)
    pdf.cell(20, 8, moeda(totalPedido), 0, 1, 'R',True)
    if obs:
        pdf.ln(2)
        pdf.set_font('Times', 'B', 8)
        pdf.cell(130, 8, "Observação:".decode('UTF-8').encode('cp1252'), 0, 0, 'L',False)
        pdf.ln(6)
        pdf.set_font('Times', '', 10)
        pdf.multi_cell(190,4, obs.decode('UTF-8').encode('cp1252'), 0, 0, 'J',)

    response.headers['Content-Type'] = 'application/pdf'

    anexo = 'Ped%s_%s.pdf' % ('{:0>3}'.format(Compras[id_compra].fornecedor), Compras[id_compra].documento)
    nome = os.path.join(request.folder, 'static', 'pdf', '%s') %anexo
    if request.function == 'compraPdf':
        return pdf
    else:
        pdf.output(name=nome, dest='F')
        return

#@auth.requires_membership('admin')
'''
def pagamentos():

    id_pagamento = request.args(0) or "0"

    Conta_corrente.lote.readable = False
    Conta_corrente.vlrecebimento.readable = Conta_corrente.vlrecebimento.writable = False
    Conta_corrente.descricao.readable = Conta_corrente.descricao.writable = False
    Conta_corrente.vlrecebimento.default = 0
    Conta_corrente.desconto.default = 0
    Conta_corrente.juros.default = 0

    if id_pagamento == "0":
        Conta_corrente.dtpagamento.default= request.now.date()
        Conta_corrente.vlpagamento.default = session.total_pagar - session.total_pagamentos
        form_pagamentos = SQLFORM.factory(Lote,Conta_corrente,_id='form_pagamentos',field_id='id',table_name='pagamentos')

        if form_pagamentos.process().accepted:
            if session.id_lote == 0:
                session.id_lote = Lote.insert(dtlote = form_pagamentos.vars.dtpagamento,tipo = 'pagar',parcelas=session.ids)

            descricao = "PAG LT %s %s" %('{:0>4}'.format(session.id_lote),buscadoc(0,session.id_lote)[0])

            Conta_corrente.insert(dtpagamento = form_pagamentos.vars.dtpagamento,
                                  vlpagamento = form_pagamentos.vars.vlpagamento,
                                  desconto = form_pagamentos.vars.desconto,
                                  juros = form_pagamentos.vars.juors,
                                  tipo = 'pagar',
                                  lote=session.id_lote,
                                  conta= form_pagamentos.vars.conta,
                                  descricao=descricao)
    
            atualizaPagamentos(session.id_lote)
            response.flash='Pagamentos Salvo com Sucesso!'
            response.js = 'hide_modal(%s);' %("'pagamentos_lista'")
        elif form_pagamentos.errors:
            response.flash = 'Erro no Formulário...!' 
    else:
        valoranterior = db(Conta_corrente.id == id_pagamento).select(Conta_corrente.vlpagamento).first()[Conta_corrente.vlpagamento]

        form_pagamentos = SQLFORM(Conta_corrente,id_pagamento,submit_button='Alterar',_id='form_pagamentos',field_id='id')

        if form_pagamentos.process().accepted:
            atualizaPagamentos(session.id_lote)
            response.flash = 'Pagamento Alterado com Sucesso!'
            response.js = 'hide_modal(%s);' %("'pagamentos_lista'")

        elif form_pagamentos.errors:
            response.flash = 'Erro no Formulário...!'

    return locals()
'''

'''
#@auth.requires_membership('admin')
def atualizaPagamentos(idlote):

    query = db(Conta_corrente.lote == idlote)
    sum = (Conta_corrente.vlpagamento + Conta_corrente.desconto - Conta_corrente.juros).sum()
    #sum = (Conta_corrente.vlpagamento).sum()
    try:
        valor = round(float(query.select(sum).first()[sum]),2)
    except:
        valor = 0

    ids = Lote[idlote].parcelas

    datapg = query.select(Conta_corrente.dtpagamento,orderby=~Conta_corrente.dtpagamento).first() or None

    parcelas = db(Pagar_parcelas.id.belongs(ids)).select(Pagar_parcelas.id, Pagar_parcelas.valor,
                                                                 Pagar_parcelas.valorpago,
                                                                 orderby=Pagar_parcelas.vencimento)
    # zerando pagamentos e parcelas
    for row in parcelas:
        Pagar_parcelas[row.id] = dict(valorpago=0.0,dtpagamento=None)

    for row in parcelas:
        if valor >= row.valor:
            valor = valor - float(row.valor)
            valorpago = row.valor
        else:
            valorpago = valor
            valor = 0
        if valorpago > 0:
            Pagar_parcelas[row.id] = dict(valorpago=valorpago, lote=session.id_lote)
            if row.valor-row.valorpago ==0 :
                Pagar_parcelas[row.id] = dict(dtpagamento=datapg.dtpagamento)
        else:
            Pagar_parcelas[row.id] = dict(valorpago=0.0, lote=None,dtpagamento=None)

    if valor > 0:
        parcela = db(Pagar_parcelas.id.belongs(ids)).select(Pagar_parcelas.id, Pagar_parcelas.valor,
                                                                    Pagar_parcelas.valorpago,
                                                                    orderby=~Pagar_parcelas.vencimento).first()
        id_parcela = parcela[Pagar_parcelas.id]
        Pagar_parcelas[id_parcela] = dict(valorpago=float(parcela[Pagar_parcelas.valor]) + valor)
'''
'''
#@auth.requires_membership('admin')
def pagar_lista_old():
    from datetime import timedelta,date

    status = request.vars.status if request.vars.status else 'Pendente'
    situacao = request.vars.situacao if request.vars.situacao else 'Todos'
    periodo = request.vars.periodo if request.vars.periodo else 'Todos'
       
    periodoset = ['Todos','-7 dias','+7 dias','-30 dias','+30 dias','-60 dias','+60 dias']
    form_pesq = SQLFORM.factory(
        Field('status',default = status, requires=IS_IN_SET(['Todos','Pendente','Pago'],zero=None)),
        Field('situacao',default = situacao, requires=IS_IN_SET(['Todos','Vencidos','a Vencer'],zero=None)),
        Field('periodo',default = periodo, requires=IS_IN_SET(periodoset,zero=None)),
        table_name='pesquisar',
        submit_button='Filtrar',
        )  
    
    if form_pesq.process().accepted:
        status = form_pesq.vars.status
        periodo = form_pesq.vars.periodo
        situacao = form_pesq.vars.situacao        
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    datainicial = datafinal = request.now
    datainicial = datainicial - timedelta(7) if periodo == '-7 dias' else datainicial
    datainicial = datainicial - timedelta(30) if periodo == '-30 dias' else datainicial
    datafinal = datafinal + timedelta(7) if periodo == '+7 dias' else datafinal
    datafinal = datafinal + timedelta(30) if periodo == '+30 dias' else datafinal
    datainicial = datainicial - timedelta(60) if periodo == '-60 dias' else datainicial
    datafinal = datafinal + timedelta(60) if periodo == '+60 dias' else datafinal

    query = (Pagar_parcelas.pagar == Pagar.id)
    query = query & (Pagar_parcelas.dtpagamento == None) if status == 'Pendente' else query
    query = query & (Pagar_parcelas.dtpagamento != None) if status == 'Pago' else query
    query = query & (Pagar_parcelas.vencimento < request.now) if situacao == 'Vencidos' else query
    query = query & (Pagar_parcelas.vencimento > request.now) if situacao == 'a Vencer' else query
    query = query & (Pagar_parcelas.vencimento <= datafinal) & (Pagar_parcelas.vencimento >= datainicial) if periodo != 'Todos' else query
    query = query & request.vars.keywords if request.vars.keywords else query

    total = db(query).select(Pagar_parcelas.valor.sum()).first()[Pagar_parcelas.valor.sum()] or 0
    total_pago = db(query).select(Pagar_parcelas.valorpago.sum()).first()[Pagar_parcelas.valorpago.sum()] or 0
    total_pendente = total - total_pago

    fields = [Pagar.fornecedor,Pagar.documento,Pagar_parcelas.parcela,Pagar.emissao,Pagar_parcelas.vencimento,
              Pagar_parcelas.dtpagamento,Pagar_parcelas.valor,Pagar_parcelas.valorpendente, Pagar_parcelas.status]
    
    #selectable = (lambda ids: redirect(URL('pagar',vars=dict(ids=ids)))) if status != "Pendente" else None
    selectable = None if status != "Pendente" else (lambda ids: redirect(URL('pagar',vars=dict(ids=ids,url="pagar_lista"))))

    grid_pagar = grid(db(query),
        formname="lista_pagar",field_id = Pagar_parcelas.id,
        fields=fields,orderby=Pagar_parcelas.vencimento,selectable= selectable, 
        deletable = False,editable = False,create=False) 

    heading = grid_pagar.elements('th')
    if heading and status == "Pendente":
        heading[0].append(INPUT(_type='checkbox',_onclick="$('input[name=records]').each(function() {this.checked=!this.checked;});"))

    form_lotes = LOAD(c='pagar',f='lotes',target='pagarLotes',ajax=True)

    return locals()
'''