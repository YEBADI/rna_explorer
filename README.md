# RNA explorer

**RNA Explorer** (RNA-E) is an Amazon Web Services (AWS) hosted web application, designed for quick and easy analysis of raw bulk RNA sequencing (RNA-seq) data. Users can upload a CSV file containing raw  gene expression counts data and RNA-E will quickly produce useful detailed tables and visualizations. As RNA-E is hosted on AWS, RNA-E is scalable, secure and efficient.

## Features

- **CSV File Upload:** Upload raw bulk RNA-seq data in CSV format.
- **Data Table:** View processed gene expression data in easy to use tables.
- **Data Visualization:** Plot nice and clear graphs to explore gene expression.
- **AWS Integration:** RNA-E leverages AWS for data storage, computation, and deployment to provide a robust and scalable web app solution.
- ** CI/CD ** RNA_E has CI/CD implemented, meaning pushes to main are deployed on AWS.
- **User Authentication:** RNA-E has integrity - with a secure login system to protect data and maintain privacy.

## Technology Stack

- **Frontend:** 
- **Backend:** Python 3.11 Flask web framework.
- **Data Processing:** Pandas and numpy for data manipulation and matplotlib for plotting.
- **Deployment:** AWS (S3 for storage, - for application deployment, nginx for authentication, CloudWatch for monitoring)
- **Version Control:** Git, hosted on GitHub

## Installation

- **Clone the repository:** 

1. git clone https://github.com/YEBADI/rna_explorer.git
2. cd rna_explorer

- **Set up the environment:**

1. python3 -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt

- **Run the application:**

1. python app.py

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For any inquiries or support, please contact yusefbadi@gmail.com.
