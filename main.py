from fastapi import FastAPI, HTTPException
import psycopg
import os
from dotenv import load_dotenv

# .env の読み込み（シンプル化）
load_dotenv()

app = FastAPI()

def get_conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require"
    )

@app.get("/")
def root():
    return {"message": "POS Backend API is running"}

@app.get("/products")
def get_all_products():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, price, jan_code, created_at FROM products;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [
            {
                "id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "jan_code": row[3],
                "created_at": row[4].isoformat()
            }
            for row in rows
        ]
    except Exception as e:
        print("❌ /products でエラー:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/products/{jan_code}")
def get_product_by_jan(jan_code: str):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, price, jan_code, created_at FROM products WHERE jan_code = %s;", (jan_code,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return {
                "id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "jan_code": row[3],
                "created_at": row[4].isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/health")
def health_check():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except:
        return {"status": "unhealthy", "database": "disconnected"}
