# -*- coding: utf-8 -*-

def teste():
    rows = db(Cadastros.id > 0).select()
    for r in rows:
      Fornecedores[r.id] = dict(
        razao=r.razao,
        tipo=r.tipo,
        cnpj_cpf=r.cnpj_cpf,
        ie_rg=r.ie_rg,
        ) 
    return 'teste'

#@auth.requires_membership('admin')
def clientes():
    fields = (Clientes.id,Clientes.nome)
    form = grid(Clientes,formname="clientes",fields=fields)
            
    form = DIV(form, _class="well")

    if request.args(-2) == 'new':
       redirect(URL('cliente'))
    elif request.args(-3) == 'edit':
       idCliente = request.args(-1)
       redirect(URL('cliente', args=idCliente ))

    return locals()

#@auth.requires_membership('admin')
def cliente():
    idCliente = request.args(0) or "0"

    if idCliente == "0":
        formCliente = SQLFORM(Clientes,field_id='id', _id='form_cliente')

        btnNovo=btnExcluir=btnVoltar = ''
        formDemandas=formContatos=formEnderecos= "Primeiro Cadastre um Cliente"
    else:
        formCliente = SQLFORM(Clientes,idCliente,_id='formCliente',field_id='id')
        formEnderecos = LOAD(c='cadastro', f='clienteEnderecos', args=[idCliente],
                          target='enderecos', ajax=True)
        formContatos = LOAD(c='cadastro', f='clienteContatos', args=[idCliente],
                          target='contatos', ajax=True)        
        formDemandas = LOAD(c='cadastro', f='clienteDemandas', args=[idCliente],
                          target='demandas', ajax=True)
        btnExcluir = excluir("#")
        btnNovo = novo("cliente")

    btnVoltar = voltar("clientes")

    if formCliente.process().accepted:
        response.flash = 'Cliente Salvo com Sucesso!'
        redirect(URL('cliente', args=formCliente.vars.id))

    elif formCliente.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formCliente=formCliente,formEnderecos=formEnderecos,formContatos=formContatos,
                formDemandas=formDemandas,btnVoltar=btnVoltar,btnExcluir=btnExcluir,btnNovo=btnNovo)

def clienteContatos():  
  idCliente = int(request.args(0))
  Contatos.cliente.default = idCliente
  Contatos.fornecedor.default = None

  formContatos = grid(Contatos.cliente==idCliente,formname="contatos",
                 searchable = False,args=[idCliente],)

  btnVoltar = voltar1('contatos')

  if formContatos.update_form:
      btnExcluir = excluir("#")
  else:
      btnExcluir = ''

  return dict(formContatos=formContatos,btnVoltar=btnVoltar,btnExcluir=btnExcluir)

def clienteEnderecos():
  idCliente = int(request.args(0))
        
  Enderecos.cliente.default = idCliente
  Enderecos.fornecedor.default = 0

  formEnderecos = grid((Enderecos.cliente==idCliente),formname="enderecos",
                        searchable = False,args=[idCliente])

  btnVoltar = voltar1('enderecos')

  if formEnderecos.update_form:
      btnExcluir = excluir("#")
  else:
      btnExcluir = ''

  return dict(formEnderecos=formEnderecos,btnVoltar=btnVoltar,btnExcluir=btnExcluir)


##@auth.requires_membership('admin')
def clienteDemandas():
    idCliente = int(request.args(0))

    formClienteDemandas = grid((Demandas.cliente == idCliente),create=False,deletable=False,editable=False,
                                 formname="demandas", searchable=False, args=[idCliente])
    return locals()

#@auth.requires_membership('admin')
def fornecedores():
    fields = (Fornecedores.id,Fornecedores.nome)
    form = grid(Fornecedores,formname="lista_fornecedores",fields=fields)
    
    if request.args(-2) == 'new':
       redirect(URL('fornecedor'))
    elif request.args(-3) == 'edit':
       id_fornecedor = request.args(-1)
       redirect(URL('fornecedor', args=id_fornecedor ))

    return locals()

