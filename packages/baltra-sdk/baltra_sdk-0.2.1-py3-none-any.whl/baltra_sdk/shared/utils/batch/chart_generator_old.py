from flask import current_app
import matplotlib.pyplot as plt
from PIL import Image, UnidentifiedImageError
import matplotlib.gridspec as gridspec
from matplotlib import rcParams
import requests
from io import BytesIO
from datetime import datetime
from baltra_sdk.shared.utils.postgreSQL_utils import connect_to_db, close_connection
import logging
import boto3
from io import BytesIO
from baltra_sdk.shared.utils.employee_data import Employee

"""
This script generates personalized rewards reports for employees based on their points and prizes available for their company.
It connects to a PostgreSQL database to fetch employee data, processes that data to generate visual reports, 
and uploads the reports to an S3 bucket. Each report includes a doughnut chart representing the employee's 
total available points and rewards.

The EmployeeCharts class is responsible for creating visualizations, adding a logo, and saving the generated 
report to an S3 bucket. The script also ensures that employee links to the reports are updated in the database.

This is part of the old chart generation framework and is triggered with a flask command

Functions:
- fetch_employee_ids: Fetches the list of active employee IDs for a given company.
- convert_data: Converts the employee data into the format required by the chart generator.
- generate_charts: Orchestrates the process of generating rewards charts for all employees in a company.
- EmployeeCharts class: Contains methods for creating rewards charts, adding logos, saving reports to S3, 
  and updating employee records in the database.
"""

#Fetch employee ids that match to company_id
def fetch_employee_ids(company_id, cur):
    """
    Fetches the list of active employee IDs for a given company.

    Args:
        company_id (int): The ID of the company.
        cur: The database cursor to execute the SQL query.

    Returns:
        list: A list of employee IDs.
    """
    query = """
        SELECT employee_id
        FROM employees
        WHERE company_id = %s
        AND active = true;
    """
    cur.execute(query, (company_id,))
    employee_ids = cur.fetchall()
    return [employee_id[0] for employee_id in employee_ids]  # Return a list of employee_ids

# Convert the data from original format to format required 
def convert_data(employee_id, company_id):
    """
    Converts employee data to the required format for generating rewards reports.

    Args:
        employee_id (int): The ID of the employee.
        company_id (int): The ID of the company.

    Returns:
        dict: A dictionary containing the employee's ID, company ID, total points, and rewards data.
    """
    employee_data = {
        "employee_id": str(employee_id),
        "company_id": str(company_id),
        "total_points": Employee().calculate_total_points(employee_id),
        "rewards": Employee().format_prizes_legacy(company_id=company_id)
    }

    return employee_data

