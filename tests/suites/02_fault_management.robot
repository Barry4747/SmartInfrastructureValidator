*** Settings ***
Documentation     Test scenarios verifying hardware fault management handling in 5G network.
Resource          ../resources/variables.robot

Library           ../libraries/SimulatorLibrary.py
Library           ../libraries/AggregatorLibrary.py

Test Teardown     Fix All Faults On Base Station    ${SIMULATOR_URL}

*** Test Cases ***
Aggregator Should See Registered Station
    [Documentation]    Checks if the base station correctly registered in the central system.
    [Tags]             smoke    registration
    
    ${node_id}=    Verify Node Is Registered    ${AGGREGATOR_URL}    ${TARGET_NODE_NAME}
    Log To Console    \n[OK] Station ${TARGET_NODE_NAME} registered with ID: ${node_id}

Injecting Cooling Fault Does Not Break Connection
    [Documentation]    Verifies system behavior during overheating. The station should raise an alarm, but still respond.
    [Tags]             fault_management    critical
    
    # BDD Style (Given / When / Then) improves readability
    Given Verify Node Is Registered    ${AGGREGATOR_URL}    ${TARGET_NODE_NAME}
    
    When Inject Cooling Fault To Base Station    ${SIMULATOR_URL}
    Log To Console    \n[!] Fault injected. Waiting 10 seconds for logs propagation in network...
    And Sleep    10s
    
    # The system should still see the station (despite critical fault it didn't disappear from network)
    Then Verify Node Is Registered    ${AGGREGATOR_URL}    ${TARGET_NODE_NAME}
    
    ${total_nodes}=    Get Total Registered Nodes    ${AGGREGATOR_URL}
    Should Be True     ${total_nodes} > 0