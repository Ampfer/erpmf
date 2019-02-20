# -*- coding: utf-8 -*-
#@auth.requires_membership('admin')
def entrada_lista():

    fields=(Receber.emissao, Receber.documento,Receber.cliente,Receber.condicao,Receber.valor)
    grid_receber = grid(Receber,formname="lista_receber",fields=fields)

    if request.args(-2) == 'new':
       redirect(URL('entrada'))
    elif request.args(-3) == 'edit':
       idReceber = request.args(-1)
       redirect(URL('entrada', args=idReceber ))

    return dict(grid_receber=grid_receber)

#@auth.requires_membership('admin')
def entrada():
    
    idReceber = request.args(0) or "0"

    btnVoltar = voltar("entrada_lista")
    
    if idReceber == "0":
        Receber.emissao.default= request.now.date()
        form_receber = SQLFORM(Receber,field_id='id',_id='form_receber')        
        form_parcelas = form_produtos = form_receitas = " Primeiro Cadastre um Contas a Receber"
        btnExcluir = btnNovo = ''
        
    else:
        form_receber = SQLFORM(Receber,idReceber,_id='form_receber',field_id='id',)

        form_produtos = LOAD(c='receber',f='receber_produtos',args=[idReceber],
                     content='Aguarde, carregando...',target='produtos',ajax=True)

        form_parcelas = LOAD(c='receber',f='receber_parcelas',args=[idReceber],
                     content='Aguarde, carregando...',target='parcelas',ajax=True)

        form_receitas = LOAD(c='receber',f='receber_receitas',args=[idReceber],
                     content='Aguarde, carregando...',target='receitas',ajax=True)

        btnNovo = novo("entrada")
        btnExcluir = excluir('#')

    if form_receber.process().accepted:
        response.flash = 'Salvo com sucesso!'
        session.valor = form_receber.vars.valor
        redirect(URL('entrada', args=[form_receber.vars.id]))
        session.valor = 0

    elif form_receber.errors:
        response.flash = 'Erro no Formulário Principal!'
    
    return dict(form_receber=form_receber,form_parcelas=form_parcelas,form_receitas=form_receitas,
                form_produtos=form_produtos, btnNovo=btnNovo,btnExcluir=btnExcluir,btnVoltar=btnVoltar)

#@auth.requires_membership('admin')
def receber_produtos():
    idReceber = int(request.args(0))
    sum = (ReceberProdutos.preco * ReceberProdutos.quantidade - ReceberProdutos.desconto).sum()
    total_produtos = float(db(ReceberProdutos.receber==idReceber).select(sum).first()[sum] or 0)

    ReceberProdutos.receber.default = idReceber
    ReceberProdutos.desconto.default = 0.00

    fields=[ReceberProdutos.produto,ReceberProdutos.unidade,ReceberProdutos.quantidade,ReceberProdutos.preco,ReceberProdutos.desconto,
            ReceberProdutos.total,]

    gridProdutos = grid(ReceberProdutos.receber==idReceber,alt='250px',
                               args=[idReceber],formname = "produtos",
                               searchable = False, fields=fields,deletable=True,
                               )

    if gridProdutos.create_form or gridProdutos.update_form:
        gridProdutos[1].element(_name='produto')['_onchange'] = "ajax('%s', ['produto'], ':eval');" % URL('receber', 'receberTrigger',vars=dict(idReceber=idReceber))
        gridProdutos[1].element(_name='produto')['_onblur']   = "ajax('%s', ['produto'], ':eval');" % URL('receber', 'receberTrigger',vars=dict(idReceber=idReceber))

    btnVoltar = voltar1('produtos')

    if gridProdutos.update_form:
        btnExcluir = excluir("#")
    else:
        btnExcluir = ''

    return dict(gridProdutos=gridProdutos,btnExcluir=btnExcluir,btnVoltar=btnVoltar,
        total_produtos=total_produtos)

