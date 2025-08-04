from abc import ABC, abstractmethod
from datetime import datetime
import textwrap

# ==========================
# CLASSES DE SUPORTE
# ==========================

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })

# ==========================
# CLASSES ABSTRATAS
# ==========================

class Conta(ABC):
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @abstractmethod
    def sacar(self, valor):
        pass

    @abstractmethod
    def depositar(self, valor):
        pass


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

# ==========================
# CLASSES DE TRANSAÇÕES
# ==========================

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

# ==========================
# CLASSES DE CLIENTE
# ==========================

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

# ==========================
# CONTA CORRENTE
# ==========================

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        saques_realizados = len([
            t for t in self.historico.transacoes
            if t["tipo"] == "Saque"
        ])

        excedeu_limite = valor > self.limite
        excedeu_saques = saques_realizados >= self.limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! Valor excede o limite. @@@")
        elif excedeu_saques:
            print("\n@@@ Operação falhou! Limite de saques excedido. @@@")
        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! Valor inválido. @@@")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! Valor inválido. @@@")
            return False

    def __str__(self):
        return f"""
Agência:\t{self.agencia}
C/C:\t\t{self.numero}
Titular:\t{self.cliente.nome}
"""

    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)

# ==========================
# FUNÇÕES DO SISTEMA
# ==========================

def menu():
    menu = """
=============== MENU ===============
[d]\tDepositar
[s]\tSacar
[e]\tExtrato
[nc]\tNova conta
[lc]\tListar contas
[nu]\tNovo usuário
[q]\tSair
=> """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    return next((c for c in clientes if c.cpf == cpf), None)


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui contas. @@@")
        return None
    return cliente.contas[0]


def criar_cliente(clientes):
    cpf = input("Informe o CPF: ")
    if filtrar_cliente(cpf, clientes):
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Nome completo: ")
    data_nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço (logradouro, número, bairro - cidade/estado): ")

    cliente = PessoaFisica(nome, data_nascimento, cpf, endereco)
    clientes.append(cliente)
    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return

    conta = ContaCorrente.nova_conta(numero_conta, cliente)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def depositar(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return

    valor = float(input("Valor do depósito: "))
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    transacao = Deposito(valor)
    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return

    valor = float(input("Valor do saque: "))
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    transacao = Saque(valor)
    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n=============== EXTRATO ===============")
    transacoes = conta.historico.transacoes
    if not transacoes:
        print("Nenhuma transação realizada.")
    else:
        for t in transacoes:
            print(f"{t['tipo']}:\n\tR$ {t['valor']:.2f} em {t['data']}")

    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("=======================================")

# ==========================
# MAIN
# ==========================

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)
        elif opcao == "s":
            sacar(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "nc":
            criar_conta(len(contas) + 1, clientes, contas)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "q":
            print("Saindo do sistema. Até logo!")
            break
        else:
            print("\n@@@ Operação inválida. Tente novamente. @@@")

main()
