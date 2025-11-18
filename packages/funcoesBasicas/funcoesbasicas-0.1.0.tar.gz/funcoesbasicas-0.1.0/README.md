# Funções Básicas para Python

Este repositório contém um pequeno conjunto de utilitários úteis para scripts Python. O arquivo principal é `funcoesBasicas.py`, que reúne funções para configuração de logging, formatação de texto no terminal (com suporte a cor de texto e cor de fundo), limpeza da tela e pausas no fluxo do programa.

## Arquivo

- `funcoesBasicas.py` — implementa as funções descritas abaixo.

## Funções incluídas

- `logging_config(nomeArquivo)`
  - Configura o logging do Python para gravar arquivos em um diretório `logs` ao lado do script em execução. Passe `__file__` (ou outra string) para nomear o arquivo de log.
  - Gera um arquivo com timestamp e envia a saída também para stdout (FileHandler UTF-8 + StreamHandler).

- `textoCor(texto: str, cor_texto: Cores = None, cor_fundo: Cores = None)`
  - Formata uma string aplicando códigos ANSI para cor do texto e opcionalmente cor de fundo.
  - `Cores` é uma enum definida em `funcoesBasicas.py` (ex.: `Cores.VERDE`, `Cores.VERMELHO_CLARO`, `Cores.FUNDO_AZUL`).
  - Se nenhum parâmetro de cor for passado, a função retorna o texto sem modificação.
  - Observação: terminais modernos (Windows 10+/PowerShell/Windows Terminal, Linux, macOS) suportam ANSI nativamente; em Windows antigos pode ser necessário habilitar VT100.

- `limpar()`
  - Limpa o terminal usando `cls` no Windows e `clear` em outros sistemas.

- `pausa(time: float = 0.5)`
  - Pausa a execução por `time` segundos (usa `time.sleep`).

## Exemplos de uso

Exemplo mínimo em um script `meu_script.py`:

```python
from funcoesBasicas import logging_config, textoCor, limpar, pausa, Cores

if __name__ == '__main__':
    logging_config(__file__)
    print(textoCor('Iniciando processo...', Cores.VERDE))
    # Texto em vermelho claro sobre fundo amarelo
    print(textoCor('Aviso: operação lenta', Cores.VERMELHO_CLARO, Cores.FUNDO_AMARELO))
    pausa(1)
    limpar()
    print('Pronto')
```

## Observações

- O `logging_config` cria automaticamente a pasta `logs` ao lado do script em execução. Os logs são gravados em UTF-8.
- A função `textoCor` usa sequências ANSI. Terminais modernos suportam essas sequências por padrão; em versões antigas do Windows pode ser necessário habilitar `VT100` ou usar um helper para cores.

## Compatibilidade

As funções foram escritas para serem simples e portáveis. São adequadas para scripts utilitários e projetos pequenos.

## Licença

Sinta-se à vontade para usar ou adaptar estas funções em seus projetos pessoais e profissionais.
