# -*- coding: utf-8 -*-

#@auth.requires_membership('admin')
def curva():
    form_pesq = SQLFORM.factory(
        Field('demanda','integer',requires=IS_EMPTY_OR(IS_IN_DB(db,'demandas.id','%(codigo)s - %(descricao)s',zero='TODAS')),label='Demanda'),
        Field('abc',requires=IS_IN_SET(['INSUMO','FORNECEDOR'], zero=None),label='Curva ABC'),
        Field('tipo',requires=IS_EMPTY_OR(IS_IN_DB(db,'tipoInsumo.descricao','%(descricao)s',zero='TODOS')),label='Tipo Insumo'),
        table_name='pesquisar',
        submit_button='Gerar Curva ABC',
        keepvalues = True,
        )

    if form_pesq.process().accepted:
        idDemanda = form_pesq.vars.demanda
        abc = form_pesq.vars.abc
        tipo = form_pesq.vars.tipo
        
    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    return dict(form_pesq=form_pesq)

#@auth.requires_membership('admin')
def gerar_abc():
    idDemanda = request.vars.demanda
    abc = request.vars.abc
    tipo = request.vars.tipo
    Relatorio.truncate()
    demanda = tipoInsumo = "Todos"

    if abc == 'INSUMO':
        sum = PagarInsumos.quantidade.sum()
        sum1 = (PagarInsumos.quantidade * PagarInsumos.preco - PagarInsumos.desconto).sum()
        groupby=PagarInsumos.insumo
        query = (PagarInsumos.pagar == Pagar.id) & (PagarInsumos.insumo == Insumo.id)
        xdesc = 'Insumo[row.pagarInsumos.insumo].descricao'
        if idDemanda != '':
            query = query & (PagarInsumos.demanda==idDemanda)
            demanda = Demandas[int(idDemanda)].descricao
        if tipo != '':
            query = query & (Insumo.tipo==tipo)
            #tipoInsumo = TipoInsumo[tipo].descricao

    elif abc == 'FORNECEDOR':
        sum = Pagar.valor.sum()
        sum1 = Pagar.valor.sum()
        groupby = Pagar.fornecedor
        if idDemanda != '':
            query = (PagarInsumos.demanda==idDemanda)
            demanda = Demandas[int(idDemanda)].descricao
        else:
            query = (Pagar.id > 0)
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

        curva = db(Relatorio.id>0).select()
    else:
        curva = ''

    resumo = H5('Curva ABC: ', abc, ' - Demanda: ', demanda,' - Tipo de Insumo: ', tipo)

    return dict(curva=curva, resumo=resumo)

#@auth.requires_membership('admin')
def historico_insumo():
    form_pesq = SQLFORM.factory(
        Field('demanda','integer',requires=IS_EMPTY_OR(IS_IN_DB(db,'demandas.id','%(codigo)s - %(descricao)s',zero='TODOS')),label='Demanda:'),
        Field('insumo','integer',requires=IS_EMPTY_OR(IS_IN_DB(db,'insumos.id','%(descricao)s',zero='TODOS')),label='Insumo:'),
        Field('dtinicial','date',requires=data, label='Data Inicial'),
        Field('dtfinal','date',requires=data,default=request.now,label='Data Final'),
        table_name='pesquisar',
        submit_button='Histórico de Insumos',
        keepvalues = True,
    )

    if form_pesq.process().accepted:
        pass

    elif form_pesq.errors:
        response.flash = 'Erro no Formulário'

    return dict(form_pesq=form_pesq)


