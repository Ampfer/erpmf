@auth.requires_membership('admin')
def contas():
    formConta = SQLFORM.grid(Conta,
            csv=False,user_signature=False,details=False,
            )
    return locals()

@auth.requires_membership('admin')
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

@auth.requires_membership('admin')
def extrato():
    
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
    
    fields = [Conta_corrente.dtpagamento, Conta_corrente.descricao,Conta_corrente.vlpagamento,Conta_corrente.vlrecebimento,Conta_corrente.tipo]          
    form_conta = SQLFORM.grid(query,
            formname="conta_corrente",field_id = Conta_corrente.id,
            orderby=Conta_corrente.dtpagamento,deletable = False,editable = False,
            details=False,create=False,searchable=False,csv=False,user_signature=False,
            fields=fields,sortable=False,maxtextlength=50,
            links = [dict(header='Saldo',body=lambda row:saldo(row)),
            lambda row: A(SPAN(_class="glyphicon glyphicon-pencil"),' Editar', _class="btn btn-default",_href='#',_onclick="show_modal('%s','Conta Corrente');" % URL('financeiro','conta_lancamento',args=[row.id,row.tipo])),
                    lambda row: A(SPAN(_class="glyphicon glyphicon-trash"),' Excluir', _class="btn btn-default",_id='excluir',_onclick="return confirm('Deseja Excluir esse Lançamento ?');" ,_href=URL('financeiro','conta_corrente_delete',args=[row.id,row.tipo])) if row.tipo == "MAN" else " "
                    ],
            )

    novo =A(SPAN(_class="glyphicon glyphicon-plus"),' Novo', _class="btn btn-default", _id='novo')
    my_extra_element = TR(H4('Saldo Anterior: ', saldo_inicial))
    
    form_conta[0].insert(-1,novo)                      
    form_conta[1].insert(-1,my_extra_element)

    form_conta = DIV(form_conta, _class="well")

    return locals()

@auth.requires_membership('admin')
def conta_lancamento():
    id_contacorrente = request.args(0) or "0"
    tipo = request.args(1) or "MAN"
    Conta_corrente.lote.readable = Conta_corrente.writable = False
    Conta_corrente.descricao.readable = Conta_corrente.descricao.writable = True
    Conta_corrente.conta.readable = Conta_corrente.conta.writable = False
    Conta_corrente.tipo.default = tipo
    Conta_corrente.conta.default = session.conta
    Conta_corrente.vlrecebimento.default = 0.00
    Conta_corrente.vlpagamento.default = 0.00
    Conta_corrente.vlpagamento.lote = 0

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

@auth.requires_membership('admin')
def conta_corrente_delete():
    id = request.args(0)
    tipo = request.args(1)
    if tipo == "MAN":
        del Conta_corrente[id]
    redirect(URL('conta_corrente',vars=dict(conta = session.conta)))
    return locals()

@auth.requires_membership('admin')
def banco():
    formBanco = SQLFORM.grid(Banco,
            csv=False,user_signature=False,details=False,maxtextlength=50,
            )
    return locals()

@auth.requires_membership('admin')
def cheques():
    formCheques = SQLFORM.grid(Cheques,
            csv=False,user_signature=False,details=False,maxtextlength=50,
            )

    btnVoltar = A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning",
                  _title="Voltar...",
                  _href=URL(c="financeiro", f="cheques"))
    btnExcluir = A(SPAN(_class="glyphicon glyphicon-trash"), ' Excluir ', _class="btn btn-danger", _title="Excluir...",
                   _href="#")
    btnNovo = A(SPAN(_class="glyphicon glyphicon-plus"), ' Novo ', _class="btn btn-primary",
                _title="Novo...", _href=URL("cheques/new/cheques"))
    return locals()