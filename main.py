from fastapi import FastAPI, HTTPException
from database import connection, cursor

app = FastAPI()

@app.get("/")
def home():
    return {
    "message": "Personal Finance Management API"
    }

@app.post("/transactions")
def add_transactions(
    title:str,
    amount:float,
    category:str,
    type:str,
    date:str
):
    type = type.lower()
    if amount <= 0:
        return {"message": "Invalid amount"}

    if type not in ["income", "expense"]:
        return {"message": "Invalid transaction type"}
    
    cursor.execute("INSERT INTO transactions (title, amount, category, type, date) VALUES (?,?,?,?,?)",
                   (title, amount, category, type, date))
    connection.commit()

    return {"message": "Transaction added successfully"}

@app.get("/transactions")
def get_transactions():
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()

    result = []

    for transaction in transactions:
        result.append({
            "id": transaction[0],
            "title": transaction[1],
            "amount": transaction[2],
            "category": transaction[3],
            "type": transaction[4],
            "date": transaction[5],
        })

    return result


@app.get("/transactions/{transaction_id}")
def get_transaction_by_id(transaction_id:int):
    cursor.execute("SELECT * FROM transactions WHERE id=?", (transaction_id,))
    result = cursor.fetchone()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return {
            "id": result[0],
            "title": result[1],
            "amount": result[2],
            "category": result[3],
            "type": result[4],
            "date": result[5],
        }



@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id:int,
                       title:str,
                       amount: float,
                       category:str,
                       type:str,
                       date:str):
    type = type.lower()
    if amount <= 0:
        return {"message": "Invalid amount"}
    
    if type not in ["income", "expense"]:
        return {"message": "Invalid transaction type"}
    
    cursor.execute("UPDATE transactions SET title=?,amount=?,category=?,type=?,date=? WHERE id=?",
                   (title, amount, category, type, date, transaction_id))
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    
    connection.commit()
    return {"message": "Transaction updated successfully"}

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id:int):
    cursor.execute("DELETE FROM transactions WHERE id=?",
                   (transaction_id,))
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    
    connection.commit()
    return {"message": "Transaction deleted successfully"}

@app.get("/summary/income")
def total_income():
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type=?",("income",))
    result = cursor.fetchone()
    total = result[0] or 0

    return {"total_income": total}

@app.get("/summary/expense")
def total_expense():
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type=?", ("expense",))
    result = cursor.fetchone()
    total = result[0] or 0

    return {"total_expense":total}

@app.get("/summary/balance")
def total_balance():
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type=?", ("income",))
    income = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type=?", ("expense",))
    expense = cursor.fetchone()[0] or 0

    balance = income - expense

    return {"total_balance": balance}

@app.get("/summary/category/{category}")
def category_summary(category: str):
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE category=?", (category,))
    result = cursor.fetchone()
    total = result[0] or 0

    return {
        "category": category,
        "total": total
    }