#@auth.requires_membership('admin')
def fornecedor():
    idFornecedor = request.args(0) or "0"

    if idFornecedor == "0":
        formFornecedor = SQLFORM(Fornecedores,field_id='id',_id='formFornecedor')
        formInsumo = formEnderecos = formContatos = "Primeiro Cadastre um Fornecedor"
        btnNovo = btnExcluir = btnVoltar = ''
    else:
        formFornecedor = SQLFORM(Fornecedores,idFornecedor,_id='formFornecedor',field_id='id')
        formEnderecos = LOAD(c='cadastro', f='fornecedorEnderecos', args=[idFornecedor],
                          target='enderecos', ajax=True)
        formContatos = LOAD(c='cadastro', f='fornecedorContatos', args=[idFornecedor],
                          target='contatos', ajax=True)        
        formInsumo= LOAD(c='cadastro',f='custo',args=[idFornecedor], target='custo', ajax=True)

        btnExcluir = excluir("#")
        btnNovo = novo("fornecedor")

    btnVoltar = voltar("fornecedores")
    
    if formFornecedor.process().accepted:
        response.flash = 'Fornecedor Salvo com Sucesso!'
        redirect(URL('fornecedor', args=formFornecedor.vars.id))

    elif formFornecedor.errors:
        response.flash = 'Erro no Formulário Principal!'

    btnVoltar = voltar("fornecedores")

    return dict(formFornecedor=formFornecedor,formEnderecos=formEnderecos,formContatos=formContatos,
                formInsumo=formInsumo,btnVoltar=btnVoltar,btnExcluir=btnExcluir,btnNovo=btnNovo)

def fornecedorContatos():  
  idFornecedor = int(request.args(0))
  Contatos.cliente.default = None
  Contatos.fornecedor.default = idFornecedor

  formContatos = grid(Contatos.fornecedor==idFornecedor,formname="contatos",
                 searchable = False,args=[idFornecedor],)

  btnVoltar = voltar1('contatos')

  if formContatos.update_form:
      btnExcluir = excluir("#")
  else:
      btnExcluir = ''

  return dict(formContatos=formContatos,btnVoltar=btnVoltar,btnExcluir=btnExcluir)

def fornecedorEnderecos():
  idFornecedor = int(request.args(0))
        
  Enderecos.cliente.default = None
  Enderecos.fornecedor.default = idFornecedor

  formEnderecos = grid((Enderecos.fornecedor==idFornecedor),formname="enderecos",
                        searchable = False,args=[idFornecedor])

  btnVoltar = voltar1('enderecos')

  if formEnderecos.update_form:
      btnExcluir = excluir("#")
  else:
      btnExcluir = ''

  return dict(formEnderecos=formEnderecos,btnVoltar=btnVoltar,btnExcluir=btnExcluir)

def custo():
    idFornecedor = int(request.args(0))
    Custo.insumo.readable = Custo.insumo.writable = True
    Custo.fornecedor.default = idFornecedor
    Custo.embalagem.default = 1

    def validarInsumo(form,fornecedor_id=idFornecedor):
        insumo_id = form.vars.insumo
        if db((db.custos.insumo == insumo_id) & (db.custos.fornecedor==fornecedor_id)).count():
            if 'new' in request.args:
                form.errors.insumo = 'Insumo já Cadastrado neste Fornecedor'

    formCusto = grid((Custo.fornecedor==idFornecedor),args=[idFornecedor],
                    onvalidation=validarInsumo,)

    btnVoltar = voltar1('custo')

    if formCusto.update_form:
        btnExcluir = excluir("#")
    else:
        btnExcluir = ''

    return dict(formCusto=formCusto,btnVoltar=btnVoltar,btnExcluir=btnExcluir)


#@auth.requires_membership('admin')
def condicao():
    formCondicao = grid(Condicao)
    return dict(formCondicao=formCondicao)

#@auth.requires_membership('admin')
def unidade():
    formUnidade = grid(Unidade)
    return dict(formUnidade=formUnidade)

#@auth.requires_membership('admin')
def tipoInsumo():
    formTpInsumo = grid(TipoInsumo)
    return dict(formTpInsumo=formTpInsumo)

def planoContas():
    formPc1 = grid(PlanoContas1,formname='planocontas1')
    loadPc2 = LOAD(c='cadastro', f='planoContas2', 
                          target='planocontas2', ajax=True)
    loadPc3 = LOAD(c='cadastro', f='planoContas3', 
                          target='planocontas3', ajax=True)

    return dict(formPc1=formPc1,loadPc2=loadPc2,loadPc3=loadPc3)

