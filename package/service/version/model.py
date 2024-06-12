from ..database.db import connection

def get_version():

    cur = connection.cursor()

    try: 
        cur.execute('''
                SELECT * from "PBL7".model_version
                WHERE status=true
                LIMIT 1
                ''')
    
        connection.commit() 
    except: pass
    
    data = cur.fetchone()
    cur.close()
    
    if data == None: return None
    return data[1]

def change_version(version):
    try: 
        cur = connection.cursor()
        cur.execute('''
                UPDATE "PBL7".model_version
                SET status=true
                WHERE name='{}'
                '''.format(version))
    
        connection.commit() 
        cur = connection.cursor()
        cur.execute('''
                UPDATE "PBL7".model_version
                SET status=false
                WHERE name!='{}'
                '''.format(version))
        
        connection.commit()
        cur.close()
        return True
    except: return False
    
def get_all_version():
    cur = connection.cursor()

    try: 
        cur.execute('''
                SELECT * from "PBL7".model_version
                ''')
    
        connection.commit() 
    except: pass
    
    data = cur.fetchall()
    cur.close()
    
    if data == None: return None
    return data