# RNA explorer

**RNA Explorer** (RNA-E) is an Amazon Web Services (AWS) hosted web application, designed for quick and easy analysis of raw bulk RNA sequencing (RNA-seq) data. Users can upload a CSV file containing raw  gene expression counts data and RNA-E will quickly produce useful detailed tables and visualizations. As RNA-E is hosted on AWS, RNA-E is scalable, secure and efficient and, in its current state, can handle 10-20 concurrent users.

## Features

- **CSV File Upload:** Upload raw bulk RNA-seq data in CSV format (samples as columns, genes as rows).
- **Data Table:** View processed gene expression data in easy to use tables.
- **Data Visualization:** View nice and clear graphs to explore gene expression.
- **AWS Integration:** RNA-E leverages AWS for data storage, computation, and deployment to provide a robust and scalable web-app solution for on-the-go bioinformatics. This web-app 
- **CI/CD** RNA_E has CI/CD implemented, meaning pushes to main are deployed on AWS.
- **User Authentication:** RNA-E has integrity - with a secure login system to protect data and maintain privacy.

## Technology Stack

- **Frontend:** Bootstrap CSS framework (https://getbootstrap.com/) and DataTables Javascript HTML table library (https://datatables.net/).
- **Backend:** Python 3.9 Flask 3.0.3 web framework.
- **Data Processing:** Pandas 2.2.2 and numpy 2.0.1 for data manipulation and matplotlib 3.9.2 and Seaborn 0.13.2 for plotting.
- **Deployment:** AWS for application deployment, Flask-SQLAlchemy 3.1.1 SQLite based Flask-login 0.6.3 for authentication, CloudWatch for monitoring.
- **Version Control:** Git, hosted on GitHub with CI/CD implemented via GitHub Actions.

## Installation

- **Clone the repository:** 
 ```

git clone https://github.com/YEBADI/rna_explorer.git
cd rna_explorer

 ```

- **Set up the environment:**
 ```

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

 ```
- **Run the application:**
 ```

python app/app.py

 ```
## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For any inquiries or support, please contact yusefbadi@gmail.com.
