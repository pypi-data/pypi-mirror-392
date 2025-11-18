# SPED Reader
Um leitor de arquivos SPED em formato txt.

## Instalação
```
pip install spedreader
```

## Uso
```
from spedreader import SpedReader

spedReader = SpedReader('caminho/para/arquivo.txt')
sped = spedReader.read_sped()

parent_id = 3
# Retorna todos os registros C100 que tem pai C010 número 3.
result = sped["Bloco C"]["C100"].query("id_c010 == @parent_id")
print(result)

sped.write_sped('caminho/para/novo/arquivo.txt')
```
