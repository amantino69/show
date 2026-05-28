#!/usr/bin/env python3
"""
Script para converter MANUAL_USUARIO.md para HTML formatado
"""

import markdown
import os

def convert_md_to_html():
    # Ler o arquivo Markdown
    with open('MANUAL_USUARIO.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Converter para HTML com extensões
    html = markdown.markdown(md_content, extensions=['tables', 'toc', 'fenced_code'])
    
    # Template HTML com CSS bonito
    html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manual do Usuário - Sistema de Gerenciamento de Artistas</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            padding-left: 10px;
            border-left: 4px solid #3498db;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        code {{
            background: #f1f2f6;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background: #2f3640;
            color: #f5f6fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background: #ecf0f1;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #3498db;
            color: white;
        }}
        .emoji {{
            font-size: 1.2em;
        }}
        .highlight {{
            background: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }}
        .success {{
            background: #d4edda;
            border-left: 4px solid #28a745;
        }}
        .info {{
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
        }}
        .warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
        }}
        ul, ol {{
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
        .header-info {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-info">
            <h1>📱 Manual do Usuário</h1>
            <p>Sistema de Gerenciamento de Artistas</p>
            <p><small>Versão atualizada: Julho 2025</small></p>
        </div>
        {html}
        <hr>
        <footer style="text-align: center; color: #7f8c8d; margin-top: 40px;">
            <p>Sistema desenvolvido para gerenciamento profissional de artistas</p>
            <p><small>© 2025 - Todos os direitos reservados</small></p>
        </footer>
    </div>
</body>
</html>
"""
    
    # Salvar arquivo HTML
    with open('MANUAL_USUARIO.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("✅ Manual convertido para HTML: MANUAL_USUARIO.html")
    print("📁 Arquivo salvo na pasta do projeto")
    print("🌐 Abra o arquivo .html no navegador para visualizar")

if __name__ == '__main__':
    convert_md_to_html()
