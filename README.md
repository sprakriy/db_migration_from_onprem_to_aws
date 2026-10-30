# Local-to-Cloud Enterprise Database Migration Pipeline

A robust, automated database migration pipeline that provisions a secure AWS RDS MySQL instance using Terraform, detects and remediates legacy table encodings from a local MariaDB database, dumps the data via mysqldump, and streams it over the wire to the cloud target.

---

## Architecture & Workflow

```mermaid
graph TD
    subgraph Local Environment
        A[Local MariaDB] --> B{Check Collation}
        B -->|Has latin1| C[Convert to utf8mb4]
        B -->|Already utf8| D[Ready for Export]
        C --> D
        D --> E[mysqldump Backup]
    end

    subgraph AWS Cloud
        F[Terraform Apply] --> G[AWS RDS MySQL]
    end

    E -->|Stream via mysql CLI| G
    G --> H[Migration Success]
    
```
Project Structure

# Start the service
sudo systemctl start mariadb

# Stop native service
sudo systemctl stop mariadb
# OR sudo systemctl stop mysql

# Remove the failed container attempt
docker rm local-mariadb

# Rerun your Docker command
docker run --name local-mariadb -e MYSQL_ROOT_PASSWORD=xxxxxx -p 3306:3306 -d mariadb:latest

mysql -h 127.0.0.1 -P 3306 -u root -p

# Create .venv environment
python3 -m venv .venv
source .venv/bin/activate
pip install mysql.connector

generate_data.py: Generates 10,000 mock ledger entries with legacy latin1 encoding.

main.tf: Terraform configuration for VPC, subnets, and RDS.

execute_migration.py: Automated pipeline script for collation check, dump, and stream.

README.md: Project documentation.

Step-by-Step Execution Guide
Generate Local Mock Data:


python3 generate_data.py
Provision AWS RDS Infrastructure:


terraform init
terraform apply -auto-approve
Run the Migration Pipeline:
Update the AWS_RDS_ENDPOINT in execute_migration.py with your Terraform output, then run:


python3 execute_migration.py
Cleanup (Teardown):


terraform destroy -auto-approve
    
