
r"""
    structures.py | Aurora Siger (Semana 4)

    Responsabilidades deste módulo:
        *   Implementar no módulo `structures.py` a classe `AlertHeap` (fila de prioridade com rotinas explícitas de `heapify-up` e `heapify-down`) 
            consumindo os alertas da Semana 3 para ordenar e extrair os eventos mais críticos em $O(\log N)$. 
        *   Implementar a estrutura `PrefixTrie` (árvore de prefixos) com métodos de inserção, busca exata e autocomplete para indexação rápida de 
            nomes de módulos e códigos hexadecimais de sensores da colônia.

"""
from numerical_analysis import * 


# ---------------------------------------------------------------------------------------------------------
# Classe AlertHeap: fila de prioridade dos alertas, ordena e extrai os mais críticos
# ---------------------------------------------------------------------------------------------------------

class AlertHeap:
    def __init__(self):
        self.alertas = []  #heap 
        self.lista_ordenada = []

    def comparar(self, alerta):
        '''
            Critério de comparação dos alertas para identificar qual o prioritário
        '''
        return (alerta["severidade_alerta"], -alerta["prioridade"], alerta["erro_absoluto"])

    def formatar(self, alerta):
        '''
            Critério de formatação dos alertas

        '''
        return (
            f"Modulo: {alerta['modulo_nome']} | "
            f"Sensor: {alerta['sensor_hex_id']} | "
            f"Severidade: {alerta['severidade_alerta']} | "
            f"Prioridade: {alerta['prioridade']} | "
            f"Erro: {alerta['erro_absoluto']} ms"
        )

    def heapify_up(self, i):
        '''
            Resumo: heapify_up 

            Lógica: pega o elemento na posição i e sobe comparando com o pai, ou seja, realiza comparações e trocas até achar um pai maior ou igual a ele
        '''
        while i > 0:

            pai = (i - 1) // 2

            if self.comparar(self.alertas[i]) > self.comparar(self.alertas[pai]):
                temp = self.alertas[i]
                self.alertas[i] = self.alertas[pai]
                self.alertas[pai] = temp
                i = pai
            else:
                break
        return self.alertas

    def heapify_down(self, i):
        '''
            Resumo: heapify_down

            Lógica: pega o elemento na posição i e desce trocando com o maior filho, ou seja, realiza comparações e trocas até que seja menor que os dois filhos ou não tenha filhos

        '''
        n = len(self.alertas)
        while True:

            pai = i  
            esq = 2*i + 1
            dir = 2*i + 2

            if esq < n and self.comparar(self.alertas[esq]) > self.comparar(self.alertas[pai]):
                pai = esq

            if dir < n and self.comparar(self.alertas[dir]) > self.comparar(self.alertas[pai]):
                pai = dir

            if pai != i:
                temp = self.alertas[i]
                self.alertas[i] = self.alertas[pai]
                self.alertas[pai] = temp
                i = pai
            else:
                break
        return self.alertas

    def inserir(self, alerta):
        '''
            Resumo: coloca o alerta no final e sobe ate o lugar certo usando o heapify_up
        '''
        self.alertas.append(alerta)
        self.heapify_up(len(self.alertas) - 1)

    def alerta_prioritario(self):
        '''
            Resumo: devolve qual o alerta com a maior prioridade no momento sem alterar nenhum dado do heap
        '''
        if len(self.alertas) == 0:
            return None
        return self.alertas[0]

    def remover_alerta_prioritario(self):
        '''
            Resumo: devolve qual o alerta com a maior prioridade no momento e tira o alerta mais crítico do heap
        '''
        if len(self.alertas) == 0:
            return None

        inicio = self.alertas[0]   
        fim = self.alertas.pop()   

        if len(self.alertas) > 0:  
            self.alertas[0] = fim      
            self.heapify_down(0) 

        return inicio

    def heapsort(self, lista=None, limpar=True):
        '''
            Resumo: tira os alertas do heap um por um (do mais critico pro menos crítico)

            Logica:  limpar = True -> zera o heap e monta de novo com a lista recebida
                   limpar = False -> usa o heap como ele está (sem reinserir nada) e só esvazia ele
        '''
        if limpar:
            self.alertas = []
            for alerta in (lista or []):
                self.inserir(alerta)

        ordenados = []

        while self.alertas:
            ordenados.append(self.remover_alerta_prioritario())

        self.lista_ordenada = ordenados

        return ordenados
# ---------------------------------------------------------------------------------------------------------
# Classes Trie: inserem e buscam palavras por prefixo, usadas pra indexar nomes de modulos e códigos 
# hexadecimais de sensores da colônia
# ---------------------------------------------------------------------------------------------------------

class TrieNode:

    def __init__(self):
        self.filhos = {}
        self.fim = False 

