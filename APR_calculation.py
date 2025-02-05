from web3 import Web3

def get_base_apr_usdc_pool(web3, pool_addr, pool_abi):
    pool = web3.eth.contract(address=pool_addr, abi=pool_abi)

    # on-chain calls
    cash = pool.functions.getCash().call()
    borrowed = pool.functions.totalBorrow().call()
    reserves = pool.functions.totalReserve().call()
    reserve_factor = pool.functions.reserveFactor().call()

    base_rate = 0.02
    slope = 0.18

    denom = (cash + borrowed - reserves)
    if denom <= 0:
        return 0.0

    utilization = borrowed / denom
    borrow_rate = base_rate + slope * utilization
    reserve_factor = reserve_factor / 1e18

    supply_rate = borrow_rate * utilization * (1 - reserve_factor)
    return supply_rate

def get_projected_apr_after_deposit(web3, pool_addr, pool_abi, additional_deposit):
    pool = web3.eth.contract(address=pool_addr, abi=pool_abi)
    cash = pool.functions.getCash().call()
    borrowed = pool.functions.totalBorrow().call()
    reserves = pool.functions.totalReserve().call()
    reserve_factor = pool.functions.reserveFactor().call()

    # Ajustes decimales
    reserve_factor = reserve_factor / 1e18

    new_cash = cash + additional_deposit
    denom = (new_cash + borrowed - reserves)
    if denom <= 0:
        return 0.0

    new_util = borrowed / denom

    # Mismo modelo:
    base_rate = 0.02
    slope = 0.18
    new_borrow_rate = base_rate + slope * new_util
    new_supply_rate = new_borrow_rate * new_util * (1 - reserve_factor)
    return new_supply_rate


if __name__ == "__main__":
    MODE_RPC_URL = " https://mainnet.mode.network/"  
    web3 = Web3(Web3.HTTPProvider(MODE_RPC_URL))
    #Funciones necesarias del ABI del contrato:
    POOL_ABI = [
  {
    "inputs": [],
    "name": "getCash",
    "outputs": [
      { "internalType": "uint256", "name": "", "type": "uint256" }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalBorrow",
    "outputs": [
      { "internalType": "uint256", "name": "", "type": "uint256" }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalReserve",
    "outputs": [
      { "internalType": "uint256", "name": "", "type": "uint256" }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "reserveFactor",
    "outputs": [
      { "internalType": "uint256", "name": "", "type": "uint256" }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]

    POOL_ADDRESS = "0xBa6e89c9cDa3d72B7D8D5B05547a29f9BdBDBaec"

    base_apr = get_base_apr_usdc_pool(web3, POOL_ADDRESS, POOL_ABI)
    print(f"Current Base APR: {base_apr*100:.2f}%")

    # USDC
    deposit_sim = 200_000  
    projected_apr = get_projected_apr_after_deposit(web3, POOL_ADDRESS, POOL_ABI, deposit_sim)
    print(f"Projected APR after +{deposit_sim} USDC: {projected_apr*100:.2f}%")
