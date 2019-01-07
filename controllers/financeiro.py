#@auth.requires_membership('admin')
def banco():
    formBanco = SQLFORM.grid(Banco,
            csv=False,user_signature=False,details=False,maxtextlength=50,
            )
    btnVoltar = voltar('banco')
    btnNovo = novo('banco/new/banco')
    btnExcluir = excluir('#')

    return locals()

#@auth.requires_membership('admin')
def contas():
    formConta = grid(Conta)

    btnVoltar = voltar('contas')
    btnNovo = novo('contas/new/conta')
    btnExcluir = excluir('#')

    return locals()

#@auth.requires_membership('admin')
def cheques():
    formCheques = grid(Cheques)

    btnVoltar = voltar("cheques")
    btnExcluir = excluir("#")
    btnNovo = novo("cheques/new/cheques")

    return locals()

#@auth.requires_membership('admin')
def conta_corrente():
    from datetime import datetime
    
    today = datetime.now().replace(day=1)
    session.conta=request.vars.conta if request.vars.conta else 0
    session.datainicial=datetime.strptime(request.vars.datainicial,'%d/%m/%Y').date() if request.vars.datainicial else today
    session.datafinal=datetime.strptime(request.vars.datafinal,'%d/%m/%Y').date() if request.vars.datafinal else request.now

    form_pesq = SQLFORM.factory(
        Field('conta',default=session.conta,requires=IS_IN_DB(db,"conta.id",'%(descricao)s',zero='Selecione uma conta')),
        Field('datainicial','date',default=session.datainicial,requires=data),
        Field('datafinal','date',default=session.datafinal,requires=data),
        table_name='pesquisar',
        submit_button='Filtrar',
        )  

    if form_pesq.process().accepted:
        session.conta = form_pesq.vars.conta
        session.datainicial=form_pesq.vars.datainicial
        session.datafinal=form_pesq.vars.datafinal
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    form_extrato = LOAD(c='financeiro',f='extrato',target='extrato',ajax=True,) if session.conta != 0 else ' '
    
    return locals()

#@auth.requires_membership('admin')
def extrato():

    Conta_corrente.descricao.readable = Conta_corrente.descricao.writable = True
    
    query = (Conta_corrente.conta == session.conta) & (Conta_corrente.dtpagamento >= session.datainicial) & (Conta_corrente.dtpagamento <= session.datafinal)
    query1 = (Conta_corrente.conta == session.conta) & (Conta_corrente.dtpagamento < session.datainicial)
    session.saldo = db(query1).select((Conta_corrente.vlrecebimento- Conta_corrente.vlpagamento).sum()).first()[(Conta_corrente.vlrecebimento- Conta_corrente.vlpagamento).sum()] or 0
    saldo_inicial = session.saldo
    
    session.totrec = 0
    session.totpag = 0
    
    def saldo(row):
        saldo = session.saldo
        saldo += row.vlrecebimento - row.vlpagamento
        session.saldo = saldo
        session.totrec = session.totrec + row.vlrecebimento
        session.totpag = session.totpag + row.vlpagamento
        return saldo

    fields = [Conta_corrente.dtpagamento, Conta_corrente.descricao,Conta_corrente.vlrecebimento,Conta_corrente.vlpagamento,Conta_corrente.tipo]          
    form_conta = grid(query,formname="conta_corrente",field_id = Conta_corrente.id,
            orderby=Conta_corrente.dtpagamento,deletable = False,editable = False,
            create=False,searchable=False,fields=fields,sortable=False,
            links = [dict(header='Saldo',body=lambda row:saldo(row)),
            lambda row: A(SPAN(_class="glyphicon glyphicon-pencil"),' Editar', _class="btn btn-default",_href='#',_onclick="show_modal('%s','Conta Corrente');" % URL('financeiro','conta_lancamento',args=[row.id,row.tipo])),
            lambda row: A(SPAN(_class="glyphicon glyphicon-trash"),' Excluir', _class="btn btn-default",_id='excluir',_onclick="return confirm('Deseja Excluir esse Lançamento ?');" ,_href=URL('financeiro','conta_corrente_delete',args=[row.id,row.tipo])) if row.tipo == "MAN" else " "
                      ],
            )

    novo =A(SPAN(_class="glyphicon glyphicon-plus"),' Novo Lançamento', _class="btn btn-default", _id='novo')
    my_extra_element = TR(H4('Saldo Anterior: ', saldo_inicial))
    
    form_conta[0].insert(-1,novo)                      
    form_conta[1].insert(-1,my_extra_element)

    return locals()

