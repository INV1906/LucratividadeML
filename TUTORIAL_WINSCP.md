# 📁 TUTORIAL COMPLETO WINSCP

## 🎯 **O QUE É O WINSCP?**

O WinSCP é uma ferramenta gratuita para transferir arquivos entre seu computador Windows e servidores Linux (como sua instância EC2 na AWS).

---

## 📥 **PASSO 1: BAIXAR E INSTALAR WINSCP**

### **1.1: Acessar Site Oficial**
1. **Abra seu navegador**
2. **Acesse**: https://winscp.net/
3. **Clique em**: "Download" (Download)

### **1.2: Baixar Instalador**
1. **Clique em**: "Download WinSCP"
2. **Escolha**: "Installer" (Instalador)
3. **Aguarde** o download terminar

### **1.3: Instalar WinSCP**
1. **Execute** o arquivo baixado
2. **Aceite** os termos de licença
3. **Escolha**: "Typical installation" (Instalação típica)
4. **Clique em**: "Install" (Instalar)
5. **Aguarde** a instalação terminar
6. **Clique em**: "Finish" (Finalizar)

---

## 🔧 **PASSO 2: CONFIGURAR CONEXÃO**

### **2.1: Abrir WinSCP**
1. **Clique duas vezes** no ícone do WinSCP na área de trabalho
2. **Ou procure** "WinSCP" no menu Iniciar

### **2.2: Configurar Nova Conexão**
1. **Clique em**: "New Session" (Nova Sessão)
2. **Ou pressione**: Ctrl+N

### **2.3: Preencher Dados da Conexão**
```
File protocol: SFTP
Host name: SEU_IP_PUBLICO_DA_EC2
Port number: 22
User name: ec2-user
Password: (deixe vazio)
```

### **2.4: Configurar Chave SSH**
1. **Clique em**: "Advanced..." (Avançado...)
2. **Vá para**: "SSH" > "Authentication"
3. **Clique em**: "..." ao lado de "Private key file"
4. **Navegue** até onde salvou seu arquivo .pem
5. **Selecione** o arquivo .pem
6. **Clique em**: "Open" (Abrir)
7. **Clique em**: "OK"

### **2.5: Salvar Conexão**
1. **Clique em**: "Save..." (Salvar...)
2. **Nome da sessão**: "MercadoLivre AWS"
3. **Clique em**: "OK"

---

## 🔌 **PASSO 3: CONECTAR À EC2**

### **3.1: Estabelecer Conexão**
1. **Selecione** a sessão "MercadoLivre AWS"
2. **Clique em**: "Login" (Conectar)
3. **Aguarde** a conexão ser estabelecida

### **3.2: Aceitar Chave SSH (Primeira Vez)**
1. **Aparecerá** uma janela "Warning" (Aviso)
2. **Clique em**: "Yes" (Sim)
3. **Marque**: "Add host key to cache" (Adicionar chave ao cache)

---

## 📁 **PASSO 4: NAVEGAR PELOS ARQUIVOS**

### **4.1: Entender a Interface**
```
┌─────────────────────────────────────────────────────────────┐
│  WinSCP - MercadoLivre AWS                                 │
├─────────────────┬───────────────────────────────────────────┤
│  Local (Seu PC) │  Remote (Servidor AWS)                   │
│                 │                                           │
│  📁 Desktop     │  📁 /home/ec2-user                       │
│  📁 Documents   │  📁 /home/ec2-user/mercadolivre-app     │
│  📁 Downloads   │  📁 /var/log                             │
│  📁 ...         │  📁 /etc                                 │
└─────────────────┴───────────────────────────────────────────┘
```

### **4.2: Navegar no Servidor**
1. **Lado direito**: Arquivos do servidor AWS
2. **Navegue** até: `/home/ec2-user/mercadolivre-app`
3. **Clique duas vezes** nas pastas para entrar

### **4.3: Navegar no Seu PC**
1. **Lado esquerdo**: Arquivos do seu computador
2. **Navegue** até onde salvou o `mercadolivre_app_ec2.zip`

---

## 📤 **PASSO 5: FAZER UPLOAD DOS ARQUIVOS**

### **5.1: Selecionar Arquivo**
1. **No lado esquerdo** (seu PC): Encontre `mercadolivre_app_ec2.zip`
2. **Clique uma vez** para selecionar

### **5.2: Fazer Upload**
1. **Arraste** o arquivo do lado esquerdo para o lado direito
2. **Ou clique com botão direito** > "Upload" (Enviar)
3. **Ou pressione**: F5

### **5.3: Confirmar Upload**
1. **Aparecerá** uma janela de confirmação
2. **Clique em**: "OK"
3. **Aguarde** o upload terminar

### **5.4: Verificar Upload**
1. **Verifique** se o arquivo apareceu no servidor
2. **Deve estar** em `/home/ec2-user/mercadolivre-app/`

