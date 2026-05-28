#!/usr/bin/env python3
"""
Script simples para migrar dados existentes
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Artist, ArtistType

def main():
    """Executa a migração"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Verificando migração de tipos de artistas...")
        
        # Verificar artistas sem tipo
        artists_without_type = Artist.query.filter_by(artist_type_id=None).all()
        
        if not artists_without_type:
            print("✅ Todos os artistas já possuem tipos definidos.")
            return
        
        # Pegar tipo "Outros" como padrão
        default_type = ArtistType.query.filter_by(name="Outros").first()
        if not default_type:
            default_type = ArtistType.query.first()
        
        print(f"📋 Atualizando {len(artists_without_type)} artistas...")
        
        for artist in artists_without_type:
            artist.artist_type_id = default_type.id
            print(f"  📌 {artist.stage_name or artist.name} → {default_type.name}")
        
        db.session.commit()
        print("✅ Migração concluída!")

if __name__ == '__main__':
    main()