def planoContas2():
    fields = (PlanoContas2.id, PlanoContas2.nivel1, PlanoContas2.conta)
    formPc2 = grid(PlanoContas2,formname='planocontas2', fields=fields,
      orderby = PlanoContas2.nivel1|PlanoContas2.conta)
    return dict(formPc2=formPc2)

def planoContas3():
    fields = (PlanoContas3.id, PlanoContas3.nivel1,PlanoContas3.nivel2, PlanoContas3.conta)
    formPc3 = grid(PlanoContas3,formname='planocontas3',fields=fields,
              orderby = PlanoContas3.nivel1|PlanoContas3.nivel2|PlanoContas3.conta
              )
    return dict(formPc3=formPc3)

#@auth.requires_membership('admin')def demandas():
def demandas():
    pass
    formDemandas = grid((Demandas),
                              formname="listaDemandas",deletable=False )

    if request.args(-2) == 'new':
       redirect(URL('demanda'))
    elif request.args(-3) == 'edit':
       idDemanda = request.args(-1)
       redirect(URL('demanda', args=idDemanda ))

    return locals()

#@auth.requires_membership('admin')
def demanda():
    idDemanda = request.args(0) or "0"
    btnVoltar = voltar('demandas')

    if idDemanda == "0":
        formDemanda = SQLFORM(Demandas,field_id='id',_id='formDemanda')
        formDespesas = formInsumos = formAbc = '' 
        btnExcluir = btnNovo = ''
    else:
        formDemanda = SQLFORM(Demandas, idDemanda,_id='formDemanda',field_id='id')

        formDespesas = LOAD(c='cadastro', f='demandaDespesas', content='Aguarde, carregando...',
                           target='demandaDespesas', ajax=True, args=idDemanda)
        '''
        formInsumos = LOAD(c='cadastro', f='demandaInsumos', content='Aguarde, carregando...',
                           target='demandaInsumos', ajax=True, args=idDemanda)
        formAbc = LOAD(c='cadastro', f='demandaAbc', content='Aguarde, carregando...',
                           target='demandaAbc', ajax=True, args=idDemanda)
        '''           
        formInsumos = formAbc = ''                 
        btnExcluir = excluir("#")
        btnNovo = novo("demanda")

    if formDemanda.process().accepted:
        response.flash = 'Demanda Salva com Sucesso!'
        redirect(URL('demanda', args=formDemanda.vars.id))

    elif formDemanda.errors:
        response.flash = 'Erro no Formulário Principal!'

    return locals()

#@auth.requires_membership('admin')
def demandaDespesas():

    idDemanda = int(request.args(0))

    from datetime import datetime

    today = db(Despesas.demanda == idDemanda).select(Despesas.dtdespesa, orderby = Despesas.dtdespesa).first()['dtdespesa']

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

#@auth.requires_membership('admin')
def demandaInsumos():

    idDemanda = int(request.args(0))
    q = (PagarInsumos.pagar == Pagar.id) & (Pagar.demanda==idDemanda)
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


    rows = db(PagarInsumos.demanda==idDemanda).select(PagarInsumos.insumo.with_alias('insumo'),
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
        demandaInsumos = db(query).select(Relatorio.datarel,
                                                Relatorio.codigo,
                                                Relatorio.descricao,
                                                Relatorio.unidade,
                                                Relatorio.quantidade,
                                                Relatorio.valor,
                                                Relatorio.total,orderby=Relatorio.datarel)


        insumos = SQLTABLE(demandaInsumos,_id='demandainsumos',
                                        _class='display',
                                        _cellspacing = "0",
                                        _width = "100%",
                                        headers='labels',
                                        truncate = 100)
    else:
        insumos = ''

    return dict(insumos=insumos,form_pesq=form_pesq)

#@auth.requires_membership('admin')
def demandaAbc():
    idDemanda = int(request.args(0))
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
            query = (PagarInsumos.demanda == idDemanda) & (PagarInsumos.insumo == Insumo.id)
            xdesc = 'Insumo[row.pagarInsumos.insumo].descricao'
            if tipo != None:
                query = query & (Insumo.tipo==tipo)
        else:
            groupby = PagarInsumos.etapa
            query = (PagarInsumos.demanda == idDemanda)
            xdesc = 'Etapas[row.pagarInsumos.etapa].etapa'
    elif abc == 'FORNECEDOR':
        sum = Despesas.valor.sum()
        sum1 = Despesas.valor.sum()
        query = (Despesas.demanda == idDemanda) & (Despesas.pagar == Pagar.id)
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