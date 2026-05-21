from flask import Flask, request, jsonify
from flask_cors import CORS
import oracledb

app = Flask(__name__)
CORS(app)

connection = oracledb.connect(
    user="bkuser",
    password="db123",
    dsn="localhost:1521/XEPDB1"
)
cursor = connection.cursor()
print("oracle database connected successfully")
#create account 
@app.route('/create_account', methods=['POST'])
def create_account():

    data = request.json

    sql = """
    INSERT INTO Acco
    VALUES (:1,:2,:3,:4,:5,:6)
    """

    values = (
        data['acc_no'],
        data['name'],
        data['address'],
        data['phone'],
        data['email'],
        data['balance']
    )

    cursor.execute(sql, values)

    connection.commit()

    return jsonify({
        "message": "Account Created Successfully"
    })
#deposit amount
@app.route('/deposit', methods=['POST'])
def deposit():

    data = request.json

    sql = """
    UPDATE Acco
    SET balance = balance + :1
    WHERE acc_no = :2
    """

    cursor.execute(sql, (
        data['amount'],
        data['acc_no']
    ))
# Insert transaction record
    transaction_sql = """
    INSERT INTO tra
    VALUES (:1, :2, :3, :4, SYSDATE)
    """

    cursor.execute(transaction_sql, (
        data['trans_id'],     # Example: 33
        data['acc_no'],       # Example: 5
        'deposit',            # Transaction type
        data['amount']        # Example: 2000
    ))

    connection.commit()

    return jsonify({
        "message": "Amount Deposited and transaction stored"
    })
#withdraw amount
@app.route('/withdraw', methods=['POST'])
def withdraw():

    data = request.json

    sql = """
    UPDATE Acco
    SET balance = balance - :1
    WHERE acc_no = :2
    """

    cursor.execute(sql, (
        data['amount'],
        data['acc_no']
    ))
# Store withdraw transaction
    transaction_sql = """
    INSERT INTO tra
    VALUES (:1, :2, :3, :4, SYSDATE)
    """

    cursor.execute(transaction_sql, (
        data['trans_id'],   # Example: 44
        data['acc_no'],     # Example: 5
        'withdraw',
        data['amount']      # Example: 1000
    ))
    connection.commit()

    return jsonify({
        "message": "Amount Withdrawn"
    })
#balance check 
@app.route('/balance/<int:acc_no>', methods=['GET'])
def balance(acc_no):

    sql = """
    SELECT balance
    FROM Acco
    WHERE acc_no = :1
    """

    cursor.execute(sql, [acc_no])

    result = cursor.fetchone()

    return jsonify({
        "balance": result[0]
    })
#transaction statement 
@app.route('/transactions/<int:acc_no>', methods=['GET'])
def transactions(acc_no):

    sql = """
    SELECT *
    FROM Tra
    WHERE acc_no = :1
    """

    cursor.execute(sql, [acc_no])

    rows = cursor.fetchall()

    return jsonify(rows)

@app.route('/string',methods=['GET'])
def string():
    return "plalanisamy"

#amount transfer
@app.route('/transfer', methods=['POST'])
def transfer():

    data = request.json

    sender = data['sender']
    receiver = data['receiver']
    amount = data['amount']

    # Deduct sender
    cursor.execute("""
    UPDATE Acco
    SET balance = balance - :1
    WHERE acc_no = :2
    """, (amount, sender))

    # Add receiver
    cursor.execute("""
    UPDATE Acco
    SET balance = balance + :1
    WHERE acc_no = :2
    """, (amount, receiver))

    connection.commit()

    return jsonify({
        "message": "Transfer Successful"
    })
#update account 
@app.route('/update_account', methods=['PUT'])
def update_account():

    data = request.json

    sql = """
    UPDATE Acco
    SET address=:1,
        phone=:2,
        email=:3
    WHERE acc_no=:4
    """

    cursor.execute(sql, (
        data['address'],
        data['phone'],
        data['email'],
        data['acc_no']
    ))

    connection.commit()

    return jsonify({
        "message": "Account Updated"
    })
#delete account
@app.route('/delete_account/<int:acc_no>', methods=['DELETE'])
def delete_account(acc_no):

    sql = """
    DELETE FROM Acco
    WHERE acc_no = :1
    """

    cursor.execute(sql, [acc_no])

    connection.commit()

    return jsonify({
        "message": "Account Deleted"
    })
#main method
if __name__ == '__main__':
    app.run(debug=True)