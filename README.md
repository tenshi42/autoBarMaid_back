# AutoBarMaid_back

## Requirements
- Python > 3.9 (3.10 is best)
- Libraries : 
    - websocket_server (https://github.com/Pithikos/python-websocket-server : pip install websocket-server)
- :warning: Has to be run on a Raspberry PI (V2, V3 or V4), due to usage of the GPIO library :warning:

## Communication protocol
### Websocket :
- Address : 0.0.0.0
- Port : 8765
### Message format
- Example : {"type": "echo", "data": "anything"}

## Global infos
- 8 pump : from 0 to 7
- Blocking action are actions that can't be parallelized or multiples at the same time. However, non-blocking actions can still be done. 

## Message types
### From Gui
- blend
    - Description
        - Blocking action
        - Run a blend action for given time depending on cup_size
        - Periodically send messages of type "status" while blending
    - Data : {"cup_size": number, "ratios": {"0": number, "4": number, ...}}
        - cup_size in litter
        - not used liquid can be omitted
        - ratio for each liquid (0.0->1.0) (sum not checked)
    - Example : {"type": "blend", "data": {"cup_size": 0.04, "ratios": {"1": 0.2, "2": 0.1, "5": 0.7}}}
- refill
    - Description
        - Blocking action
        - Used to indicate that a previously empty container need to be refilled (refill the tube)
        - Time is computed automatically from pump position
    - Data : {"pump": integer}
    - Example : {"type": "refill", "data": {"pump": 4}}
- echo
    - Description : echo anything sent
    - Data : anything
    - Example : {"type": "echo", "data": {"msg": "toaster"}}
- get_pumps_states
    - Description
        - get current pumps states
        - receive a "pumps_states" message when done
    - Data : none
    - Example : {"type": "get_pumps_states"}
- set_pump_state
    - Description
        - set a pump state
        - receive a "pumps_states" message when done
    - Data : {"pump_index": integer, "state": bool}
    - Example : {'type': 'set_pump_state', 'data': {'pump_index': 0, 'state': false}}
- set_pump_refill_time
    - Description
        - :warning: only for configuration purposes :warning:
        - set pump refill time
        - receive a "pumps_states" message when done
    - Data : {'pump_index': integer, 'refill_time': integer}
    - Example : {'type': 'set_pump_refill_time', 'data': {'pump_index': 0, 'refill_time': 45}}
- set_sec_per_liter
    - Description
        - :warning: only for configuration purposes :warning:
        - set the global "sec_per_second" value
        - receive a "sec_per_liter" message when done
    - Data : {'sec_per_liter': integer}
    - Example : {'type': 'set_sec_per_liter', 'data': {'sec_per_liter': 666}}
- get_config
    - Description
        - :warning: only for configuration purposes :warning:
        - return global config
        - receive a "config" message when done
    - Data : None
    - Example : {'type': 'get_config'}
    
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
- pumps_state
    - Description : current status of all pumps
    - Data : list
    - Example : {"type": "pumps_states", "data": [{"enabled": true, "refill_time": 2}, {"enabled": true, "refill_time": 2}, {"enabled": true, "refill_time": 3}, {"enabled": true, "refill_time": 3}, {"enabled": true, "refill_time": 4}, {"enabled": true, "refill_time": 4}, {"enabled": true, "refill_time": 5}, {"enabled": true, "refill_time": 5}]}
- sec_per_liter
    - Description : get the current "sec_per_liter" config
    - Data : integer
    - Example : {"type": "sec_per_litter", "data": 666}
- config
    - Description : get the global config
    - Data : object
    - Example : {"type": "config", "data": {"pumps": [{"enabled": true, "refill_time": 2}, {"enabled": true, "refill_time": 2}, {"enabled": true, "refill_time": 3}, {"enabled": true, "refill_time": 3}, {"enabled": true, "refill_time": 4}, {"enabled": true, "refill_time": 4}, {"enabled": true, "refill_time": 5}, {"enabled": true, "refill_time": 5}], "sec_per_liter": 666}}