def receberTrigger():
    preco=Produtos[request.vars.produto].preco
    unidade = Produtos[request.vars.produto].unidade

    return "jQuery('#receber_produtos_preco').val('%s');" \
           "jQuery('#receber_produtos_unidade').val('%s');" \
           "jQuery('#receber_produtos_quantidade').focus();" \
           % (preco,unidade)


#@auth.requires_membership('admin')
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
    #Receber_parcelas.parcela.writable = False
           
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

    formParcelas = grid((Receber_parcelas.receber==id_receber),alt='250px',
            formname="parcelas",searchable = False,args=[id_receber],onvalidation=validar,
            ondelete = deletar_parcela,deletable=False, editargs= dict(deletable=True),
            orderby=Receber_parcelas.vencimento
            )

    btnVoltar = voltar1('parcelas')

    if formParcelas.update_form:
        btnExcluir = excluir("#")
    else:
        btnExcluir = ''
 
    return dict(formParcelas=formParcelas,btnVoltar=btnVoltar,btnExcluir=btnExcluir,total_parcela=total_parcela)

def receber_receitas():

    idReceber = int(request.args(0))
    receber = Receber[idReceber]
    Receitas.receber.default = idReceber
    Receitas.dtreceita.default = receber.emissao
    Receitas.demanda.default = receber.demanda

    total_receitas = (db(Receitas.receber==idReceber).select(Receitas.valor.sum()).first())[Receitas.valor.sum()] or 0
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
            session.flash = 'Valor do Documento: %s Soma das Receitas: %s ' %(receber_valor,total_receitas) 

    fields= (Receitas.receita, Receitas.dtreceita,Receitas.valor)
    btnVoltar = voltar1('receitas')

    formReceitas = grid(Receitas.receber==idReceber,alt='250px',
        formname="receitas",searchable = False,args=[idReceber],fields=fields,onvalidation=validar)

    if formReceitas.update_form:
        btnExcluir = excluir("#")
    else:
        btnExcluir = ''

    return dict(formReceitas=formReceitas,total_receitas=total_receitas,btnVoltar=btnVoltar,btnExcluir=btnExcluir)

def cliente_ficha():

    form_pesq = SQLFORM.factory(
        Field('cliente',default=request.vars.cliente or session.cliente,requires=IS_IN_DB(db,"clientes.id",'%(nome)s',zero='Selecione um cliente')),
        table_name='pesquisar',
        submit_button='Selecionar',
        )  

    if form_pesq.process().accepted:
        session.cliente = form_pesq.vars.cliente
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    
    query = (Receber_parcelas.receber == Receber.id) & (Receber.cliente==session.cliente)
    lotes=[0]
    for row in db(query).select(Receber_parcelas.lote):
        lotes.append(row.lote)
    total = db(query).select(Receber_parcelas.valor.sum()).first()[Receber_parcelas.valor.sum()] or 0
    total_pago = db(query).select(Receber_parcelas.valorpago.sum()).first()[Receber_parcelas.valorpago.sum()] or 0
    total_pendente = total - total_pago

    form_parcelas = ' '
    fields = [Receber_parcelas.id,Receber.documento,Receber_parcelas.parcela,Receber.emissao,Receber_parcelas.vencimento,
              Receber_parcelas.valor,Receber_parcelas.valorpago,Receber_parcelas.lote,Receber_parcelas.valorpendente, Receber_parcelas.status]
    
    if session.cliente:

        form_parcelas = SQLFORM.grid(query,
            formname="cliente_parcelas",field_id = Receber_parcelas.id,orderby=Receber_parcelas.vencimento,fields=fields,
            links = [lambda row: A(SPAN(_class="glyphicon glyphicon-share-alt"),' Receber', _class="btn btn-default",_id='receber',_title="Receber Parcelas",
                                        _href=URL('receber',vars=dict(id_lote = row.receber_parcelas.lote,ids = row.receber_parcelas.id,url="cliente_ficha")))
            ],deletable = False,editable = False,details=False,create=False,searchable=False,
            csv=False,user_signature=False,)

    formRecebimentos = LOAD(c='receber',f='cliente_recebimentos',target='clienterecebimentos',ajax=True,args=session.cliente)

    btnPesquisar = pesquisar('receber', 'pesquisarcliente', 'Pesquisar Cliente')

    return dict(form_pesq=form_pesq,formRecebimentos=formRecebimentos,form_parcelas=form_parcelas,
        btnPesquisar=btnPesquisar,total=total,total_pago=total_pago,total_pendente=total_pendente)

