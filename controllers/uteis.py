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
            row.append(atividadeId) # 'CODIGO DA COMPOSICAO',
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
        row.append(atividadeId) # 'CODIGO DA COMPOSICAO',
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



