# -*- coding: utf-8 -*-

'''
#@auth.requires_membership('admin')
def cadastros():
    fields = (Cadastros.razao,Cadastros.tipo,Cadastros.cnpj_cpf)
    grid_cadastros = SQLFORM.grid(Cadastros,
            formname="lista_cadastros",fields=fields,csv=False,user_signature=False,details=False,maxtextlength=50)

    if request.args(-2) == 'new':
       redirect(URL('cadastro'))
    elif request.args(-3) == 'edit':
       id_cadastro = request.args(-1)
       redirect(URL('cadastro', args=id_cadastro ))

    return locals()
    
#@auth.requires_membership('admin')
def cadastro():

    id_cadastro = request.args(0) or "0"

    if id_cadastro == "0":
        formCadastro = SQLFORM(Cadastros,field_id='id',_id='form_cadastro_editar')

        formCadastroEnderecos = formCadastroContatos = " Primeiro Cadastre uma Empresa ou Pessoa"

        btnExcluir = btnNovo = ''
    else:
        formCadastro = SQLFORM(Cadastros,id_cadastro,_id='form_cadastro_editar',field_id='id')

        formCadastroContatos = LOAD(c='cadastro',f='contatos',args=[id_cadastro], target='contatos', ajax=True,content='Aguarde, carregando...')

        formCadastroEnderecos = LOAD(c='cadastro',f='enderecos',args=[id_cadastro],target='enderecos',ajax=True, content='Aguarde, carregando...')

        btnExcluir = A(SPAN(_class="glyphicon glyphicon-trash"), ' Excluir ', _class="btn btn-danger", _title="Excluir...",
                   _href="#")
        btnNovo = A(SPAN(_class="glyphicon glyphicon-plus"), ' Novo ', _class="btn btn-primary",
                _title="Novo...", _href=URL("cadastro"))

    btnVoltar = A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning", _title="Voltar...",
                  _href=URL("cadastros"))
    
    if formCadastro.process().accepted:
        response.flash = 'Salvo com sucesso!'
        redirect(URL('cadastro', args=formCadastro.vars.id))

    elif formCadastro.errors:
        response.flash = 'Erro no Formulário Principal!'
    return locals()

#@auth.requires_membership('admin')
def contatos():
    
    id_cadastro = int(request.args(0))
        
    Contatos.cadastro.default = id_cadastro

    formContatos = SQLFORM.grid((Contatos.cadastro==id_cadastro),
                   formname="contatos",searchable = False,details=False, args=[id_cadastro],csv=False,)

    btnVoltar = A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning",
                 _onClick="jQuery('#contatos').get(0).reload()")

    if formContatos.update_form:
        btnExcluir = A(SPAN(_class="glyphicon glyphicon-trash"), ' Excluir ', _class="btn btn-danger", _title="Excluir...",
                   _href="#")
    else:
        btnExcluir = ''

    return locals()

#@auth.requires_membership('admin')
def enderecos():
    id_cadastro = int(request.args(0))
        
    Enderecos.cadastro.default = id_cadastro

    formEnderecos = SQLFORM.grid((Enderecos.cadastro==id_cadastro),details=False,
            formname="enderecos",searchable = False,args=[id_cadastro],csv=False)

    btnVoltar = A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning",
                 _onClick="jQuery('#enderecos').get(0).reload()")

    if formEnderecos.update_form:
        btnExcluir = A(SPAN(_class="glyphicon glyphicon-trash"), ' Excluir ', _class="btn btn-danger", _title="Excluir...",
                   _href="#")
    else:
        btnExcluir = ''

    return locals()
'''

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

    return locals()

def clienteContatos():  
  idCliente = int(request.args(0))
  Contatos.cliente.default = idCliente
  Contatos.fornecedor.default = None
  '''
  formContatos = SQLFORM.grid((Contatos.cliente==idCliente),
                 formname="contatos",searchable = False,details=False,
                 args=[idCliente],csv=False,)
  '''
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

  formEnderecos = SQLFORM.grid((Enderecos.cliente==idCliente),details=False,
          formname="enderecos",searchable = False,args=[idCliente],csv=False)

  btnVoltar = voltar1('enderecos')

  if formEnderecos.update_form:
      btnExcluir = excluir("#")
  else:
      btnExcluir = ''

  return dict(formEnderecos=formEnderecos,btnVoltar=btnVoltar,btnExcluir=btnExcluir)


