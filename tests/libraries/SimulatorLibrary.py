import requests
import logging

class SimulatorLibrary:
    """
    Robot Framework library for simulating base station faults.
    """
    
    def __init__(self):
        self.session = requests.Session()

    def inject_cooling_fault_to_base_station(self, simulator_url: str):
        """
        Injects cooling fault to the base station.
        """
        endpoint = f"{simulator_url}/api/fault/cooling"
        logging.info(f"Injecting cooling fault to base station: {endpoint}")
        
        response = self.session.post(endpoint, timeout=5)
        
        if response.status_code != 200:
            raise AssertionError(f"Failed to inject cooling fault! Status: {response.status_code}. Response: {response.text}")
        
        logging.info("Cooling fault injected successfully.")

    def fix_all_faults_on_base_station(self, simulator_url: str):
        """
        Fixes all faults on the base station.
        """
        endpoint = f"{simulator_url}/api/fault/fix"
        logging.info(f"Fixing all faults on base station: {endpoint}")
        
        response = self.session.post(endpoint, timeout=5)
        
        if response.status_code != 200:
            raise AssertionError(f"Failed to fix all faults! Status: {response.status_code}. Response: {response.text}")
        
        logging.info("All faults fixed successfully.")