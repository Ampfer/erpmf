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
    (T('Cadastros'), False, URL(request.application,'default','index'), [
    ('Cliente', False, URL(r=request, c='cadastro', f='clientes')),
    ('Fornecedor', False, URL(r=request, c='cadastro', f='fornecedores')),
    ('Produto', False, URL(r=request, c='cadastro', f='produtos')),
    ('Condição de Pagamento', False, URL(r=request, c='cadastro', f='condicao')),
    ('Unidade', False, URL(r=request, c='cadastro', f='unidade')),
    ('Tipo de Insumo', False, URL(r=request, c='cadastro', f='tipoInsumo')),
    ('Plano de Contas', False, URL(r=request, c='cadastro', f='planoContas')),
    ])]
response.menu+=[
    (T('Contas a Receber'), False, URL(request.application,'default','index'), [
    ('Entrada de Contas a Receber', False, URL(r=request, c='receber', f='entrada_lista')),
    ('Ficha Cliente', False, URL(r=request, c='receber', f='cliente_ficha')),
    ('Contas a Receber', False, URL(r=request, c='receber', f='receber_lista')),
    ])]
response.menu+=[
    (T('Contas a Pagar'), False, URL(request.application,'default','index'), [
    ('Pedido de Compra', False, URL(r=request, c='pagar', f='compras')),
    ('Entrada Contas a Pagar', False, URL(r=request, c='pagar', f='entrada_lista')),
    ('Ficha Fornecedor', False, URL(r=request, c='pagar', f='fornecedor_ficha')),      
    ('Contas a Pagar', False, URL(r=request, c='pagar', f='pagar_lista')),
    ('Pagamentos', False, URL(r=request, c='pagar', f='lotes')), 
    ])]
response.menu+=[
    (T('Financeiro'), False, URL(request.application,'default','index'), [
    ('banco', False, URL(r=request, c='financeiro', f='banco')),
    ('Conta', False, URL(r=request, c='financeiro', f='contas')),
    ('Cheques', False, URL(r=request, c='financeiro', f='cheques')),
    ('Conta Corrente', False, URL(r=request, c='financeiro', f='conta_corrente')),
    ('Transferências', False, URL(r=request, c='financeiro', f='transferencias')),
    ])]
response.menu+=[
    (T('Engenharia'), False, URL(request.application,'default','index'), [
    ('Demandas', False, URL(r=request, c='obra', f='demandas')),    
    ('Etapas', False, URL(r=request, c='obra', f='etapas')),
    ('Tarefas', False, URL(r=request, c='obra', f='atividades')),
    ('Composição', False, URL(r=request, c='obra', f='composicao')),
    ('Insumo', False, URL(r=request, c='obra', f='insumos')),
    ('Obras', False, URL(r=request, c='obra', f='obras')),
    ])]
response.menu+=[
    (T('Relatórios'), False, URL(request.application,'default','index'), [
    ('Curva ABC', False, URL(r=request, c='relatorios', f='curva')),    
    ('Histórico Insumos', False, URL(r=request, c='relatorios', f='historico_insumo')),
    ('Despesas', False, URL(r=request, c='relatorios', f='despesas')),
    ])]
    
DEVELOPMENT_MENU = True

if "auth" in locals(): auth.wikimenu() 