#@auth.requires_membership('admin')
def cliente_recebimentos():
    idCliente = request.args(0)
    fields = [Conta_corrente.lote,Conta_corrente.descricao,Conta_corrente.conta,Conta_corrente.dtpagamento,Conta_corrente.vlrecebimento]
    query = (Conta_corrente.lote == Receber_parcelas.lote) & (Receber_parcelas.receber == Receber.id) & (Receber.cliente == idCliente)
    
    gridRecebimentos = grid(query,searchable=False,create=False,deletable=False,editable=False,fields=fields)
    
    return dict(gridRecebimentos=gridRecebimentos)

#@auth.requires_membership('admin')   
def pesquisar_cliente():
    pesq=request.vars.pesq
    return locals()

#@auth.requires_membership('admin')
def receber():
    session.id_lote = request.vars.id_lote or 0
    try:
        int(session.id_lote)
    except ValueError:
        session.id_lote = 0

    btnVoltar = voltar('receber_lista')  

    if session.id_lote ==0:
        ids=[]
        for row in request.vars:
            ids.append( request.vars[row])
        if ids == []:
            session.flash = 'Selecione pelo menos uma Parcela'
            redirect(URL(c="receber",f="receber_lista"))
        else:
            session.ids = ids
    else:
        session.ids = Lote[session.id_lote].parcelas

    formParcelas = LOAD(c='receber',f='mostrar_parcelas',
        content='Aguarde, carregando...',target='mostrarparcelas',ajax=True,)

    formRecebimentos = LOAD(c='receber',f='recebimentos_lista',
        content='Aguarde, carregando...',target='recebimentoslista',ajax=True,)

    formCheques = LOAD(c='receber',f='recebimentos_cheques',
        content='Aguarde, carregando...',target='recebimentoscheques',ajax=True,)

    return dict(formParcelas=formParcelas,formRecebimentos=formRecebimentos,formCheques=formCheques,
        btnVoltar=btnVoltar)
    
#@auth.requires_membership('admin')
def mostrar_parcelas():

    query = db(Receber_parcelas.id.belongs(session.ids))  
    sum = (Receber_parcelas.valor - Receber_parcelas.valorpago).sum()  
    session.total_receber = query.select(sum).first()[sum] or 0

    form = grid(query,searchable = False,create=False,deletable = False,editable = False,)

    return dict(form=form)

#@auth.requires_membership('a#dmin')    
def recebimentos_lista():

    query = db(Conta_corrente.lote == session.id_lote)
    session.total_recebimentos = query.select(Conta_corrente.vlrecebimento.sum()).first()[Conta_corrente.vlrecebimento.sum()] or 0
    fields = [Conta_corrente.lote, Conta_corrente.descricao, Conta_corrente.conta, Conta_corrente.dtpagamento,
              Conta_corrente.vlrecebimento]
    Conta_corrente.lote.default = session.id_lote
    form = grid(Conta_corrente.lote==session.id_lote,formname="recebimentos",fields=fields,searchable = False,create=False,deletable=False,editable=False,
            links =[lambda row: A(SPAN(_class="glyphicon glyphicon-pencil"), _class="btn btn-default",_href='#',_onclick="show_modal('%s','recebimentos');" % URL('receber','recebimentos',args=[row.id])),
                    lambda row: A(SPAN(_class="glyphicon glyphicon-trash"), _class="btn btn-default",_id='excluir',_onclick="return confirm('Deseja Excluir esse Pagamento ?');"  ,callback=URL('receber','recebimentos_delete',args=[row.id]))
                   ],
            )
    
    novo =A(SPAN(_class="glyphicon glyphicon-plus"), _class="btn btn-default", _id='novo')
    form[0].insert(-1,novo)

    return dict(form=form,novo = novo)

