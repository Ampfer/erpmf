# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('M&F'),XML('&trade;&nbsp;'),
                  _class="navbar-brand",_href="#",
                  _id="web2py-logo")
#response.title = request.application.replace('_',' ').title()
response.title = 'M&F'
response.subtitle = '- Engenharia & Construções'

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = myconf.get('app.author')
response.meta.description = myconf.get('app.description')
response.meta.keywords = myconf.get('app.keywords')
response.meta.generator = myconf.get('app.generator')

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL(request.application,'default','index'), [])
    ]

response.menu+=[
    (T('Arquivos'), False, URL(request.application,'default','index'), [
    ('Cadastro', False, URL(r=request, c='cadastro', f='cadastros')),
    ('Cliente', False, URL(r=request, c='cadastro', f='clientes')),
    ('Fornecedor', False, URL(r=request, c='cadastro', f='fornecedores')),
    ('Condição de Pagamento', False, URL(r=request, c='cadastro', f='condicao')),
    ('Unidade', False, URL(r=request, c='cadastro', f='unidade')),
    ('Tipo de Insumo', False, URL(r=request, c='cadastro', f='tipoInsumo')),
    ])]
response.menu+=[
    (T('Contas a Receber'), False, URL(request.application,'default','index'), [
    ('Entrada', False, URL(r=request, c='receber', f='entrada_lista')),
    ('Ficha Cliente', False, URL(r=request, c='receber', f='cliente_ficha')),
    ('Contas a Receber', False, URL(r=request, c='receber', f='receber_lista')),
    ])]
response.menu+=[
    (T('Contas a Pagar'), False, URL(request.application,'default','index'), [
    ('Pedido de Compra', False, URL(r=request, c='pagar', f='compras')),
    ('Entrada de Nota Fiscal', False, URL(r=request, c='pagar', f='entrada_lista')),
    ('Ficha Fornecedor', False, URL(r=request, c='pagar', f='fornecedor_ficha')),      
    ('Contas a Pagar', False, URL(r=request, c='pagar', f='pagar_lista')),      
    ])]
response.menu+=[
    (T('Financeiro'), False, URL(request.application,'default','index'), [
    ('banco', False, URL(r=request, c='financeiro', f='banco')),
    ('Conta', False, URL(r=request, c='financeiro', f='contas')),
    ('Cheques', False, URL(r=request, c='financeiro', f='cheques')),
    ('Conta Corrente', False, URL(r=request, c='financeiro', f='conta_corrente')),
    ])]
response.menu+=[
    (T('Obra'), False, URL(request.application,'default','index'), [
    ('Etapas', False, URL(r=request, c='obra', f='etapas')),
    ('Insumo', False, URL(r=request, c='obra', f='insumos')),
    ('Composição', False, URL(r=request, c='obra', f='composicao')),
    ('Obras', False, URL(r=request, c='obra', f='obras')),
    ('Diário de Obras', False, URL(r=request, c='obra', f='diarios')),
    ('Orçamentos', False, URL(r=request, c='obra', f='orcamentos')),
    ('Quantitativo', False, URL(r=request, c='obra', f='quantitativos')),
    ])]

DEVELOPMENT_MENU = True

if "auth" in locals(): auth.wikimenu() 
