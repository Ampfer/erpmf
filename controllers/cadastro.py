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

    formClienteObras = grid((Obras.cliente == idCliente),create=False,deletable=False,editable=False,
                                 formname="obras", searchable=False, args=[idCliente])
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
        formInsumo = "Primeiro Cadastre um Fornecedor"
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
        redirect(URL('fornecedor', args=form_fornecedor.vars.id))

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
    formPc2 = grid(PlanoContas2,formname='planocontas2')
    return dict(formPc2=formPc2)

def planoContas3():
    formPc3 = grid(PlanoContas3,formname='planocontas3')
    return dict(formPc3=formPc3)