#@auth.requires_membership('admin')
def recebimentos_cheques():

    sum = Cheques.valor.sum()
    total_cheques= db(Cheques.lotrec == session.id_lote).select(sum).first()[sum]

    Cheques.lotrec.default = session.id_lote
    gridCheques = grid(Cheques.lotrec==session.id_lote,searchable=False,
                        formname="recebimentoscheques",args=[session.id_lote])
    btnVoltar = voltar1('recebimentoscheques')

    if gridCheques.update_form:
      btnExcluir = excluir("#")
    else:
      btnExcluir = ''

    return locals()


    pass

def recebimentos():

    idRecebimento = request.args(0) or "0"

    Conta_corrente.lote.readable = Conta_corrente.lote.writable = False 
    Conta_corrente.vlpagamento.readable = Conta_corrente.vlpagamento.writable = False
    Conta_corrente.descricao.readable = Conta_corrente.descricao.writable = False
    Conta_corrente.tipo.readable = Conta_corrente.tipo.writable = False
    Conta_corrente.vlpagamento.default = 0
    Conta_corrente.desconto.default = 0
    Conta_corrente.juros.default = 0

    if idRecebimento == "0":
        Conta_corrente.dtpagamento.default= request.now.date()
        Conta_corrente.vlrecebimento.default = session.total_receber - session.total_recebimentos
        formRecebimentos = SQLFORM.factory(Lote,Conta_corrente,_id='formRecebimentos',field_id='id',table_name='conta_corrente')
        
        if formRecebimentos.process().accepted:
            if session.id_lote == 0:
                session.id_lote = Lote.insert(dtlote = formRecebimentos.vars.dtpagamento,tipo = 'receber',parcelas=session.ids)

            descricao = "REC LT %s %s" %('{:0>4}'.format(session.id_lote),buscadoc(0,session.id_lote)[0])
            
            Conta_corrente.insert(dtpagamento = formRecebimentos.vars.dtpagamento, 
                                  vlrecebimento = formRecebimentos.vars.vlrecebimento,
                                  tipo = 'receber', 
                                  lote=session.id_lote,
                                  conta= formRecebimentos.vars.conta,
                                  descricao=descricao,
                                  desconto = formRecebimentos.vars.desconto,
                                  juros = formRecebimentos.vars.juros,
                                  )                

            atualizaRecebimentos(session.id_lote)              

            response.flash='Recebimento Salvo com Sucesso!'
            response.js = 'hide_modal(%s);' %("'recebimentoslista'")
        elif formRecebimentos.errors:
            response.flash = 'Erro no Formulário...!' 
        
    else:
        valoranterior = db(Conta_corrente.id == idRecebimento).select(Conta_corrente.vlrecebimento).first()[Conta_corrente.vlrecebimento]

        formRecebimentos = SQLFORM(Conta_corrente,idRecebimento,submit_button='Alterar',_id='formRecebimentos',field_id='id',table_name='recebimentos')

        if formRecebimentos.process().accepted:
            atualizaRecebimentos(session.id_lote)
            response.flash = 'Recebimento Alterado com Sucesso!'
            response.js = 'hide_modal(%s);' %("'recebimentoslista'")

        elif formRecebimentos.errors:
            response.flash = 'Erro no Formulário...!'

    return locals()


def buscadoc(ids,loteId=0):

    if loteId != 0:
        ids = Lote[loteId].parcelas

    dcto = db(Receber_parcelas.id.belongs(ids)).select(db.receber.documento, db.receber_parcelas.parcela,
          left=db.receber_parcelas.on(db.receber.id == db.receber_parcelas.receber))


    doctos = []
    for x in dcto:
        doctos.append('(' + x.receber.documento + '-' + x.receber_parcelas.parcela + ') ')
    return doctos

