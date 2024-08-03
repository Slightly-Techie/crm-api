from io import BytesIO
import re
import logging
from datetime import datetime
from core.config import settings
from fastapi import UploadFile
import requests
import cairosvg

import boto3
from botocore.exceptions import ClientError

# from utils.s3 import upload_file_to_s3

bucket_name = settings.AWS_BUCKET_NAME
region = settings.AWS_REGOIN
access_key = settings.AWS_ACCESS_KEY
secret_key = settings.AWS_SECRET_KEY


def get_skills_image(skill_name: str):
    """Attempt to get the skills image

    :param: skill_name: str
    The name of the skill to get the image for
    """
    icon_name = f"logos:{skill_name}"
    response = get_icon(icon_name)
    if response:
        if response.isnumeric():
            return None
        url = save_svg_as_png(response, skill_name)
        return url
    else:
        return None


def get_icon(icon_name):
    url = f"https://api.iconify.design/{icon_name.lower()}.svg"
    response = requests.get(url)
    # print(f"Status Code is {response.status_code}, {response.text}")
    if response.status_code == 200:
        return response.text
    else:
        return None

def save_svg_as_png(svg_data, skill_name):
    png_output = BytesIO()
    cairosvg.svg2png(bytestring=svg_data, write_to=png_output)
    png_output.seek(0)
    url = upload_file_to_s3(png_output, skill_name, "skills")
    print(f"Url is {url}")
    return url


def upload_file_to_s3(file: UploadFile, username, type: str) -> str:
    s3 = boto3.client('s3', region_name=region,
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    try:
        name = ''.join(e for e in username if e.isalnum())
        date = datetime.now().strftime("%Y%m%d-%H-%M-%S")
        file_name = f"{username}/{type}/{date}/{name}.png"
        url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

        s3.upload_fileobj(file, bucket_name, file_name)
        return url
    except ClientError as e:
        logging.error(f"Client Error {e}")
        return False


tools = [
    "Agile/Scrum", "Android", "Angular", "AngularJS", "Ansible", "Apache", "ASP.NET", "AWS",
    "Backbone.js", "Bitbucket", "Bootstrap", "C#", "C/C++", "Cassandra", "Chef", "Cloud Computing",
    "Computer Vision", "Dart", "Data Analysis", "Data Science", "Django", "Docker", "Ember.js",
    "Express.js", "FastAPI", "Firewall Management", "Flask", "Flutter", "GIS", "Git/GitHub", "GitLab",
    "Go", "Google Cloud Platform (GCP)", "GraphQL", "Groovy", "Heroku", "Hibernate", "HTML/CSS",
    "Intrusion Detection Systems (IDS)", "iOS", "Java", "JavaScript", "Jenkins", "jQuery",
    "Keras", "Kotlin", "Kubernetes", "Laravel", "Linux", "Lua", "MATLAB", "Microsoft SQL Server",
    "Microservices", "MongoDB", "MySQL", "Natural Language Processing (NLP)", "Neo4j", "Nginx",
    "Node.js", "OpenCV", "Oracle", "Penetration Testing", "Perl", "PHP", "PostgreSQL", "Project Management",
    "PyTorch", "Python", "React", "React Native", "Redis", "Redux", "Redux-Saga", "Reinforcement Learning",
    "RESTful API", "Ruby", "Ruby on Rails", "Rust", "Sass/Less", "Scala", "Scikit-learn",
    "Security Auditing", "Security Information and Event Management (SIEM)", "Shell Scripting",
    "Spring Framework", "SQLite", "Swift", "TensorFlow", "Terraform", "Travis CI", "TypeScript",
    "User Experience (UX) Design", "User Interface (UI) Design", "VB.NET", "Vagrant", "Virtualization",
    "Vue.js", "VPN", "WebSockets", "Windows Server", "Xamarin"
]
