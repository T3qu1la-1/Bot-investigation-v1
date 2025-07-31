
import os
import json
import time
import asyncio
from pathlib import Path
from configparser import ConfigParser
from telethon import TelegramClient, events, Button
from telethon.errors import ChannelInvalidError, FloodWaitError, PeerIdInvalidError
from telethon.tl.types import InputPeerChannel, InputPeerChat, InputPeerUser
from setup import version

class CloneChatBot:
    def __init__(self):
        self.config = self.get_config_data()
        self.bot = None
        self.user_sessions = {}
        self.active_tasks = {}
        
    def get_config_data(self):
        """Carrega configurações do arquivo config.ini"""
        config_file = ConfigParser()
        config_file.read(os.path.join("user", "config.ini"))
        return dict(config_file["default"])
    
    async def start_bot(self):
        """Inicia o bot do Telegram"""
        # Credenciais configuradas diretamente no código
        api_id = 25317254
        api_hash = 'bef2f48bb6b4120c9189ecfd974eb820'
        bot_token = '8375395762:AAG_wTWCaQuGKq4zO_DtuSFfmOBuc8sewQY'
            
        self.bot = TelegramClient('bot', api_id, api_hash)
        
        await self.bot.start(bot_token=bot_token)
        print(f"Bot CloneChat v{version} iniciado!")
        
        # Registrar handlers de comandos
        self.register_handlers()
        
        # Manter o bot rodando
        await self.bot.run_until_disconnected()
    
    def register_handlers(self):
        """Registra todos os handlers de comandos do bot"""
        
        @self.bot.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await self.start_command(event)
        
        @self.bot.on(events.NewMessage(pattern='/help'))
        async def help_handler(event):
            await self.help_command(event)
        
        @self.bot.on(events.NewMessage(pattern='/clone'))
        async def clone_handler(event):
            await self.clone_command(event)
        
        @self.bot.on(events.NewMessage(pattern='/status'))
        async def status_handler(event):
            await self.status_command(event)
        
        @self.bot.on(events.NewMessage(pattern='/stop'))
        async def stop_handler(event):
            await self.stop_command(event)
        
        @self.bot.on(events.NewMessage(pattern='/protect_download'))
        async def protect_download_handler(event):
            await self.protect_download_command(event)
        
        @self.bot.on(events.NewMessage(pattern='/protect_upload'))
        async def protect_upload_handler(event):
            await self.protect_upload_command(event)
        
        @self.bot.on(events.CallbackQuery)
        async def callback_handler(event):
            await self.handle_callback(event)
        
        # Handler para mensagens não-comando
        @self.bot.on(events.NewMessage)
        async def message_handler(event):
            if not event.is_private:
                return
            
            if event.raw_text and event.raw_text.startswith('/'):
                return
            
            await self.process_message(event)
    
    async def start_command(self, event):
        """Comando /start"""
        user_id = event.sender_id
        welcome_msg = f"""
🤖 **CloneChat Bot v{version}**

Bem-vindo ao CloneChat Bot! Eu posso ajudá-lo a clonar chats do Telegram.

**Comandos disponíveis:**
/help - Mostrar ajuda
/clone - Iniciar clonagem de chat
/protect_download - Download de chat protegido
/protect_upload - Upload de chat protegido
/status - Ver status das tarefas
/stop - Parar tarefa ativa

Use /help para mais detalhes sobre cada comando.
        """
        await event.respond(welcome_msg, parse_mode='md')
    
    async def help_command(self, event):
        """Comando /help"""
        help_msg = """
📖 **Ajuda do CloneChat Bot**

**Comandos principais:**

🔄 `/clone` - Clona mensagens de um chat para outro
• Suporta todos os tipos de mídia
• Permite filtrar por tipo de conteúdo
• Pode continuar clonagem interrompida

🛡️ `/protect_download` - Baixa conteúdo de chats protegidos
• Para chats com conteúdo protegido
• Salva localmente para posterior upload

📤 `/protect_upload` - Faz upload de conteúdo baixado
• Complemento do protect_download
• Envia conteúdo para chat de destino

📊 `/status` - Mostra status das tarefas ativas
⏹️ `/stop` - Para tarefa em execução

**Tipos de conteúdo suportados:**
• Fotos • Textos • Documentos • Stickers
• Animações • Áudios • Voz • Vídeos • Enquetes
        """
        await event.respond(help_msg, parse_mode='md')
    
    async def clone_command(self, event):
        """Comando /clone - Inicia processo de clonagem"""
        user_id = event.sender_id
        
        if user_id in self.active_tasks:
            await event.respond("❌ Você já tem uma tarefa ativa. Use /stop para cancelar.")
            return
        
        # Verificar se usuário tem sessão ativa
        if user_id not in self.user_sessions:
            await event.respond(
                "📱 Primeiro você precisa fazer login com sua conta do Telegram.\n"
                "Envie seu **phone number** no formato internacional (ex: +5511999999999)",
                parse_mode='md'
            )
            self.user_sessions[user_id] = {'step': 'phone'}
            return
        
        # Iniciar processo de clonagem
        await self.start_clone_process(event, user_id)
    
    async def start_clone_process(self, event, user_id):
        """Inicia o processo de clonagem"""
        await event.respond(
            "🔄 **Iniciando Clonagem**\n\n"
            "Envie o **ID do chat de origem** (número ou @username):",
            parse_mode='md'
        )
        self.user_sessions[user_id] = {'step': 'origin_chat'}
    
    async def protect_download_command(self, event):
        """Comando para download de conteúdo protegido"""
        user_id = event.sender_id
        
        await event.respond(
            "🛡️ **Download de Conteúdo Protegido**\n\n"
            "Esta função baixa conteúdo de chats com proteção.\n"
            "Envie o **link da mensagem** ou **ID do chat**:",
            parse_mode='md'
        )
        self.user_sessions[user_id] = {'step': 'protect_download'}
    
    async def protect_upload_command(self, event):
        """Comando para upload de conteúdo protegido"""
        user_id = event.sender_id
        
        await event.respond(
            "📤 **Upload de Conteúdo Protegido**\n\n"
            "Esta função envia conteúdo baixado anteriormente.\n"
            "Envie o **ID do chat de destino**:",
            parse_mode='md'
        )
        self.user_sessions[user_id] = {'step': 'protect_upload'}
    
    async def status_command(self, event):
        """Comando /status - Mostra status das tarefas"""
        user_id = event.sender_id
        
        if user_id not in self.active_tasks:
            await event.respond("📊 Nenhuma tarefa ativa no momento.")
            return
        
        task = self.active_tasks[user_id]
        status_msg = f"""
📊 **Status da Tarefa**

🎯 Origem: {task.get('origin_title', 'N/A')}
📤 Destino: {task.get('dest_title', 'N/A')}
📊 Progresso: {task.get('current', 0)}/{task.get('total', 0)}
⏱️ Iniciado: {task.get('start_time', 'N/A')}
        """
        await event.respond(status_msg, parse_mode='md')
    
    async def stop_command(self, event):
        """Comando /stop - Para tarefa ativa"""
        user_id = event.sender_id
        
        if user_id in self.active_tasks:
            del self.active_tasks[user_id]
            await event.respond("⏹️ Tarefa cancelada com sucesso!")
        else:
            await event.respond("❌ Nenhuma tarefa ativa para cancelar.")
    
    async def handle_callback(self, event):
        """Manipula callbacks de botões inline"""
        data = event.data.decode('utf-8')
        user_id = event.sender_id
        
        if data.startswith('type_'):
            # Seleção de tipos de arquivo
            selected_types = data.replace('type_', '').split(',')
            await self.process_file_types(event, user_id, selected_types)
    
    async def process_message(self, event):
        """Processa mensagens baseado no estado do usuário"""
        user_id = event.sender_id
        text = event.raw_text
        
        if user_id not in self.user_sessions:
            return
        
        session = self.user_sessions[user_id]
        step = session.get('step')
        
        if step == 'phone':
            await self.handle_phone_step(event, user_id, text)
        elif step == 'code':
            await self.handle_code_step(event, user_id, text)
        elif step == 'password':
            await self.handle_password_step(event, user_id, text)
        elif step == 'origin_chat':
            await self.handle_origin_chat_step(event, user_id, text)
        elif step == 'dest_chat':
            await self.handle_dest_chat_step(event, user_id, text)
        elif step == 'file_types':
            await self.handle_file_types_step(event, user_id, text)
    
    async def handle_phone_step(self, event, user_id, phone):
        """Manipula entrada do telefone"""
        try:
            # Limpar sessão anterior se existir
            if user_id in self.user_sessions and 'client' in self.user_sessions[user_id]:
                try:
                    await self.user_sessions[user_id]['client'].disconnect()
                except:
                    pass
            
            # Criar cliente do usuário
            api_id = 25317254
            api_hash = 'bef2f48bb6b4120c9189ecfd974eb820'
            client = TelegramClient(f'user_{user_id}', api_id, api_hash)
            
            await client.connect()
            
            # Configurar timeout mais longo para evitar expiração rápida
            result = await client.send_code_request(phone, force_sms=False)
            
            # Salvar timestamp para controlar expiração
            import time
            self.user_sessions[user_id].update({
                'step': 'code',
                'phone': phone,
                'client': client,
                'phone_code_hash': result.phone_code_hash,
                'code_sent_time': time.time(),
                'attempts': 0
            })
            
            await event.respond(
                "📱 **Código enviado com sucesso!**\n\n"
                "🔢 Digite o código de verificação recebido no Telegram\n"
                "⏱️ **Tempo:** Você tem até **5 minutos** para usar o código\n"
                "📝 **Formato:** Digite apenas os números (ex: 12345)\n\n"
                "⚠️ **IMPORTANTE:**\n"
                "• **Aguarde pelo menos 30 segundos** antes de digitar\n"
                "• **Use apenas este código** (não reutilize antigos)\n"
                "• **Digite com calma** para evitar bloqueios\n\n"
                "💡 **Se der erro:** Use `/clone` para solicitar novo código",
                parse_mode='md'
            )
            
        except Exception as e:
            await event.respond(
                f"❌ **Erro ao enviar código:** {str(e)}\n\n"
                "💡 **Possíveis soluções:**\n"
                "• Verifique o formato: +5511999999999\n"
                "• Aguarde 1 minuto antes de tentar novamente\n"
                "• Certifique-se que o número está correto\n"
                "• Verifique se sua conta não está suspensa",
                parse_mode='md'
            )
    
    async def handle_code_step(self, event, user_id, code):
        """Manipula entrada do código de verificação"""
        try:
            session = self.user_sessions[user_id]
            client = session['client']
            
            await client.sign_in(
                session['phone'], 
                code, 
                phone_code_hash=session['phone_code_hash']
            )
            
            session.update({
                'step': 'ready',
                'authenticated': True
            })
            
            await event.respond(
                "✅ Login realizado com sucesso!\n"
                "Agora você pode usar /clone para iniciar a clonagem.",
                parse_mode='md'
            )
            
        except Exception as e:
            error_msg = str(e).lower()
            session = self.user_sessions[user_id]
            
            if "expired" in error_msg or "confirmation code" in error_msg or "invalid" in error_msg:
                # Verificar quantas tentativas já foram feitas
                attempts = session.get('attempts', 0) + 1
                session['attempts'] = attempts
                
                if attempts >= 3:
                    # Muitas tentativas - resetar completamente
                    await event.respond(
                        "🔄 **Muitas tentativas falharam**\n\n"
                        "Vou resetar o processo de login.\n"
                        "Use `/clone` novamente para recomeçar:",
                        parse_mode='md'
                    )
                    del self.user_sessions[user_id]
                else:
                    # Solicitar novo código automaticamente
                    await event.respond(
                        f"⏰ **Código inválido ou expirado** (Tentativa {attempts}/3)\n\n"
                        "🔄 Solicitando novo código automaticamente...",
                        parse_mode='md'
                    )
                    
                    try:
                        # Solicitar novo código
                        result = await session['client'].send_code_request(session['phone'])
                        session['phone_code_hash'] = result.phone_code_hash
                        session['code_sent_time'] = time.time()
                        
                        await event.respond(
                            "📱 **Novo código enviado!**\n\n"
                            "Digite o novo código de verificação:",
                            parse_mode='md'
                        )
                    except Exception as retry_error:
                        await event.respond(
                            f"❌ **Erro ao solicitar novo código:** {str(retry_error)}\n\n"
                            "Use `/clone` para recomeçar o processo.",
                            parse_mode='md'
                        )
                        del self.user_sessions[user_id]
                        
            elif "password" in error_msg or "2fa" in error_msg or "two" in error_msg:
                # Conta tem 2FA - solicitar senha
                await event.respond(
                    "🔐 **Autenticação de Dois Fatores Detectada**\n\n"
                    "Sua conta tem senha de 2FA ativada.\n"
                    "Digite sua **senha de 2FA**:",
                    parse_mode='md'
                )
                session['step'] = 'password'
            elif "shared" in error_msg or "previously" in error_msg or "block" in error_msg:
                # Código foi reutilizado ou login bloqueado
                await event.respond(
                    "🚫 **Login Bloqueado pelo Telegram**\n\n"
                    "⚠️ **Motivo:** Código reutilizado ou login muito rápido\n\n"
                    "🔧 **Como resolver:**\n"
                    "• Aguarde **5 minutos** antes de tentar novamente\n"
                    "• Use `/clone` para solicitar **novo código**\n"
                    "• **NÃO reutilize** códigos anteriores\n"
                    "• Digite o código com **calma** (aguarde 30s)\n\n"
                    "🛡️ **Dica de Segurança:** Nunca compartilhe códigos de login!",
                    parse_mode='md'
                )
                # Resetar sessão completamente
                del self.user_sessions[user_id]
            else:
                await event.respond(
                    f"❌ **Erro no login:** {str(e)}\n\n"
                    "💡 **Soluções:**\n"
                    "• Verifique se digitou apenas números\n"
                    "• Use o código mais recente\n"
                    "• Aguarde receber novo código\n"
                    "• Use `/clone` para recomeçar\n\n"
                    f"**Tentativa:** {session.get('attempts', 0)}/3",
                    parse_mode='md'
                )
    
    async def handle_password_step(self, event, user_id, password):
        """Manipula entrada da senha de 2FA"""
        try:
            session = self.user_sessions[user_id]
            client = session['client']
            
            await client.check_password(password)
            
            session.update({
                'step': 'ready',
                'authenticated': True
            })
            
            await event.respond(
                "✅ **Login realizado com sucesso!**\n\n"
                "🔐 Autenticação de 2FA confirmada!\n"
                "Agora você pode usar /clone para iniciar a clonagem.",
                parse_mode='md'
            )
            
        except Exception as e:
            await event.respond(
                f"❌ **Erro na senha de 2FA:** {str(e)}\n\n"
                "💡 **Dicas:**\n"
                "• Verifique se a senha está correta\n"
                "• É a mesma senha usada no app do Telegram\n"
                "• Tente digitar novamente\n\n"
                "Digite sua senha de 2FA novamente:",
                parse_mode='md'
            )
    
    async def handle_origin_chat_step(self, event, user_id, chat_input):
        """Manipula entrada do chat de origem"""
        try:
            session = self.user_sessions[user_id]
            client = session['client']
            
            # Verificar se o chat existe e é acessível
            entity = await client.get_entity(chat_input)
            
            session.update({
                'step': 'dest_chat',
                'origin_chat': entity,
                'origin_id': entity.id,
                'origin_title': getattr(entity, 'title', str(entity.id))
            })
            
            await event.respond(
                f"✅ Chat de origem: **{session['origin_title']}**\n\n"
                "Agora envie o **ID do chat de destino**:",
                parse_mode='md'
            )
            
        except Exception as e:
            await event.respond(f"❌ Erro ao acessar chat de origem: {str(e)}")
    
    async def handle_dest_chat_step(self, event, user_id, chat_input):
        """Manipula entrada do chat de destino"""
        try:
            session = self.user_sessions[user_id]
            client = session['client']
            
            # Verificar se o chat existe e é acessível
            entity = await client.get_entity(chat_input)
            
            session.update({
                'step': 'file_types',
                'dest_chat': entity,
                'dest_id': entity.id,
                'dest_title': getattr(entity, 'title', str(entity.id))
            })
            
            # Mostrar opções de tipos de arquivo
            await self.show_file_type_options(event, user_id)
            
        except Exception as e:
            await event.respond(f"❌ Erro ao acessar chat de destino: {str(e)}")
    
    async def show_file_type_options(self, event, user_id):
        """Mostra opções de tipos de arquivo para clonar"""
        buttons = [
            [Button.inline("📷 Todos os arquivos", b"type_all")],
            [Button.inline("🖼️ Fotos", b"type_photo"), Button.inline("📝 Textos", b"type_text")],
            [Button.inline("📄 Documentos", b"type_document"), Button.inline("😀 Stickers", b"type_sticker")],
            [Button.inline("🎬 Animações", b"type_animation"), Button.inline("🎵 Áudios", b"type_audio")],
            [Button.inline("🎤 Voz", b"type_voice"), Button.inline("🎥 Vídeos", b"type_video")],
            [Button.inline("📊 Enquetes", b"type_poll")]
        ]
        
        await event.respond(
            "📋 **Selecione os tipos de conteúdo para clonar:**",
            buttons=buttons,
            parse_mode='md'
        )
    
    async def process_file_types(self, event, user_id, selected_types):
        """Processa tipos de arquivo selecionados e inicia clonagem"""
        session = self.user_sessions[user_id]
        
        if 'all' in selected_types:
            file_types_excluded = []
        else:
            # Mapear tipos excluídos
            all_types = ['photo', 'text', 'document', 'sticker', 'animation', 'audio', 'voice', 'video', 'poll']
            file_types_excluded = [t for t in all_types if t not in selected_types]
        
        session['file_types_excluded'] = file_types_excluded
        
        await event.edit(
            f"🚀 **Iniciando clonagem...**\n\n"
            f"📥 Origem: {session['origin_title']}\n"
            f"📤 Destino: {session['dest_title']}\n"
            f"📋 Tipos: {', '.join(selected_types) if 'all' not in selected_types else 'Todos'}",
            parse_mode='md'
        )
        
        # Iniciar tarefa de clonagem
        task = asyncio.create_task(self.start_cloning_task(user_id, session))
        self.active_tasks[user_id] = {
            'task': task,
            'origin_title': session['origin_title'],
            'dest_title': session['dest_title'],
            'start_time': time.strftime('%H:%M:%S'),
            'current': 0,
            'total': 0
        }
    
    async def start_cloning_task(self, user_id, session):
        """Executa a tarefa de clonagem"""
        try:
            client = session['client']
            origin_chat = session['origin_chat']
            dest_chat = session['dest_chat']
            file_types_excluded = session.get('file_types_excluded', [])
            
            # Obter cache de mensagens processadas
            cache_file = f"cache_{user_id}_{session['origin_id']}_{session['dest_id']}.json"
            posted_messages = self.load_cache(cache_file)
            
            # Contar total de mensagens
            total_messages = 0
            async for message in client.iter_messages(origin_chat):
                total_messages += 1
            
            self.active_tasks[user_id]['total'] = total_messages
            
            # Processar mensagens
            processed = 0
            async for message in client.iter_messages(origin_chat):
                if user_id not in self.active_tasks:
                    break  # Tarefa foi cancelada
                
                if message.id in posted_messages:
                    continue
                
                if await self.should_skip_message(message, file_types_excluded):
                    posted_messages.append(message.id)
                    continue
                
                try:
                    await self.forward_message(client, message, dest_chat)
                    posted_messages.append(message.id)
                    processed += 1
                    
                    self.active_tasks[user_id]['current'] = processed
                    
                    # Salvar cache periodicamente
                    if processed % 10 == 0:
                        self.save_cache(cache_file, posted_messages)
                    
                    # Delay para evitar flood
                    await asyncio.sleep(float(self.config.get('user_delay_seconds', 1)))
                    
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    print(f"Erro ao processar mensagem {message.id}: {e}")
                    continue
            
            # Finalizar
            self.save_cache(cache_file, posted_messages)
            if user_id in self.active_tasks:
                del self.active_tasks[user_id]
            
            await self.bot.send_message(
                user_id, 
                f"✅ **Clonagem concluída!**\n\n"
                f"📊 Mensagens processadas: {processed}\n"
                f"⏱️ Tempo total: {time.strftime('%H:%M:%S')}",
                parse_mode='md'
            )
            
        except Exception as e:
            await self.bot.send_message(
                user_id, 
                f"❌ **Erro na clonagem:** {str(e)}",
                parse_mode='md'
            )
            if user_id in self.active_tasks:
                del self.active_tasks[user_id]
    
    async def should_skip_message(self, message, file_types_excluded):
        """Verifica se mensagem deve ser ignorada"""
        if not message or message.empty or message.service:
            return True
        
        if message.photo and 'photo' in file_types_excluded:
            return True
        if message.text and 'text' in file_types_excluded:
            return True
        if message.document and 'document' in file_types_excluded:
            return True
        if message.sticker and 'sticker' in file_types_excluded:
            return True
        if message.gif and 'animation' in file_types_excluded:
            return True
        if message.audio and 'audio' in file_types_excluded:
            return True
        if message.voice and 'voice' in file_types_excluded:
            return True
        if message.video and 'video' in file_types_excluded:
            return True
        if message.poll and 'poll' in file_types_excluded:
            return True
        
        return False
    
    async def forward_message(self, client, message, dest_chat):
        """Encaminha mensagem para chat de destino"""
        try:
            await client.forward_messages(dest_chat, message)
        except Exception:
            # Se forward falhar, tentar enviar cópia
            if message.text:
                await client.send_message(dest_chat, message.text)
            elif message.photo:
                await client.send_file(dest_chat, message.photo, caption=message.message)
            elif message.document:
                await client.send_file(dest_chat, message.document, caption=message.message)
            elif message.video:
                await client.send_file(dest_chat, message.video, caption=message.message)
            elif message.audio:
                await client.send_file(dest_chat, message.audio, caption=message.message)
            elif message.voice:
                await client.send_file(dest_chat, message.voice)
            elif message.sticker:
                await client.send_file(dest_chat, message.sticker)
    
    def load_cache(self, filename):
        """Carrega cache de mensagens processadas"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_cache(self, filename, data):
        """Salva cache de mensagens processadas"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")

# Instância global do bot
bot_instance = CloneChatBot()

async def main():
    """Função principal"""
    await bot_instance.start_bot()

if __name__ == '__main__':
    asyncio.run(main())
