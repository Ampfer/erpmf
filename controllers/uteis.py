def valor_atividade(idAtividade):
    itens = db(Atividades_Itens.atividade == idAtividade).select()
    total = 0
    for item in itens:
        if item.composicao:
            valor = round(float(valorComposicao(int(item.composicao)))*float(item.quantidade),2)
        else:
            valor = round(float(Insumo[int(item.insumo)].preco)*float(item.quantidade),2)
        total += valor
    return "{0:.2f}".format(total)

def exportar_atividades():
    import csv
    c = csv.writer(open("sigo_composicao2.csv", "wb",),delimiter=';')
    c.writerow(['SIGLA DA CLASSE','CODIGO DA COMPOSICAO','DESCRICAO DA COMPOSICAO','UNIDADE','CUSTO TOTAL',
                'TIPO ITEM','CODIGO ITEM','DESCRIÇÃO ITEM','UNIDADE ITEM','COEFICIENTE','UNITARIO','CUSTO TOTAL'])
    
    
    itens = db(Atividades_Itens.id >0).select(orderby = Atividades_Itens.atividade)
    atividadeId = 0
    for item in itens:
        if item.atividade != atividadeId:
            atividadeId = item.atividade
            atv = Atividades[atividadeId]
            atividade = atv.atividade
            unidade = atv.unidade
            valor = valor_atividade(int(atividadeId))
            row = []
            row.append('')  # 'SIGLA DA CLASSE',
            row.append(int(atividadeId)+247) # 'CODIGO DA COMPOSICAO',
            row.append(atividade) # 'DESCRICAO DA COMPOSICAO',
            row.append(unidade) # 'UNIDADE',
            row.append(valor) # 'CUSTO TOTAL',
            c.writerow(row)
            
        if item.tipo == 'Composição':
            cod_item = item.composicao
            desc_item = db(Composicao.id == item.composicao).select().first()['descricao']
            vl_item = valorComposicao(item.composicao)
        elif item.tipo == 'Insumo':
            cod_item = item.insumo
            desc_item = db(Insumo.id == item.insumo).select().first()['descricao']
            vl_item = db(Insumo.id == item.insumo).select().first()['preco']
        
        row = []
        row.append('')  # 'SIGLA DA CLASSE',
        row.append(int(atividadeId)+247) # 'CODIGO DA COMPOSICAO',
        row.append(atividade) # 'DESCRICAO DA COMPOSICAO',
        row.append(unidade) # 'UNIDADE',
        row.append(valor) # 'CUSTO TOTAL',
        row.append(item.tipo) # 'TIPO ITEM',
        row.append(cod_item) # 'CODIGO ITEM',
        row.append(desc_item) # 'DESCRIÇÃO ITEM',
        row.append(item.unidade) # 'UNIDADE ITEM',
        row.append(item.quantidade) # 'COEFICIENTE',
        row.append(vl_item) # 'UNITARIO',
        row.append(round(item.quantidade*vl_item,2)) # 'CUSTO TOTAL'
        
        c.writerow(row)


def exportar_composicao():
    import csv
    c = csv.writer(open("sigo_composicao1.csv", "wb",),delimiter=';')
    c.writerow(['SIGLA DA CLASSE','CODIGO DA COMPOSICAO','DESCRICAO DA COMPOSICAO','UNIDADE','CUSTO TOTAL',
                'TIPO ITEM','CODIGO ITEM','DESCRIÇÃO ITEM','UNIDADE ITEM','COEFICIENTE','UNITARIO','CUSTO TOTAL'])
    
    itens = db(Composicao_Insumos.id >0).select(orderby = Composicao_Insumos.composicao)
    composicaoId = 0
    for item in itens:
        if item.composicao != composicaoId:
            composicaoId = item.composicao
            com = Composicao[composicaoId]
            composicao = com.descricao
            unidade = com.unidade
            valor = valorComposicao(int(composicaoId))
            row = []
            row.append('')  # 'SIGLA DA CLASSE',
            row.append(composicaoId) # 'CODIGO DA COMPOSICAO',
            row.append(composicao) # 'DESCRICAO DA COMPOSICAO',
            row.append(unidade) # 'UNIDADE',
            row.append(valor) # 'CUSTO TOTAL',
            c.writerow(row)
            
        desc_item = db(Insumo.id == item.insumo).select().first()['descricao']
        vl_item = db(Insumo.id == item.insumo).select().first()['preco']
        
        row = []
        row.append('')  # 'SIGLA DA CLASSE',
        row.append(composicaoId) # 'CODIGO DA COMPOSICAO',
        row.append(composicao) # 'DESCRICAO DA COMPOSICAO',
        row.append(unidade) # 'UNIDADE',
        row.append(valor) # 'CUSTO TOTAL',
        row.append('INSUMO') # 'INSUMO',
        row.append(item.insumo) # 'CODIGO ITEM',
        row.append(desc_item) # 'DESCRIÇÃO ITEM',
        row.append(item.unidade) # 'UNIDADE ITEM',
        row.append(item.quantidade) # 'COEFICIENTE',
        row.append(vl_item) # 'UNITARIO',
        row.append(round(item.quantidade*vl_item,2)) # 'CUSTO TOTAL'
        
        c.writerow(row)

def exportar_fornecedor():
    import csv
    c = csv.writer(open("sigo_fornecedor.csv", "wb",),delimiter=';')
    fornecedores = db(Fornecedores.id>0).select()
    c.writerow(['Tipo de Fornecedor','Nome/Razão Social','Nome Fantasia','CPF/CNPJ','Inscrição Estadual','Inscrição Municipal',
            'Data de Nascimento','RG','Emissor RG','Estado RG','Telefone 1','Telefone 2','Telefone 3','Email 1','Email 2',
            'Email 3','Tipo de Endereço','Estado','Municipio','CEP','Rua/Est./Av.','Bairro','Número','Complemento','Andar',
            'Apartamento','Bloco','Acesso' ])
    
    for forn in fornecedores:
        tipo = 'Pessoa {}'.format(forn.tipo)
        if forn.razao == '':
            razao = forn.nome
        else:
            razao = forn.razao

        try:
            con = db(Contatos.fornecedor == forn.id).select().first()
            fone = con.fone
            email = con.email
        except:
            fone = ''
            email = ''
        try:
            end = db(Enderecos.fornecedor == forn.id).select().first()
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
        row.append(tipo) #Tipo de Fornecedor
        row.append(razao) #Nome/Razão Social
        row.append(forn.nome) #Nome Fantasia
        row.append(forn.cnpj_cpf) #CPF/CNPJ
        row.append('') #Inscrição Estadual
        row.append('') #Inscrição Municipal
        row.append('') #Data de Nascimento
        row.append(forn.ie_rg) #RG
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

