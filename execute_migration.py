import os
import mysql.connector
import sys

AWS_RDS_ENDPOINT = "terraform-0a22e14d0c72c9c6fb0f58e675.cope6ooyg8yw.us-east-1.rds.amazonaws.com:3306" # You will change this shortly

def run_pipeline():
    print("\n[1/4] Connecting to Local Docker DB to check Encodings...")
    db = mysql.connector.connect(host="localhost", user="root", password="EnterprisePass2026", database="corporate_data")
    cursor = db.cursor()
    
    cursor.execute("SELECT TABLE_NAME, TABLE_COLLATION FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'corporate_data'")
    for name, collation in cursor.fetchall():
        print(f" -> Found Table: '{name}' | Collation: {collation}")
        if "latin1" in collation:
            print(f" ⚠️ Remediation Triggered: Shifting '{name}' to modern utf8mb4 before exporting...")
            #cursor.execute(f"ALTER TABLE {name} CONVERT TO CHARACTER SET utf8mb4 COLLATION utf8mb4_0900_ai_ci")
            cursor.execute(f"ALTER TABLE {name} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")

            db.commit()
    
    print("\n[2/4] Executing Production-Grade Dump (mysqldump)...")
    #dump_cmd = "docker exec local-enterprise-db mysqldump --single-transaction --quick -u root -pEnterprisePass2026! corporate_data > migration_dump.sql"
    dump_cmd = "mysqldump --single-transaction --quick -h 127.0.0.1 -P 3306 -u root -pEnterprisePass2026 corporate_data > migration_dump.sql"
    if os.system(dump_cmd) != 0:
        print("Extraction Failed."); sys.exit(1)
        
    print("\n[3/4] Streaming data directly over the wire to AWS RDS...")
    clean_host = AWS_RDS_ENDPOINT.split(":")[0]
    import_cmd = f"mysql -h {clean_host} -P 3306 -u cloud_admin -pCloudSecurePass2026! corporate_data_cloud < migration_dump.sql"
    if os.system(import_cmd) != 0:
        print("Cloud Injection Failed."); sys.exit(1)
        
    print("\n[4/4] Post-Migration Cleanup...")
    if os.path.exists("migration_dump.sql"):
        os.remove("migration_dump.sql")
    print("🚀 SUCCESS: Enterprise Migration Completed.")

if __name__ == "__main__":
    run_pipeline()
