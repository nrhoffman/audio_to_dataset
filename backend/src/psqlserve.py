import logging
import psycopg2

logging.basicConfig(level=logging.INFO)

class PsqlServe:
    def __init__(self, config):
        self.config = config
        self.createtables()

    def connectdb(self):
        try:
            return psycopg2.connect(database = self.config["DATABASE"]["Database"], 
                            user = self.config["DATABASE"]["UserName"], 
                            host= self.config["DATABASE"]["Host"],
                            password = self.config["DATABASE"]["Password"],
                            port = self.config["DATABASE"]["Port"],
                            connect_timeout=10)
        except Exception as e:
            logging.error(f"Connection error: {e}")
            return None
    
    def createtables(self):
        logging.info("Connecting to the database...")
        with self.connectdb() as connect:
            logging.info("Connected...")
            with connect.cursor() as cur:
                logging.info("Creating tables...")
                query = f"""CREATE TABLE IF NOT EXISTS original_wav(
                            id VARCHAR(100) PRIMARY KEY,
                            url VARCHAR(100),
                            type VARCHAR(50),
                            audio_chunk BYTEA,
                            sequence INTEGER)"""
                cur.execute(query)
                # query = f"""CREATE TABLE IF NOT EXISTS noise_samples(
                #             id VARCHAR(100) PRIMARY KEY,
                #             url VARCHAR(100),
                #             sec_id VARCHAR(100),
                #             audio_chunk BYTEA,
                #             sequence INTEGER)"""
                # cur.execute(query)
                # query = f"""CREATE TABLE IF NOT EXISTS spliced_audio(
                #             id VARCHAR(100),
                #             sequence INTEGER,
                #             audio BYTEA)"""
                # cur.execute(query)
                connect.commit()
    
    def droptables(self, table=None):
        with self.connectdb() as connect:
            with connect.cursor() as cur:
                if table == None:
                    cur.execute("""SELECT table_name FROM information_schema.tables
                        WHERE table_schema = 'public'""")
                    for t in cur.fetchall():
                        cur.execute("""DROP table IF EXISTS """ + t[0])
                else:
                    cur.execute("""DROP table IF EXISTS """ + table)
        return self.gettables()

    def gettables(self):
        data = {}
        with self.connectdb() as connect:
            with connect.cursor() as cur:
                cur.execute("""SELECT table_name FROM information_schema.tables
                            WHERE table_schema = 'public'""")
                for table in cur.fetchall():
                    print(table)
                    query = "SELECT COUNT(*) FROM " + table[0]
                    cur.execute(query)
                    data[table[0]] = cur.fetchall()
        return data
    
    def insertwav(self, table, id, type, audio, sec_id = None, chunk_size=1024 * 1024):
        try:
            with self.connectdb() as connect:
                with connect.cursor() as cur:
                    if table == "original_wav":
                        query = """INSERT INTO {}(id, url, type, audio_chunk, sequence) VALUES(%s, %s, %s, %s, %s)
                                ON CONFLICT DO NOTHING""".format(table)
                    elif table == "noise_samples":
                        query = """INSERT INTO {}(id, url, sec_id, audio_chunk, sequence) VALUES(%s, %s, %s, %s, %s)
                                ON CONFLICT DO NOTHING""".format(table)
                    
                    total_size = len(audio)
                    total_chunks = total_size // chunk_size + (1 if total_size % chunk_size > 0 else 0)
                    for i in range(total_chunks):
                        chunk_start = i * chunk_size
                        chunk_end = chunk_start + chunk_size
                        chunk = audio[chunk_start:chunk_end]

                        logging.info(f"Inserting chunk {i + 1} of {total_chunks}")
                        
                        if table == "original_wav":
                            new_id = f"{id}_{i}"
                            cur.execute(query, (new_id, id, type, chunk, i))
                        elif table == "noise_samples":
                            new_id = f"{id}_{sec_id}"
                            cur.execute(query, (new_id, id, sec_id, chunk, i))
                        connect.commit()
                        
                        logging.info(f"Inserted chunk {i + 1}/{total_chunks} ({(chunk_end / total_size) * 100:.2f}% complete)")
                    
            return {"success": True, "message": "Audio inserted in chunks successfully"}
    
        except Exception as e:
            logging.error(f"Error inserting data: {e}")
            return {"success": False, "error": str(e)}
        
    def getwav(self, table, id):
        try:
            with self.connectdb() as connect:
                with connect.cursor() as cur:
                    query = "SELECT audio_chunk FROM {} WHERE url = %s ORDER BY sequence".format(table)
                    cur.execute(query, (id,))
                    logging.info(f"Fetching chunks")
                    chunks = cur.fetchall()
                    if not chunks:
                        logging.warning("No audio chunks found for the specified ID.")
                    
                    logging.info(f"Joining chunks")
                    audio_data = b''.join(chunk[0] for chunk in chunks)

                    return audio_data
        
        except Exception as e:
            logging.error(f"Error retrieving audio from the database: {e}")
    
    def getoriginalwavs(self):
        try:
            with self.connectdb() as connect:
                with connect.cursor() as cur:
                    query = f"SELECT DISTINCT url, type FROM original_wav"

                    cur.execute(query)
                    
                    results = cur.fetchall()
                    
                    if not results:
                        logging.warning("No data found in table.")
                        return [{"url": "", "type": ""}]
                    
                    # Extract URLs from the result and return them as a list
                    unique_values = [{"url": result[0], "type": result[1]} for result in results]

                    return unique_values
    
        except Exception as e:
            logging.error(f"Error fetching unique types from table. Exception: {e}")
            return []
