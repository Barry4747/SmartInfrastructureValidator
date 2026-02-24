*** Settings ***
Documentation     Quick smoke tests verifying if the infrastructure has been raised correctly.
Resource          ../resources/variables.robot

Library           RequestsLibrary
Library           ../libraries/AggregatorLibrary.py

*** Test Cases ***
Central Aggregator Responds To Requests
    [Documentation]    Checks if the main Aggregator API is alive and returns status 200 OK.
    [Tags]             smoke    healthcheck    api
    
    Create Session    aggregator    ${AGGREGATOR_URL}
    ${response}=      GET On Session    aggregator    /
    Status Should Be  200    ${response}
    Log To Console    \n[OK] Aggregator API works correctly.

At Least One Base Station Is Present In The Network
    [Documentation]    Checks if simulators managed to register after system start (docker compose up).
    [Tags]             smoke    network_status
    
    ${total_nodes}=    Get Total Registered Nodes    ${AGGREGATOR_URL}
    Should Be True     ${total_nodes} > 0
    Log To Console    \n[OK] Network is active. Nodes found: ${total_nodes}