##@auth.requires_membership('admin')
def clienteDemandas():
    idCliente = int(request.args(0))

    formClienteObras = SQLFORM.grid((Obras.cliente == idCliente), details=False,create=False,deletable=False,editable=False,
                                 formname="obras", searchable=False, args=[idCliente], csv=False,maxtextlength=50)
    return locals()

#@auth.requires_membership('admin')
def fornecedores():
    fields = (Fornecedores.id,Fornecedores.nome,Fornecedores.cadastro)
    form = SQLFORM.grid(Fornecedores,
            formname="lista_fornecedores",fields=fields,csv=False,user_signature=False,details=False,maxtextlength=50)
    form = DIV(form, _class="well")

    if request.args(-2) == 'new':
       redirect(URL('fornecedor'))
    elif request.args(-3) == 'edit':
       id_fornecedor = request.args(-1)
       redirect(URL('fornecedor', args=id_fornecedor ))

    return locals()

#@auth.requires_membership('admin')
def fornecedor():
    id_fornecedor = request.args(0) or "0"

    if id_fornecedor == "0":
        form_fornecedor = SQLFORM(Fornecedores,field_id='id',_id='form_fornecedor')
        formInsumo = "Primeiro Cadastre um Fornecedor"
        btnNovo = btnExcluir = btnVoltar = ''
    else:
        form_fornecedor = SQLFORM(Fornecedores,id_fornecedor,_id='form_fornecedor',field_id='id')
        formInsumo= LOAD(c='cadastro',f='custo',args=[id_fornecedor], target='custo', ajax=True,content='Aguarde, carregando...')

        btnExcluir = A(SPAN(_class="glyphicon glyphicon-trash"), ' Excluir ', _class="btn btn-danger",
                       _title="Excluir...",
                       _href="#")
        btnNovo = A(SPAN(_class="glyphicon glyphicon-plus"), ' Novo ', _class="btn btn-primary",
                    _title="Novo...", _href=URL("fornecedor"))

    btnVoltar = A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning",
                  _title="Voltar...",
                  _href=URL("fornecedores"))
    
    if form_fornecedor.process().accepted:
        response.flash = 'Fornecedor Salvo com Sucesso!'
        redirect(URL('fornecedor', args=form_fornecedor.vars.id))

    elif form_fornecedor.errors:
        response.flash = 'Erro no Formulário Principal!'

    return locals()

def custo():
    id_fornecedor = int(request.args(0))
    Custo.insumo.readable = Custo.insumo.writable = True
    Custo.fornecedor.default = id_fornecedor
    Custo.embalagem.default = 1

    def validarInsumo(form,fornecedor_id=id_fornecedor):
        insumo_id = form.vars.insumo
        if db((db.custos.insumo == insumo_id) & (db.custos.fornecedor==fornecedor_id)).count():
            if 'new' in request.args:
                form.errors.insumo = 'Insumo já Cadastrado neste Fornecedor'

    formCusto = SQLFORM.grid((Custo.fornecedor==id_fornecedor),csv=False,user_signature=False
                             ,maxtextlength=50,details=False,args=[id_fornecedor],
                             onvalidation=validarInsumo,)

    btnVoltar = A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning",
                 _onClick="jQuery('#custo').get(0).reload()")

    if formCusto.update_form:
        btnExcluir = A(SPAN(_class="glyphicon glyphicon-trash"), ' Excluir ', _class="btn btn-danger", _title="Excluir...",
                   _href="#")
    else:
        btnExcluir = ''

    return locals()


#@auth.requires_membership('admin')
def condicao():

    formCondicao = SQLFORM.grid(Condicao,csv=False,user_signature=False,maxtextlength=50,details=False)

    return locals()

#@auth.requires_membership('admin')
def unidade():

    formUnidade = SQLFORM.grid(Unidade,csv=False,user_signature=False, maxtextlength=50,details=False)

    return locals()

#@auth.requires_membership('admin')
def tipoInsumo():

    formTpInsumo = SQLFORM.grid(TipoInsumo,csv=False,user_signature=False, maxtextlength=50,details=False)

    return locals()
