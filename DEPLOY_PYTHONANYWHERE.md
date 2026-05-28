# Deploy do Show no PythonAnywhere (Plano Free)

Guia prático para publicar o sistema `Show` sem conflito com HVD e sem custo inicial.

## 1) Pré-requisitos

- Conta gratuita no PythonAnywhere.
- Repositório do projeto no GitHub (pode ser privado).
- Projeto local funcionando (já validado).

## 2) Criar Web App no PythonAnywhere

1. Acesse **Web** > **Add a new web app**.
2. Escolha:
   - **Manual configuration**
   - **Python 3.13** (ou a versão mais próxima disponível)
3. Anote o caminho do WSGI indicado pelo PythonAnywhere (ex.: `/var/www/seuusuario_pythonanywhere_com_wsgi.py`).

## 3) Subir código no servidor

No console **Bash** do PythonAnywhere:

```bash
cd ~
git clone https://github.com/SEU_USUARIO/SEU_REPO.git show
cd show
```

Se já existir pasta `show`, atualize com:

```bash
cd ~/show
git pull
```

## 4) Criar e ativar ambiente virtual

```bash
cd ~/show
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Configurar variáveis de ambiente (.env)

Crie o arquivo `~/show/.env`:

```bash
nano ~/show/.env
```

Exemplo mínimo:

```env
SECRET_KEY=troque-por-uma-chave-forte
DATABASE_URL=sqlite:///artistas_sistema.db
GOOGLE_REDIRECT_URI=https://SEUUSUARIO.pythonanywhere.com/google/callback
```

Observações:
- Esse banco SQLite ficará isolado do HVD.
- Não use credenciais do HVD.

## 6) Inicializar banco e usuário admin

```bash
cd ~/show
source .venv/bin/activate
python app.py
```

Se o script acima apenas iniciar servidor sem criar tabelas, rode:

```bash
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all(); print('ok')"
```

Depois crie/atualize o admin:

```bash
python scripts/ensure_admin_julia.py
```

Login esperado:
- Usuário: `julia`
- Senha: `123`

## 7) Configurar WSGI do PythonAnywhere

Abra o arquivo WSGI criado pelo PythonAnywhere e substitua o conteúdo por:

```python
import sys
path = '/home/SEUUSUARIO/show'
if path not in sys.path:
    sys.path.insert(0, path)

from app import create_app
application = create_app()
```

No painel **Web**:
- **Virtualenv**: `/home/SEUUSUARIO/show/.venv`
- Clique em **Reload**.

## 8) Validar acesso

URL:

`https://SEUUSUARIO.pythonanywhere.com`

Checklist rápido:
- Login com `julia / 123`
- Sidebar com rolagem independente
- CRUD de CRM / Equipe / Assessorados
- Backup e restauração
- Limpeza de dados de teste

## 9) Fluxo de atualização (quando tiver novas mudanças)

```bash
cd ~/show
git pull
source .venv/bin/activate
pip install -r requirements.txt
```

Depois clique em **Reload** no painel Web.

## 10) Troubleshooting rápido

- Erro 500:
  - Ver **Web > Log files > error.log**
  - Verifique caminho da virtualenv e do WSGI.
- Módulo não encontrado:
  - Ative `.venv` e rode `pip install -r requirements.txt`.
- Arquivos estáticos não carregam:
  - Confirme `app/static` no projeto.
- Google OAuth falha:
  - Atualize `GOOGLE_REDIRECT_URI` no `.env` e no console Google.

---

## Limites do plano free (esperados)

- Sem domínio customizado no plano grátis.
- Recursos limitados (ok para teste da cliente).
- Ainda assim, suficiente para uso contínuo de validação.

Quando vender, migre para VPS Viezes mantendo o mesmo código e processo de backup.
