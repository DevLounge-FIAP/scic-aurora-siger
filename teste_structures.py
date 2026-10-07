'''
    Script de Testes e Validação do Arquivo structures.py
'''

from numerical_analysis import processar_dataset

from structures import (AlertHeap, TrieNode, PrefixTrie)

print("=== Verificação do gerenciamento de alertas ===")
print("\n=== TESTE 1: Verificação do heapsort ===")

df, alertas = processar_dataset(salvar=False)
print(f"✓ Registros carregados: {len(df)}")

heap = AlertHeap()
ordenados = heap.heapsort(alertas)
assert len(ordenados) == len(alertas), "Heapsort perdeu ou duplicou alerta"
assert heap.alertas == [], "Heap deveria estar vazio depois do heapsort"
for i in range(len(ordenados) - 1):
    assert heap.comparar(ordenados[i]) >= heap.comparar(ordenados[i + 1]), f"Fora de ordem na posicao {i}"
print("\nLista de alertas ordenados - Função Heapsort")
for alerta in ordenados[:5]:
    print(heap.formatar(alerta))

print("✓ Heapsort válido")


print("\n=== TESTE 2: Verificação das propriedades do heap ===")
for alerta in alertas:
    heap.inserir(alerta)
assert len(heap.alertas) == len(alertas)
for i in range(1, len(heap.alertas)):
    pai = (i - 1) // 2
    assert heap.comparar(heap.alertas[pai]) >= heap.comparar(heap.alertas[i]), f"Pai menor que filho na posição {i}"
print("✓ Inserção de alertas válida")


print("\n=== TESTE 3: Verificação da devolução do alerta prioritário ===")
tamanho = len(heap.alertas)
inicio = heap.alerta_prioritario()
assert heap.comparar(inicio) == heap.comparar(ordenados[0]), "O primeiro alerta não é o mais crítico"
assert len(heap.alertas) == tamanho, "Alerta_prioritario nao pode remover"

print("\nAlerta com maior prioridade (sem remover)")
print(heap.formatar(inicio))

print("✓ Devolução de alerta prioritário sem remoção válida")

print("\n=== TESTE 4: Verificação da devolução do alerta prioritário com remoção ===")
removido = heap.remover_alerta_prioritario()
assert removido is inicio, "Removeu um alerta diferente do topo"
assert len(heap.alertas) == tamanho - 1
assert heap.comparar(heap.alerta_prioritario()) <= heap.comparar(removido)
for i in range(1, len(heap.alertas)):
    pai = (i - 1) // 2
    assert heap.comparar(heap.alertas[pai]) >= heap.comparar(heap.alertas[i]), "Heap quebrou depois da remoção"

print("\nRemovendo alerta prioritário")
print(heap.formatar(removido))

print("\nHeap depois da remoção (heapsort sem reinserir)")
pos_remocao = heap.heapsort(limpar=False)
assert len(pos_remocao) == tamanho - 1, "Heapsort(limpar=False) perdeu alerta"
assert removido not in pos_remocao, "Alerta removido voltou pro heap"
for alerta in pos_remocao[:5]:
    print(heap.formatar(alerta))

print("✓ Devolução de alerta prioritário com remoção válida")

print("\n=== TESTE 5: Segunda verificação do heapsort ===")
ordenados2 = heap.heapsort(alertas)
assert [heap.comparar(a) for a in ordenados2] == [heap.comparar(a) for a in ordenados]

print("\nLista de alertas ordenados - Função Heapsort (2a vez)")
for alerta in ordenados2[:5]:
    print(heap.formatar(alerta))

print("✓ Segunda verificação do heapsort válida")

print("\n=== TESTE 6: Verificações do heap vazio ===")
vazio = AlertHeap()
assert vazio.alerta_prioritario() is None
assert vazio.remover_alerta_prioritario() is None
unico = AlertHeap()
unico.inserir(alertas[0])
assert unico.remover_alerta_prioritario() is alertas[0]
assert unico.alertas == []
print("✓ Verificações de heap vazio válidas")

print("=== Verificação da estrutura de prefixos ===")

trie = PrefixTrie()
trie.inserir_df(df)
trie.inserir_palavra("teste")

print("\n=== TESTE 7: Verificações do buscar ===")
assert trie.buscar("hab") is False, "Prefixo não pode contar como palavra"
assert trie.buscar("test") is False
assert trie.buscar("teste") is True
assert trie.buscar("TESTE") is True, "Busca não pode diferenciar maiúscula e minúscula"
print("✓ Verificações de busca válidas")

print("\n=== TESTE 8: Verificações do autocomplete ===")
for prefixo in ["ha", "t", "alo"]:
    sugestoes = trie.autocomplete(prefixo)
    assert all(s.lower().startswith(prefixo) for s in sugestoes), f"Sugestão fora do prefixo '{prefixo}'"
    assert sugestoes == sorted(sugestoes), f"Sugestões de '{prefixo}' fora de ordem"

assert len(trie.autocomplete("ha")) > 0, "Esperava achar algo com 'ha'"
assert "teste" in trie.autocomplete("t")
assert trie.autocomplete("xyz") == []
print("✓ Verificações do autocomplete válidas")


print("\nVerificações extras interativas: ")
print("\nBuscar autocomplete interativo - Função autocomplete_interativo")
trie.autocomplete_interativo()
print("\nBuscar interativo - Função buscar_interativo")
trie.buscar_interativo()


print("\n=== TODOS OS TESTES DO MÓDULO STRUCTURES CONCLUÍDOS COM SUCESSO! ===")



