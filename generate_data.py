import mysql.connector
import random
import string

db = mysql.connector.connect(
    host="localhost", user="root", password="EnterprisePass2026", database="corporate_data"
)
cursor = db.cursor()

# Intentionally creating a table with old latin1 encoding to simulate messy legacy data
cursor.execute("""
CREATE TABLE IF NOT EXISTS ledger_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_number VARCHAR(20),
    transaction_amount DECIMAL(10,2),
    status VARCHAR(10)
) CHARACTER SET latin1;
""")

print("Generating 10,000 mock enterprise ledger entries...")
sql = "INSERT INTO ledger_entries (account_number, transaction_amount, status) VALUES (%s, %s, %s)"
values = [
    ("ACT-" + ''.join(random.choices(string.digits, k=8)), 
     round(random.uniform(10.00, 50000.00), 2), 
     random.choice(['SUCCESS', 'PENDING', 'FAILED'])) 
    for _ in range(10000)
]

cursor.executemany(sql, values)
db.commit()
print(f"Successfully loaded {cursor.rowcount} records into local Docker database!")
cursor.close()
db.close()
