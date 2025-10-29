import mysql.connector #pip install mysql-connector-python
import os

def getLogin(): #retrieves login credentials from login.env file
    # Get the folder where this script lives
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Construct full path to login.env
    login_file = os.path.join(BASE_DIR, "login.env")
    
    # read text from login file for database password
    try:
        with open(login_file, "r") as file:
            text = file.read().strip()
            user = text.split()
            return [user[0], user[1]]
    except:
        print("ERROR: NO LOGIN FILE FOUND 404")
        return None


def serverLogin(): # connects to the database, returns the connection object, all other methods require this to function
    login = getLogin()
    if login is None:
        print("ERROR: Login is NONE")
    username, password = login

    try:
        connection = mysql.connector.connect(
            host = "classdb.it.mtu.edu",
            user = username,
            password = password,
            database = "cgclark"
        )
        if connection.is_connected():
            print("Connected to MySQL database")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    return connection

def serverLogout(connection, cursor): #closes the connection to the database, called at the end of each method
    connection.close()
    cursor.close()



def newBuilding(building_name): #building_name is case sensitive, capitalize first letter only
    try:
        connection = serverLogin()
        cursor = connection.cursor()
        
        val_insert = (building_name,)
        cursor.execute("INSERT INTO Buildings (Name) VALUES (%s)", val_insert)
        create_table_query = f"CREATE TABLE IF NOT EXISTS {building_name} LIKE BuildingTemplate"
        cursor.execute(create_table_query)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)


def newVM(building_name, room_num, location_description): #location_description: 100 character limit, building_name is case sensitive
    try:
        connection = serverLogin()
        cursor = connection.cursor()
        get_abbrev_query = f"SELECT abbrev FROM Buildings WHERE Name = '{building_name}'"
        cursor.execute(get_abbrev_query)
        row = cursor.fetchone()
        abbrev = row[0]
        base_prefix = f"VM{abbrev}{room_num}"
        count_vms_query = f"SELECT COUNT(*) FROM {building_name} WHERE VMID LIKE '{base_prefix}%'"
        cursor.execute(count_vms_query)
        row = cursor.fetchone()
        vm_count = row[0]
        vm_id = f"{base_prefix}{vm_count}"
        insert_query = f"INSERT INTO {building_name} (VMID, Location) VALUES('{vm_id}', '{location_description}')"
        cursor.execute(insert_query)
        update_building_query = f"UPDATE Buildings SET VMs = VMs + 1 WHERE Name = '{building_name}'"
        cursor.execute(update_building_query)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)



def newProduct(product_name, price, vm_id): #product_name is case sensitive on entry, price allows for 3 digits, 2 after the decimal
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        insert_query = f"INSERT INTO Products (Name, Price, VMID) VALUES('{product_name}', {price}, '{vm_id}')"
        cursor.execute(insert_query)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)


def editPrice(product_name, vm_id, new_price, user_email): #edits the price of a product in a specified VM, records the edit in PriceEdits table
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        get_old_price_query = f"SELECT Price FROM Products WHERE Name = '{product_name}' AND VMID = '{vm_id}'"
        cursor.execute(get_old_price_query)
        row = cursor.fetchone()
        old_price = row[0]
        edit_price_query = f"UPDATE Products SET Price = {new_price} WHERE Name = '{product_name}' AND VMID = '{vm_id}'"
        cursor.execute(edit_price_query)
        record_edit_query = f"INSERT INTO PriceEdits(VMID, ProductName, NewPrice, OldPrice, UserEmail) VALUES('{vm_id}', '{product_name}', {new_price}, {old_price}, '{user_email}')"
        cursor.execute(record_edit_query)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)
        


def reportStock(product_name, vm_id): #changes products in stock to out of stock, and vice versa
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        get_stock_status_query = f"SELECT InStock FROM Products WHERE Name = '{product_name}' AND VMID = '{vm_id}'"
        cursor.execute(get_stock_status_query)
        row = cursor.fetchone()
        stock_status = row[0]
        if stock_status == 1:
            change_stock_status_query = f"UPDATE Products SET InStock = 0 WHERE Name = '{product_name}' AND VMID = '{vm_id}'"
        else:
            change_stock_status_query = f"UPDATE Products SET InStock = 1 WHERE Name = '{product_name}' AND VMID = '{vm_id}'"
        cursor.execute(change_stock_status_query)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)

#reportStock("TestProduct2", "VMTES1210")

def authenticateLogin(user_email, user_password): #password is limited to 30 characters, returns true if email and password are correct, false if otherwise
    try:
        # Connect to the database
        connection = serverLogin()
        cursor = connection.cursor()
        
        # Use a parameterized query to prevent SQL injection
        query = "SELECT Password FROM Users WHERE Email = %s"
        cursor.execute(query, (user_email,))

        # Fetch the first row from the results (one user per email)
        row = cursor.fetchone()

        # If no user found 
        if row is None:
            return False

        password = row[0]

        # check password
        return user_password == password

    except mysql.connector.Error as err:
        print(f"Error: {err}")

        # Rollback any changes if the connection is active
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()

        return False

    finally:
        # clean up connections
        if 'connection' in locals() and 'cursor' in locals():
            serverLogout(connection, cursor)



def newUser(user_email, user_password): #creates a new user with the specified email and password, returns true if user created, false if email already exists
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        check_username_query = f"SELECT COUNT(*) FROM Users WHERE Email = '{user_email}'"
        cursor.execute(check_username_query)
        row = cursor.fetchone()
        if row[0] > 0 :
            user_created = False
        else:
            create_user_query = f"INSERT INTO Users(Email, Password) VALUES ('{user_email}', '{user_password}')"
            cursor.execute(create_user_query)
            user_created = True
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)
        return user_created



def fetchVMs(building_name): #returns a list of VM IDs in the specified building
    vm_list = []
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        fetch_vms_query = f"SELECT VMID FROM {building_name}"
        cursor.execute(fetch_vms_query)
        rows = cursor.fetchall()
        for row in rows:
            vm_list.append(row[0])
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)
        return vm_list



def fetchProducts(vm_id): #returns a list of product names and prices in the specified VM
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        fetch_products_query = f"SELECT Name, Price, CASE InStock WHEN 1 THEN 'In Stock' ELSE 'Out of Stock' END FROM Products WHERE VMID = '{vm_id}'"
        cursor.execute(fetch_products_query)
        rows = cursor.fetchall()
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)
        return rows

def fetchBuildings(): #returns a list of building names and how many VMs they have
    building_list = []
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        fetch_buildings_query = "SELECT Name, VMs FROM Buildings"
        cursor.execute(fetch_buildings_query)
        rows = cursor.fetchall()
        for row in rows:
            building_list.append((row[0], row[1]))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)
        return building_list
    
def fetchPriceEdits(): #returns a list of all price edits made, including VMID, product name, new price, old price, user email, and when the edit occured
    price_edit_list = []
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        fetch_price_edits_query = "SELECT VMID, ProductName, NewPrice, OldPrice, UserEmail, OccuredAt FROM PriceEdits"
        cursor.execute(fetch_price_edits_query)
        rows = cursor.fetchall()
        for row in rows:
            price_edit_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)
        return price_edit_list
