
# CloneChat Bot - Telegram Bot Version

Bot do Telegram para clonagem de chats usando Telethon, mantendo todas as funcionalidades do projeto original.

## 🚀 Funcionalidades

- **Clonagem completa** de chats/canais
- **Conteúdo protegido** - Download e upload
- **Filtros de conteúdo** - Escolha quais tipos clonar
- **Interface amigável** - Comandos simples via bot
- **Continuação de tarefas** - Retoma clonagens interrompidas
- **Status em tempo real** - Acompanhe o progresso

## 📋 Comandos Disponíveis

- `/start` - Inicializar bot
- `/help` - Mostrar ajuda
- `/clone` - Iniciar clonagem de chat
- `/protect_download` - Download de conteúdo protegido
- `/protect_upload` - Upload de conteúdo protegido  
- `/status` - Ver status das tarefas
- `/stop` - Parar tarefa ativa

## ⚙️ Configuração no Replit

### 1. Variáveis de Ambiente (Secrets)

Configure estas variáveis no painel **Secrets**:

- `BOT_TOKEN` - Token do seu bot (obtido com @BotFather)
- `API_ID` - ID da API do Telegram
- `API_HASH` - Hash da API do Telegram

### 2. Como obter as credenciais:

**Bot Token:**
1. Fale com [@BotFather](https://t.me/botfather) no Telegram
2. Use `/newbot` e siga as instruções
3. Copie o token gerado

**API ID e Hash:**
1. Acesse [my.telegram.org](https://my.telegram.org)
2. Faça login com seu número
3. Vá em "API development tools"
4. Crie um novo app
5. Copie `api_id` e `api_hash`

## 🎯 Como Usar

1. **Inicie uma conversa** com seu bot no Telegram
2. **Digite `/start`** para inicializar
3. **Use `/clone`** para começar uma clonagem
4. **Siga as instruções** do bot passo a passo

### Processo de Clonagem:

1. **Login** - Forneça seu número de telefone
2. **Código** - Digite o código de verificação
3. **Origem** - ID/username do chat origem
4. **Destino** - ID/username do chat destino  
5. **Tipos** - Escolha quais conteúdos clonar
6. **Aguarde** - O bot fará o resto!

## 🛡️ Conteúdo Protegido

Para chats com proteção contra encaminhamento:

1. **Use `/protect_download`** para baixar o conteúdo
2. **Use `/protect_upload`** para enviar para destino

## 📊 Monitoramento

- **Status em tempo real** com `/status`
- **Controle total** - pare com `/stop`
- **Cache inteligente** - continua de onde parou

## 🔧 Configurações Avançadas

Edite `user/config.ini` para ajustar:

- `user_delay_seconds` - Delay entre mensagens (usuário)
- `bot_delay_seconds` - Delay entre mensagens (bot)
- `skip_delay_seconds` - Delay para mensagens ignoradas
- `max_retries` - Tentativas em caso de erro

## ⚡ Deploy no Replit

1. **Clone este repositório**
2. **Configure as variáveis** no Secrets
3. **Clique em Run** 
4. **Seu bot estará online!**

## 📝 Suporte

- Todos os tipos de mídia suportados
- Filtros personalizáveis
- Resistente a flood wait
- Recuperação automática de erros

---

**Desenvolvido com ❤️ usando Telethon**
