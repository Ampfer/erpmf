# -*- coding: utf-8 -*-
@auth.requires_membership('admin')
def entrada_lista():
    
    grid_receber = SQLFORM.grid(Receber,
        showbuttontext=False,formname="lista_receber",csv=False,user_signature=False)

    grid_receber = DIV(grid_receber, _class="well")

    if request.args(-2) == 'new':
       redirect(URL('entrada'))
    elif request.args(-3) == 'edit':
       idd = request.args(-1)
       redirect(URL('entrada', args=idd ))

    return locals()

@auth.requires_membership('admin')
def entrada():
    
    idd = request.args(0) or "0"
    voltar = A(SPAN(_class="icon leftarrow icon-arrow-left"),' Voltar', _class="button btn",_title="Voltar...", _href=URL(c="receber",f="entrada_lista"))
    novo = A(SPAN(_class="icon leftarrow icon-arrow-left"),' Novo', _class="button btn",_title="Novo...", _href=URL(c="receber",f="entrada"))
    
    if idd == "0":
        Receber.emissao.default= request.now.date()
        form_receber = SQLFORM(Receber,
                              submit_button='Incluir',
                              field_id='id',
                              _id='form_receber')
        
        form_parcelas = form_receitas = " Primeiro Cadastre um Contas a Receber"
        
    else:
        form_receber = SQLFORM(Receber,idd,
                                      submit_button='Alterar',
                                      _id='form_receber' ,
                                      field_id='id',
                                      )

        form_parcelas = LOAD(c='receber',
                     f='receber_parcelas',
                     args=[idd],
                     content='Aguarde, carregando...',
                     target='parcelas',
                     ajax=True
                     )

        form_receitas = LOAD(c='receber',
                     f='receber_receitas',
                     args=[idd],
                     content='Aguarde, carregando...',
                     target='receitas',
                     ajax=True
                     )

    if form_receber.process().accepted:
        response.flash = 'Salvo com sucesso!'
        session.valor = form_receber.vars.valor
        redirect(URL('entrada', args=[form_receber.vars.id]))
        session.valor = 0

    elif form_receber.errors:
        response.flash = 'Erro no Formulário Principal!'
    return locals()


@auth.requires_membership('admin')
def receber_parcelas():
    id_receber = int(request.args(0))

    old_valor = request.post_vars.valor or "0"

    receber = db(Receber.id==id_receber).select(Receber.valor,Receber.condicao,Receber.emissao).first()
    receber_valor = float(receber[Receber.valor])
    receber_condicao = int(receber[Receber.condicao])
    receber_emissao = receber[Receber.emissao]
    rows = db(Receber_parcelas.receber==id_receber).select(Receber_parcelas.valor.sum()).first()
    total_parcela = float(rows[Receber_parcelas.valor.sum()] or 0) 

    def atualiza_parcela():
        rows = db(Receber_parcelas.receber==id_receber).select(orderby=Receber_parcelas.vencimento)
        for index,row in enumerate(rows):
            id_parc = int(row[Receber_parcelas.id])
            parc = (str(index+1) + '/' + str(len(rows)))
            Receber_parcelas[int(id_parc)] = dict(parcela=parc)
                    
    def gera_parcela(id_receber,receber_valor,receber_condicao,receber_emissao):
        from datetime import timedelta
        condicao = db(Condicao.id ==  receber_condicao ).select(Condicao.dias).first()[Condicao.dias]
        for index,dia in enumerate(condicao):
            parcela_valor = receber_valor/len(condicao)
            parcela_parcela = '1'
            parcelas = dict(receber = id_receber,parcela=parcela_parcela,vencimento = receber_emissao + timedelta(dia),valor=parcela_valor)
            Receber_parcelas[0] = parcelas 

    if total_parcela == 0:
        gera_parcela(id_receber,receber_valor,receber_condicao,receber_emissao)
   
    Receber_parcelas.receber.default = id_receber
    Receber_parcelas.valor.default = receber_valor - total_parcela
    Receber_parcelas.valorpago.default = 0
    Receber_parcelas.parcela.writable = False
           
    atualiza_parcela()

    def validar(form,total_parcela=total_parcela,receber_valor=receber_valor):
        if request.args(-3) == 'edit':
            id_parcela = request.args(-1)
            old_valor = float(Receber_parcelas(id_parcela).valor)
        else:
            old_valor = 0    
        if (total_parcela + float(form.vars.valor) - old_valor) > receber_valor:
            form.errors.valor = "Soma das Parcelas é Maior que o Valor do Documento"
        elif (total_parcela + float(form.vars.valor) - old_valor) < receber_valor:
            session.flash = 'Valor do Ducumento: %s Soma das Parcelas: %s ' %(receber_valor,total_parcela) 

    def deletar_parcela(table,id):
        return atualiza_parcela()

    form = SQLFORM.grid((Receber_parcelas.receber==id_receber),
            formname="parcelas",searchable = False,showbuttontext=False, 
            _class='web2py_grid',args=[id_receber],csv=False,onvalidation=validar,
            ondelete = deletar_parcela,deletable=False, editargs= dict(deletable=True),
            orderby=Receber_parcelas.vencimento
            )
 

    return dict(form=form)

