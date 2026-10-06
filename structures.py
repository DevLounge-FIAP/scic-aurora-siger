"""
structures.py | Aurora Siger (Semana 4)

Responsabilidades deste módulo:
    *   Implementar no módulo `structures.py` a classe `AlertHeap` (fila de prioridade com rotinas explícitas de `heapify-up` e `heapify-down`) 
        consumindo os alertas da Semana 3 para ordenar e extrair os eventos mais críticos em $O(\log N)$. 
    *   Implementar a estrutura `PrefixTrie` (árvore de prefixos) com métodos de inserção, busca exata e autocomplete para indexação rápida de 
        nomes de módulos e códigos hexadecimais de sensores da colônia.

"""

from numerical_analysis import * 

# classe AlertHeap: fila de prioridade dos alertas, ordena e extrai os mais criticos
class AlertHeap:
    def __init__(self):
        self.alertas = []          # o heap
        self.lista_ordenada = []   # resultado do heapsort

    # critério de comparação dos alertas para identificar qual o prioritário
    def comparar(self, alerta):
        return (alerta["severidade_alerta"], -alerta["prioridade"], alerta["erro_absoluto"])

    # heapify_up: pega o elemento na posicao i e sobe comparando com o pai
    # troca enquanto ele for maior que o pai, para quando achar o lugar
    def heapify_up(self, i):
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

    # heapify_down: pega o elemento na posicao i e desce trocando com o maior filho
    # para quando ele for maior que os dois filhos (ou nao tiver filhos)
    def heapify_down(self, i):
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

    # coloca o alerta no final e sobe ate o lugar certo usando o heapify_up
    def inserir(self, alerta):
        self.alertas.append(alerta)
        self.heapify_up(len(self.alertas) - 1)

    # devolve qual o alerta com a maior prioridade no momento sem alterar nenhum dado
    def alerta_prioritario(self):
        if len(self.alertas) == 0:
            return None
        return self.alertas[0]

    # tira o alerta mais critico do heap e devolve
    def remover_alerta_prioritario(self):
        if len(self.alertas) != 0:   
            inicio = self.alertas[0]   
            fim = self.alertas.pop()   

        if len(self.alertas) > 0:  # se so tinha 1 nao sobra nada pra reaolocar
            self.alertas[0] = fim      
            self.heapify_down(0) 
        return inicio

    # monta um heap novo com a lista e tira um por um (do mais crítico pro menos crítico)
    def heapsort(self, lista):
        self.alertas = []
        self.lista_ordenada = []

        for alerta in lista:
            self.inserir(alerta)

        while len(self.alertas) > 0:
            self.lista_ordenada.append(self.remover_alerta_prioritario())

        return self.lista_ordenada

# ---------------------------------------------------------------------------------------------------------
# classes trie: inserem e buscam palavras por prefixo, usadas pra indexar
# nomes de modulos e codigos hexadecimais de sensores da colonia
# ---------------------------------------------------------------------------------------------------------

# guarda os filhos (um por letra) e se ali termina uma palavra
class TrieNode:
    def __init__(self):
        self.filhos = {}
        self.fim = False

class PrefixTrie:
    def __init__(self):
        self.root = TrieNode()
        self.palavra_og = {}   # guarda a palavra com a escrita original

    # insere a palavra letra por letra e cria nós que faltam
    def inserir_palavra(self, palavra):
        p = self.root
        for letra in palavra:
            if letra not in p.filhos:
                p.filhos[letra] = TrieNode()
            p = p.filhos[letra]
        p.fim = True

    # obtém os dados do arquivo CSV e adiciona eles em novos valores na Trie
    def inserir_df(self, df, colunas=("modulo_nome", "sensor_hex_id")):
        for coluna in colunas:
            for valor in df[coluna]:
                original = str(valor)
                self.inserir_palavra(original.lower())
                self.palavra_og[original.lower()] = original

    # busca palavra exata: True se existe e False se não
    def buscar(self, palavra):
        palavra = palavra.lower()
        p = self.root

        for letra in palavra:
            if letra not in p.filhos:
                return False
            p = p.filhos[letra]

        return p.fim

    # devolve todas as palavras que comecam com o prefixo em ordem alfabetica
    def autocomplete(self, prefixo):
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
