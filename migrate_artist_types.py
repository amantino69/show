#!/usr/bin/env python3
"""
Script para migrar dados existentes para incluir tipos de artistas
"""

from app import create_app, db
from app.models import Artist, ArtistType
from config import Config

def migrate_existing_artists():
    """Migra artistas existentes para incluir tipos de artistas"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migração de tipos de artistas...")
        
        # Verificar se já existem tipos de artistas
        if ArtistType.query.count() == 0:
            print("❌ Nenhum tipo de artista encontrado. Execute o script de inicialização primeiro.")
            return
        
        # Pegar o tipo "Outros" como padrão
        default_type = ArtistType.query.filter_by(name="Outros").first()
        if not default_type:
            default_type = ArtistType.query.first()
        
        # Migrar artistas sem tipo
        artists_without_type = Artist.query.filter_by(artist_type_id=None).all()
        
        if not artists_without_type:
            print("✅ Todos os artistas já possuem tipos definidos.")
            return
        
        print(f"📋 Encontrados {len(artists_without_type)} artistas sem tipo definido.")
        
        # Tentar categorizar automaticamente baseado no gênero/nome
        categorizations = {
            'cantor': 'Cantor/Cantora',
            'cantora': 'Cantor/Cantora',
            'singer': 'Cantor/Cantora',
            'vocal': 'Cantor/Cantora',
            'música': 'Cantor/Cantora',
            'rap': 'Cantor/Cantora',
            'rock': 'Cantor/Cantora',
            'pop': 'Cantor/Cantora',
            'sertanejo': 'Cantor/Cantora',
            'funk': 'Cantor/Cantora',
            'dj': 'DJ/Produtor',
            'producer': 'DJ/Produtor',
            'produtor': 'DJ/Produtor',
            'modelo': 'Modelo',
            'model': 'Modelo',
            'influencer': 'Influenciador Digital',
            'influenciador': 'Influenciador Digital',
            'youtuber': 'Influenciador Digital',
            'instagram': 'Influenciador Digital',
            'tiktoker': 'Influenciador Digital',
            'ator': 'Ator/Atriz',
            'atriz': 'Ator/Atriz',
            'actor': 'Ator/Atriz',
            'dança': 'Dançarino',
            'dance': 'Dançarino',
            'dançarino': 'Dançarino',
            'bailarino': 'Dançarino',
            'stand-up': 'Comediante',
            'comediante': 'Comediante',
            'humor': 'Comediante',
            'pintor': 'Artista Visual',
            'designer': 'Artista Visual',
            'artista visual': 'Artista Visual'
        }
        
        updated_count = 0
        
        for artist in artists_without_type:
            artist_type = default_type
            
            # Tentar categorizar baseado no gênero ou descrição
            search_text = f"{artist.genre or ''} {artist.description or ''} {artist.name or ''} {artist.stage_name or ''}".lower()
            
            for keyword, type_name in categorizations.items():
                if keyword in search_text:
                    found_type = ArtistType.query.filter_by(name=type_name).first()
                    if found_type:
                        artist_type = found_type
                        break
            
            artist.artist_type_id = artist_type.id
            updated_count += 1
            
            print(f"  📌 {artist.stage_name or artist.name} → {artist_type.name}")
        
        try:
            db.session.commit()
            print(f"✅ Migração concluída! {updated_count} artistas atualizados.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro na migração: {str(e)}")

if __name__ == '__main__':
    migrate_existing_artists()
