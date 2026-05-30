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

    try:
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
            data['trans_id'],
            data['acc_no'],
            'deposit',
            data['amount']
        ))

        connection.commit()

        return jsonify({
            "message": "Amount Deposited and transaction stored"
        })

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        })
#withdraw amount
@app.route('/withdraw', methods=['POST'])
def withdraw():

    try:
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
            data['trans_id'],
            data['acc_no'],
            'withdraw',
            data['amount']
        ))

        connection.commit()

        return jsonify({
            "message": "Amount Withdrawn"
        })

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
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
#amount transfer
@app.route('/transfer', methods=['POST'])
def transfer():

    try:
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

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
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

    try:

        # Delete transactions first (child table)
        transaction_sql = """
        DELETE FROM TRA
        WHERE acc_no = :1
        """

        cursor.execute(transaction_sql, [acc_no])

        # Delete account next (parent table)
        account_sql = """
        DELETE FROM ACCO
        WHERE acc_no = :1
        """

        cursor.execute(account_sql, [acc_no])

        # Check whether account existed
        if cursor.rowcount == 0:
            connection.rollback()

            return jsonify({
                "message": "Account not found"
            }), 404

        connection.commit()

        return jsonify({
            "message": "Account Deleted"
        }), 200

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 500
#main method
if __name__ == '__main__':
    app.run(debug=True)