#@auth.requires_membership('admin')
def gerar_historico_insumo():

    from datetime import datetime
    idDemanda = request.vars.demanda
    idInsumo = request.vars.insumo
    inicial = datetime.strptime(request.vars.dtinicial,'%d/%m/%Y').date() if request.vars.dtinicial != '' else ''
    final = datetime.strptime(request.vars.dtfinal,'%d/%m/%Y').date() if request.vars.dtfinal != '' else request.now

    #query = (Pagar.id == PagarInsumos.pagar ) & (Pagar.emissao >= request.vars.dtinicial and Pagar.emissao <= request.vars.dtfinal) & (PagarInsumos.insumo == Insumo.id)
    query = (Pagar.id == PagarInsumos.pagar )  & (PagarInsumos.insumo == Insumo.id)
    if inicial != '':
        query = query & (Pagar.emissao >= inicial)
    if final != '':
        query = query & (Pagar.emissao <= final)
    if idDemanda != '': 
        query = query & (PagarInsumos.demanda == idDemanda)
    if idInsumo != '':
        query = query & (PagarInsumos.insumo == idInsumo)
    
    insumos = db(query).select(Insumo.descricao.with_alias('insumo'),
                            Insumo.codigo.with_alias('codigo'),
                            Pagar.emissao.with_alias('emissao'),
                            PagarInsumos.unidade.with_alias('unidade'),
                            PagarInsumos.quantidade.with_alias('quantidade'),
                            PagarInsumos.preco.with_alias('preco'),
                            #(round(float(PagarInsumos.quantidade)*float(PagarInsumos.preco)-float(PagarInsumos.desconto),2)).with_alias('total')
                            orderby = Pagar.emissao
                            )
    
   
    return dict(insumos=insumos)

def exportar_cliente():
    import csv
    c = csv.writer(open("sigo_clientes.csv", "wb",),delimiter=';')
    clientes = db(Clientes.id>0).select()
    
    for cli in clientes:
        tipo = 'Pessoa {}'.format(cli.tipo)
        if cli.razao == '':
            razao = cli.nome
        else:
            razao = cli.razao

        try:
            con = db(Contatos.cliente == cli.id).select().first()
            fone = con.fone
            email = con.email
        except:
            fone = ''
            email = ''
        try:
            end = db(Enderecos.cliente == cli.id).select().first()
            endereco = end.endereco
            bairro = end.bairro
            cidade = end.cidade
            estado = end.estado
            cep = end.cep
        except:
            endereco = ''
            bairro = ''
            cidade = ''
            estado = ''
            cep = ''

        row = []    
        row.append(tipo) #Tipo de Cliente
        row.append(razao) #Nome/Razão Social
        row.append(cli.nome) #Nome Fantasia
        row.append(cli.cnpj_cpf) #CPF/CNPJ
        row.append('') #Inscrição Estadual
        row.append('') #Inscrição Municipal
        row.append('') #Data de Nascimento
        row.append(cli.ie_rg) #RG
        row.append('') #Emissor RG
        row.append('') #Estado RG
        row.append(fone) #Telefone 1
        row.append('') #Telefone 2
        row.append('') #Telefone 3
        row.append(email) #Email 1
        row.append('') #Email 2
        row.append('') #Email 3
        row.append('Residencial') #Tipo de Endereço
        row.append(estado) #Estado
        row.append(cidade) #Municipio
        row.append(cep) #CEP
        row.append(endereco) #Rua/Est./Av.
        row.append(bairro) #Bairro
        row.append('') #Número
        row.append('') #Complemento
        row.append('') #Andar
        row.append('') #Apartamento
        row.append('') #Bloco
        row.append('') #Acesso 
    
        c.writerow(row)


def exportar_atividades():
    atividades = db(Atividades.id>0).select()
    for atv in atividades:
        vl_atv = valor_atividade(int(1))
        print vl_atv
        itens = db(Atividades_Itens.id == atv.id).select()
        for item in itens:
            if item.tipo == 'Composição':
                cod_item = item.composicao
                desc_item = db(Composicao.id == item.composicao).select().first()['descricao']
                vl_item = valorComposicao(item.composicao)
            elif item.tipo == 'Insumo':
                cod_item = item.insumo
                desc_item = db(Insumos.id == item.insumo).select().first()['descricao']
                vl_item = db(Insumos.id == item.insumo).select().first()['preco']
            row = []
            row.append('')  # 'SIGLA DA CLASSE',
            row.append(atv.id) # 'CODIGO DA COMPOSICAO',
            row.append(atv.atividade) # 'DESCRICAO DA COMPOSICAO',
            row.append(atv.unidade) # 'UNIDADE',
            row.append(vl_atv) # 'CUSTO TOTAL',
            row.append(item.tipo.upper()) # 'TIPO ITEM',
            row.append(cod_item) # 'CODIGO ITEM',
            row.append(desc_item) # 'DESCRIÇÃO ITEM',
            row.append(item.unidade) # 'UNIDADE ITEM',
            row.append(item.quantidade) # 'COEFICIENTE',
            row.append(vl_item) # 'UNITARIO',
            row.append(round(item.quantidade*vl_item,2)) # 'CUSTO TOTAL'
            print row