@auth.requires_membership('admin')
def receber_receitas():
    id_receber = int(request.args(0))
    receber = Receber(id_receber)
    Receitas.receber.default = id_receber
    Receitas.descricao.default = receber.cliente.nome + ' - ' + receber.documento
    Receitas.dtreceita.default = receber.emissao
    total_receitas = (db(Receitas.receber==id_receber).select(Receitas.valor.sum()).first())[Receitas.valor.sum()]
    Receitas.valor.default = float(receber.valor) - float(total_receitas or 0)
    
    def validar(form,total_receitas=float(total_receitas or 0),receber_valor=receber.valor):
        if 'edit' in request.args:
            id_receita = request.args(-1)
            old_valor = float(Receitas(id_receita).valor)
        else:
            old_valor = 0  
        if (total_receitas + float(form.vars.valor) - old_valor) > receber_valor:
            form.errors.valor = "Soma das Receitas é Maior que o Valor do Documento" 
        elif (total_receitas + float(form.vars.valor) - old_valor) < receber_valor:
            session.flash = 'Valor do Documento: %s Soma das Receitas: %s ' %(Receber_valor,total_receitas) 
        
    form = SQLFORM.grid((Receitas.receber==id_receber),
            formname="receitas",searchable = False,showbuttontext=False, 
            _class='web2py_grid',args=[id_receber],csv=False,
            onvalidation=validar,
            )

    form = DIV(form, _class="well")

    return dict(form=form)

@auth.requires_membership('admin')   
def cliente_ficha():
    cliente = 0
    if request.vars.cliente:
        cliente=request.vars.cliente

    form_pesq = SQLFORM.factory(
        Field('cliente',default=cliente,requires=IS_IN_DB(db,"clientes.id",'%(nome)s',zero='Selecione um cliente')),
        table_name='pesquisar',
        submit_button='Selecionar',
        )  

    if form_pesq.process().accepted:
        cliente = form_pesq.vars.cliente
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    
    query = (Receber_parcelas.receber == Receber.id) & (Receber.cliente==cliente)
    total = db(query).select(Receber_parcelas.valor.sum()).first()[Receber_parcelas.valor.sum()] or 0
    total_pago = db(query).select(Receber_parcelas.valorpago.sum()).first()[Receber_parcelas.valorpago.sum()] or 0
    total_pendente = total - total_pago

    form_parcelas = ' '
    fields = [Receber_parcelas.id,Receber.documento,Receber_parcelas.parcela,Receber.emissao,Receber.valor,
              Receber_parcelas.vencimento,Receber_parcelas.valor,Receber_parcelas.valorpago,Receber_parcelas.valorpendente, Receber_parcelas.status]
    
    if int(cliente) > 0:
        
        form_parcelas = SQLFORM.grid(query,
            showbuttontext=False,formname="receber_parcelas",field_id = Receber_parcelas.id,
            orderby=Receber_parcelas.vencimento,fields=fields,
            selectable= lambda ids: redirect(URL('receber_lista',vars=dict(id=ids))),
            deletable = False,editable = False,details=False,create=False,searchable=False,
            csv=False,user_signature=False,)

    form_parcelas = DIV(form_parcelas, _class="well")

    session.id_lote = None
    form_pagamentos = LOAD(c='pagar',f='pagamentos_lista',target='pagamentos',ajax=True,)

    return locals()

@auth.requires_membership('admin')   
def pesquisar_cliente():
    pesq=request.vars.pesq
    return locals()