'''
def buscadoc(loteId):
    if loteId == 0:
        dcto = db(Receber_parcelas.id.belongs(session.ids)).select(db.receber.documento, db.receber_parcelas.parcela,
              left=db.receber_parcelas.on(db.receber.id == db.receber_parcelas.receber))
    else:
        dcto = db(Receber_parcelas.lote == loteId).select(db.receber.documento, db.receber_parcelas.parcela,
              left=db.receber_parcelas.on(db.receber.id == db.receber_parcelas.receber))
    doctos = []
    for x in dcto:
        doctos.append('(' + x.receber.documento + '-' + x.receber_parcelas.parcela + ') ')
    return doctos

def atualizaRecebimentos(idlote):
    query = db(Conta_corrente.lote == idlote)
    sum = Conta_corrente.vlrecebimento.sum()
    valor = float(query.select(sum).first()[sum]) or 0
    datapg = query.select(Conta_corrente.dtpagamento,orderby=~Conta_corrente.dtpagamento).first() or None

    parcelas = db(Receber_parcelas.id.belongs(session.ids)).select(Receber_parcelas.id, Receber_parcelas.valor,
                                                                 Receber_parcelas.valorpago,
                                                                 orderby=Receber_parcelas.vencimento)
    for row in parcelas:
        if valor >= row.valor:
            valor = valor - float(row.valor)
            valorpago = row.valor
        else:
            valorpago = valor
            valor = 0
        if valorpago > 0:
            Receber_parcelas[row.id] = dict(valorpago=valorpago, lote=session.id_lote)
            if row.valor-row.valorpago ==0 :
                Receber_parcelas[row.id] = dict(dtpagamento=datapg.dtpagamento)
        else:
            Receber_parcelas[row.id] = dict(valorpago=0.0, lote=None,dtpagamento=None)

    if valor > 0:
        parcela = db(Receber_parcelas.id.belongs(session.ids)).select(Receber_parcelas.id, Receber_parcelas.valor,
                                                                    Receber_parcelas.valorpago,
                                                                    orderby=~Receber_parcelas.vencimento).first()
        id_parcela = parcela[Receber_parcelas.id]
        Receber_parcelas[id_parcela] = dict(valorpago=float(parcela[Receber_parcelas.valor]) + valor)
'''
def totalLote(idLote):
    query = (Conta_corrente.lote == idLote)
    sum = (Conta_corrente.vlrecebimento + Conta_corrente.desconto - Conta_corrente.juros).sum()
    try:
        total = round(float(db(query).select(sum).first()[sum]),2)
    except:
        total = 0
    return total


def atualizaRecebimentos(idLote):

    ids = Lote[idLote].parcelas
    valorpago = totalLote(idLote)
    datapg = None 
    parcelas = db(Receber_parcelas.id.belongs(ids)).select(Receber_parcelas.id, Receber_parcelas.valor,
                                                                 orderby=Receber_parcelas.vencimento)
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
    query = (Lote_parcelas.parcela == idParcela) & (Lote_parcelas.lote==Lote.id) & (Lote.tipo=='receber')
    sum = (Lote_parcelas.valpag).sum()
    try:
        valor = round(float(db(query).select(sum).first()[sum]),2)
    except:
        valor = 0
    return valor   

def atualizaParcela(idParcela,idLote):
    
    valor=valorPago(idParcela)
    Receber_parcelas[idParcela] = dict(valorpago=valor)

    if idLote == None:
        Receber_parcelas[idParcela] = dict(dtpagamento=None)
    
    elif round(Receber_parcelas[idParcela].valor,2) <= round(valor,2):
        datapg = db(Conta_corrente.lote == idLote).select(Conta_corrente.dtpagamento,orderby=~Conta_corrente.dtpagamento).first() or None
        Receber_parcelas[idParcela] = dict(dtpagamento=datapg['dtpagamento'])

def atualizarcontasreceber():
    contas = db(Conta_corrente.id>0).select(orderby=Conta_corrente.dtpagamento)
    for conta in contas:
        if conta.tipo == 'receber':
            try:
                atualizaRecebimentos(conta.lote)
            except:
                print conta.lote


