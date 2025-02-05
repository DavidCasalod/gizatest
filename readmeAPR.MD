# Cálculo del APR del Pool de USDC Layerbank

Explicación de un script sencillo  que calcula:
1. El **APR base actual** de un pool de USDC en el protocolo Layerbank.
2. El **APR proyectado** después de depositar más cantidad de USDC en el pool.

## Descripción

- **Contrato del Pool**: `0xBa6e89c9cDa3d72B7D8D5B05547a29f9BdBDBaec`
- **ABI**: Proporcionado en `POOL_ABI` (solo las funciones necesarias para este caso).
- **Modelo de Tasa**: Para esta solución, utilizo un modelo simplificado, aunque en la realidad se llamaría al contrato `getRateModel()` del protocolo para obtener las tasas de préstamo y suministro.

## Cómo Funciona

### 1. Conexión a la blockchain Mode usando `web3.py`

Una instancia `Web3` apuntando al endpoint público RPC de Mode:

```python
MODE_RPC_URL = "https://mainnet.mode.network/"
web3 = Web3(Web3.HTTPProvider(MODE_RPC_URL))
```

## 2. Llamadas al Smart-contract

Instancia del contrato utilizando:

```python
pool_contract = web3.eth.contract(
    address=POOL_ADDRESS,
    abi=POOL_ABI
)
```

Llamadas al contrato:

- `getCash()`
- `totalBorrow()`
- `totalReserve()`
- `reserveFactor()`

## 3. Modelo Simplificado de  la Tasa

Modelo lineal para la tasa de préstamo:

```python
borrowRate = baseRate + (slope * utilization)
```

Luego, la tasa de suministro (APR) se calcula como:

```python
supplyRate = borrowRate * utilization * (1 - reserveFactor)
```

En realidad, se podría llamar directamente al contrato del modelo de tasas si el pool hace referencia a un contrato `IRateModel`.

## 4. Proyección del APR Después de un Depósito

Al aumentar la cantidad con un depósito de USDC, recalculo la utilización y, por lo tanto, la nueva tasa APR.

