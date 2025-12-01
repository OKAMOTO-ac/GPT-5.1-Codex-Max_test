import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///schedule.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "description": self.description or "",
        }


@app.before_first_request
def setup_database():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


def parse_event_payload(payload):
    title = (payload.get("title") or "").strip()
    description = (payload.get("description") or "").strip()
    start_time = payload.get("start_time")
    end_time = payload.get("end_time")

    if not title or not start_time or not end_time:
        abort(400, description="Title, start time, and end time are required.")

    try:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
    except ValueError:
        abort(400, description="Invalid date format. Use ISO 8601.")

    if end_dt < start_dt:
        abort(400, description="End time cannot be earlier than start time.")

    return title, description, start_dt, end_dt


@app.route("/api/events", methods=["GET"])
def list_events():
    events = Event.query.order_by(Event.start_time.asc()).all()
    return jsonify([event.to_dict() for event in events])


@app.route("/api/events", methods=["POST"])
def create_event():
    title, description, start_dt, end_dt = parse_event_payload(request.json or {})

    event = Event(title=title, description=description, start_time=start_dt, end_time=end_dt)
    db.session.add(event)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(500, description="Failed to create event.")

    return jsonify(event.to_dict()), 201


@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    title, description, start_dt, end_dt = parse_event_payload(request.json or {})

    event.title = title
    event.description = description
    event.start_time = start_dt
    event.end_time = end_dt

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(500, description="Failed to update event.")

    return jsonify(event.to_dict())


@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return "", 204


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