def recebimentos_delete():
    id = request.args(0)
    valoranterior = 0 - db(Conta_corrente.id == id).select(Conta_corrente.vlrecebimento).first()[Conta_corrente.vlrecebimento]
    datapg = None
    idLote = db(Conta_corrente.id==id).select(Conta_corrente.lote).first()['lote']
    del Conta_corrente[id]

    if not db(Conta_corrente.lote).count():
        del Lote[idLote]
        idsCheques = db(Cheques.lotpag == idLote).select(Cheques.id)
        for idCheque in idsCheques:
            Cheques[idCheque.id] = dict(lotpag=None)

    atualizaPagamentos(float(valoranterior),datapg)
    
    response.js = "$('#recebimentos_lista').get(0).reload()"


#@auth.requires_membership('admin')
def lotes():
    Lote.id.readable = True
    Lote.dtlote.readable = True
    Lote.documentos = Field.Virtual('documentos',lambda row: buscadoc(row.lote.parcelas),label='Documentos')
    form = grid(Lote.tipo == "receber",
    orderby=~Lote.dtlote,create=False,deletable=False,editable=False,
    searchable=False,formname="receberLotes",
    links =[lambda row: A(SPAN(_class="glyphicon glyphicon-pencil"), _class="btn btn-default",
    _href=URL('receber','receber',vars=dict(id_lote=row.id,target='receberLotes',url='receber_lista'))),
    lambda row: A(SPAN(_class="glyphicon glyphicon-trash"),_id="lote_delete", _class="btn btn-default",
    _href=URL('receber','lote_delete',vars=dict(id_lote=row.id,total=row.total,url='lotes')))
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
    #db(Cheques.lotpag==id_lote).delete()

    for parcela in parcelas:
        atualizaParcela(parcela,None)
    
    redirect(URL(url))

def receber_lista():
           
    form_pesq = SQLFORM.factory(
        Field('cliente','integer',label='Cliente:',requires=IS_IN_DB(db,'clientes.id','clientes.nome',zero='TODOS')),
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

def gerar_receber():
    from datetime import datetime

    idCliente = request.vars.cliente
    inicial = datetime.strptime(request.vars.dtinicial,'%d/%m/%Y').date() if request.vars.dtinicial != '' else ''
    final = datetime.strptime(request.vars.dtfinal,'%d/%m/%Y').date() if request.vars.dtfinal != '' else ''
    status = request.vars.status
    documento = request.vars.documento.split(',')
    

    query = (Receber_parcelas.receber == Receber.id) & (Clientes.id == Receber.cliente)
    if idCliente:
        query = query & (Receber.cliente == idCliente)
    if inicial != '':
        query = query & (Receber_parcelas.vencimento >= inicial)
    if final != '':
        query = query & (Receber_parcelas.vencimento <= final)
    if status == 'Pendente':
        query = query & (Receber_parcelas.dtpagamento == None)
    if status == 'Pago':
        query = query & (Receber_parcelas.dtpagamento != None) 
    if documento != ['']:
        query = query & (Receber.documento.contains(documento))

    total = db(query).select(Receber_parcelas.valor.sum()).first()[Receber_parcelas.valor.sum()] or 0
    total_pago = db(query).select(Receber_parcelas.valorpago.sum()).first()[Receber_parcelas.valorpago.sum()] or 0
    total_pendente = total - total_pago

    duplicatas = db(query).select(
                            Receber_parcelas.id.with_alias('rowId'),
                            Clientes.nome.with_alias('cliente'),
                            Receber.documento.with_alias('documento'),
                            Receber_parcelas.parcela.with_alias('parcela'),
                            Receber.emissao.with_alias('emissao'),
                            Receber_parcelas.vencimento.with_alias('vencimento'),
                            Receber_parcelas.dtpagamento.with_alias('pagamento'),
                            Receber_parcelas.valor.with_alias('valor'),
                            (Receber_parcelas.valor - Receber_parcelas.valorpago).with_alias('pendente'),
                            orderby = Receber_parcelas.vencimento
                            )

    return dict(duplicatas=duplicatas,total=total,total_pago=total_pago,total_pendente=total_pendente)