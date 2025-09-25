#!/usr/bin/env python3
"""
Script para executar migrações do banco de dados
"""

from database import DatabaseManager

def executar_migracoes():
    """Executa todas as migrações necessárias"""
    print("🔄 Iniciando migrações do banco de dados...")
    
    db = DatabaseManager()
    
    # Criar tabelas básicas
    print("📋 Criando tabelas básicas...")
    if db.criar_tabelas():
        print("✅ Tabelas básicas criadas com sucesso")
    else:
        print("❌ Erro ao criar tabelas básicas")
        return False
    
    # Criar tabelas de sincronização
    print("🔄 Criando tabelas de sincronização...")
    try:
        from sync_manager import inicializar_sync_manager
        sync_manager = inicializar_sync_manager()
        if sync_manager.criar_tabelas_sync():
            print("✅ Tabelas de sincronização criadas com sucesso")
        else:
            print("❌ Erro ao criar tabelas de sincronização")
    except Exception as e:
        print(f"⚠️ Erro ao criar tabelas de sincronização: {e}")
    
    print("🎉 Migrações concluídas!")
    return True

if __name__ == "__main__":
    executar_migracoes()
