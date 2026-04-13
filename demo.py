#!/usr/bin/env python3
"""
Script de demonstração da API de Clientes
Mostra o funcionamento das camadas sem dependências externas
"""

from datetime import datetime
from unittest.mock import Mock

# Import das camadas da aplicação
from src.domain.client import Client
from src.application.use_cases import CreateClientUseCase, GetClientUseCase, ListClientsUseCase
from src.application.dtos import CreateClientRequest, PaginationRequest
from src.application.interfaces.client_repository import ClientRepository


class InMemoryClientRepository(ClientRepository):
    """Implementação em memória do repositório para demonstração"""
    
    def __init__(self):
        self._clients = {}
        self._next_id = 1
    
    def save(self, client: Client) -> Client:
        saved_client = Client(
            name=client.name,
            email=client.email,
            phone=client.phone,
            client_id=self._next_id,
            created_at=client.created_at
        )
        self._clients[self._next_id] = saved_client
        self._next_id += 1
        return saved_client
    
    def find_by_id(self, client_id: int):
        return self._clients.get(client_id)
    
    def find_by_email(self, email: str):
        for client in self._clients.values():
            if client.email == email:
                return client
        return None
    
    def find_all(self, limit: int = 100, offset: int = 0):
        all_clients = list(self._clients.values())
        return all_clients[offset:offset + limit]
    
    def update(self, client: Client):
        if client.id in self._clients:
            self._clients[client.id] = client
            return client
        return None
    
    def delete_by_id(self, client_id: int):
        if client_id in self._clients:
            del self._clients[client_id]
            return True
        return False
    
    def exists_by_email(self, email: str, exclude_id: int = None):
        for client_id, client in self._clients.items():
            if client.email == email and (exclude_id is None or client_id != exclude_id):
                return True
        return False


def demo_clean_architecture():
    """Demonstra o funcionamento da arquitetura limpa"""
    
    print("🏗️  DEMONSTRAÇÃO DA API DE CLIENTES - ARQUITETURA LIMPA")
    print("=" * 60)
    
    # Setup - Dependency Injection
    repository = InMemoryClientRepository()
    create_use_case = CreateClientUseCase(repository)
    get_use_case = GetClientUseCase(repository)
    list_use_case = ListClientsUseCase(repository)
    
    print("\n1. ✅ Criando clientes...")
    
    # Criar clientes de exemplo
    clients_data = [
        CreateClientRequest("João Silva", "joao.silva@email.com", "11999999999"),
        CreateClientRequest("Maria Santos", "maria.santos@email.com", "11888888888"),
        CreateClientRequest("Pedro Oliveira", "pedro.oliveira@email.com", "11777777777"),
    ]
    
    created_clients = []
    for client_data in clients_data:
        try:
            response = create_use_case.execute(client_data)
            created_clients.append(response)
            print(f"   Cliente criado: {response.name} ({response.email}) - ID: {response.id}")
        except Exception as e:
            print(f"   ❌ Erro ao criar cliente: {e}")
    
    print(f"\n2. ✅ Listando {len(created_clients)} clientes cadastrados...")
    
    # Listar clientes
    pagination = PaginationRequest(page=1, per_page=10)
    clients_list = list_use_case.execute(pagination)
    
    for client in clients_list:
        print(f"   ID: {client.id} | {client.name} | {client.email} | {client.phone or 'N/A'}")
    
    print("\n3. ✅ Buscando cliente específico...")
    
    # Buscar cliente específico
    if clients_list:
        first_client_id = clients_list[0].id
        client = get_use_case.execute(first_client_id)
        print(f"   Cliente encontrado: {client.name} ({client.email})")
        print(f"   Criado em: {client.created_at}")
    
    print("\n4. ✅ Validações de domínio funcionando...")
    
    # Teste de validações
    try:
        # Email inválido
        CreateClientRequest("Teste", "email-invalido", "11999999999")
    except ValueError as e:
        print(f"   ✅ Validação de email: {e}")
    
    try:
        # Nome vazio
        CreateClientRequest("", "test@email.com", "11999999999")
    except ValueError as e:
        print(f"   ✅ Validação de nome: {e}")
    
    print("\n5. ✅ Testando regra de negócio - email único...")
    
    # Tentar criar cliente com email duplicado
    try:
        duplicate_request = CreateClientRequest("João Duplicado", "joao.silva@email.com", "11999999999")
        create_use_case.execute(duplicate_request)
        print("   ❌ Erro: deveria ter falhado!")
    except Exception as e:
        print(f"   ✅ Regra de negócio funcionando: {e}")
    
    print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print("\n💡 Pontos importantes da arquitetura:")
    print("   • Separação clara de responsabilidades")
    print("   • Regras de negócio isoladas na camada de domínio") 
    print("   • Inversão de dependências com interfaces abstratas")
    print("   • Casos de uso bem definidos")
    print("   • Fácil testabilidade com mocks")
    print("   • Alto desacoplamento entre camadas")
    
    return created_clients


def demo_validations():
    """Demonstra as validações da entidade Client"""
    
    print("\n📋 DEMONSTRAÇÃO DAS VALIDAÇÕES DE DOMÍNIO")
    print("=" * 50)
    
    # Casos de teste de validação
    test_cases = [
        # (nome, email, phone, deve_falhar, motivo)
        ("João Silva", "joao@email.com", "11999999999", False, "Dados válidos"),
        ("", "joao@email.com", "11999999999", True, "Nome vazio"),
        ("a" * 121, "joao@email.com", "11999999999", True, "Nome muito longo"),
        ("João", "", "11999999999", True, "Email vazio"),
        ("João", "email-inválido", "11999999999", True, "Email inválido"),
        ("João", "a" * 115 + "@email.com", "11999999999", True, "Email muito longo"),
        ("João", "joao@email.com", "1" * 31, True, "Telefone muito longo"),
        ("João", "joao@email.com", None, False, "Telefone opcional"),
    ]
    
    for i, (name, email, phone, should_fail, reason) in enumerate(test_cases, 1):
        try:
            client = Client(name=name, email=email, phone=phone)
            if should_fail:
                print(f"{i:2d}. ❌ FALHOU: {reason} - deveria ter falhado")
            else:
                print(f"{i:2d}. ✅ PASSOU: {reason}")
        except ValueError as e:
            if should_fail:
                print(f"{i:2d}. ✅ PASSOU: {reason} - {e}")
            else:
                print(f"{i:2d}. ❌ FALHOU: {reason} - erro inesperado")


if __name__ == "__main__":
    # Executar demonstrações
    demo_clean_architecture()
    demo_validations()
    
    print(f"\n🚀 Para executar o projeto completo:")
    print("   1. docker-compose up -d    # Subir MySQL")
    print("   2. python -m src.main      # Executar API")
    print("   3. Acessar http://localhost:5000/health")
    
    print(f"\n🧪 Para executar todos os testes:")
    print("   pytest --cov=src --cov-report=term-missing")