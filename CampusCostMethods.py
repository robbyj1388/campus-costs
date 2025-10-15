import mysql.connector

def serverLogin():
    try:
        connection = mysql.connector.connect(
            host = "classdb.it.mtu.edu",
            user = "cgclark",
            password = "Pineapple1!",
            database = "cgclark"
        )
        if connection.is_connected():
            print("Connected to MySQL database")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    return connection

def serverLogout(connection, cursor):
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

newBuilding("TEST")
def newVM(building_name, vm_id, location_description): #vm_id: 10 charcacter limit, location_description: 100 character limit, building_name is case sensitive
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        insert_query = f"INSERT INTO {building_name} (VMID, Loction) VALUES({vm_id}, {location_description})"
        cursor.execute(insert_query)
        update_building_query = f"UPDATE Buildings SET VMs = VMs + 1 WHERE Name = {building_name}"
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

        insert_query = f"INSERT INTO Products (Name, Price, VMID) VALUES({product_name}, {price}, {vm_id})"
        cursor.execute(insert_query)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)


def editPrice(product_name, vm_id, new_price, user_email):
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        get_old_price_query = f"SELECT Price FROM Products WHERE Name = {product_name} AND VMID = {vm_id}"
        cursor.execute(get_old_price_query)
        row = cursor.fetchone()
        old_price = row[0]
        edit_price_query = f"UPDATE Products SET Price = {new_price} WHERE Name = {product_name} AND VMID = {vm_id}"
        cursor.execute(edit_price_query)
        record_edit_query = f"INSERT INTO PriceEdits(VMID, ProductName, NewPrice, OldPrice, UserEmail) VALUES({vm_id}, {product_name}, {new_price}, {old_price}, {user_email})"
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

        get_stock_status_query = f"SELECT InStock FROM Products WHERE Name = {product_name} AND VMID = {vm_id}"
        row = cursor.fetchone()
        stock_status = row[0]
        if stock_status == 1:
            change_stock_status_query = f"UPDATE Products SET InStock = 0 WHERE Name = {product_name} AND VMID = {vm_id}"
        else:
            change_stock_status_query = f"UPDATE Products SET InStock = 1 WHERE Name = {product_name} AND VMID = {vm_id}"
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)



def authenticateLogin(user_email, user_password): #password is limited to 30 characters, returns true if email and password are correct, false if otherwise
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        get_password_query = f"SELECT Password FROM Users WHERE Email = {user_email}"
        cursor.execute(get_password_query)
        row = cursor.fetchone()
        password = row[0]
        
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
    finally :
        serverLogout(connection, cursor)
        
        if user_password == password:
            return True
        else:
            return False



def newUser(user_email, user_password):
    try:
        connection = serverLogin()
        cursor = connection.cursor()

        check_username_query = f"SELECT COUNT(*) FROM Users WHERE Email = {user_email}"
        cursor.execute(check_username_query)
        row = cursor.fetchone()
        if row[0] > 0 :
            user_created = False
        else:
            create_user_query = f"INSERT INTO Users(Email, Password) VALUES ({user_email}, {user_password})"
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
