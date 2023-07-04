# AutoBarMaid_back

## Requirements
- Python > 3.9 (3.10 is best)
- Libraries : 
    - websocket_server (https://github.com/Pithikos/python-websocket-server : pip install websocket-server)

## Communication protocol
### Websocket :
- Address : 0.0.0.0
- Port : 8765
### Message format
- Example : {"type": "echo", "data": "anything"}

## Message types
### From Gui
- blend
    - Description
        - Run a blend action for given time depending on cup_size
        - Periodically send messages of type "status" while blending
    - Data : {"cup_size": number, "ratios": {"1": number, "4": number, ...}}
        - cup_size in litter
        - not used liquid can be omitted
        - ratio for each liquid (0.0->1.0) (sum not checked)
    - Example : {"type": "blend", "data": {"cup_size": 0.04, "ratios": {"1": 0.2, "2": 0.1, "5": 0.7}}}
- echo
    - Description : echo anything sent
    - Data : anything
    - Example : {"type": "echo", "data": {"msg": "toaster"}}
    
### From server
- status
    - Description
        - Blending status
        - Sent periodically while blending
    - Data : {"remaining_time": integer}
        - remaining_time in seconds to the end
    - Example : {"type": "status", "data": {"remaining_time": 2}}
- echo
    - Description : echo from an echo message
    - Data : original sent data
    - Example : {"type": "echo", "data": {"msg": "toaster"}}
- error
    - Description : message sent if anything goes wrong/unexpected
    - Data : {"msg": string}
    - Example : {"type": "error", "data": {"msg": "Already blending ! Retry in 3 sec"}}