import json
from datetime import datetime
from typing import Dict, List
from enum import Enum



# 1. Clases Chain y Action
# -------------------------------------------------------
class Chain(str, Enum):
    ETHEREUM = "Ethereum"
    POLYGON = "Polygon"
    ARBITRUM = "Arbitrum"
    BASE = "Base"  

class Action(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    BORROW = "borrow"
    REPAY = "repay"


# 2. Clase Transaction
# -------------------------------------------------------
class Transaction:
    def __init__(
        self,
        timestamp: datetime,
        chain: Chain,
        protocol: str,
        action: Action,
        asset: str,
        amount: float,
        usd_value: float
    ):
        self.timestamp = timestamp
        self.chain = chain
        self.protocol = protocol
        self.action = action
        self.asset = asset
        self.amount = amount
        self.usd_value = usd_value

# 3. Clase Position
#    - Sirve para almaccenar info de un activo en una wallet
# -------------------------------------------------------
class Position:
    """
    Mantiene la cantidad de un activo y el precio en USD

    """
    def __init__(self, asset: str):
        self.asset = asset
        self.quantity = 0.0
        self.cost_basis_usd = 0.0

    def update_position(self, action: Action, amount: float, usd_value: float):
        """
        - DEPOSIT: Aumentar cantidad y cost basis total.
        - WITHDRAW: Disminuir cantidad y cost basis.
        """
        if action == Action.DEPOSIT:
            # Aumentamos la cantidad
            old_qty = self.quantity
            self.quantity += amount

            # Sumamos al cost_basis_usd lo pagado
            self.cost_basis_usd += usd_value

        elif action == Action.WITHDRAW:
            if amount > self.quantity:
                raise ValueError(f"No se puede retirar más {self.asset} de lo que se posee.")
            # Fracción del total que se está retirando
            fraction = amount / self.quantity

            self.quantity -= amount
            # Reducimos cost basis proporcionalmente
            self.cost_basis_usd -= self.cost_basis_usd * fraction
        else:
            pass

    def market_value(self, current_price: float) -> float:
        return self.quantity * current_price

# 4. Clase Wallet
#    - Contiene varias posiciones y transacciones
# -------------------------------------------------------
class Wallet:
    def __init__(self, address: str, chain: Chain):
        self.address = address
        self.chain = chain
        # Diccionario de posiciones: asset -> Position
        self.positions: Dict[str, Position] = {}
        # Historial de transacciones
        self.transactions: List[Transaction] = []

    def add_transaction(self, tx: Transaction):
        """
        Agrega la transacción al historial y actualiza/crea la Position correspondiente.
        """
        self.transactions.append(tx)
        asset = tx.asset
        if asset not in self.positions:
            self.positions[asset] = Position(asset)

        self.positions[asset].update_position(tx.action, tx.amount, tx.usd_value)

    def get_wallet_value(self, price_feed: Dict[str, float]) -> float:
        """
        Suma el valor de mercado actual de todas las posiciones en la wallet.
        """
        total = 0.0
        for asset, pos in self.positions.items():
            current_price = price_feed.get(asset, 0.0)
            total += pos.market_value(current_price)
        return total

# 5. Clase Portfolio
#    - Maneja múltiples Wallets
# -------------------------------------------------------
class Portfolio:
    def __init__(self):
        # Diccionario: wallet_address -> Wallet
        self.wallets: Dict[str, Wallet] = {}

    def add_wallet(self, address: str, chain: Chain):

        if address in self.wallets:
            raise ValueError(f"Wallet {address} ya existe en el portfolio.")

        self.wallets[address] = Wallet(address, chain)

    def process_transaction(self, address: str, tx: Transaction):

        if address not in self.wallets:
            raise ValueError(f"Wallet {address} no está registrado en el portfolio.")
        self.wallets[address].add_transaction(tx)

    def get_total_value(self, price_feed: Dict[str, float]) -> float:

        total = 0.0
        for wallet in self.wallets.values():
            total += wallet.get_wallet_value(price_feed)
        return total

    def get_portfolio_analytics(self, price_feed: Dict[str, float]) -> Dict[str, Dict[str, float]]:

        chain_exposure = {}
        protocol_exposure = {}
        asset_exposure = {}

        # Recorremos cada wallet
        for wallet in self.wallets.values():
            w_value = wallet.get_wallet_value(price_feed)
            # Sumar a la cadena del wallet
            chain_str = wallet.chain.value
            chain_exposure[chain_str] = chain_exposure.get(chain_str, 0.0) + w_value
 
            #   - Miramos la market_value real de la Position 
            #   - Repartimos el "valor" entre protocolos en proporción a transacciones 
            #    sumamos "market_value" del asset a su "protocol" del TX,
            #   suponiendo que no se repartió en varios protocolos. 

            # Agrupamos por asset
            for asset, pos in wallet.positions.items():
                asset_mv = pos.market_value(price_feed.get(asset, 0.0))
                asset_exposure[asset] = asset_exposure.get(asset, 0.0) + asset_mv

            # Agrupamos por protocolo basado en transacciones
            for tx in wallet.transactions:
                current_prc = price_feed.get(tx.asset, 0.0)
                val_estimate = tx.amount * current_prc
                protocol_exposure[tx.protocol] = protocol_exposure.get(tx.protocol, 0.0) + val_estimate

        return {
            "chains": chain_exposure,
            "protocols": protocol_exposure,
            "assets": asset_exposure
        }

if __name__ == "__main__":
    import json
    from datetime import datetime

    # 1) Instanciar Portfolio
    portfolio = Portfolio()

    # 2) Crear Wallets
    portfolio.add_wallet("0x123", Chain.ETHEREUM)
    portfolio.add_wallet("0x456", Chain.POLYGON)

    # 3) Procesar Transacciones (ejemplo similar al enunciado)
    portfolio.process_transaction(
        "0x123",
        Transaction(
            timestamp=datetime.now(),
            chain=Chain.ETHEREUM,
            protocol="Aave",
            action=Action.DEPOSIT,
            asset="ETH",
            amount=1.5,
            usd_value=4500,
        )
    )

    portfolio.process_transaction(
        "0x456",
        Transaction(
            timestamp=datetime.now(),
            chain=Chain.POLYGON,
            protocol="Quickswap",
            action=Action.DEPOSIT,
            asset="MATIC",
            amount=1000,
            usd_value=1500,
        )
    )

    portfolio.process_transaction(
        "0x123",
        Transaction(
            timestamp=datetime.now(),
            chain=Chain.ETHEREUM,
            protocol="Compound",
            action=Action.DEPOSIT,
            asset="USDC",
            amount=2000,
            usd_value=2000,
        )
    )

    # 4) Prices actuales
    current_prices = {
        "ETH": 3000,
        "MATIC": 1.8,
        "USDC": 1.0
    }

    # 5) Cálculo de valor total
    total_value = portfolio.get_total_value(current_prices)
    print(f"Total Portfolio Value: ${total_value}")

    # 6) Analítica de exposición
    exposure = portfolio.get_portfolio_analytics(current_prices)
    print("Exposure:")
    print(json.dumps(exposure, indent=2))