from flask import Flask, render_template, request, redirect, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "smartwastekey"

class WasteItem:
    def __init__(self, waste_type, weight):
        self.waste_type = waste_type
        self.weight = weight
        self.timestamp = datetime.now()

    def process(self):
        return "Processing waste..."

class RecyclableWaste(WasteItem):
    def process(self):
        return f"♻️ Recycled {self.weight} kg successfully"

class HazardousWaste(WasteItem):
    def process(self):
        return f"⚠️ Hazardous waste disposed safely ({self.weight} kg)"

class OrganicWaste(WasteItem):
    def process(self):
        return f"🌱 Organic waste composted ({self.weight} kg)"

class RewardSystem:
    def __init__(self):
        self.__points = 0

    def calculate_points(self, waste):
        if waste.waste_type == "recyclable":
            return int(waste.weight * 15)
        elif waste.waste_type == "organic":
            return int(waste.weight * 10)
        else:
            return int(waste.weight * 5)

class EcoScore:
    def calculate_score(self, history):
        score = 0
        for item in history:
            if "Recycled" in item:
                score += 20
            elif "composted" in item:
                score += 15
            else:
                score += 5
        return score

class User:
    def __init__(self, username):
        self.username = username
        self.points = 0
        self.history = []
        self.recyclable_weight = 0
        self.organic_weight = 0
        self.hazardous_weight = 0
        self.balance = 0

    def add_activity(self, activity, points, waste_type, weight):
        self.history.append(activity)
        self.points += points
        if waste_type == "recyclable":
            self.recyclable_weight += weight
            self.balance += weight * 20
        elif waste_type == "organic":
            self.organic_weight += weight
            self.balance += weight * 10
        else:
            self.hazardous_weight += weight

users = {}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        session["user"] = username
        if username not in users:
            users[username] = User(username)
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")
    user = users[session["user"]]
    result = ""
    if request.method == "POST":
        waste_type = request.form["type"]
        weight = float(request.form["weight"])
        if waste_type == "recyclable":
            waste = RecyclableWaste(waste_type, weight)
        elif waste_type == "organic":
            waste = OrganicWaste(waste_type, weight)
        else:
            waste = HazardousWaste(waste_type, weight)
        result = f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {waste.process()}"
        reward = RewardSystem()
        points = reward.calculate_points(waste)
        user.add_activity(result, points, waste_type, weight)
    eco = EcoScore()
    eco_score = eco.calculate_score(user.history)
    return render_template("dashboard.html", user=user, result=result, eco_score=eco_score)

@app.route("/calculator")
def calculator():
    if "user" not in session:
        return redirect("/")
    user = users[session["user"]]
    total_money = (user.recyclable_weight * 20) + (user.organic_weight * 10)
    return render_template("calculator.html",
                           recyclable_weight=user.recyclable_weight,
                           organic_weight=user.organic_weight,
                           hazardous_weight=user.hazardous_weight,
                           total_money=total_money)

@app.route("/essentials", methods=["GET", "POST"])
def essentials():
    if "user" not in session:
        return redirect("/")
    user = users[session["user"]]
    message = ""
    items = {
        "Toothbrush & Toothpaste": 80,
        "Bath Soap": 40,
        "Shampoo": 120,
        "Face Wash": 100,
        "Hand Wash": 60,
        "Hair Oil": 90,
        "Shaving Kit": 150,
        "Deodorant": 200,
        "Moisturizer": 180,
        "Towel": 250,
        "Cooking Oil": 180,
        "Tea/Coffee": 120,
        "Rice & Flour": 300,
        "Pulses": 200,
        "Spices": 150,
        "Dishwash": 70,
        "Detergent": 160,
        "Floor Cleaner": 120,
        "Toilet Cleaner": 110,
        "Garbage Bags": 60,
        "Water Bottle": 100,
        "Mobile Charger": 300,
        "Slippers": 250,
        "Sanitary Pads": 120
    }
    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "buy":
            item = request.form.get("item", "")
            if item in items:
                price = items[item]
                if user.balance >= price:
                    user.balance -= price
                    message = f"✅ Purchased {item} for ₹{price}"
                else:
                    message = "❌ Not enough balance. Submit more waste to earn!"
            else:
                message = "❌ Item not found."
        elif action == "add_money":
            try:
                amount = float(request.form.get("amount", 0))
                upi = request.form.get("upi", "")
                if amount > 0 and upi:
                    user.balance += amount
                    message = f"✅ ₹{int(amount)} added via UPI: {upi}"
                else:
                    message = "❌ Enter a valid amount and UPI ID."
            except ValueError:
                message = "❌ Invalid amount entered."
        elif action == "pay_upi":
            item = request.form.get("item", "")
            upi = request.form.get("upi", "")
            if item in items and upi:
                price = items[item]
                message = f"💳 Payment of ₹{price} for {item} initiated to UPI: {upi}"
            else:
                message = "❌ Item or UPI ID missing."
        elif action == "withdraw":
            upi = request.form.get("upi", "")
            if upi and user.balance > 0:
                message = f"💸 ₹{user.balance} will be sent to UPI: {upi}"
                user.balance = 0
            elif user.balance <= 0:
                message = "❌ No balance to withdraw."
            else:
                message = "❌ Please enter your UPI ID."
    return render_template("dailyessentials.html", items=items, balance=user.balance, message=message)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return render_template("logout.html")

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=5000, debug=True)