@auth.requires_membership('admin')
def receber_lista():
    from datetime import timedelta,date

    status = request.vars.status if request.vars.status else 'Todos'
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

    query = (Receber_parcelas.receber == Receber.id)
    query = query & (Receber_parcelas.dtpagamento == None) if status == 'Pendente' else query
    query = query & (Receber_parcelas.dtpagamento != None) if status == 'Pago' else query
    query = query & (Receber_parcelas.vencimento < request.now) if situacao == 'Vencidos' else query
    query = query & (Receber_parcelas.vencimento > request.now) if situacao == 'a Vencer' else query
    query = query & (Receber_parcelas.vencimento <= datafinal) & (Receber_parcelas.vencimento >= datainicial) if periodo != 'Todos' else query
    query = query & request.vars.keywords if request.vars.keywords else query

    total = db(query).select(Receber_parcelas.valor.sum()).first()[Receber_parcelas.valor.sum()] or 0
    total_pago = db(query).select(Receber_parcelas.valorpago.sum()).first()[Receber_parcelas.valorpago.sum()] or 0
    total_pendente = total - total_pago

    if status == 'Pendente':
        selectable = lambda ids: redirect(URL('pagar','pagar',vars=dict(ids=ids)))
    else:
        selectable =None

    fields = [Receber_parcelas.id,Receber.cliente,Receber.documento,Receber_parcelas.parcela,Receber.emissao,Receber.valor,
              Receber_parcelas.vencimento,Receber_parcelas.valor,Receber_parcelas.valorpago,Receber_parcelas.valorpendente, Receber_parcelas.status]
    #session.id_lote = None
    
    grid_receber = SQLFORM.grid(query,
        showbuttontext=False,formname="lista_receber",field_id = Receber_parcelas.id,
        fields=fields,orderby=Receber_parcelas.vencimento,selectable= selectable,
        deletable = False,editable = False,details=False,create=False,
        csv=False,user_signature=False,) 
    
    grid_receber = DIV(grid_receber, _class="well")

    form_lotes = LOAD(c='receber',f='lotes',target='lotes',ajax=True,vars=dict(id_lote=None))

    return locals()

@auth.requires_membership('admin')
def lotes():
    Lote.id.readable = True
    Lote.dtlote.readable = True
    Lote.parcelas.readable = True 
    def buscadocumentos(row):
        ids = str(row.lote.parcelas).replace("L","").replace("[","").replace("]","")
        dcto = db.executesql('SELECT receber.documento,receber_parcelas.parcela FROM receber,receber_parcelas WHERE receber.id = receber_parcelas.receber AND receber_parcelas.id IN(%s)'%(ids)) 
        doctos = []
        for x in dcto:
            doctos.append('('+x[0]+'-'+x[1]+') ')
        return doctos

    Lote.documentos = Field.Virtual('documentos',lambda row: buscadocumentos(row),label='Documentos')

    form = SQLFORM.grid(Lote.tipo == 'receber',
        orderby=~Lote.dtlote,
        create=False,deletable=False,editable=False,details = False,searchable = False,
        _class='web2py_grid',csv=False,formname="lotes",
        links =[lambda row: A(SPAN(_class="glyphicon glyphicon-pencil"), _class="btn btn-default",
                                   _href=URL('receber','receber',vars=dict(id=row.parcelas,id_lote=row.id))),
                lambda row: A(SPAN(_class="glyphicon glyphicon-trash"),_id="lote_delete", _class="btn btn-default",
                                   _href=URL('receber','lote_delete',vars=dict(id=row.parcelas,id_lote=row.id,total=row.total)))
               ],
        )
    
    form = DIV(form, _class="well") 

    return locals()

@auth.requires_membership('admin')
def lote_delete():
    if type(request.vars.ids) is list:
        session.ids = request.vars.ids
    else:
        session.ids = []
        session.ids.append(request.vars.ids)
    
    id_lote = request.vars.id_lote
    total = 0 - float(request.vars.total)
    datapg = None
    del Lote[id_lote]
    atualizaRecebimentos(total,datapg)
    redirect(URL('receber_lista'))

@auth.requires_membership('admin')
def atualizaRecebimentos(valor,datapg):
    if valor > 0:
        parcelas = db(Receber_parcelas.id.belongs(session.ids)).select(Receber_parcelas.id,Receber_parcelas.valor,Receber_parcelas.valorpago,orderby=Receber_parcelas.vencimento)
        for row in parcelas:
            valor = float(row.valorpago or 0) + valor
            if valor >= row.valor:
                valor = valor-float(row.valor)
                valorpago = row.valor
            else:
                valorpago = valor
                valor = 0
            if valorpago > 0:
                Receber_parcelas[row.id] = dict(valorpago=valorpago,lote=session.id_lote)
                if valorpago >= row.valor:
                    Receber_parcelas[row.id] = dict(dtpagamento=datapg)
    if valor < 0:
        parcelas = db(Receber_parcelas.id.belongs(session.ids)).select(Receber_parcelas.id,Receber_parcelas.valor,Receber_parcelas.valorpago,orderby=~Receber_parcelas.vencimento)
        for row in parcelas:
            valor = float(row.valorpago or 0) + valor
            if valor <= 0:
                valorpago = 0
                dtpag = None
                lote = 0
            else:
                valorpago = valor
                valor = 0
                dtpag = datapg
                lote=session.id_lote
            
            Receber_parcelas[row.id] = dict(valorpago=valorpago,lote=lote)
            if valorpago < row.valor:
                dtpag = None
            Receber_parcelas[row.id] = dict(dtpagamento=dtpag)