---

## 📋 **PASSO 6: COMANDOS ÚTEIS**

### **6.1: Criar Pasta**
1. **Clique com botão direito** no servidor
2. **Escolha**: "New" > "Directory" (Nova > Diretório)
3. **Digite** o nome da pasta

### **6.2: Renomear Arquivo**
1. **Clique com botão direito** no arquivo
2. **Escolha**: "Rename" (Renomear)
3. **Digite** o novo nome

### **6.3: Excluir Arquivo**
1. **Clique com botão direito** no arquivo
2. **Escolha**: "Delete" (Excluir)
3. **Confirme** a exclusão

### **6.4: Editar Arquivo**
1. **Clique duas vezes** no arquivo
2. **Escolha** um editor (Notepad, etc.)
3. **Faça** as alterações
4. **Salve** o arquivo

---

## 🔧 **PASSO 7: CONFIGURAÇÕES AVANÇADAS**

### **7.1: Configurar Editor Padrão**
1. **Vá em**: Options > Preferences (Opções > Preferências)
2. **Vá em**: Editors
3. **Clique em**: "Add..." (Adicionar...)
4. **Escolha** seu editor preferido (ex: Notepad++)

### **7.2: Configurar Transferência**
1. **Vá em**: Options > Preferences
2. **Vá em**: Transfer
3. **Configure**:
   - **Binary mode**: Para arquivos .zip, .exe, etc.
   - **Text mode**: Para arquivos .txt, .py, etc.

### **7.3: Configurar Interface**
1. **Vá em**: Options > Preferences
2. **Vá em**: Interface
3. **Configure**:
   - **Language**: Português (se disponível)
   - **Theme**: Escolha seu tema preferido

---

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **❌ Erro: "Connection refused"**
**Problema**: Não consegue conectar
**Solução**:
1. Verificar se a instância EC2 está rodando
2. Verificar se o Security Group tem porta 22 aberta
3. Verificar se o IP público está correto

### **❌ Erro: "Authentication failed"**
**Problema**: Erro de autenticação
**Solução**:
1. Verificar se o arquivo .pem está correto
2. Verificar se o usuário é "ec2-user"
3. Verificar se a chave SSH está configurada

### **❌ Erro: "Permission denied"**
**Problema**: Sem permissão para acessar pasta
**Solução**:
1. Verificar se está navegando para `/home/ec2-user/`
2. Verificar se a pasta existe
3. Verificar permissões da pasta

### **❌ Upload muito lento**
**Problema**: Transferência lenta
**Solução**:
1. Verificar conexão com internet
2. Verificar se não há outros uploads simultâneos
3. Tentar em horário de menor tráfego

---

## 📋 **CHECKLIST DE UPLOAD**

### **✅ Antes de Conectar**
- [ ] ✅ WinSCP instalado
- [ ] ✅ Arquivo .pem da chave SSH
- [ ] ✅ IP público da instância EC2
- [ ] ✅ Arquivo `mercadolivre_app_ec2.zip`

### **✅ Durante a Conexão**
- [ ] ✅ Protocolo SFTP
- [ ] ✅ Host name correto
- [ ] ✅ Usuário "ec2-user"
- [ ] ✅ Chave SSH configurada

### **✅ Após o Upload**
- [ ] ✅ Arquivo enviado com sucesso
- [ ] ✅ Arquivo aparece no servidor
- [ ] ✅ Conexão estável
- [ ] ✅ Pronto para próximos passos

---

## 🎯 **PRÓXIMOS PASSOS**

### **Após fazer upload do arquivo ZIP:**

1. **Conectar via SSH** para extrair arquivos
2. **Instalar dependências** Python
3. **Configurar serviços** (Nginx, systemd)
4. **Testar aplicação** no navegador

---

## 💡 **DICAS IMPORTANTES**

### **🔒 Segurança**
- **Nunca** compartilhe sua chave SSH
- **Sempre** desconecte após usar
- **Mantenha** o WinSCP atualizado

### **⚡ Performance**
- **Feche** outros programas durante upload
- **Use** conexão estável (cabo ethernet)
- **Evite** uploads simultâneos

### **📁 Organização**
- **Mantenha** arquivos organizados
- **Use** nomes descritivos
- **Faça backup** dos arquivos importantes

---

## 🎉 **RESUMO**

### **✅ O que você aprendeu:**
1. **Instalar** WinSCP
2. **Configurar** conexão com AWS
3. **Navegar** pelos arquivos
4. **Fazer upload** de arquivos
5. **Resolver** problemas comuns

### **🚀 Agora você pode:**
- **Conectar** à sua instância EC2
- **Transferir** arquivos facilmente
- **Gerenciar** arquivos no servidor
- **Configurar** sua aplicação

**Pronto para fazer upload da sua aplicação!** 🎉
