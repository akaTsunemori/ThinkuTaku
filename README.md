# PAA Projeto Final
## Setup

```bash
# Clonar este repositório
git clone https://github.com/akaTsunemori/paa-projeto-final.git

# Mudar o diretório corrente ao do repositório
cd paa-projeto-final

# Criar ambiente conteinerizado
python3 -m venv venv

# Ativar o ambiente criado
source ./venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```
> **Notas:**<br>
> - As instruções acima foram direcionadas a um ambiente Linux;<br>
> - Para desativar o ambiente virtual criado, apenas digite **deactivate** em seu terminal;<br>
> - Refira-se a https://docs.python.org/3/library/venv.html para mais informações sobre ambientes virtuais em Python.

## Run
Para rodar o app, basta executar a aplicação em um terminal
```bash
# Executar a aplicação
python3 app.py
```
e abrir em um navegador o endereço **localhost:5000**.

## Estrutura de pastas
```
root
|_src          # "Source", (the /src folder comprises of the raw non-minified code)
|_templates    # Templates html para o Flask ficam aqui
|_static       # Conteúdo estático (imagens etc.)
```