class PrefixTrie:
    def __init__(self):
        self.root = TrieNode() # Cria um novo nó 
        self.palavra_og = {}   # Guarda a palavra com a escrita original

    def inserir_palavra(self, palavra):
        '''
            Resumo: insere a palavra letra por letra e cria nós que faltam

            Lógica: percorre cada letra da palavra (já em minúsculo) e cria um nó para ela caso ainda não exista. Quando chega na última letra, marca esse nó como o fim da palavra
            p.fim = True). Por último verifica se a palavra em minúsculo já existe como chave no dicionário palavra_og. Caso não exista, guarda a palavra com a escrita original (como 
            veio do CSV) como valor

        '''

        p = self.root
        for letra in palavra.lower():
            if letra not in p.filhos:
                p.filhos[letra] = TrieNode()
            p = p.filhos[letra]
        p.fim = True

        if palavra.lower() not in self.palavra_og:
            self.palavra_og[palavra.lower()] = palavra

    def inserir_df(self, df, colunas=("modulo_nome", "sensor_hex_id")):
        '''
            Resumo: obtém os dados do arquivo CSV e adiciona eles em novos valores na Trie 

            Lógica: pega cada coluna do arquivo CSV, armazena cada valor em uma variável (original) e transforma o valor em string (para manter todos os dados formatados).
            Depois manda a palavra como veio para a função inserir_palavra, que cuida de transformar em minúsculo para a trie e de guardar a escrita original no dicionário palavra_og

        '''

        for coluna in colunas:
            for valor in df[coluna]:
                original = str(valor)
                self.inserir_palavra(original)

    def buscar(self, palavra):
        '''
            Resumo: busca pela palavra exata 

            Lógica: armazena a palavra em letras minúsculas e faz verificações em cada uma das letras da palavra. A partir do momento que não encontra alguma letra,
            entende que a palavra não existe e retorna False. Quando termina todas as verificações com sucesso, retorna True (p.fim)

        '''
        palavra = palavra.lower()
        p = self.root

        for letra in palavra:
            if letra not in p.filhos:
                return False
            p = p.filhos[letra]

        return p.fim

    def buscar_interativo(self):
        '''
            Resumo: versão interativa do buscar 

            Lógica: usuário insere a palavra que deseja buscar. Esse input é formatado: os espaços iniciais e finais são ignorados e todas as letras ficam minúsculas. 
            Se o usuário digitar "sair", a função é encerrada. Caso contrário, o código procura pela palavra através da função buscar. 
            Quando encontra, devolve a palavra encontrada e se não encontrar, permite que o usuário procure novamente até que ele opte por sair ou encontre a palavra.

        '''
        while True:
            busca = input('Insira a palavra que deseja buscar (insira "sair" para sair da busca): ').strip().lower()
            if busca == "sair":
                return None

            if not self.buscar(busca): 
                print("A palavra não foi encontrada. Tente novamente.")
                continue  

            print("A palavra encontrada foi", self.palavra_og[busca])
            return self.palavra_og[busca]

    def autocomplete(self, prefixo):
        '''
            Resumo: devolve todas as palavras que começam com o prefixo em ordem alfabética 

            Lógica: armazena o prefixo em letras minúsculas e, de modo semelhante a função buscar, procura nos nós cada letra do prefixo. Caso alguma letra não seja 
            encontrada, devolve uma lista vazia. Se encontra todas, parte do nó onde o prefixo termina e percorre tudo que vem abaixo usando uma pilha. Sempre que um 
            nó marca o fim de uma palavra, o código busca a escrita original no dicionário palavra_og e adiciona no resultado. No final ordena a lista e devolve

        '''

        prefixo = prefixo.lower()
        p = self.root
        for letra in prefixo:
            if letra not in p.filhos:
                return []  
            p = p.filhos[letra]

        resultado = []
        pilha = [(p, prefixo)]

        while len(pilha) > 0:
            atual = pilha.pop()
            no = atual[0]
            texto = atual[1]
            if no.fim:
                resultado.append(self.palavra_og[texto])
            for letra in no.filhos:
                pilha.append((no.filhos[letra], texto + letra))

        resultado.sort()
        return resultado

    def autocomplete_interativo(self):
        '''
            Resumo: versão interativa do autocomplete: pede o prefixo, mostra as sugestões numeradas, pede que o usuário escolha e devolve a palavra escolhida

            Lógica: usuário insere a palavra que deseja buscar. Esse input é formatado: os espaços iniciais e finais são ignorados e todas as letras ficam minúsculas. 
            Se o usuário digitar "sair", a função é encerrada. Caso contrário, o código procura pela palavra através da função autocomplete e armazena o(s) resultado(s)
            na variável resultado. Depois disso, verifica o tamanho da variável resultado. Se for igual a 0, indica que não foram encontradas palavras que atendam ao prefixo e
            permite que o usuário faça uma nova busca. Caso contrário, devolve na tela as opções ordenadas em números seguindo a ordem alfabética. O usuário então deve indicar
            um número. Esse input passa por uma verificação e ou devolve a palavra selecionada ou permite que o usuário faça uma nova busca
        '''
        while True:
            busca_autocomplete = input('Insira o prefixo (insira "sair" para sair da busca): ').strip().lower()
            if busca_autocomplete == "sair":
                return None

            resultado = self.autocomplete(busca_autocomplete) 

            if len(resultado) == 0:
                print("Não foram encontradas palavras que atendam ao prefixo. Tente novamente.")
                continue

            for i in range(len(resultado)):
                print(i + 1, "-", resultado[i])

            escolha = input("Selecione um número para completar a palavra: ").strip()

            if escolha.isdigit() and 1 <= int(escolha) <= len(resultado):
                palavra = resultado[int(escolha) - 1]  # int pq input vem como string (se por int no input pode acabar dando erro)
                print("A palavra encontrada foi", palavra)
                return palavra
            print("Número inválido. Tente novamente.")


