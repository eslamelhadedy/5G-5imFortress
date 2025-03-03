"""
Modbus master
This file communicates with server/slave via modbustcp and dashboard
"""
import datetime
import logging
import json
from time import sleep
from pyModbusTCP.client import ModbusClient
from HMI.frontend.datalogger import logger

POWER_ADDR_COIL = 1
BITRATE_ACTIVE_ADDR_REG = 1
BITRATE_TOTAL_ADDR_REG = 5
USERS_ADDR_REG = 9
GAIN_ADDR_REG = 11

# set host to IP of BS/slaves/servers


CLIENTS = []

def start_client():
    """
    Setup for modbus client/master
    Start client/master and set up logging
    """

    #Get IP addresses and ports of slaves from "config_HMI.json"
    with open("HMI/config_HMI.json", "r", encoding = "utf-8") as f:
        json_data = json.load(f)

    CLIENTS.append(ModbusClient(host = json_data["HMI_CONNECT_TO_SLAVE"]["SLAVE1"], port = json_data["HMI_CONNECT_TO_SLAVE"]["PORT1"], auto_open = True, auto_close = True, timeout = 1))
    CLIENTS.append(ModbusClient(host = json_data["HMI_CONNECT_TO_SLAVE"]["SLAVE2"], port = json_data["HMI_CONNECT_TO_SLAVE"]["PORT2"], auto_open = True, auto_close = True, timeout = 1))
    CLIENTS.append(ModbusClient(host = json_data["HMI_CONNECT_TO_SLAVE"]["SLAVE3"], port = json_data["HMI_CONNECT_TO_SLAVE"]["PORT3"], auto_open = True, auto_close = True, timeout = 1))
    CLIENTS.append(ModbusClient(host = json_data["HMI_CONNECT_TO_SLAVE"]["SLAVE4"], port = json_data["HMI_CONNECT_TO_SLAVE"]["PORT4"], auto_open = True, auto_close = True, timeout = 1))
    CLIENTS.append(ModbusClient(host = json_data["HMI_CONNECT_TO_SLAVE"]["SLAVE5"], port = json_data["HMI_CONNECT_TO_SLAVE"]["PORT5"], auto_open = True, auto_close = True, timeout = 1))
    logging.basicConfig()

    slave_up_list = []
    print('CLIENTS : ',CLIENTS)
    for i, client in enumerate(CLIENTS):
        state = client.open()
        print('state : ',state)
        print("CLIENT", i, ":", state)
        #Try to connect again if failed
        while not state:
            print("NO CONNECTION TO SLAVE:", i)
            sleep(0.3)
            state = client.open()
        print("CLIENT", i, ":", state)

        state = client.write_single_coil(POWER_ADDR_COIL, 1)
        slave_up_list.append(state)
        f = client.write_multiple_coils(2, [1,1,1,1])

    cur_time = datetime.datetime.now()
    time_str = cur_time.strftime('%H:%M:%S')
    log = f"({time_str})-[MODBUS_MASTER] Master starting"
    logger.log(0, log)

    print("Master is online...")
    cur_time = datetime.datetime.now()

    time_str = cur_time.strftime('%H:%M:%S')
    log = f"({time_str})-[MODBUS_MASTER] Master is online..."
    logger.log(0, log)

    cur_time = datetime.datetime.now()

    time_str = cur_time.strftime('%H:%M:%S')
    log = f"({time_str})-[MODBUS_MASTER] Slave connection -  1:{slave_up_list[0]}, 2:{slave_up_list[1]}, 3:{slave_up_list[2]}, 4:{slave_up_list[3]}, 5:{slave_up_list[4]}"
    logger.log(0, log)

def get_bitrate(bs_id):
    """
    Calls read_register to get the bitrate registers
    """
    bitlist = read_register(bs_id = bs_id, choice = "BITR")
    return bitlist

def get_users(bs_id):
    """
    Calls read_register to get user registers
    """
    users = read_register(bs_id, "USR")
    return users

def change_gain(bs_id, gain):
    """
    Write to holding register the value of antenna gain
    """
    write_register(bs_id, gain, "GAIN")
    return True

def change_antenna_power(bs_id, antenna_id, status):
    """
    Write to coil containing status of antenna
    """
    write_coil(bs_id, status, "ANTENNA", antenna_id+1)
    return True

def read_register(bs_id, choice):
    """
    Reads registers on address calculated by id and choice
    data is "function code" and determines address and length to read
    """
    # read bitrate register
    client = CLIENTS[bs_id - 1]
    if choice == "BITR":
        bitrate_list = []
        bitrate = client.read_input_registers(BITRATE_ACTIVE_ADDR_REG, 8)
        if bitrate is None:
            return False
        bitrate_list.append(sum(bitrate[0:4]))
        bitrate_list.append(sum(bitrate[4:]))

        return bitrate_list

    # read user count register
    if choice == "USR":
        users = sum(client.read_input_registers(USERS_ADDR_REG, 2))
        return users
    print("One bitrate error here with", bs_id)
    return False

def write_register(bs_id, data, choice):
    """
    Write to holding register, address calculated with bs_idand choice.
    Data gets written to holding register.
    """
    client = CLIENTS[bs_id - 1]
    # write new value into gain register
    if choice == "GAIN":
        client.write_single_register(GAIN_ADDR_REG, data)
        return True
    return False

def read_coil(bs_id):
    """
    Reads coils
    """
    client = CLIENTS[bs_id - 1]
    #read 5 bits contining statuses for bs's
    coil_bitrate = client.read_coils(0, 5)
    print("coil", coil_bitrate)

def write_coil(bs_id = None, value = None, data = None, addr = None):
    """
    Writes value into address pointed to by id or addr
    """
    #print("[Debug] trying to write", id, " to give it,", value)

    if data == "POW":
        addr = POWER_ADDR_COIL
    client = CLIENTS[bs_id - 1]

    a = client.write_single_coil(addr, value)
    #print("[Debug] Wrote to coil", id, " and gave it value,", value)
    if a is True:
        pass
    else:
        print("ERROR: Can't write to coil - ",addr)
        current_time = datetime.datetime.now()

        time_string = current_time.strftime('%H:%M:%S')
        log = f"({time_string})-[MODBUS_MASTER] ERROR: Can't write to coil - " + addr
        logger.log(0, log)