class EmployeeCharts:
    """
    A class for generating and saving rewards charts for individual employees. 

    This class is responsible for creating personalized reports based on the employee's total points and 
    available rewards. It generates a visual representation of rewards in the form of doughnut charts, 
    includes an organization logo, and saves the generated report to an S3 bucket. Additionally, the 
    class updates the employee's record in the database with a link to their rewards report.

    Attributes:
        employee_data (dict): The employee's data including total points and rewards information.
        s3_bucket (str): The name of the S3 bucket where the reports will be saved.
        logo_path (str): The URL of the Baltra logo to be added to the reports.
        colors (dict): A dictionary of colors used for charts and design elements.
    """
    def __init__(self, employee_data,s3bucket='baltrabucket' ):
        self.employee_data = employee_data
        self.s3_bucket = s3bucket
        self.logo_path = "https://baltrabucket.s3.us-east-2.amazonaws.com/premios/Color+logo+-+no+background_small.png" ### add image from a url
        self.colors = self.get_colors()  
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['DejaVu Sans']
    
    #Definition of colors to be used in chart generation
    def get_colors(self):
        colors = {
            'traffic_light': ['#008450', '#b81d13'],
            'blue': ['#22A9B8', self.to_rgba('#22A9B8', 0.3)],
            'red': ['#E74C58', self.to_rgba('#E74C58', 0.3)],
            'grey': ['#B0B0B0', self.to_rgba('#B0B0B0', 0.3)],
            'purple': ['#8F6EAF', self.to_rgba('#8F6EAF', 0.3)],
        }
        return colors

    #Convert hex to rgb
    def to_rgba(self, hex_color, alpha):
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
        return (r, g, b, alpha)
    
    #Create a doughnut chart
    @staticmethod
    def create_doughnut(ax, sizes, colors, central_label, chart_title, label_size, title_size):
        wedges, _ = ax.pie(sizes, colors=colors, startangle=90)
        ax.axis('equal')
        # Add white circle in the middle to create a doughnut effect
        centre_circle = plt.Circle((0, 0), 0.70, color='white', fc='white', linewidth=0)
        ax.add_artist(centre_circle)
        # Split the center_label into two parts: one bold and one regular
        label_parts = central_label.split("\n")
        bold_label = label_parts[0] if len(label_parts) > 0 else ""
        regular_label = label_parts[1] if len(label_parts) > 1 else ""
        # Add central label bold
        ax.text(0, 0, bold_label, ha='center', va='center', fontsize=label_size, fontweight='bold')
        #Add central sub label not bold
        ax.text(0, -0.3, regular_label, ha='center', va='center', fontsize=label_size * 0.6)
        # Add chart title
        ax.text(0, -1.3, chart_title, ha='center', va='center', fontsize=title_size, fontweight='bold')
        # Add shadow effect to chart edges
        for w in wedges:
            w.set_edgecolor('gray')

    #Add Baltra Logo
    def add_logo(self, fig, x, y):
        """
        Adds Baltra Logo to the top right corner of the chart

        Args:
            fig : plt object.
            logo_path: url or location where the logo image is stored
            x, y : coordinates to locate the logo
        """
        response = requests.get(self.logo_path)
        if response.status_code == 200:
            try:
                img_logo = Image.open(BytesIO(response.content)).convert("RGBA").resize((75, 75))
            except UnidentifiedImageError:
                print("Cannot identify image file.")
        else:
            print(f"Failed to retrieve the image. Status code: {response.status_code}")
        ax_logo = fig.add_axes([x, y, 0.11, 0.11], anchor='NE')
        ax_logo.imshow(img_logo)
        ax_logo.axis('off')

    #Save report to AWS S3
    def save_report(self, plt, chart_type): 

        ###Uploads report to S3 and returns the URL.
        s3 = boto3.client('s3')
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)  # Rewind the buffer to start

        # Constructing the file name and path in S3
        path = f"{self.employee_data['employee_id']}/{chart_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}.png"

        # Upload to S3
        s3.upload_fileobj(
            buffer,
            self.s3_bucket,
            path,
            ExtraArgs={'ContentType': 'image/png'}
        )

        url = f"https://{self.s3_bucket}.s3.amazonaws.com/{path}"
        logging.info(f"Image Generated: {url}")
        plt.close()  # Close the figure to free up memory
        return url

    #Create rewards image
    def create_rewards_report(self):

        total_points = self.employee_data['total_points']
        rewards = self.employee_data['rewards']
        num_rewards = len(rewards)
        logging.info(f'Total Points: {total_points}')

        # Calculate the number of rows dynamically
        total_rows = num_rewards * 2 + 1  # 1 row for title, then 2 per reward
        height_ratios = [0.2] + [0.2, 1] * num_rewards  # Title row + repeating title/content for each reward

        # Create figure and gridspec
        fig = plt.figure(figsize=(6, 2.5 * num_rewards + 2))
        gs = gridspec.GridSpec(total_rows, 2, width_ratios=[1, 1], height_ratios=height_ratios)

        # Add report title
        fig.text(0.5, 1, "Premios Baltra", ha='center', fontsize=24, fontweight='bold')
        fig.text(0.5, 0.97, f"Puntos Disponibles:{total_points}", ha='center', fontsize=14)

        # Configure subplots for images and doughnut charts
        for i, data in enumerate(self.employee_data['rewards']):
            value = max(total_points,0)  # Use the calculated total_points instead of self.employee_data['total_points']
            total = data['points']
            image_path = data['image_url']
            title = data['title']
            row = i * 2 + 1

            # Add background color to the title rows
            if i % 2 != 0 or i % 2 == 0:  # Apply background color to rows 1, 3, 5
                ax_bg = fig.add_subplot(gs[row, :])
                ax_bg.set_facecolor(self.colors['red'][0])
                ax_bg.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax_bg.transAxes, color=self.colors['red'][0]))
                ax_bg.axis('off')

            ax_title = fig.add_subplot(gs[row, :])
            ax_title.axis('off')
            ax_title.text(0.5, 0.5, title, ha='center', va='center', color='white', fontsize=18, fontweight='bold')

            ax_img = fig.add_subplot(gs[row + 1, 0])
            response = requests.get(image_path)
            img = Image.open(BytesIO(response.content))
            
            ax_img.imshow(img)
            ax_img.axis('off')

            ax_chart = fig.add_subplot(gs[row + 1, 1])
            remaining = max(total - value,0)
            self.create_doughnut(ax_chart, [value, remaining], self.colors['blue'], f"{total}\npuntos", "", 24,18)


        # Add logo to the figure
        self.add_logo(fig, 0.76, 0.95)
        # Uploads figure and returns url 
        output_path = self.save_report(plt, "rewards")
        # Return output path
        return output_path


    #Update new links in employees database
    def update_employee_links(self, cur, conn, rewards_path):
        # SQL query to update the employee's context with the summarized conversation
        query = """
            UPDATE employees
            SET 
                rewards_path = %s
            WHERE employee_id = %s;
        """
        cur.execute(query, (rewards_path, self.employee_data["employee_id"]))  # Execute the query with the summary and employee ID as parameters
        conn.commit()  # Commit the transaction to save the changes
        logging.info(f'Links for employee_id: {self.employee_data["employee_id"]} saved successfuly')

def generate_charts(company_id):
    """
    Orchestrates the process of generating rewards charts for all employees in a company.

    Args:
        company_id (int): The ID of the company for which the charts will be generated.

    Returns:
        None
    """
    conn, cur = connect_to_db()
    # Fetch employee IDs for the given company
    employee_ids = fetch_employee_ids(company_id, cur)
    logging.info(f'employees: {len(employee_ids)}')
    # Iterate over each employee ID, fetch data, and generate charts
    for employee_id in employee_ids:
        employee_data = convert_data(employee_id, company_id) # Convert data as required for chart generator
        chart = EmployeeCharts(employee_data)  # Initialize EmployeeCharts
        rewards_path = chart.create_rewards_report()
        chart.update_employee_links(cur, conn, rewards_path)

    # Close the database connection
    close_connection(conn, cur)
