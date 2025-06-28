
# Sistema de Gestão de Contas Pessoais

Um sistema web completo para gestão e controle de contas pessoais, desenvolvido em Flask com interface responsiva usando Bootstrap.

## 📋 Índice

- [Características](#características)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Como Executar](#como-executar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Funcionalidades](#funcionalidades)
- [Como Hospedar no Replit](#como-hospedar-no-replit)
- [API Endpoints](#api-endpoints)
- [Contribuição](#contribuição)
- [Licença](#licença)

## 🚀 Características

- **Interface Responsiva**: Desenvolvida com Bootstrap 5
- **Importação de Dados**: Suporte a arquivos CSV e Excel
- **Gestão de Fontes**: Cadastro e gerenciamento de fontes de despesas
- **Rateio Inteligente**: Divisão automática de despesas entre pessoas
- **Controle de Pagamentos**: Acompanhamento individual de quitações
- **Relatórios**: Exportação de dados em CSV
- **Tratamento de Erros**: Sistema robusto de validação e tratamento de erros

## 💻 Tecnologias Utilizadas

### Backend
- **Flask** (3.0.x) - Framework web Python
- **Pandas** (2.0.x) - Manipulação de dados
- **OpenPyXL** (3.1.x) - Leitura de arquivos Excel
- **MSOffCrypto-tool** (5.0.x) - Descriptografia de arquivos Office

### Frontend
- **Bootstrap** (5.3.0) - Framework CSS
- **jQuery** (3.7.0) - Biblioteca JavaScript
- **DataTables** (1.13.4) - Tabelas interativas
- **Bootstrap Icons** (1.10.0) - Ícones
- **Notiflix** (3.2.6) - Notificações e modais

### Ferramentas de Desenvolvimento
- **Python** (3.8+)
- **HTML5/CSS3**
- **JavaScript ES6+**

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno

## ⚙️ Instalação e Configuração

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd sistema-gestao-contas
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Estrutura de diretórios
O sistema criará automaticamente os diretórios necessários:
```
data/           # Arquivos JSON de dados
temp/           # Arquivos temporários
logs/           # Logs da aplicação
uploads/        # Arquivos enviados
```

## 🚀 Como Executar

### Desenvolvimento Local
```bash
python app.py
```

O sistema estará disponível em: `http://localhost:5000`

### Produção
```bash
python app.py
```

## 📁 Estrutura do Projeto

```
sistema-gestao-contas/
├── app.py                 # Aplicação principal Flask
├── config.py              # Configurações
├── requirements.txt       # Dependências Python
├── README.md             # Documentação
├── data/                 # Dados JSON
│   ├── fontes.json       # Fontes de despesas
│   ├── transacoes.json   # Transações importadas
│   ├── revisoes.json     # Revisões aprovadas
│   └── pendentes.json    # Transações pendentes
├── services/             # Serviços de negócio
│   └── importador.py     # Importação de arquivos
├── utils/                # Utilitários
│   ├── hash.py          # Geração de hashes
│   └── error_handler.py  # Tratamento de erros
├── static/               # Arquivos estáticos
│   ├── css/
│   │   └── style.css    # Estilos personalizados
│   └── js/
│       └── app.js       # JavaScript personalizado
├── templates/            # Templates HTML
│   ├── base.html        # Template base
│   ├── upload.html      # Upload de arquivos
│   ├── fontes.html      # Gestão de fontes
│   ├── pendentes.html   # Revisão de transações
│   ├── rateio.html      # Rateio de despesas
│   ├── pagamentos.html  # Controle de pagamentos
│   ├── listagens.html   # Listagens e relatórios
│   └── nova_despesa.html # Cadastro manual
├── logs/                 # Logs da aplicação
└── temp/                # Arquivos temporários
```

## 🎯 Funcionalidades

### 1. Upload e Importação
- Importação de arquivos CSV e Excel
- Mapeamento flexível de colunas
- Validação automática de dados
- Detecção de duplicatas por hash

### 2. Gestão de Fontes
- Cadastro de fontes de despesas
- Edição e exclusão de fontes
- Integração com importação de dados

### 3. Revisão de Transações
- Lista de transações pendentes
- Edição de descrições
- Definição de percentuais de rateio
- Aprovação ou exclusão de transações

### 4. Rateio de Despesas
- Visualização por pessoa
- Filtros por data e status
- Cálculo de saldos entre pessoas
- Indicadores visuais de pendências

### 5. Controle de Pagamentos
- Quitação individual por pessoa
- Filtros avançados
- Quitação em lote
- Histórico de pagamentos

### 6. Relatórios e Exportação
- Listagens detalhadas
- Exportação em CSV
- Filtros personalizáveis
- Resumos financeiros

## 🌐 Como Hospedar no Replit

### Passo 1: Preparação do Projeto
1. Acesse [Replit.com](https://replit.com) e faça login
2. Clique em "Create Repl"
3. Selecione "Python" como linguagem
4. Nomeie seu projeto (ex: "gestao-contas-pessoais")

### Passo 2: Upload dos Arquivos
1. Faça upload de todos os arquivos do projeto para o Repl
2. Certifique-se de que a estrutura de diretórios está correta
3. Verifique se o `requirements.txt` está presente

### Passo 3: Configuração do Ambiente
1. O Replit detectará automaticamente as dependências do `requirements.txt`
2. As dependências serão instaladas automaticamente

### Passo 4: Configuração de Execução
1. No arquivo principal `app.py`, certifique-se de que está configurado para:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Passo 5: Execução
1. Clique no botão "Run" no Replit
2. O sistema será executado em `https://seu-projeto.nome-usuario.repl.co`

### Passo 6: Configuração de Domínio (Opcional)
1. No painel do Replit, vá para a aba "Deployments"
2. Configure um domínio personalizado se desejar
3. Configure variáveis de ambiente se necessário

### Variáveis de Ambiente Recomendadas
```
SECRET_KEY=sua_chave_secreta_super_segura_aqui
FLASK_ENV=production
```

### Considerações Importantes para Replit
- **Persistência**: Os dados em `data/` são persistentes no Replit
- **Recursos**: Monitore o uso de CPU e memória
- **Logs**: Os logs ficam disponíveis no console do Replit
- **HTTPS**: O Replit fornece HTTPS automaticamente
- **Domínio**: Você recebe um domínio gratuito .repl.co

### Monitoramento no Replit
1. **Console**: Visualize logs em tempo real
2. **Recursos**: Monitore CPU e memória na aba "Resources"
3. **Analytics**: Acompanhe acessos na aba "Analytics"

### Backup dos Dados
É recomendado fazer backup regular dos arquivos em `data/`:
1. Baixe os arquivos JSON periodicamente
2. Configure um repositório Git para versionamento
3. Use a exportação CSV para backup dos dados processados

## 🔧 API Endpoints

### Gestão de Fontes
- `GET /fontes` - Listar fontes
- `POST /salvar_fonte` - Criar nova fonte
- `POST /editar_fonte` - Editar fonte
- `POST /excluir_fonte` - Excluir fonte

### Upload e Importação
- `GET /upload` - Página de upload
- `POST /process_upload` - Processar arquivo
- `GET /mapear_colunas` - Mapear colunas
- `POST /processar_mapeamento` - Processar mapeamento

### Gestão de Transações
- `GET /pendentes` - Transações pendentes
- `POST /salvar_revisao` - Salvar revisão
- `POST /excluir_pendente` - Excluir pendente
- `POST /salvar_nova_despesa` - Nova despesa manual

### Relatórios
- `GET /rateio` - Rateio de despesas
- `GET /pagamentos` - Controle de pagamentos
- `GET /listagens` - Listagens detalhadas
- `GET /exportar_listagem_csv` - Exportar CSV
- `POST /atualizar_status_pagamento` - Atualizar status
- `POST /quitar_em_lote` - Quitação em lote

## 📊 Formato dos Dados

### Estrutura de Transações
```json
{
  "id": "string",
  "tipo": "string",
  "data": "YYYY-MM-DD",
  "descricao": "string",
  "valor": "float",
  "tipo_movimento": "entrada|saida",
  "fonte": "string",
  "hash": "string",
  "observacoes": "string"
}
```

### Estrutura de Revisões
```json
{
  "hash": "string",
  "id_original": "string",
  "nova_descricao": "string",
  "donos": {
    "pessoa1": "percentual",
    "pessoa2": "percentual"
  },
  "comentarios": "string",
  "pago_por": "string",
  "quitado": "boolean",
  "quitacao_individual": {
    "pessoa1": "boolean",
    "pessoa2": "boolean"
  },
  "data_revisao": "ISO datetime",
  "revisado_por": "string"
}
```

## 🤝 Contribuição

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Changelog

### Versão 1.0.0
- Sistema básico de gestão de contas
- Importação de arquivos CSV/Excel
- Gestão de fontes e rateio
- Controle de pagamentos

## 🔒 Segurança

- Validação de entrada em todos os endpoints
- Sanitização de dados de upload
- Logs de auditoria
- Tratamento seguro de arquivos temporários

## 📞 Suporte

Para suporte técnico ou dúvidas:
1. Abra uma issue no repositório
2. Consulte a documentação
3. Verifique os logs da aplicação

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido com ❤️ para simplificar a gestão de contas pessoais**
