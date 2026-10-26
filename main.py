import random
from datetime import datetime
from html import escape
from pyscript import document, when

# ---- Edit these sample prices (PHP) ----
PRICE_PER_PAGE = {
    ("short", "bw"): 2.00,
    ("a4", "bw"): 2.00,
    ("long", "bw"): 3.00,
    ("short", "color"): 8.00,
    ("a4", "color"): 8.00,
    ("long", "color"): 10.00,
}
DELIVERY_FEE = 20.00
PAPER_NAMES = {"short": "Short", "a4": "A4", "long": "Long"}
COLOR_NAMES = {"bw": "Black & White", "color": "Full Color"}


def get_int(element_id, default=1):
    """Read a positive whole number from an input box."""
    try:
        value = int(document.querySelector(element_id).value)
        return value if value > 0 else default
    except (ValueError, TypeError):
        return default


def compute():
    pages = get_int("#pages")
    copies = get_int("#copies")
    paper = document.querySelector("#paper").value
    color = document.querySelector("#color").value
    delivery = document.querySelector("#delivery").checked

    rate = PRICE_PER_PAGE[(paper, color)]
    print_cost = pages * copies * rate
    delivery_cost = DELIVERY_FEE if delivery else 0.0
    total = print_cost + delivery_cost

    return {
        "pages": pages, "copies": copies, "paper": paper, "color": color,
        "rate": rate, "print_cost": print_cost,
        "delivery": delivery, "delivery_cost": delivery_cost, "total": total,
    }


def update(event=None):
    d = compute()
    document.querySelector("#total").innerText = f"PHP {d['total']:,.2f}"

    lines = [
        f"<p><span>{d['pages']} pages x {d['copies']} copies x PHP {d['rate']:.2f}</span>"
        f"<span>PHP {d['print_cost']:,.2f}</span></p>"
    ]
    if d["delivery"]:
        lines.append(
            f"<p><span>Delivery fee</span><span>PHP {d['delivery_cost']:,.2f}</span></p>"
        )
    document.querySelector("#breakdown").innerHTML = "".join(lines)


# Recalculate whenever the customer changes something
for selector in ["#pages", "#copies", "#paper", "#color", "#delivery"]:
    when("input", selector)(update)
    when("change", selector)(update)


@when("click", "#order-btn")
def place_order(event):
    d = compute()
    name = document.querySelector("#name").value.strip() or "Customer"
    method = "Delivery" if d["delivery"] else "Pick-up"
    order_no = f"PP-{random.randint(1000, 9999)}"
    placed = datetime.now().strftime("%b %d, %Y %I:%M %p")

    def row(label, value):
        return f'<p class="rcpt"><span>{label}</span><span>{value}</span></p>'

    msg = document.querySelector("#message")
    msg.className = "message"
    msg.innerHTML = (
        '<div class="received"><div class="check-badge">&#10004;</div>'
        '<div><strong>Order Received</strong><span class="status">Status: Received</span></div></div>'
        + row("Order no.", order_no)
        + row("Name", escape(name))
        + row("Items", f"{d['pages']} pages x {d['copies']} copies, {PAPER_NAMES[d['paper']]}, {COLOR_NAMES[d['color']]}")
        + row("Method", method)
        + row("Placed", placed)
        + row("Total", f"PHP {d['total']:,.2f}")
    )
    msg.scrollIntoView()


# ---------------- Register / account (demo, stored in this browser only) ----------------
import json, hashlib
from pyscript import window

USERS_KEY = "printpal_users"
SESSION_KEY = "printpal_session"


def store_get(key):
    try:
        return window.localStorage.getItem(key)
    except Exception:
        return None


def store_set(key, value):
    try:
        window.localStorage.setItem(key, value)
    except Exception:
        pass


def store_remove(key):
    try:
        window.localStorage.removeItem(key)
    except Exception:
        pass


def load_users():
    raw = store_get(USERS_KEY)
    return json.loads(raw) if raw else {}


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def reg_message(text, ok=False):
    box = document.querySelector("#reg-msg")
    box.className = "reg-msg " + ("ok" if ok else "err")
    box.innerText = text


def refresh_user():
    raw = store_get(SESSION_KEY)
    nav = document.querySelector("#nav-user")
    form = document.querySelector("#reg-form")
    done = document.querySelector("#reg-done")
    if raw:
        user = json.loads(raw)
        first = user["name"].split()[0]
        nav.innerText = f"Hi, {first}"
        document.querySelector("#reg-welcome").innerText = f"Welcome, {user['name']}!"
        document.querySelector("#name").value = user["name"]
        form.hidden = True
        done.hidden = False
    else:
        nav.innerText = "Register"
        form.hidden = False
        done.hidden = True


@when("click", "#reg-btn")
def register(event):
    name = document.querySelector("#reg-name").value.strip()
    email = document.querySelector("#reg-email").value.strip().lower()
    school_id = document.querySelector("#reg-id").value.strip()
    pw = document.querySelector("#reg-pass").value
    pw2 = document.querySelector("#reg-pass2").value

    if not name or not email:
        return reg_message("Please enter your name and email.")
    if "@" not in email or "." not in email.split("@")[-1]:
        return reg_message("That email doesn't look right.")
    if len(pw) < 6:
        return reg_message("Password must be at least 6 characters.")
    if pw != pw2:
        return reg_message("Passwords don't match.")

    users = load_users()
    if email in users:
        return reg_message("That email is already registered.")

    users[email] = {"name": name, "id": school_id, "pw": hash_password(pw)}
    store_set(USERS_KEY, json.dumps(users))
    store_set(SESSION_KEY, json.dumps({"email": email, "name": name}))
    reg_message("Registration successful!", ok=True)
    refresh_user()


@when("click", "#logout-btn")
def logout(event):
    store_remove(SESSION_KEY)
    document.querySelector("#reg-msg").innerText = ""
    for field in ["#reg-name", "#reg-email", "#reg-id", "#reg-pass", "#reg-pass2", "#name"]:
        document.querySelector(field).value = ""
    refresh_user()


refresh_user()

update()  # show the first total when the page loads
