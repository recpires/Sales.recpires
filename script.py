from graphviz import Digraph

# Cria o fluxograma
flowchart = Digraph(format='png')
flowchart.attr(rankdir='LR', size='10')

# Processo de Pedido
flowchart.node('A', 'Cliente navega pelos produtos')
flowchart.node('B', 'Seleciona produto + variação\n(ex: camisa azul, M)')
flowchart.node('C', 'Escolhe quantidade')
flowchart.node('D', 'Adiciona ao carrinho')
flowchart.node('E', 'Vai para checkout')
flowchart.node('F', 'Escolhe método de pagamento\n(Pagar na entrega: dinheiro, pix, cartão)')
flowchart.node('G', 'Cadastra/seleciona endereço')
flowchart.node('H', 'Pedido é criado com status:\n“Aguardando entrega”')
flowchart.node('I', 'Lojista visualiza pedido:\nItens, endereço, cliente')
flowchart.node('J', 'Lojista atualiza status:\n“Pedido saiu para entrega”')
flowchart.node('K', 'Lojista pode confirmar pagamento\ne finalizar pedido')

# Lógica de Variação de Produto
flowchart.node('P1', 'Cadastro de Produto')
flowchart.node('P2', 'Adiciona variações:\n(ex: cor, tamanho)')
flowchart.node('P3', 'Define estoque e preço\npor variação')
flowchart.node('P4', 'Sistema atualiza estoque\nquando pedido é feito')

# Conexões do processo de pedido
flowchart.edges([
    ('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E'),
    ('E', 'F'), ('F', 'G'), ('G', 'H'),
    ('H', 'I'), ('I', 'J'), ('J', 'K')
])

# Conexões da lógica de variação
flowchart.edge('P1', 'P2')
flowchart.edge('P2', 'P3')
flowchart.edge('P3', 'P4')
flowchart.edge('P4', 'B', label='(dados usados na compra)')

# Salva e abre o arquivo
flowchart.render('pedido_variacao_fluxo', cleanup=False)
flowchart.view()
