import requests
import logging

class AggregatorLibrary:
    """
    Robot Framework library for verifying network state in Aggregator.
    """

    def __init__(self):
        self.session = requests.Session()

    def verify_node_is_registered(self, aggregator_url: str, expected_node_name: str):
        """
        Checks if the base station with the given name is visible in Aggregator.
        Returns the ID of the found node.
        """
        endpoint = f"{aggregator_url}/api/nodes/"
        response = self.session.get(endpoint, timeout=5)
        
        if response.status_code != 200:
            raise AssertionError(f"Failed to retrieve node list. Status: {response.status_code}")

        nodes = response.json()
        
        for node in nodes:
            if node.get("node_name") == expected_node_name:
                logging.info(f"Found base station {expected_node_name} (ID: {node.get('node_id')})")
                return node.get("node_id")
                
        raise AssertionError(f"Base station '{expected_node_name}' NOT FOUND in Aggregator!")

    def get_total_registered_nodes(self, aggregator_url: str) -> int:
        """
        Returns the total number of base stations in the network.
        """
        endpoint = f"{aggregator_url}/api/nodes/"
        response = self.session.get(endpoint, timeout=5)
        response.raise_for_status()
        
        count = len(response.json())
        logging.info(f"Aggregator sees {count} base stations.")
        return count