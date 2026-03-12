from io import BytesIO
import logging
from datetime import datetime

import requests
import cairosvg
import cloudinary
import cloudinary.uploader

from core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

logger = logging.getLogger(__name__)


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


def get_icon(icon_name) -> str | None:
    url = f"https://api.iconify.design/{icon_name.lower()}.svg"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None


def save_svg_as_png(svg_data, skill_name) -> str | None:
    png_output = BytesIO()
    cairosvg.svg2png(bytestring=svg_data, write_to=png_output)
    png_output.seek(0)
    return upload_bytes_to_cloudinary(png_output, skill_name, "skills")


def upload_bytes_to_cloudinary(data: BytesIO, public_id_prefix: str, folder: str) -> str | None:
    date = datetime.now().strftime("%Y%m%d-%H-%M-%S")
    public_id = f"{public_id_prefix}/{folder}/{date}"
    try:
        result = cloudinary.uploader.upload(data, public_id=public_id, resource_type="image")
        return result["secure_url"]
    except Exception as e:
        logger.error("Cloudinary upload failed: %s", e)
        return None


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