#@auth.requires_membership('admin')
def conta_lancamento():
    id_contacorrente = request.args(0) or "0"
    tipo = request.args(1) or "MAN"
    Conta_corrente.conta.readable = Conta_corrente.conta.writable = False
    Conta_corrente.descricao.readable = Conta_corrente.descricao.writable = True
    Conta_corrente.tipo.default = tipo
    Conta_corrente.conta.default = session.conta
    Conta_corrente.vlrecebimento.default = 0.00
    Conta_corrente.vlpagamento.default = 0.00
    Conta_corrente.desconto.default = 0.00
    Conta_corrente.juros.default = 0.00
    Conta_corrente.lote.default = None

    if id_contacorrente == "0":
        form = SQLFORM(Conta_corrente,field_id='id',_id='conta_lancamento')
    else:
        if tipo != "MAN":
            Conta_corrente.dtpagamento.writable = False
            Conta_corrente.vlpagamento.writable = False
            Conta_corrente.vlrecebimento.writable = False
        form = SQLFORM(Conta_corrente,id_contacorrente,field_id='id',_id='conta_lancamento')

    if form.process().accepted:
        response.flash = 'Salvo com Sucesso!'
        response.js = 'hide_modal(%s);' %("'extrato'")

    elif form.errors:
        response.flash = 'Erro no Formulário Principal!'

    return locals()

#@auth.requires_membership('admin')
def conta_corrente_delete():
    id = request.args(0)
    tipo = request.args(1)
    if tipo == "MAN":
        del Conta_corrente[id]
    redirect(URL('conta_corrente',vars=dict(conta = session.conta)))
    return locals()
    
#@auth.requires_membership('admin')
def transferencias():
    fields=[Transferencias.origem,Transferencias.destino,Transferencias.valor]
    gridTransferencia = grid(Transferencias,formname="transferencia",fields=fields,ondelete = transferencia_delete)

    if request.args(-2) == 'new':
       redirect(URL('transferencia'))
    elif request.args(-3) == 'edit':
       idTransferencia = request.args(-1)
       redirect(URL('transferencia', args=idTransferencia ))

    return dict(gridTransferencia=gridTransferencia)

#@auth.requires_membership('admin')
def transferencia():
    idTransferencia = request.args(0) or "0"
    Transferencias.ccorigem.writable = False
    Transferencias.ccdestino.writable = False
    Transferencias.dttransferencia.default = request.now

    if idTransferencia == "0":
        formTransferencia = SQLFORM(Transferencias,field_id='id', _id='form_cliente')
        btnNovo=btnExcluir=btnVoltar = ''
    else:
        formTransferencia = SQLFORM(Transferencias,idTransferencia,_id='formTransferencia',field_id='id')

        btnExcluir = excluir("#")
        btnNovo = novo("transferencia")

    btnVoltar = voltar("transferencias")

    if formTransferencia.process().accepted:
        origem = formTransferencia.vars.origem
        destino = formTransferencia.vars.destino
        dttransferencia = formTransferencia.vars.dttransferencia
        valor = formTransferencia.vars.valor
        descricaoOgigem = 'TRANSFERÊNCIA: %s' %(Conta[destino].descricao)
        descricaoDestino = 'TRANSFERÊNCIA: %s' %(Conta[origem].descricao)

        response.flash = 'transferencia Salvo com Sucesso!'

        if idTransferencia == "0":
            
            idOrigem = Conta_corrente.insert(
                conta = origem,
                descricao=descricaoOgigem,
                dtpagamento=dttransferencia,
                vlpagamento = valor,
                vlrecebimento = 0,
                tipo = 'transferencia',
                juros = 0,
                desconto = 0
                )
            
            idDestino = Conta_corrente.insert(
                conta = destino,
                descricao=descricaoDestino,
                dtpagamento=dttransferencia,
                vlpagamento = 0,
                vlrecebimento = valor,
                tipo = 'transferencia',
                juros = 0,
                desconto = 0
                )

            Transferencias[int(formTransferencia.vars.id)] = dict(ccorigem = idOrigem,ccdestino = idDestino)
            
        else:
            ccorigem = Transferencias[int(formTransferencia.vars.id)].ccorigem
            Conta_corrente[ccorigem] = dict(conta = origem,
                                            descricao=descricaoOgigem,
                                            vlpagamento = valor, 
                                            dtpagamento = dttransferencia)

            ccdestino = Transferencias[int(formTransferencia.vars.id)].ccdestino
            Conta_corrente[ccdestino] = dict(conta = destino,
                                             descricao=descricaoDestino,
                                             vlrecebimento = valor, 
                                             dtpagamento = dttransferencia)

        redirect(URL('transferencia', args=formTransferencia.vars.id))


    elif formTransferencia.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formTransferencia=formTransferencia,btnNovo=btnNovo,btnVoltar=btnVoltar,btnExcluir=btnExcluir)

#@auth.requires_membership('admin')
def transferencia_delete(table,id):
    ccorigem = Transferencias[id].ccorigem
    ccdestino = Transferencias[id].ccdestino
    del Conta_corrente[ccorigem]
    del Conta_corrente[ccdestino]

