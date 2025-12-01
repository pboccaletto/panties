import json
import secrets
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    flash,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy

# ------------------------------------------------------------------------------
# Flask & DB setup
# ------------------------------------------------------------------------------

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///panties.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "change-me-in-prod"  # cambia in prod

db = SQLAlchemy(app)


# ------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------

class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    errors = db.relationship("ErrorEvent", backref="project", lazy=True)

    def __repr__(self):
        return f"<Project {self.id} {self.name!r}>"


class ErrorEvent(db.Model):
    __tablename__ = "error_events"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    event_id = db.Column(db.String(64), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    event_type = db.Column(db.String(32), nullable=False, default="exception")  # exception | message
    level = db.Column(db.String(16), nullable=True)

    exception_type = db.Column(db.String(128), nullable=True)
    message = db.Column(db.Text, nullable=True)
    stacktrace = db.Column(db.Text, nullable=True)

    tags_json = db.Column(db.Text, nullable=True)
    extra_json = db.Column(db.Text, nullable=True)
    raw_json = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def tags(self):
        try:
            return json.loads(self.tags_json) if self.tags_json else {}
        except Exception:
            return {}

    def extra(self):
        try:
            return json.loads(self.extra_json) if self.extra_json else {}
        except Exception:
            return {}

    def raw(self):
        try:
            return json.loads(self.raw_json) if self.raw_json else {}
        except Exception:
            return {}


# ------------------------------------------------------------------------------
# Create tables ONCE at startup (Flask 3 compatible)
# ------------------------------------------------------------------------------

with app.app_context():
    db.create_all()


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

def generate_api_key() -> str:
    # 32 hex chars ~ 128 bit random
    return secrets.token_hex(32)


def get_project_from_auth_header():
    """
    Reads Authorization: Bearer <API_KEY>
    Returns Project or None.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1].strip()
    if not token:
        return None
    return Project.query.filter_by(api_key=token).first()


# ------------------------------------------------------------------------------
# Web views
# ------------------------------------------------------------------------------

@app.route("/")
def index():
    return redirect(url_for("list_projects"))


@app.route("/projects", methods=["GET", "POST"])
def list_projects():
    # Create project via POST from same page
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Project name is required", "is-danger")
        else:
            api_key = generate_api_key()
            project = Project(
                name=name,
                description=description or None,
                api_key=api_key,
            )
            db.session.add(project)
            db.session.commit()
            flash("Project created", "is-success")
            return redirect(url_for("list_projects"))

    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("projects.html", projects=projects)


@app.route("/projects/<int:project_id>")
def project_detail(project_id: int):
    project = Project.query.get_or_404(project_id)
    errors = (
        ErrorEvent.query.filter_by(project_id=project.id)
        .order_by(ErrorEvent.created_at.desc())
        .all()
    )
    return render_template(
        "project_detail.html",
        project=project,
        errors=errors,
    )


@app.route("/projects/<int:project_id>/delete", methods=["POST"])
def delete_project(project_id: int):
    project = Project.query.get_or_404(project_id)

    # Delete all associated errors first
    ErrorEvent.query.filter_by(project_id=project.id).delete()

    # Delete the project
    db.session.delete(project)
    db.session.commit()

    flash(f"Project '{project.name}' has been deleted", "is-success")
    return redirect(url_for("list_projects"))


@app.route("/projects/<int:project_id>/errors/<int:error_id>")
def error_detail(project_id: int, error_id: int):
    project = Project.query.get_or_404(project_id)
    error = ErrorEvent.query.filter_by(id=error_id, project_id=project.id).first()
    if error is None:
        abort(404)
    return render_template(
        "error_detail.html",
        project=project,
        error=error,
    )


# ------------------------------------------------------------------------------
# API endpoint for panties client
# ------------------------------------------------------------------------------

@app.route("/api/events", methods=["POST"])
def api_events():
    project = get_project_from_auth_header()
    if project is None:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    # Expected structure from client:
    # {
    #   "event_id": "...",
    #   "timestamp": 1735590000,
    #   "environment": "...",
    #   "service_name": "...",
    #   "type": "exception" | "message",
    #   "exception": { "type": "...", "message": "...", "stacktrace": [...] },
    #   "message": { "text": "...", "level": "info" },
    #   "tags": { ... },
    #   "extra": { ... },
    #   "sdk": { ... }
    # }

    event_type = payload.get("type", "exception")

    # Convert timestamp (int) to datetime if present
    ts = payload.get("timestamp")
    try:
        if ts is not None:
            timestamp = datetime.fromtimestamp(ts)
        else:
            timestamp = datetime.utcnow()
    except Exception:
        timestamp = datetime.utcnow()

    exception_data = payload.get("exception") or {}
    message_data = payload.get("message") or {}
    tags = payload.get("tags") or {}
    extra = payload.get("extra") or {}

    # Flatten stacktrace list -> string
    stacktrace = None
    if exception_data.get("stacktrace"):
        if isinstance(exception_data["stacktrace"], list):
            stacktrace = "".join(exception_data["stacktrace"])
        else:
            stacktrace = str(exception_data["stacktrace"])

    error = ErrorEvent(
        project_id=project.id,
        event_id=payload.get("event_id"),
        timestamp=timestamp,
        event_type=event_type,
        level=message_data.get("level"),
        exception_type=exception_data.get("type"),
        message=(
            exception_data.get("message")
            if event_type == "exception"
            else message_data.get("text")
        ),
        stacktrace=stacktrace,
        tags_json=json.dumps(tags) if tags else None,
        extra_json=json.dumps(extra) if extra else None,
        raw_json=json.dumps(payload),
    )

    db.session.add(error)
    db.session.commit()

    return jsonify({"status": "ok", "id": error.id}), 201


# ------------------------------------------------------------------------------
# Main entrypoint
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
