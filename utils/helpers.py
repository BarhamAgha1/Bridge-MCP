import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='bridge_mcp.log'
    )
    return logging.getLogger("BridgeMCP")
