import csv
import os
from sys import stderr
import json
from flask import (
    Blueprint,
    request,
    render_template,
    session,
    current_app,
    redirect,
    url_for,
    send_from_directory,
)

from routes.utils.decorators import login_required

from models.Ticket import Ticket as TicketModel
from models.Ticket import CATEGORIES, LEVELS, GRADES, PRICES, DATE_FORMAT

from routes.utils.PaymentPDF import PaymentPDF
from routes.utils.PlSql import PlSql


Ticket = Blueprint("Ticket", __name__, url_prefix="/ticket")
PATH_DATA = "src/db/data.json"


# print("---SESSION", file=stderr)
# print(session["payment"], file=stderr)


def get_data(where=None) -> list:
    _ReferencePlSql = PlSql(current_app.config["DSN_PSQL"])
    data = list()
    slots = [
        "id",
        "ticketid",
        "personid",
        "levelid",
        "gradeid",
        "categoryid",
        "stateid",
        "write_uid",
        "write_at",
        "name",
        "flag",
    ]
    query = "SELECT id,ticketid,personid,levelid,gradeid,categoryid,stateid,write_uid,write_at,name,0 FROM ticket"
    if where is not None:
        query += where
    query += " ORDER BY id"
    _ReferencePlSql.exec(query)
    data = [dict(zip(slots, row)) for row in _ReferencePlSql.data]
    return data


@Ticket.route("/", defaults={"idx": None})
@Ticket.route("/<idx>")
@login_required
def tickets(idx):
    ladatos = list()
    if idx is None:
        data = get_data(" WHERE stateid = 'P'")
    else:
        data = get_data(f" WHERE id = {idx}")
    if session.get("payment"):
        print("---SESSION")
        print(session["payment"])
        for indice in range(len(data)):
            if data[indice]["id"] in session["payment"]:
                data[indice]["flag"] = 1    
    ladatos = data
    return render_template(
        "ticket.html",
        title="ticket",
        current_user=session["current_user"],
        datos=ladatos,
        levels=LEVELS,
        grades=GRADES,
        categories=CATEGORIES,
    )


@Ticket.route("/reset_pay")
@login_required
def reset_payment():
    session["payment"] = set()
    return {"ok": 1, "message": "SESSION LIMPIA"}


@Ticket.route("/add_pays")
@login_required
def add_payment():
    param = request.args.get("param").upper()
    session["payment"] = set()
    lst = param.split(",")
    for item in lst:
        session["payment"].add(int(item))
    return {"ok": 1, "message": "SESSION LIMPIA"}


@Ticket.route("/view_ticket/<int:idx>", methods=["GET"])
def view_ticket(idx):
    return get_data(f" WHERE id = {int(idx)}")[0]


@Ticket.route("/filter", methods=["GET"])
def filter_ticket():
    ladatos = list()
    param = request.args.get("param").upper()
    data = get_data(f" WHERE ticketid LIKE '%{param}%' OR name LIKE '%{param}%'")
    if session.get("payment"):
        for indice in range(len(data)):
            if data[indice]["id"] in session["payment"]:
                data[indice]["flag"] = 1    
    ladatos = data
    return render_template(
        "ticket.html",
        title="ticket",
        current_user=session["current_user"],
        datos=ladatos,
        search=param,
        levels=LEVELS,
        grades=GRADES,
        categories=CATEGORIES,
    )


@Ticket.route("/add_to_car", methods=["GET"])
def add_to_car():
    try:
        id = int(request.args.get("idx"))
        if not session.get("payment"):
            session["payment"] = set()
        if id not in session["payment"]:
            session["payment"].add(id)
    except Exception as err:
        print("---ERROR")
        print(err)
    return redirect(url_for("Ticket.tickets"))


@Ticket.route("/drop_from_car", methods=["GET"])
def drop_from_car():
    id = int(request.args.get("idx"))
    if session.get("payment"):
        if id in session["payment"]:
            session["payment"].remove(id)
    return redirect(url_for("Ticket.pays"))


@Ticket.route("/pay", methods=["GET"])
def pays():
    ladatos = list()
    total = 0
    if session.get("payment"):
        filter = ",".join([str(item) for item in session["payment"]])
        ladatos = get_data(f" WHERE id in ({filter})")
        for item in ladatos:
            total += PRICES[item["categoryid"]]
        print(ladatos)
    return render_template(
        "payment.html",
        title="payment",
        current_user=session["current_user"],
        datos=ladatos,
        categories=CATEGORIES,
        prices=PRICES,
        total=total
    )


@Ticket.route("/drop_ticket", methods=["GET"])
def drop_ticket():
    _ReferencePlSql = PlSql(current_app.config["DSN_PSQL"])
    idx = int(request.args.get("idx"))
    ladata = get_data(f" WHERE id = {int(idx)}")
    if ladata:
        query = f"UPDATE ticket SET stateid = 'X' WHERE id = {idx}"
        _ReferencePlSql.exec(query)
    return redirect(url_for("Ticket.tickets"))


@Ticket.route("/save_ticket", methods=["POST"])
def save_ticket():
    _ReferencePlSql = PlSql(current_app.config["DSN_PSQL"])
    tmp = request.get_json()
    isnew = tmp["isnew"]
    if isnew == '1':
        query0 = f"""SELECT LPAD(((MAX(ticketid)::INTEGER)+1)::TEXT,4,'0') AS serial FROM ticket WHERE categoryid = '{tmp["categoryid"]}' LIMIT 1"""
        _ReferencePlSql.exec(query0)
        nserial = [row for row in _ReferencePlSql.data][0][0]
        query = f"""
        INSERT INTO ticket
        (ticketid,name,levelid,gradeid,categoryid,stateid,write_uid,write_at) VALUES
        ('{nserial}', UPPER('{tmp["name"]}'),{tmp["levelid"]},{tmp["gradeid"]},'{tmp["categoryid"]}','P',{session["current_user"]["id"]},NOW())"""
    else:
        query = f"""
        UPDATE ticket SET
        name=UPPER('{tmp["name"]}'),levelid={tmp["levelid"]},gradeid={tmp["gradeid"]},categoryid='{tmp["categoryid"]}',write_uid={session["current_user"]["id"]},write_at=NOW()
        WHERE id = {tmp["id"]}"""
    _ReferencePlSql.exec(query)
    print(query)
    return {"ok": 1, "message": "CREADO EXITOSAMENTE(TICKET)"}


@Ticket.route("/payment", methods=["POST"])
def payment():
    _ReferencePlSql = PlSql(current_app.config["DSN_PSQL"])
    tmp = request.get_json()
    name = tmp.get("name").upper()  if tmp.get("name") else "GRACIAS POR SU PARTICIPACION"
    response = {"ok": 0, "message": "ERROR AL GENERAR PAGART"}
    if session.get("payment"):
        filter = ",".join([str(item) for item in session["payment"]])
        tmp = get_data(f" WHERE id in ({filter}) AND stateid = 'E' AND paymentid IS NOT NULL")
        err = ""
        for row in tmp:
            if row["id"] in session["payment"]:
                err += f"\n ITEM PAGADO {row['id']}"
        if err == "":
            query = f"INSERT INTO payment(name, stateid) VALUES('{name}', 'A') RETURNING id"
            _ReferencePlSql.exec(query)
            serial = _ReferencePlSql.data[0][0]
            query1 = f"UPDATE ticket SET stateid = 'E', paymentid = {serial} WHERE id IN ({filter})"
            _ReferencePlSql.exec(query1)
            res = print(serial)
            if res["ok"]:
                session["payment"] = set()
                response = {"ok": 1, "message": str(serial).zfill(8)}
        else:
            response = {"ok": 0, "message": err}
    return response


@Ticket.route("/generate_again/<id>", methods=["GET"])
def print(id):
    try:
        nserial = str(id).zfill(8)
        _ReferencePlSql = PlSql(current_app.config["DSN_PSQL"])
        query = f"SELECT name FROM payment WHERE id = {id}"
        _ReferencePlSql.exec(query)
        name = _ReferencePlSql.data[0][0]
        loPdf = PaymentPDF(current_app.config["PATH_FILE"], nserial)
        loPdf.setData({"name": name, "id": nserial})
        tmp_data = get_data(f" WHERE paymentid = {id}")
        loPdf.setDatos(tmp_data)
        loPdf.mxprint(CATEGORIES, PRICES, DATE_FORMAT)
        response = {"ok": 1, "message": "good"}
    except Exception as e:
        response = {"ok": 0, "message": str(e)}
    finally:
        return response

@Ticket.route("/drop_payment", methods=["POST"])
def drop_payment():
    _ReferencePlSql = PlSql(current_app.config["DSN_PSQL"])
    try:
        tmp = request.get_json()
        paymentid = int(tmp["paymentid"])
    except Exception as e:
        return {"ok": 0, "message": "DEBE SER UN NUMERO"}    
    query = f"UPDATE payment SET stateid = 'X' WHERE id = {paymentid}"
    _ReferencePlSql.exec(query)
    query1 = f"UPDATE ticket SET stateid = 'P', paymentid = NULL WHERE paymentid = {paymentid}"
    _ReferencePlSql.exec(query1)
    return {"ok": 1, "message": "ELIMINADO CORRECTAMENTE(COMPROBANTE)"}


@Ticket.route("/report/<filename>")
def send_pdf(filename):
    return send_from_directory(current_app.config["PATH_FILE"], filename)


@Ticket.route("/report/xls")
def send_xls():
    print("----REPORTE DE VENTAS")
    try:
        PATH_FILE = os.path.join(current_app.config["PATH_FILE"], "report.csv")
        ladatos = get_data(f" WHERE stateid = 'E' AND paymentid IS NOT NULL")
        data = list()
        tmp = dict()
        for indice in range(len(ladatos)):
            tmp = ladatos[indice]
            cat = tmp["categoryid"]
            tmp["category"] = CATEGORIES[cat]
            tmp["price"] = PRICES[cat]
            tmp["state"] = LEVELS[str(ladatos[indice]["stateid"])]
            tmp["level"] = LEVELS[str(ladatos[indice]["levelid"])]
            tmp["grade"] = GRADES[str(ladatos[indice]["gradeid"])]
            data.append(tmp)
        slots = [
            "id",
            "ticketid",
            "personid",
            "levelid",
            "gradeid",
            "categoryid",
            "stateid",
            "write_uid",
            "write_at",
            "name",
            'flag',
            'price',
            'category',
            'grade',
            'level',
            'state'
        ]
        print("----DATA")
        print(data)  
        with open(PATH_FILE, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=slots)
            writer.writeheader()
            writer.writerows(data)
        return {"ok": 1, "message": "GENERADO CORRECTAMENTE"}
    except Exception as e:
        return {"ok": 0, "message": "ALGO SALIO MAL"}
