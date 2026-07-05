import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# DB config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lost.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Upload config
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)


# ----------------- DATABASE MODEL -----------------
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    reg_no = db.Column(db.String(50))
    title = db.Column(db.String(100))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    contact = db.Column(db.String(50))
    image = db.Column(db.String(100))


# ----------------- HOME REDIRECT -----------------
@app.route("/")
def home():
    return redirect("/view_items")


# ----------------- ADD ITEM -----------------
@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":

        reg_no = request.form["reg_no"]
        title = request.form["title"]
        category = request.form["category"]
        description = request.form["description"]
        location = request.form["location"]
        contact = request.form["contact"]

        file = request.files["image"]
        filename = None

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        new_item = Item(
            reg_no=reg_no,
            title=title,
            category=category,
            description=description,
            location=location,
            contact=contact,
            image=filename
        )

        db.session.add(new_item)
        db.session.commit()

        return redirect("/view_items")

    return render_template("add_item.html")


# ----------------- VIEW ITEMS -----------------
@app.route("/view_items")
def view_items():
    search = request.args.get("search")
    category = request.args.get("category")

    query = Item.query

    if search:
        query = query.filter(Item.title.contains(search))

    if category:
        query = query.filter_by(category=category)

    items = query.all()

    categories = db.session.query(Item.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template(
        "view_items.html",
        items=items,
        categories=categories
    )


# ----------------- DELETE ITEM -----------------
@app.route("/delete/<int:id>", methods=["POST"])
def delete_item(id):
    item = Item.query.get_or_404(id)

    db.session.delete(item)
    db.session.commit()

    return redirect("/view_items")


# ----------------- EDIT ITEM -----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_item(id):
    item = Item.query.get_or_404(id)

    if request.method == "POST":

        item.reg_no = request.form["reg_no"]
        item.title = request.form["title"]
        item.category = request.form["category"]
        item.description = request.form["description"]
        item.location = request.form["location"]
        item.contact = request.form["contact"]

        file = request.files["image"]

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            item.image = filename

        db.session.commit()

        return redirect("/view_items")

    return render_template("edit_item.html", item=item)


# ----------------- RUN APP -----------------
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
