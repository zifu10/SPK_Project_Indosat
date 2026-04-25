# ============================================================
# routes/main.py — Halaman Utama
# ============================================================

from flask import Blueprint, render_template
from utils.db import get_all_projects

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    projects = get_all_projects()
    total    = len(projects)
    return render_template('index.html', total_project=total)
