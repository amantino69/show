# 🚨 **TROUBLESHOOTING - Computador não acessa URL do Ngrok**

## 🔍 **DIAGNÓSTICO RÁPIDO**

### **Primeiro, vamos identificar o problema:**

#### **1. Teste básico de conectividade:**
```bash
# No computador que NÃO consegue acessar:
ping google.com
ping 8.8.8.8
```

#### **2. Teste a URL do ngrok:**
```bash
# No prompt/terminal:
curl -I https://abc123.ngrok.io
# OU no PowerShell:
Invoke-WebRequest -Uri "https://abc123.ngrok.io" -Method Head
```

---

## 🛡️ **CAUSAS MAIS COMUNS:**

### **1. FIREWALL CORPORATIVO/ANTIVÍRUS**

#### **Sintomas:**
- Outros sites funcionam normalmente
- Erro: "Conexão recusada" ou "Site não pode ser acessado"
- Timeout na conexão

#### **Soluções:**
```bash
# A) Desabilitar firewall temporariamente (teste):
# Windows: Painel de Controle > Sistema e Segurança > Firewall do Windows
# Desativar temporariamente e testar

# B) Adicionar exceção para ngrok:
# Firewall > Permitir app através do firewall
# Adicionar: navegadores (Chrome, Firefox, Edge)
```

#### **Antivírus (Kaspersky, McAfee, etc.):**
- Desabilitar "Proteção Web" temporariamente
- Adicionar `*.ngrok.io` à lista de sites confiáveis

### **2. PROXY CORPORATIVO**

#### **Sintomas:**
- Empresa/escola/universidade
- Outros sites externos às vezes não funcionam
- Erro: "Proxy authentication required"

#### **Soluções:**
```bash
# A) Verificar configurações de proxy:
# Windows: Configurações > Rede e Internet > Proxy

# B) Configurar proxy no navegador:
# Chrome: Configurações > Avançado > Sistema > Abrir configurações do proxy

# C) Usar VPN como alternativa
```

### **3. DNS/BLOQUEIO DE REDE**

#### **Sintomas:**
- Site "não encontrado" ou "DNS não resolvido"
- Funciona em outros computadores da mesma rede

#### **Soluções:**
```bash
# A) Mudar DNS para público:
# DNS Primário: 8.8.8.8
# DNS Secundário: 8.8.4.4

# B) Limpar cache DNS:
ipconfig /flushdns

# C) Usar DNS Cloudflare:
# DNS Primário: 1.1.1.1
# DNS Secundário: 1.0.0.1
```

### **4. RESTRIÇÕES DE REDE CORPORATIVA**

#### **Sintomas:**
- Ambiente corporativo/empresarial
- Apenas sites "aprovados" funcionam
- Bloqueio de túneis/proxies

#### **Soluções:**
```bash
# A) Solicitar liberação para TI:
# Domínio a liberar: *.ngrok.io
# Porta: 443 (HTTPS)

# B) Usar IP direto (se possível):
# No servidor ngrok, verificar IP real e tentar acessar

# C) Alternativa: usar outro serviço de túnel
```

---

## 🔧 **SOLUÇÕES ESPECÍFICAS POR AMBIENTE:**

### **AMBIENTE CORPORATIVO:**

#### **Solução 1: Liberar no TI**
```
Solicitar liberação para:
- Domínio: *.ngrok.io
- Porta: 80, 443
- Protocolo: HTTP/HTTPS
- Justificativa: Sistema de gestão de artistas
```

#### **Solução 2: VPN Pessoal**
```bash
# Usar VPN pessoal para contornar restrições:
# - Hotspot Shield
# - ExpressVPN  
# - ProtonVPN (grátis)
```

#### **Solução 3: Hotspot Mobile**
```bash
# Usar internet do celular:
# 1. Ativar hotspot no celular
# 2. Conectar computador no hotspot
# 3. Testar acesso à URL do ngrok
```

### **AMBIENTE DOMÉSTICO:**

#### **Solução 1: Roteador com Controle Parental**
```bash
# Verificar se roteador está bloqueando:
# 1. Acessar interface do roteador (192.168.1.1)
# 2. Procurar "Controle Parental" ou "Bloqueio de Sites"
# 3. Remover *.ngrok.io da lista de bloqueados
```

#### **Solução 2: Antivírus Agressivo**
```bash
# Antivírus com proteção web ativa:
# Avast, AVG, Kaspersky, McAfee
# Desabilitar "Safe Browsing" ou "Web Shield"
```

---

## 🧪 **TESTES PARA IDENTIFICAR O PROBLEMA:**

### **Teste 1: Conectividade Básica**
```bash
# 1. Testar Google:
ping google.com

# 2. Testar DNS:
nslookup abc123.ngrok.io

# 3. Testar porta 443:
telnet abc123.ngrok.io 443
```

### **Teste 2: Navegadores Diferentes**
```bash
# Testar em:
# - Chrome
# - Firefox  
# - Edge
# - Chrome em modo incógnito
```

### **Teste 3: Linha de Comando**
```bash
# Windows PowerShell:
Invoke-WebRequest -Uri "https://abc123.ngrok.io"

# Se funcionar por linha de comando mas não no navegador = problema do navegador
# Se não funcionar em nenhum lugar = problema de rede/firewall
```

### **Teste 4: Outro Dispositivo na Mesma Rede**
```bash
# Testar no celular conectado no mesmo WiFi:
# Se funcionar no celular = problema específico do computador
# Se não funcionar no celular = problema da rede
```

---

## ⚡ **SOLUÇÕES RÁPIDAS:**

### **Solução Imediata (5 minutos):**
```bash
# 1. Desabilitar antivírus temporariamente
# 2. Usar outro navegador
# 3. Tentar modo incógnito
# 4. Usar hotspot do celular
```

### **Solução Alternativa (uso do IP local):**
```bash
# Se estiverem na mesma rede local:
# 1. No servidor, descobrir IP local: ipconfig
# 2. Usar: http://192.168.1.XXX:5001
# (substitua XXX pelo IP real)
```

### **Solução Definitiva:**
```bash
# 1. Configurar VPN no computador problemático
# 2. OU solicitar liberação do *.ngrok.io no TI
# 3. OU usar serviço alternativo (localtunnel, serveo)
```

---

## 🛠️ **ALTERNATIVAS AO NGROK:**

### **Se ngrok não funcionar, usar:**

#### **1. Localtunnel:**
```bash
npm install -g localtunnel
lt --port 5001
```

#### **2. Serveo:**
```bash
ssh -R 80:localhost:5001 serveo.net
```

#### **3. Cloudflare Tunnel:**
```bash
cloudflared tunnel --url http://localhost:5001
```

---

## 📞 **SCRIPT DE DIAGNÓSTICO AUTOMÁTICO:**

Vou criar um script para diagnosticar automaticamente:
