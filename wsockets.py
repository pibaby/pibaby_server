import asyncio
import websockets
from config import update_config, read_config
import json
import traceback
import sqlite3
import logging
def get_data(data):
    db = sqlite3.connect("baby.db")
    s = db.cursor()
    rows = None
    if "filter" in data and "filter_data" in data:
        rows = s.execute(f"""
        SELECT * FROM '{data["table"]}'
        WHERE '{data["filter"]}'
        BETWEEN '{data["filter_data"][0]}'
        AND '{data["filter_data"][1]}'
        """).fetchall()
    else:
        rows = s.execute(f"""
        SELECT * FROM '{data["table"]}'
        """).fetchall()
    logging.info(rows)
    return rows

def delete_from_table(data):
    result = json.dumps({"action":"success","message":f"Event has been deleted"})
    try:
        update = json.loads(data)['data']
        print(update)
        db = sqlite3.connect("baby.db")
        s = db.cursor()
        s.execute(f"""
        DELETE FROM {update['table']}
        WHERE id = {update['id']}
        """)
        db.commit()
    except Exception as e:
        result = json.dumps({"action":"error","message":f"ERROR delete_from_table: {e}"})
    return result

def insert_into_table(data):
    result = json.dumps({"action":"success","message":"Event has been saved"})
    try:
        update = json.loads(data)['data']
        print(update)
        db = sqlite3.connect("baby.db")
        s = db.cursor()
        if update['end'] is None:
            s.execute(f"""
            INSERT INTO {update['table']} (timestamp,title,color)
            VALUES('{update['start']}','{update['title']}','{update['color']}')
            """)
            db.commit()
        else:
            s.execute(f"""
            INSERT INTO {update['table']} (start_timestamp, end_timestamp, title, color)
            VALUES('{update['start']}','{update['end']}','{update['title']}','{update['color']}')
            """)
            db.commit()
    except Exception as e:
        result = json.dumps({"action":"error","message":f"ERROR insert_into_table: {e}"})
    return result

def update_table(data):
    result =json.dumps({"action":"success","message":"Event has been updated"})
    try:
        update = json.loads(data)['data']
        print(update)
        db = sqlite3.connect("baby.db")
        s = db.cursor()
        if update['end'] is None:
            s.execute(f"""
            UPDATE {update['table']}
            SET
            timestamp = '{update['start']}',
            title = '{update['title']}',
            color = '{update['color']}'
            WHERE id = {update['id']}
            """)
            db.commit()
        else:
            s.execute(f"""
            UPDATE {update['table']}
            SET
            start_timestamp = '{update['start']}',
            end_timestamp = '{update['end']}',
            title = '{update['title']}',
            color = '{update['color']}'
            WHERE id = {update['id']}
            """)
            db.commit()
    except Exception as e:
        result = json.dumps({"action":"error","message":f"ERROR update_table {e}"})
    return result


async def socket(websocket, path):
    while True:
        message = await websocket.recv()
        greeting = f"Hello from server!"
        try:
            data = json.loads(message)
            logging.info(f"< client {data}")
            result = None
            if data["action"] == "init":
                sleep  = get_data({"table":"sleep"})
                poops  = get_data({"table":"poops"})
                wet_diaper  = get_data({"table":"wet_diaper"})
                await websocket.send(json.dumps({
                    "action":"init",
                    "sleep":sleep,
                    "poops":poops,
                    "wet_diaper":wet_diaper,
                    "settings": read_config()
                }))
            elif data["action"] == "settings":
                result = update_config(data["settings"])
                await websocket.send(result)
            elif data["action"] == "update":
                result = update_table(message)
                await websocket.send(result)
            elif data["action"] == "delete":
                result = delete_from_table(message)
                await websocket.send(result)
            elif data["action"] == "insert":
                result = insert_into_table(message)
                await websocket.send(result)

        except Exception as ex:
            print(''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))
            await websocket.send(json.dumps({
            "action":"error",
            "message": f"ERROR on websocket {ex}" }))
            break
        except JSONDecodeError as e:
            logging.error(f"wsockets json error: {e}")
            await websocket.send(json.dumps({
            "action":"error",
            "message": f"ERROR on websocket JSON {e}" }))

        await websocket.send(json.dumps({
            "action":"console",
            "message": greeting }))

def run():
    start_server = websockets.serve(socket, "localhost", 8765)
    print(f"serving localhost on port 8765")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()



