import time
from flask import Flask, render_template
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    send_file,
    make_response,
)
import requests
from urllib.parse import unquote
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from textwrap import fill, wrap
from werkzeug.exceptions import NotFound
from io import BytesIO
from urllib.parse import unquote
from sqlalchemy import func, case
from werkzeug.utils import secure_filename
from supabase import create_client, Client
import logging
import os
from werkzeug.security import check_password_hash
import re
from flask import Flask, send_from_directory, send_file, abort
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import textwrap
import base64
from sqlalchemy import extract
from dateutil.relativedelta import relativedelta
import calendar
import pytz
import pandas as pd
from functools import wraps
from flask import session, redirect, url_for, flash, abort
from collections import Counter
import random
import string

pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", "static/font/Times-Bold.TTF"))

pdfmetrics.registerFont(TTFont("TimesNewRoman-Regular", "static/font/times.ttf"))
app = Flask(__name__)

app.secret_key = "4321Lupa"
# app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=10)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)

# Database configuration for production
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres.egjlwlrqrhtxiafnsojz:D8mnXtg2fyEpBSsC@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Inisialisasi Supabase
url = "https://egjlwlrqrhtxiafnsojz.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVnamx3bHJxcmh0eGlhZm5zb2p6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjQ5MTY2OTksImV4cCI6MjA0MDQ5MjY5OX0.lYeiR6EKs1F6UdvzKWJxjjZU3VEPP1ydAPUs6O7QGAA"
supabase: Client = create_client(url, key)


UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
UPLOAD_BUKTI = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "uploads/uploads"
)
# Enable SQLAlchemy logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

guestbook_data = []


class Family(db.Model):
    __tablename__ = "family"
    __table_args__ = {"schema": "data_keluarga"}
    id = db.Column(db.Integer, primary_key=True)
    nama_keluarga = db.Column(db.String(100), nullable=False)
    nama = db.Column(db.String(100), nullable=False)  # Field yang diperbarui
    tempat_lahir = db.Column(db.String(100), nullable=False)
    tanggal_lahir = db.Column(db.Date, nullable=False)
    nomor_keluarga = db.Column(db.String(20), nullable=False)
    hubungan_keluarga = db.Column(db.String(50), nullable=False)


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"schema": "data_keluarga"}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")


class SchedulerLog(db.Model):
    __tablename__ = "scheduler_log"
    __table_args__ = {"schema": "data_keluarga"}
    id = db.Column(db.Integer, primary_key=True)
    execution_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)


class SuratPengantar(db.Model):
    __tablename__ = "surat_pengantar"
    __table_args__ = {"schema": "data_keluarga"}
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(50))
    tanggal = db.Column(db.Date)
    tempatlahir = db.Column(db.String(100))
    jeniskelamin = db.Column(db.String(255))
    agama = db.Column(db.String(255))
    pekerjaan = db.Column(db.String(100))
    ktp = db.Column(db.String(16))
    alamatktp = db.Column(db.String(255))
    statusperkawinan = db.Column(db.String(255))
    tujuan = db.Column(db.Text)
    jenissurat = db.Column(db.String(255))
    statussurat = db.Column(db.String(50), nullable=True)


class Iuran(db.Model):
    __tablename__ = "iuran"
    __table_args__ = {"schema": "data_keluarga"}

    id = db.Column(db.Integer, primary_key=True)
    nama_keluarga = db.Column(db.String(100), nullable=False)
    jumlah_iuran = db.Column(db.Float, nullable=False)
    bukti_pembayaran = db.Column(db.String(255))
    status_pembayaran = db.Column(db.String(20), default="Menunggu")
    tanggal = db.Column(db.Date, default=func.now(), nullable=False)


class Message(db.Model):
    __tablename__ = "pesan"
    __table_args__ = {"schema": "data_keluarga"}
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(150), nullable=False)
    nomor_whatsapp = db.Column(db.String(15), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(pytz.timezone("Asia/Jakarta"))
    )


class BukuTamu(db.Model):
    __tablename__ = "buku_tamu"
    __table_args__ = {"schema": "data_keluarga"}
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.String(255), nullable=False)
    tujuan = db.Column(db.String(255), nullable=False)
    kontak = db.Column(db.String(20), nullable=False)
    kunjungan = db.Column(
        db.DateTime,
        default=lambda: datetime.now(pytz.timezone("Asia/Jakarta")).replace(
            tzinfo=None
        ),
    )


class Pengeluaran(db.Model):
    __tablename__ = "pengeluaran"
    __table_args__ = {"schema": "data_keluarga"}
    id = db.Column(db.Integer, primary_key=True)
    nama_kegiatan = db.Column(db.String(255), nullable=False)
    jenis_pengeluaran = db.Column(db.String(255), nullable=False)
    jumlah = db.Column(db.Float, nullable=False)
    tanggal = db.Column(db.Date, nullable=False)


class Register(db.Model):
    __tablename__ = "register"
    __table_args__ = {"schema": "data_keluarga"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_lengkap = db.Column(db.String(255), nullable=False)
    nomor_whatsapp = db.Column(db.String(20), nullable=False, unique=False)
    kata_sandi = db.Column(db.Text, nullable=False)
    tanggal_daftar = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default="Aktif")


class Activity(db.Model):
    __tablename__ = "activity"
    __table_args__ = {"schema": "data_keluarga"}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("data_keluarga.user.id"), nullable=False
    )
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())

    user = db.relationship("User", backref=db.backref("activities", lazy=True))

    def __init__(
        self,
        nama,
        tanggal,
        tempatlahir,
        jeniskelamin,
        agama,
        pekerjaan,
        ktp,
        alamatktp,
        statusperkawinan,
        tujuan,
        jenissurat,
        statussurat=None,
    ):
        self.nama = nama
        self.tanggal = tanggal
        self.tempatlahir = tempatlahir
        self.jeniskelamin = jeniskelamin
        self.agama = agama
        self.pekerjaan = pekerjaan
        self.ktp = ktp
        self.alamatktp = alamatktp
        self.statusperkawinan = statusperkawinan
        self.tujuan = tujuan
        self.jenissurat = jenissurat
        self.statussurat = statussurat

    def __init__(
        self,
        nama_keluarga,
        jumlah_iuran,
        bukti_pembayaran=None,
        status_pembayaran="Menunggu",
        tanggal=None,
    ):
        self.nama_keluarga = nama_keluarga
        self.jumlah_iuran = jumlah_iuran
        self.bukti_pembayaran = bukti_pembayaran
        self.status_pembayaran = status_pembayaran
        if tanggal is not None:
            self.tanggal = tanggal

    def __init__(
        self,
        user,
        nomor_whatsapp,
        message,
        timestamp=None,
    ):
        self.user = user
        self.nomor_whatsapp = nomor_whatsapp
        self.message = message
        self.timestamp = (
            timestamp if timestamp else datetime.now(pytz.timezone("Asia/Jakarta"))
        )

    def __init__(
        self,
        nama,
        alamat,
        tujuan,
        kontak,
    ):
        self.nama = nama
        self.alamat = alamat
        self.tujuan = tujuan
        self.kontak = kontak

    def __init__(self, nama_kegiatan, jenis_pengeluaran, jumlah, tanggal):
        self.nama_kegiatan = nama_kegiatan
        self.jenis_pengeluaran = jenis_pengeluaran
        self.jumlah = jumlah
        self.tanggal = tanggal

    def __init__(self, nama_lengkap, nomor_whatsapp, kata_sandi, tanggal_daftar):
        self.nama_lengkap = nama_lengkap
        self.nomor_whatsapp = nomor_whatsapp
        self.kata_sandi = kata_sandi

    def __init__(self, user_id, action, timestamp=None):
        self.user_id = user_id
        self.action = action
        self.timestamp = timestamp or datetime.utcnow()


def __init__(self, username, password):
    self.username = username
    self.password = password  # Menyimpan password sebagai plaintext


import logging


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "role" not in session or session["role"] not in allowed_roles:
                # Flash message untuk tidak memiliki akses
                return render_template(
                    "unauthorized.html",  # Menampilkan halaman unauthorized
                    original_url=request.path,
                    role=session.get("role"),
                )
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Route untuk halaman user
@app.route("/")
def index():
    return render_template("loginuser.html")


@app.route("/main")
def main():
    # Perbaikan pengecekan session
    if "user_id" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("index"))

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username or not password:
            flash("Username dan password harus diisi.", "warning")
            return render_template("login.html")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            session.permanent = True

            jakarta_tz = pytz.timezone("Asia/Jakarta")
            now_jakarta = datetime.now(jakarta_tz).replace(
                tzinfo=None
            )  # ✅ Buang informasi timezone

            new_activity = Activity(
                user_id=user.id,
                action="Login ke Dashboard Digipan",
                timestamp=now_jakarta,
            )
            db.session.add(new_activity)
            db.session.commit()

            return redirect(url_for("dashboard"))
        else:
            flash("Username atau password salah. Silakan coba lagi.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    if "user_id" in session:
        jakarta_tz = pytz.timezone("Asia/Jakarta")
        now_jakarta = datetime.now(jakarta_tz).replace(
            tzinfo=None
        )  # ✅ Buang informasi timezone

        new_activity = Activity(
            user_id=session["user_id"],
            action="Logout dari sistem",
            timestamp=now_jakarta,
        )
        db.session.add(new_activity)
        db.session.commit()

        username = session.get("username", "Tidak diketahui")
        role = session.get("role", "Tidak diketahui")

        recent_activities = (
            Activity.query.filter_by(user_id=session["user_id"])
            .order_by(Activity.timestamp.desc())
            .limit(10)
            .all()
        )

        activity_list = "\n".join(
            [
                f"🔹 {act.action} - {act.timestamp.astimezone(jakarta_tz).strftime('%Y-%m-%d %H:%M:%S')}"
                for act in recent_activities
            ]
        )

        # Kirim notifikasi Telegram saat logout dengan aktivitas-aktivitas terakhir
        send_telegram_notification(
            f"<b>Hallo pengurus RT 08/01!</b>\n\n"
            f"<b>Ada Pengurus RT yang Masuk!</b>\n\n"
            f"👤 <b>Username:</b> {username}\n"
            f"💼 <b>Role:</b> {role}\n\n"
            f"<b>Riwayat Aktivitas Terakhir:</b>\n{activity_list}\n\n"
            f"<b>Untuk detail lebih lanjut, silakan kunjungi website berikut:</b>\n"
            f"<a href='https://digiwarga.vercel.app/login'>digiwarga.vercel.app/login</a>"
        )

    session.clear()
    flash("Anda telah keluar.", "info")
    return redirect(url_for("login"))


@app.route("/logoutuser")
def logoutuser():
    user_id = session.get(
        "user_id"
    )  # Mendapatkan ID pengguna yang sedang login dari session
    if user_id:
        # Anda bisa menggunakan ID pengguna yang sedang login untuk memeriksa status mereka jika perlu
        user = Register.query.get(user_id)
        if user:
            session.pop("user_id", None)  # Hapus sesi pengguna berdasarkan ID
            flash(f"Anda telah keluar")
        else:
            flash("Pengguna tidak ditemukan.")
    else:
        flash("Tidak ada pengguna yang sedang login.")

    return redirect(url_for("index"))


# schduler setiap hari
@app.route("/run-scheduler", methods=["GET"])
def run_scheduler():
    try:
        # Hitung jumlah nama keluarga
        count_nama_keluarga = db.session.query(Family.nama_keluarga).distinct().count()

        # Buat log entri
        log_entry = SchedulerLog(
            execution_time=datetime.utcnow(),
            status="success",
            message=f"Jumlah nama keluarga: {count_nama_keluarga}",
        )
        db.session.add(log_entry)
        db.session.commit()

        return (
            jsonify({"status": "success", "message": "Scheduler ran successfully."}),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


def format_rupiah(value):
    """Format nilai menjadi rupiah dengan pemisah ribuan (misalnya, 60000 menjadi '60.000')."""
    return f"{value:,.0f}".replace(
        ",", "."
    )  # Menggunakan format koma sebagai titik pemisah ribuan

    # Daftarkan filter format rupiah di Flask


@app.route("/google9f984f41c701cb34.html")
def verify_google():
    return send_from_directory("templates", "google9f984f41c701cb34.html")


app.jinja_env.filters["rupiah"] = format_rupiah


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("login"))

    # Menghitung jumlah keluarga yang unik
    subquery = (
        db.session.query(func.lower(func.replace(Family.nama_keluarga, " ", "")))
        .distinct()
        .subquery()
    )

    family_count = db.session.query(func.count()).select_from(subquery).scalar()

    # Menghitung jumlah total surat
    surat_count = db.session.query(SuratPengantar).count()

    # Menghitung jumlah total warga
    warga_count = (
        db.session.query(func.count().label("total"))
        .filter(Family.nama.isnot(None), Family.nama != "")
        .scalar()
    )

    # Menghitung total iuran
    total_iuran = (
        db.session.query(func.sum(Iuran.jumlah_iuran))
        .filter(Iuran.status_pembayaran == "Diterima")
        .scalar()
    )
    total_iuran = total_iuran or 0
    total_pengeluaran = db.session.query(func.sum(Pengeluaran.jumlah)).scalar()
    total_pengeluaran = total_pengeluaran or 0
    net_iuran = total_iuran - total_pengeluaran
    net_iuran_formatted = format_rupiah(net_iuran)

    # Format total iuran ke dalam format '60.000'
    total_iuran_diterima_formatted = format_rupiah(total_iuran)

    # Ambil pesan dari database
    all_messages = Message.query.order_by(Message.timestamp.desc()).all()

    # Batasi pesan yang ditampilkan
    messages_to_display = all_messages[:3]
    more_messages = all_messages[3:5]  # 5 pesan tambahan untuk View More

    selesai_count = SuratPengantar.query.filter_by(statussurat="Selesai").count()
    none_count = SuratPengantar.query.filter_by(statussurat=None).count()

    # Format pesan untuk template
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            # Ganti awalan '0' dengan '62' untuk nomor Indonesia
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]

    message_list_more = [
        {
            "message": msg.message,
            "user": msg.user,
            "nomor_whatsapp": msg.nomor_whatsapp,
            "timestamp": msg.timestamp.strftime("%d %b %Y · %H:%M"),
        }
        for msg in more_messages
    ]
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    current_datetime = datetime.now(jakarta_tz).strftime(
        "%m/%d/%Y, %I:%M %p"
    )  # Formatkan sesuai kebutuhan

    return render_template(
        "dashboard.html",
        family_count=family_count,
        surat_count=surat_count,
        warga_count=warga_count,
        total_iuran=net_iuran_formatted,
        current_datetime=current_datetime,
        messages=message_list_to_display,  # Tampilkan pesan yang dibatasi
        more_messages=message_list_more,  # Kirimkan pesan tambahan untuk View More
        selesai_count=selesai_count,
        none_count=none_count,
    )


@app.route("/get_family_relationships")
def get_family_relationships():
    # Ambil semua data keluarga dari database
    families = Family.query.all()

    # Hitung hubungan keluarga
    relationships = [family.hubungan_keluarga for family in families]

    # Menghitung jumlah setiap hubungan
    relationship_counts = Counter(relationships)

    # Ubah label untuk ditampilkan di frontend
    formatted_counts = {
        rel.replace("_", " ").title(): count
        for rel, count in relationship_counts.items()
    }

    return jsonify(formatted_counts)


@app.route("/api/family-stats", methods=["GET"])
def get_family_stats():
    kepala_keluarga_count = (
        db.session.query(Family)
        .filter(func.lower(Family.hubungan_keluarga) == "kepala_keluarga")
        .count()
    )
    istri_count = (
        db.session.query(Family)
        .filter(func.lower(Family.hubungan_keluarga) == "istri")
        .count()
    )
    anak_count = (
        db.session.query(Family)
        .filter(func.lower(Family.hubungan_keluarga) == "anak")
        .count()
    )

    # Mengambil data untuk chart kedua (total surat berdasarkan jenis surat)
    surat_count = (
        db.session.query(
            SuratPengantar.jenissurat, func.count(SuratPengantar.id).label("total")
        )
        .group_by(SuratPengantar.jenissurat)
        .all()
    )

    # Format data untuk digunakan di chart
    jenis_surat = [surat[0] for surat in surat_count]
    total_surat = [surat[1] for surat in surat_count]

    return jsonify(
        {
            "kepala_keluarga": kepala_keluarga_count,
            "istri": istri_count,
            "anak": anak_count,
            "jenis_surat": jenis_surat,
            "total_surat": total_surat,
        }
    )


@app.route("/get_surat_progress")
def get_surat_progress():
    # Ambil semua data surat dari database
    surat_list = SuratPengantar.query.all()

    # Hitung jenis surat berdasarkan field 'jenissurat'
    jenis_surat = [surat.jenissurat for surat in surat_list]

    # Hitung jumlah setiap jenis surat
    surat_counts = Counter(jenis_surat)

    # Format jenis surat untuk menghilangkan underscore
    formatted_counts = {
        jenis.replace("_", " ").title(): count for jenis, count in surat_counts.items()
    }

    return jsonify(formatted_counts)


@app.route("/api/product_sold_data")
def get_product_sold_data():
    # Query untuk mendapatkan total surat berdasarkan jenissurat
    data = (
        db.session.query(
            SuratPengantar.jenissurat, db.func.count(SuratPengantar.id).label("total")
        )
        .group_by(SuratPengantar.jenissurat)
        .all()
    )

    # Fungsi untuk memformat jenissurat dari format snake_case ke format Title Case
    def format_jenissurat(jenissurat):
        # Mengganti underscore dengan spasi dan mengubah ke Title Case
        return jenissurat.replace("_", " ").title()

    # Format data untuk dikirim ke frontend
    result = [
        {"jenissurat": format_jenissurat(item.jenissurat), "total": item.total}
        for item in data
    ]

    return jsonify(result)


@app.route("/api/latest_families")
def get_latest_families():
    # Mengambil 5 data keluarga terbaru berdasarkan id yang paling besar
    latest_families = Family.query.order_by(Family.id.desc()).limit(5).all()

    # Format data untuk dikirim ke frontend
    result = [
        {
            "id": family.id,
            "nama_keluarga": family.nama_keluarga,
            "nama": family.nama,
            "hubungan_keluarga": family.hubungan_keluarga,
            "nomor_keluarga": family.nomor_keluarga,
        }
        for family in latest_families
    ]
    return jsonify(result)


@app.route("/input_keluarga")
def input_keluarga():
    if "user_id" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("index"))

    user_id = session.get("user_id")
    user = Register.query.get(user_id)

    if not user:
        flash("Pengguna tidak ditemukan.", "danger")
        return redirect(url_for("index"))

    if user.status != "Aktif":
        flash("Akun Anda tidak aktif.", "danger")
        return redirect(url_for("index"))

    return render_template("input.html")


@app.route("/input", methods=["POST"])
def input_data():
    try:
        if request.is_json:
            # Jika permintaan dalam bentuk JSON
            data = request.get_json()
            nama_keluarga = data["nama_keluarga"].upper()
            family_data = Family(
                nama_keluarga=nama_keluarga,
                nama=data["nama"],
                tempat_lahir=data["tempat_lahir"],
                tanggal_lahir=data["tanggal_lahir"],
                nomor_keluarga=data["nomor_keluarga"],
                hubungan_keluarga=data["hubungan_keluarga"],
            )
        else:
            return jsonify({"error": "Format data tidak valid. Harus dalam JSON."}), 400

        db.session.add(family_data)
        db.session.commit()

        # Menghilangkan underscore dari hubungan_keluarga
        hubungan_keluarga_formatted = family_data.hubungan_keluarga.replace("_", " ")

        # Kirim notifikasi ke Telegram (kode dikomentari tetap ada di sini)
        send_telegram_notification(
            f"<b>Hallo pengurus RT 08/01!</b>\n\n"
            f"<b>Ada keluarga baru nih!</b>\n\n"
            f"👪<b>Nama Keluarga:</b> {nama_keluarga}\n"
            f"🧑<b>Nama:</b> {family_data.nama}\n"
            f"🔗<b>Hubungan Keluarga:</b> {hubungan_keluarga_formatted}\n\n"
            f"<i>Mohon segera diproses. Terima kasih atas perhatian dan kerjasamanya 😊!</i>\n\n"
            f"<b>Untuk detail lebih lanjut, silakan kunjungi website berikut:</b>\n"
            f"<a href='https://digiwarga.vercel.app/login'>digiwarga.vercel.app/login</a>"
        )

        # Berikan respons JSON
        return jsonify({"message": "Data keluarga berhasil ditambahkan!"}), 200

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Terjadi kesalahan: {e}")
        return (
            jsonify({"error": "Terjadi kesalahan saat memproses permintaan Anda."}),
            500,
        )


@app.route("/surat_pengantar")
def surat_pengantar():
    if "user_id" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("index"))

    user_id = session.get("user_id")
    user = Register.query.get(user_id)

    if not user:
        flash("Pengguna tidak ditemukan.", "danger")
        return redirect(url_for("index"))

    if user.status != "Aktif":
        flash("Akun Anda tidak aktif. Silakan hubungi admin.", "danger")
        return redirect(url_for("index"))

    return render_template("surat/surat_pengantar.html")


@app.route("/tentang")
def tentang():
    # Periksa apakah session user_id ada
    if "user_id" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(
            url_for("index")
        )  # Redirect ke halaman login jika session tidak ada

    return render_template(
        "tentang.html"
    )  # Tampilkan halaman tentang jika login berhasil


@app.route("/input_iuran", methods=["GET", "POST"])
def input_iuran():
    if "user_id" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("index"))

    user_id = session.get("user_id")
    user = Register.query.get(user_id)

    if not user:
        flash("Pengguna tidak ditemukan.", "danger")
        return redirect(url_for("index"))

    if user.status != "Aktif":
        flash("Akun Anda tidak aktif. Silakan hubungi admin.", "danger")
        return redirect(url_for("index"))

    subquery = (
        db.session.query(func.trim(func.lower(Family.nama_keluarga)))
        .distinct()
        .subquery()
    )

    nama_keluarga = db.session.query(subquery.c["trim"]).all()
    return render_template("iuran/input_iuran.html", nama_keluarga=nama_keluarga)


# @app.route("/kirim_iuran", methods=["POST"])
# def kirim_iuran():
#     if request.method == "POST":
#         nama_keluarga = request.form.get("nama_keluarga")
#         jumlah_iuran = request.form.get("jumlah")
#         file = request.files.get("bukti_pembayaran")

#         if file:
#             try:
#                 # Tambahkan timestamp ke nama file
#                 timestamp = int(time.time())
#                 original_filename = secure_filename(file.filename)
#                 filename = f"{timestamp}_{original_filename}"
#                 # Simpan file ke Supabase Storage
#                 bucket_name = "digipan"
#                 file_path = f"bukti_pembayaran/{filename}"
#                 upload_response = supabase.storage.from_(bucket_name).upload(
#                     file_path, file.read()
#                 )

#                 if upload_response.status_code == 200:
#                     file_url = supabase.storage.from_(bucket_name).get_public_url(
#                         file_path
#                     )

#                     # Simpan nama file dan data lainnya ke database
#                     iuran_baru = Iuran(
#                         nama_keluarga=nama_keluarga,
#                         jumlah_iuran=float(
#                             jumlah_iuran.replace("Rp ", "")
#                             .replace(".", "")
#                             .replace(",", ".")
#                         ),
#                         bukti_pembayaran=file_url,  # Simpan URL file
#                         status_pembayaran="Menunggu",
#                     )
#                     db.session.add(iuran_baru)
#                     db.session.commit()

#                     # Panggil fungsi send_slack_notification dengan status_pembayaran
#                     send_slack_notification(
#                         nama_keluarga, jumlah_iuran, "Menunggu"
#                     )  # Pastikan status pembayaran disertakan

#                     # Kembalikan respons JSON yang sukses
#                     return jsonify(
#                         {"success": True, "message": "Data berhasil dikirim"}
#                     )
#                 else:
#                     logging.error(f"Upload failed: {upload_response.text}")
#                     return (
#                         jsonify(
#                             {
#                                 "success": False,
#                                 "message": "Gagal mengupload bukti pembayaran",
#                             }
#                         ),
#                         400,
#                     )

#             except Exception as e:
#                 logging.error(f"Exception: {e}")
#                 db.session.rollback()
#                 return (
#                     jsonify(
#                         {
#                             "success": False,
#                             "message": "Terjadi kesalahan saat mengupload",
#                         }
#                     ),
#                     500,
#                 )
#         else:
#             return jsonify({"success": False, "message": "File tidak ditemukan"}), 400

#     return jsonify({"success": False, "message": "Metode tidak valid"}), 405


@app.route("/kirim_iuran", methods=["POST"])
def kirim_iuran():
    if request.method == "POST":
        nama_keluarga = request.form.get("nama_keluarga")
        jumlah_iuran = request.form.get("jumlah")
        file = request.files.get("bukti_pembayaran")

        if file:
            try:
                # Tambahkan timestamp ke nama file
                timestamp = int(time.time())
                original_filename = secure_filename(file.filename)
                filename = f"{timestamp}_{original_filename}"
                # Simpan file ke Supabase Storage
                bucket_name = "digipan"
                file_path = f"bukti_pembayaran/{filename}"
                upload_response = supabase.storage.from_(bucket_name).upload(
                    file_path, file.read()
                )

                if hasattr(upload_response, "full_path"):
                    file_url = supabase.storage.from_(bucket_name).get_public_url(
                        file_path
                    )

                    # Simpan nama file dan data lainnya ke database
                    iuran_baru = Iuran(
                        nama_keluarga=nama_keluarga,
                        jumlah_iuran=float(
                            jumlah_iuran.replace("Rp ", "")
                            .replace(".", "")
                            .replace(",", ".")
                        ),
                        bukti_pembayaran=file_url,  # Simpan URL file
                        status_pembayaran="Menunggu",
                    )
                    db.session.add(iuran_baru)
                    db.session.commit()

                    # Kirim notifikasi Telegram
                    # send_telegram_notification(
                    #     f"<b>Hallo pengurus RT 08/01!</b>\n\n"
                    #     f"<b>Ada iuran baru masuk nih!</b>\n\n"
                    #     f"👪 <b>Nama Keluarga:</b> {nama_keluarga}\n\n"
                    #     f"💰 <b>Jumlah Iuran:</b> {jumlah_iuran}\n\n"
                    #     f"📅 <b>Status Pembayaran:</b> Menunggu\n\n"
                    #     f"<i>Mohon segera diproses. Terima kasih atas perhatian dan kerjasamanya 😊!</i>\n\n"
                    #     f"<b>Untuk detail lebih lanjut, silakan kunjungi website berikut:</b>\n"
                    #     f"<a href='https://digiwarga.vercel.app/login'>digiwarga.vercel.app/login</a>"
                    # )

                    # Kembalikan respons JSON yang sukses
                    return jsonify(
                        {"success": True, "message": "Data berhasil dikirim"}
                    )
                else:
                    logging.error(f"Upload failed: {upload_response.text}")
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "Gagal mengupload bukti pembayaran",
                            }
                        ),
                        400,
                    )

            except Exception as e:
                logging.error(f"Exception: {e}")
                db.session.rollback()
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Terjadi kesalahan saat mengupload",
                        }
                    ),
                    500,
                )
        else:
            return jsonify({"success": False, "message": "File tidak ditemukan"}), 400

    return jsonify({"success": False, "message": "Metode tidak valid"}), 405


@app.route("/kirim-surat", methods=["POST"])
def kirim_surat():
    data = request.json

    try:
        # Validasi nomor KTP/KK hanya boleh angka
        ktp = data.get("ktp")
        if not re.fullmatch(r"\d+", ktp):
            return jsonify({"message": "Nomor KTP/KK hanya boleh berisi angka."}), 400

        # Cek apakah format tanggal benar
        tanggal_str = data.get("tanggal")
        tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d").date()

        surat = SuratPengantar(
            nama=data["nama"],
            tanggal=tanggal,
            tempatlahir=data["tempatlahir"],
            jeniskelamin=data["jeniskelamin"],
            agama=data["agama"],
            pekerjaan=data["pekerjaan"],
            ktp=data["ktp"],
            alamatktp=data["alamatktp"],
            statusperkawinan=data["statusperkawinan"],
            tujuan=data["tujuan"],
            jenissurat=data["jenissurat"],
        )
        db.session.add(surat)
        db.session.commit()
        jenis_surat_formatted = data["jenissurat"].replace("_", " ")

        # # Kirim notifikasi Telegram dengan nama pengirim dan jenis surat
        send_telegram_notification(
            f"<b>Hallo pengurus RT 08/01!</b>\n\n"  # Menambahkan spasi baru
            f"<b>Ada surat baru masuk nih!</b>\n\n"  # Menambahkan spasi baru
            f"👤<b>Nama Pengirim:</b> {data['nama']}\n"
            f"📝<b>Jenis Surat:</b> {jenis_surat_formatted}\n\n"
            f"<i>Mohon segera diproses. Terima kasih atas perhatian dan kerjasamanya 😊!</i>\n\n"  # Spasi dan format italic
            f"<b>Untuk detail lebih lanjut, silakan kunjungi website berikut:</b>\n"
            f"<a href='https://digiwarga.vercel.app/login'>digiwarga.vercel.app/login</a>"
        )

        return jsonify({"message": "Surat berhasil dikirim!"}), 200
    except Exception as e:
        print("Error:", e)
        db.session.rollback()
        return jsonify({"message": "Terjadi kesalahan saat mengirim surat."}), 500


@app.route("/api/recent_updates")
def recent_updates():
    # Ambil data terbaru untuk keluarga
    latest_families = db.session.query(Family).order_by(Family.id.desc()).limit(5).all()

    # Ambil data terbaru untuk iuran
    latest_iuran = db.session.query(Iuran).order_by(Iuran.id.desc()).limit(5).all()

    # Ambil data terbaru untuk surat
    latest_surat = (
        db.session.query(SuratPengantar)
        .order_by(SuratPengantar.id.desc())
        .limit(5)
        .all()
    )

    # Format data
    updates = [
        {
            "title": "Data Keluarga Baru",
            "time": "2m ago",
        },  # Ganti dengan data terbaru dari `latest_families`
        {
            "title": "Data Iuran Baru",
            "time": "5m ago",
        },  # Ganti dengan data terbaru dari `latest_iuran`
        {
            "title": "Data Surat Baru",
            "time": "10m ago",
        },  # Ganti dengan data terbaru dari `latest_surat`
    ]

    return jsonify(updates)


# route menu pesan terbaru
@app.route("/messages", methods=["GET", "POST"])
def message_center():
    if request.method == "POST":
        user = request.form["user"]  # Nama pengirim
        nomor_whatsapp = request.form["nomor"]  # Nomor WhatsApp
        message = request.form["message"]  # Isi pesan

        # Simpan pesan ke database
        new_message = Message(user=user, nomor_whatsapp=nomor_whatsapp, message=message)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for("message_center"))

    # # Mengambil semua pesan dari database, urutkan berdasarkan timestamp
    # messages = Message.query.order_by(Message.timestamp.desc()).all()

    return render_template("tentang.html")


@app.route("/keluarga")
def keluarga():
    if "username" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("login"))

    # Mendapatkan role dari session (misalnya 'kader', 'admin', dll)
    user_role = session.get("role", "")

    # Mengambil nama keluarga unik dengan jumlah anak dan istri
    families = (
        db.session.query(
            func.trim(Family.nama_keluarga).label("nama_keluarga"),
            func.sum(case((Family.hubungan_keluarga == "Anak", 1), else_=0)).label(
                "jumlah_anak"
            ),
            func.sum(case((Family.hubungan_keluarga == "Istri", 1), else_=0)).label(
                "jumlah_istri"
            ),
        )
        .group_by(func.trim(Family.nama_keluarga))
        .all()
    )

    all_messages = Message.query.order_by(Message.timestamp.desc()).all()

    # Batasi pesan yang ditampilkan
    messages_to_display = all_messages[:3]

    # Format pesan untuk template
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            # Ganti awalan '0' dengan '62' untuk nomor Indonesia
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]

    # Mengirim data role ke template
    return render_template(
        "datatables.html",
        families=families,
        messages=message_list_to_display,
        user_role=user_role,  # Menambahkan role ke context template
    )


@app.route("/get_family_details/<nama_keluarga>")
def get_family_details(nama_keluarga):
    # Menghilangkan encoding URL (%20) untuk memastikan spasi diterjemahkan dengan benar
    nama_keluarga = unquote(nama_keluarga).strip()

    # Query dengan memastikan spasi tambahan dihilangkan
    family_details = Family.query.filter(
        func.trim(Family.nama_keluarga) == nama_keluarga
    ).all()

    if not family_details:
        return jsonify({"error": "Family not found"}), 404

    family_data = [
        {
            "id": member.id,
            "nama_keluarga": member.nama_keluarga,
            "nama": member.nama,
            "tempat_lahir": member.tempat_lahir,
            "tanggal_lahir": member.tanggal_lahir.strftime("%Y-%m-%d"),
            "nomor_keluarga": member.nomor_keluarga,
            "hubungan_keluarga": member.hubungan_keluarga,
        }
        for member in family_details
    ]

    return jsonify(family_data)


@app.route("/delete_family_member/<int:member_id>", methods=["DELETE"])
def delete_family_member(member_id):
    try:
        member = db.session.query(Family).filter_by(id=member_id).first()
        if not member:
            return jsonify({"error": "Anggota keluarga tidak ditemukan."}), 404

        deleted_member_name = member.nama
        jakarta_tz = pytz.timezone("Asia/Jakarta")
        now_jakarta = datetime.now(jakarta_tz).replace(
            tzinfo=None
        )  # ✅ Buang informasi timezone

        db.session.delete(member)
        db.session.commit()

        new_activity = Activity(
            user_id=session["user_id"],
            action=f"Menghapus anggota keluarga {deleted_member_name} (ID: {member_id})",
            timestamp=now_jakarta,
        )
        db.session.add(new_activity)
        db.session.commit()

        return jsonify({"message": "Anggota keluarga berhasil dihapus."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/edit_family", methods=["POST"])
@role_required(["ketua"])
def edit_family():
    data = request.form
    member_id = data.get("member_id")
    nama_keluarga = data.get("nama_keluarga")
    nama = data.get("nama")
    tempat_lahir = data.get("tempat_lahir")
    tanggal_lahir_str = data.get("tanggal_lahir")
    nomor_keluarga = data.get("nomor_keluarga")
    hubungan_keluarga = data.get("hubungan_keluarga")

    if not member_id:
        return (
            jsonify(
                {"status": "error", "message": "ID anggota keluarga tidak diberikan."}
            ),
            400,
        )

    family_member = Family.query.get(member_id)

    if family_member:
        try:
            tanggal_lahir = datetime.strptime(tanggal_lahir_str, "%Y-%m-%d").date()

            family_member.nama_keluarga = nama_keluarga
            family_member.nama = nama
            family_member.tempat_lahir = tempat_lahir
            family_member.tanggal_lahir = tanggal_lahir
            family_member.nomor_keluarga = nomor_keluarga
            family_member.hubungan_keluarga = hubungan_keluarga

            db.session.commit()

            jakarta_tz = pytz.timezone("Asia/Jakarta")
            now_jakarta = datetime.now(jakarta_tz).replace(tzinfo=None)

            new_activity = Activity(
                user_id=session["user_id"],
                action=f"Memperbarui data anggota keluarga {family_member.nama} (ID: {member_id})",
                timestamp=now_jakarta,
            )

            db.session.add(new_activity)
            db.session.commit()

            return jsonify(
                {"status": "success", "message": "Data keluarga berhasil diperbarui."}
            )
        except ValueError:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Format tanggal tidak valid. Harap gunakan format YYYY-MM-DD.",
                    }
                ),
                400,
            )
    else:
        return (
            jsonify(
                {"status": "error", "message": "Anggota keluarga tidak ditemukan."}
            ),
            404,
        )


# route untuk menu surat
@app.route("/surat")
def surat():
    if "username" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("login"))

    # Mengambil semua pesan terbaru
    all_messages = Message.query.order_by(Message.timestamp.desc()).all()

    # Batasi pesan yang ditampilkan (menampilkan 3 pesan terbaru)
    messages_to_display = all_messages[:3]

    # Format pesan untuk template dengan mengganti awalan '0' menjadi '62'
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            # Ganti awalan '0' dengan '62' untuk nomor Indonesia
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]

    # Mengambil data surat pengantar
    all_surat = SuratPengantar.query.order_by(SuratPengantar.tanggal.desc()).all()

    # Format data surat pengantar untuk template, menghilangkan underscore di jenissurat
    surat_list_to_display = [
        {
            "id": surat.id,
            "nama": surat.nama,
            "tanggal": surat.tanggal.strftime("%d %b %Y"),
            "tempatlahir": surat.tempatlahir,
            "jeniskelamin": surat.jeniskelamin,
            "agama": surat.agama,
            "pekerjaan": surat.pekerjaan,
            "ktp": surat.ktp,
            "alamatktp": surat.alamatktp,
            "statusperkawinan": surat.statusperkawinan,
            "tujuan": surat.tujuan,
            # Mengganti underscore dengan spasi pada jenissurat
            "jenissurat": surat.jenissurat.replace("_", " "),
            "statussurat": surat.statussurat,
        }
        for surat in all_surat
    ]

    # Kirim data ke template HTML
    return render_template(
        "surat/list_surat.html",
        messages=message_list_to_display,
        surat_list=surat_list_to_display,
        user_role=session.get("role"),
    )


@app.route("/update_status_surat/<int:surat_id>", methods=["POST"])
def update_status_surat(surat_id):
    # Cari surat berdasarkan ID
    surat = SuratPengantar.query.get_or_404(surat_id)

    # Perbarui status surat jika status None
    if surat.statussurat is None:
        surat.statussurat = "Selesai"
        db.session.commit()
        flash("Status surat telah diperbarui menjadi Selesai.", "success")
    else:
        flash("Status surat sudah diperbarui sebelumnya.", "warning")

    return redirect(url_for("surat"))


def read_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# nomor_surat_counter = 1
# nomor_surat_pengantar_counter = 1


# @app.route("/download_surat_pdf/<int:surat_id>", methods=["GET"])
# def download_surat_pdf(surat_id):
#     # Ambil data surat berdasarkan surat_id
#     surat = SuratPengantar.query.get(surat_id)
#     if not surat:
#         return "Surat tidak ditemukan", 404

#     # Cetak nilai jenissurat untuk debugging
#     # print(f"Jenis surat: {surat.jenissurat}")

#     # Tentukan jalur absolut gambar
#     logo_url = os.path.join(current_app.root_path, "static/img/logo/depok.png")
#     ttd_url = os.path.join(current_app.root_path, "static/img/logo/ttd2.png")
#     today = datetime.now().strftime("Pasir Gunung Selatan, %d %B %Y")
#     global nomor_surat_counter
#     global nomor_surat_pengantar_counter

#     # Buat format nomor surat otomatis
#     nomor_surat = f"SKD-{nomor_surat_counter:02d}/RT-08/01/2024"

#     # Setelah nomor dibuat, increment counter
#     nomor_surat_counter += 1

#     nomor_surat_pengantar = f"SP-{nomor_surat_pengantar_counter:02d}/RT-08/01/2024"

#     # Setelah nomor dibuat, increment counter
#     nomor_surat_pengantar_counter += 1

#     # Tentukan template berdasarkan jenis surat
#     if surat.jenissurat == "surat_keterangan_domisili":
#         template = "surat/template_surat_domisili.html"
#     elif surat.jenissurat == "surat_pengantar":
#         template = "surat/template_surat_pengantar.html"
#     elif surat.jenissurat == "surat_pernyataan_tidak_mampu":
#         template = "surat/template_surat_tidak_mampu.html"
#     elif surat.jenissurat == "surat_pernyataan_belum_menikah":
#         template = "surat/template_surat_belum_menikah.html"
#     else:
#         # app.logger.error(f"Jenis surat tidak dikenal: {surat.jenissurat}")
#         return "Jenis surat tidak dikenal", 400

#     # Cetak template yang akan digunakan
#     # print(f"Template yang digunakan: {template}")

#     try:
#         # Render template HTML dengan data surat
#         rendered_template = render_template(
#             template,
#             nama=surat.nama,
#             tempat_lahir=surat.tempatlahir,
#             tanggal=surat.tanggal,
#             jeniskelamin=surat.jeniskelamin,
#             agama=surat.agama,
#             pekerjaan=surat.pekerjaan,
#             ktp=surat.ktp,
#             alamat=surat.alamatktp,
#             statusperkawinan=surat.statusperkawinan,
#             tujuan=surat.tujuan,
#             logo_url=logo_url,
#             ttd_url=ttd_url,
#             today=today,
#             nomor_surat=nomor_surat,
#             nomor_surat_pengantar=nomor_surat_pengantar,
#         )
#     except NotFound:
#         # app.logger.error(f"Template tidak ditemukan: {template}")
#         return "Template tidak ditemukan", 500

#     # Tentukan base_url
#     base_url = os.path.abspath(current_app.root_path)

#     # Konversi HTML ke PDF menggunakan WeasyPrint
#     pdf_file = HTML(string=rendered_template, base_url=base_url).write_pdf()

#     # Mengirim file sebagai unduhan, nama file mengikuti jenis surat
#     response = make_response(pdf_file)
#     response.headers["Content-Type"] = "application/pdf"
#     response.headers["Content-Disposition"] = (
#         f"attachment; filename={surat.jenissurat}_{surat.nama}.pdf"
#     )


#     return response
@app.route("/lihat_surat/<int:sid>")
def lihat_surat(sid):
    surat = SuratPengantar.query.get(sid)

    if not surat:
        flash("Surat tidak ditemukan.", "error")
        return redirect(url_for("dashboard"))

    jakarta_tz = pytz.timezone("Asia/Jakarta")
    now_jakarta = datetime.now(jakarta_tz).replace(
        tzinfo=None
    )  # ✅ Buang informasi timezone

    new_activity = Activity(
        user_id=session.get("user_id"),
        action=f"Melihat surat {surat.jenissurat}",
        timestamp=now_jakarta,
    )
    db.session.add(new_activity)
    db.session.commit()

    template_mapping = {
        "Surat Pengantar": "surat/surat_download_pengantar.html",
        "Surat Pernyataan Belum Menikah": "surat/surat_download_belum_menikah.html",
        "Surat Pernyataan Tidak Mampu": "surat/surat_download_tidak_mampu.html",
    }

    template_name = template_mapping.get(surat.jenissurat, "surat/surat_download.html")

    return render_template(template_name, surat=surat)


# Route untuk halaman verifikasi iuran
@app.route("/verifikasi-iuran")
def verifikasi_iuran():
    if "username" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("login"))
    all_messages = Message.query.order_by(Message.timestamp.desc()).all()

    # Batasi pesan yang ditampilkan
    messages_to_display = all_messages[:3]

    # Format pesan untuk template
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            # Ganti awalan '0' dengan '62' untuk nomor Indonesia
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]
    # Ambil semua data iuran dari database
    iuran_list = Iuran.query.all()
    return render_template(
        "iuran/verifikasi_iuran.html",
        iuran_list=iuran_list,
        messages=message_list_to_display,
    )


@app.route("/update_status_iuran/<int:iuran_id>", methods=["POST"])
def update_status_iuran(iuran_id):
    iuran = Iuran.query.get_or_404(iuran_id)

    if iuran.status_pembayaran == "Menunggu":
        iuran.status_pembayaran = "Diterima"
        db.session.commit()

        flash("Iuran telah Diterima!", "success")

        user_id = session.get("user_id")
        user = User.query.get(user_id)

        if user:
            jakarta_tz = pytz.timezone("Asia/Jakarta")
            now_jakarta = datetime.now(jakarta_tz).replace(
                tzinfo=None
            )  # ✅ Buang informasi timezone

            new_activity = Activity(
                user_id=user_id,
                action=f"{user.username} telah verifikasi pembayaran",
                timestamp=now_jakarta,
            )
            db.session.add(new_activity)

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
        else:
            flash("Terjadi kesalahan: User tidak ditemukan.", "danger")

    return redirect(url_for("verifikasi_iuran"))


# Route untuk halaman verifikasi iuran
@app.route("/statistik-iuran")
def statistik_iuran():
    if "username" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("login"))
    all_messages = Message.query.order_by(Message.timestamp.desc()).all()

    # Batasi pesan yang ditampilkan
    messages_to_display = all_messages[:3]

    # Format pesan untuk template
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            # Ganti awalan '0' dengan '62' untuk nomor Indonesia
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]
    # Mendapatkan parameter tahun dari query string (atau gunakan tahun ini secara default)
    year = request.args.get("year", default=datetime.today().year, type=int)

    # Menghasilkan daftar tahun 3 tahun ke belakang dan 3 tahun ke depan
    available_years = [
        datetime.today().year - 3 + i for i in range(7)
    ]  # Daftar tahun dari 3 tahun ke belakang hingga 3 tahun ke depan

    # Query data dengan status pembayaran 'Diterima' untuk tahun yang dipilih
    data_iuran = Iuran.query.filter(
        extract("year", Iuran.tanggal) == year, Iuran.status_pembayaran == "Diterima"
    ).all()
    # Menghitung total iuran
    total_iuran = (
        db.session.query(func.sum(Iuran.jumlah_iuran))
        .filter(Iuran.status_pembayaran == "Diterima")
        .scalar()
    )
    total_iuran = total_iuran or 0

    # Format total iuran ke dalam format '60.000'
    total_iuran_diterima_formatted = format_rupiah(total_iuran)
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    current_datetime = datetime.now(jakarta_tz).strftime(
        "%m/%d/%Y, %I:%M %p"
    )  # Formatkan sesuai kebutuhan
    # Memformat data agar bisa digunakan di chart
    iuran_per_bulan = {
        bulan: 0
        for bulan in [
            "Januari",
            "Februari",
            "Maret",
            "April",
            "Mei",
            "Juni",
            "Juli",
            "Agustus",
            "September",
            "Oktober",
            "November",
            "Desember",
        ]
    }

    # Mengisi data iuran ke dictionary iuran_per_bulan
    for iuran in data_iuran:
        bulan = iuran.tanggal.strftime(
            "%B"
        )  # Mendapatkan nama bulan dalam bahasa Inggris
        # Ubah nama bulan menjadi bahasa Indonesia
        bulan_indonesia = {
            "January": "Januari",
            "February": "Februari",
            "March": "Maret",
            "April": "April",
            "May": "Mei",
            "June": "Juni",
            "July": "Juli",
            "August": "Agustus",
            "September": "September",
            "October": "Oktober",
            "November": "November",
            "December": "Desember",
        }.get(
            bulan
        )  # Mengambil nama bulan dalam bahasa Indonesia

        if bulan_indonesia:
            iuran_per_bulan[bulan_indonesia] += iuran.jumlah_iuran

    # Mengambil labels dan values dari dictionary
    iuran_labels = list(iuran_per_bulan.keys())
    iuran_values = list(iuran_per_bulan.values())

    return render_template(
        "iuran/statistik_iuran.html",
        iuran_labels=iuran_labels,
        iuran_values=iuran_values,
        total_iuran=total_iuran_diterima_formatted,
        current_datetime=current_datetime,
        selected_year=year,  # Mengirim tahun yang dipilih ke template
        available_years=available_years,  # Mengirim daftar tahun yang tersedia ke template
        messages=message_list_to_display,
    )


@app.route("/statistik-iuran-data")
def statistik_iuran_data():
    year = request.args.get("year", type=int)
    # Ambil data berdasarkan tahun dari database
    iuran_list = Iuran.query.filter(extract("year", Iuran.tanggal) == year).all()

    # Siapkan data untuk grafik
    labels = [iuran.nama_keluarga for iuran in iuran_list]
    values = [iuran.jumlah_iuran for iuran in iuran_list]

    data = {"labels": labels, "values": values}

    return jsonify(data)


# Route untuk halaman Laporan
@app.route("/laporan")
def laporan():
    if "username" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("login"))
    all_messages = Message.query.order_by(Message.timestamp.desc()).all()

    # Batasi pesan yang ditampilkan
    messages_to_display = all_messages[:3]

    # Format pesan untuk template
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            # Ganti awalan '0' dengan '62' untuk nomor Indonesia
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]
    # Ambil semua data iuran dari database
    iuran_list = Iuran.query.all()
    return render_template(
        "laporan/Laporan.html",
        iuran_list=iuran_list,
        messages=message_list_to_display,
    )


@app.route("/generate_report", methods=["POST"])
def generate_report():
    # Log data yang diterima untuk debugging
    print(request.form)

    report_type = request.form.get("report_type")
    if not report_type:
        return "No report type selected", 400

    if report_type == "keluarga":
        return generate_family_report()
    elif report_type == "keuangan":
        return generate_financial_report()
    elif report_type == "pengeluaran":
        return generate_expense_report()
    else:
        return "Invalid report type", 400


@app.route("/generate_family_report", methods=["POST"])
def generate_family_report():
    query = db.session.query(Family).all()

    # Menambahkan hubungan_keluarga ke data laporan
    laporan_data = [
        {
            "Nama Keluarga": family.nama_keluarga,
            "Nama Anggota": family.nama,
            "Hubungan Keluarga": family.hubungan_keluarga,
        }
        for family in query
    ]

    df = pd.DataFrame(laporan_data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Laporan Keluarga", index=False)

    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="laporan_keluarga.xlsx",
    )


@app.route("/generate_financial_report", methods=["POST"])
def generate_financial_report():
    # Ambil status pembayaran dari form, tetapi kita akan fokus pada "Diterima"
    status_pembayaran = "Diterima"

    # Query untuk mengambil data dari tabel Iuran dengan status "Diterima"
    query = db.session.query(Iuran).filter(Iuran.status_pembayaran == status_pembayaran)

    data = query.all()

    laporan_data = []

    for iuran in data:
        laporan_data.append(
            {
                "Nama Keluarga": iuran.nama_keluarga,
                "Jumlah Iuran": iuran.jumlah_iuran,
                "Tanggal Pembayaran": iuran.tanggal,
            }
        )

    # Buat DataFrame dengan kolom yang diperlukan
    df = pd.DataFrame(
        laporan_data, columns=["Nama Keluarga", "Jumlah Iuran", "Tanggal Pembayaran"]
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Laporan Keuangan", index=False)

    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="laporan_keuangan.xlsx",
    )


@app.route("/generate_expense_report", methods=["GET"])
def generate_expense_report():
    # Query semua data dari tabel Pengeluaran
    query = db.session.query(Pengeluaran).all()

    if not query:
        return "No data available", 404  # Jika tidak ada data di tabel

    # Konversi data ke dalam format dictionary untuk DataFrame
    laporan_data = [
        {
            "Nama Kegiatan": pengeluaran.nama_kegiatan,
            "Jenis Pengeluaran": pengeluaran.jenis_pengeluaran,
            "Jumlah": pengeluaran.jumlah,
            "Tanggal": pengeluaran.tanggal.strftime("%Y-%m-%d"),
        }
        for pengeluaran in query
    ]

    # Membuat DataFrame menggunakan pandas
    df = pd.DataFrame(laporan_data)

    # Menulis DataFrame ke file Excel menggunakan BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Laporan Pengeluaran", index=False)

    # Mengembalikan file Excel sebagai respon
    output.seek(0)
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="laporan_pengeluaran.xlsx",
    )


@app.route("/pengguna", methods=["GET", "POST"])
def pengguna():
    if "username" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("login"))

    user_role = session.get("role")  # Ambil role dari session

    # Ambil semua pesan untuk ditampilkan
    all_messages = Message.query.order_by(Message.timestamp.desc()).all()
    messages_to_display = all_messages[:3]
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]

    # Ambil semua data iuran
    iuran_list = Iuran.query.all()

    # Ambil semua pengguna dari tabel User
    all_users = User.query.order_by(User.username.asc()).all()

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form["role"]  # Ambil peran pengguna dari form

        # Cek apakah role pengguna yang login adalah 'kader'
        if user_role == "kader":
            return (
                jsonify(
                    {
                        "message": None,
                        "error": "Fitur ini hanya dapat diakses oleh Admin.",
                    }
                ),
                403,
            )

        # Cek apakah username sudah ada di database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return (
                jsonify({"message": None, "error": "Username sudah tersedia"}),
                400,
            )

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        # Tambahkan pengguna baru dengan role
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        # Kirimkan response sukses
        return (
            jsonify({"message": "Pengguna berhasil ditambahkan!", "error": None}),
            200,
        )

    return render_template(
        "pengguna.html",
        iuran_list=iuran_list,
        messages=message_list_to_display,
        all_users=all_users,
        akses_terbatas=False,  # Set ke False jika akses tidak terbatas
    )


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if "username" not in session:
        flash("Anda harus login terlebih dahulu untuk mengakses halaman ini.", "error")
        return redirect(url_for("login"))

    # Periksa role pengguna
    user_role = session.get("role")  # Ambil role dari sesi
    if user_role == "kader":
        # Jika user role adalah kader, tampilkan pesan akses terbatas menggunakan SweetAlert
        return render_template("pengguna.html", akses_terbatas=True)

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form["role"]  # Ambil peran pengguna dari form

        # Cek apakah username sudah ada di database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username sudah terdaftar", "warning")
        else:
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

            # Tambahkan pengguna baru dengan role
            new_user = User(username=username, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()

            flash("User berhasil ditambahkan!", "success")
            return redirect(url_for("add_user"))

    return render_template("pengguna.html", akses_terbatas=False)


@app.route("/get_latest_iuran_notifications", methods=["GET"])
def get_latest_iuran_notifications():
    # Filter data iuran dengan status pembayaran "Menunggu"
    latest_iuran = (
        Iuran.query.filter_by(status_pembayaran="Menunggu")
        .order_by(Iuran.tanggal.desc())
        .limit(5)
        .all()
    )

    notifications = []

    for iuran in latest_iuran:
        notifications.append(
            {
                "nama_keluarga": iuran.nama_keluarga,
                "jumlah_iuran": iuran.jumlah_iuran,
                "tanggal": iuran.tanggal.strftime("%B %d, %Y"),
                "status": iuran.status_pembayaran,
                "url": url_for("verifikasi_iuran"),
            }
        )

    return jsonify(notifications)


@app.route("/get_notification_count", methods=["GET"])
def get_notification_count():
    count = Iuran.query.filter_by(status_pembayaran="Menunggu").count()
    return jsonify({"count": count})


@app.route("/buku-tamu")
def buku_tamu():

    # Jika tidak ada user_id, anggap pengguna sebagai tamu dan langsung izinkan akses
    return render_template("tamu.html")


@app.route("/tambah_buku_tamu", methods=["POST"])
def tambah_buku_tamu():
    try:
        data = request.get_json()
        print(f"Received data: {data}")

        # Mengambil nilai dengan kunci yang sesuai
        nama = data.get("nama")  # Mengubah 'name' menjadi 'nama'
        alamat = data.get("alamat")
        tujuan = data.get("tujuan")
        kontak = data.get("kontak")

        # Validasi jika ada field yang None
        if not all([nama, alamat, tujuan, kontak]):
            return jsonify({"error": "Semua field harus diisi"}), 400

        # Tambahkan data baru ke Buku Tamu
        new_entry = BukuTamu(nama=nama, alamat=alamat, tujuan=tujuan, kontak=kontak)
        db.session.add(new_entry)
        db.session.commit()

        # Kirim notifikasi ke Telegram
        send_telegram_notification(
            f"<b>Hallo pengurus RT 08/01!</b>\n\n"
            f"<b>Ada pendatang baru nih!</b>\n\n"
            f"👪 <b>Nama:</b> {nama}\n"
            f"🏠 <b>Alamat:</b> {alamat}\n"
            f"🎯 <b>Tujuan:</b> {tujuan}\n"
            f"📞 <b>Kontak:</b> {kontak}\n\n"
            f"<i>Mohon segera diproses. Terima kasih atas perhatian dan kerjasamanya 😊!</i>\n\n"
            f"<b>Untuk detail lebih lanjut, silakan kunjungi website berikut:</b>\n"
            f"<a href='https://digiwarga.vercel.app/login'>digiwarga.vercel.app/login</a>"
        )
        return jsonify({"message": "Data berhasil ditambahkan"}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Terjadi kesalahan saat menambahkan data."}), 500


def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",  # Menggunakan format HTML
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Notifikasi Telegram berhasil dikirim!")
    else:
        logging.error(f"Gagal mengirim notifikasi Telegram: {response.text}")


# SLACK_WEBHOOK_URL = (
#     "https://hooks.slack.com/services/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"
# )
TELEGRAM_BOT_TOKEN = "7942453224:AAEUovmM066kmPLD7kh4sUwA7VXkC3Ypjio"
CHAT_ID = "-1002246795595"  # Ganti dengan chat_id yang telah kamu dapatkan


def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",  # Menggunakan format HTML
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Notifikasi Telegram berhasil dikirim!")
    else:
        logging.error(f"Gagal mengirim notifikasi Telegram: {response.text}")


# def send_slack_notification(nama_keluarga, jumlah_iuran, status_pembayaran):
#     """
#     Fungsi untuk mengirim notifikasi ke Slack.
#     """
#     message = {
#         "text": (
#             f"Halo pengurus RT 08/01,\n\n"
#             f"Ada yang baru bayar iuran nih!\n\n"
#             f"💵*Keluarga:* {nama_keluarga}\n"  # Keterangan keluarga
#             f"💵*Jumlah Iuran:* Rp {jumlah_iuran}\n"  # Keterangan jumlah iuran
#             f"📅*Status Pembayaran:* {status_pembayaran} \n\n"  # Keterangan status pembayaran
#             "Mohon segera diproses. Terima kasih atas perhatian dan kerjasamanya! :)\n\n"
#             "Untuk detail lebih lanjut, silakan kunjungi website berikut:\n"
#             "https://digiwarga.vercel.app/login"
#         )
#     }
#     response = requests.post(SLACK_WEBHOOK_URL, json=message)

#     if response.status_code == 200:
#         print("Notifikasi Slack berhasil dikirim!")
#     else:
#         logging.error(f"Gagal mengirim notifikasi Slack: {response.text}")


@app.route("/pendatang", methods=["GET", "POST"])
def daftar_buku_tamu():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_role = session.get("role")

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form["role"]

        if user_role == "kader":
            return (
                jsonify(
                    {
                        "message": None,
                        "error": "Fitur ini hanya dapat diakses oleh Admin.",
                    }
                ),
                403,
            )

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"message": None, "error": "Username sudah tersedia"}), 400

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return (
            jsonify({"message": "Pengguna berhasil ditambahkan!", "error": None}),
            200,
        )

    buku_tamu_list = BukuTamu.query.all()

    total_menetap = BukuTamu.query.filter(BukuTamu.tujuan.ilike("%Menetap%")).count()
    total_sementara = BukuTamu.query.filter(
        BukuTamu.tujuan.ilike("%Sementara%")
    ).count()
    total_lainnya = BukuTamu.query.filter(
        ~BukuTamu.tujuan.ilike("%Menetap%"), ~BukuTamu.tujuan.ilike("%Sementara%")
    ).count()

    all_messages = Message.query.order_by(Message.timestamp.desc()).limit(3).all()
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in all_messages
    ]

    iuran_list = Iuran.query.all()
    all_users = User.query.order_by(User.username.asc()).all()

    return render_template(
        "pendatang.html",
        buku_tamu_list=buku_tamu_list,
        iuran_list=iuran_list,
        messages=message_list_to_display,
        all_users=all_users,
        total_menetap=total_menetap,
        total_sementara=total_sementara,
        total_lainnya=total_lainnya,
    )


@app.route("/delete_buku_tamu/<int:tamu_id>", methods=["POST"])
def delete_buku_tamu(tamu_id):
    tamu = BukuTamu.query.get(tamu_id)
    if tamu:
        nama_tamu = tamu.nama
        db.session.delete(tamu)
        db.session.commit()

        jakarta_tz = pytz.timezone("Asia/Jakarta")
        now_jakarta = datetime.now(jakarta_tz).replace(tzinfo=None)

        user_id = session.get("user_id")  # Hindari KeyError

        if user_id:  # Pastikan user_id tersedia sebelum menambahkan aktivitas
            try:
                new_activity = Activity(
                    user_id=user_id,
                    action=f"Menghapus Pendatang atas nama {nama_tamu}",
                    timestamp=now_jakarta,
                )
                db.session.add(new_activity)
                db.session.commit()
                print("Aktivitas berhasil dicatat")
            except Exception as e:
                db.session.rollback()
                print(f"Error saat mencatat aktivitas: {e}")
        else:
            print("User ID tidak ditemukan dalam sesi, aktivitas tidak dicatat.")

        flash("Data buku tamu berhasil dihapus.", "success")
    else:
        flash("Data buku tamu tidak ditemukan.", "danger")

    return redirect(url_for("daftar_buku_tamu"))


@app.route("/get-nama-keluarga", methods=["GET"])
def get_nama_keluarga():
    # Ambil semua nama_keluarga
    families = Family.query.with_entities(Family.nama_keluarga).all()

    # Gunakan set unsstuk menghindari duplikat setelah trim
    unique_names = set()

    # Tambahkan nama keluarga ke set setelah di-trim
    for family in families:
        trimmed_name = family.nama_keluarga.strip()
        if trimmed_name:  # Pastikan tidak menambahkan nama yang kosong
            unique_names.add(trimmed_name)

    # Format hasil ke dalam list of dictionaries
    result = [{"nama_keluarga": name} for name in unique_names]

    return jsonify(result)


@app.route("/lokasi_keluarga")
def lokasi_keluarga():
    # Periksa apakah pengguna sudah login melalui session
    if "user_id" not in session:
        # Jika pengguna belum login, arahkan ke halaman login
        return redirect(url_for("login"))
    all_messages = Message.query.order_by(Message.timestamp.desc()).all()

    # Batasi pesan yang ditampilkan
    messages_to_display = all_messages[:3]

    # Format pesan untuk template
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            # Ganti awalan '0' dengan '62' untuk nomor Indonesia
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]
    # Data dummy lokasi keluarga
    lokasi_keluarga = [
        {"nama": "Keluarga A", "lat": -6.340802, "lng": 106.846949},
        {"nama": "Keluarga Abah", "lat": -6.341380, "lng": 106.847689},
        {"nama": "Keluarga Pak RT", "lat": -6.340499, "lng": 106.847635},
    ]

    # Dapatkan username dari session untuk menampilkan nama pengguna di halaman
    username = session.get("username")
    iuran_list = Iuran.query.all()

    return render_template(
        "lokasi_keluarga.html",
        iuran_list=iuran_list,
        messages=message_list_to_display,
        lokasi_keluarga=lokasi_keluarga,
        username=username,
    )


@app.route("/manual_iuran")
def manual_iuran():
    # Periksa apakah pengguna sudah login melalui session
    if "user_id" not in session:
        # Jika pengguna belum login, arahkan ke halaman login
        return redirect(url_for("login"))
    all_messages = Message.query.order_by(Message.timestamp.desc()).all()

    # Batasi pesan yang ditampilkan
    messages_to_display = all_messages[:3]

    # Format pesan untuk template
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            # Ganti awalan '0' dengan '62' untuk nomor Indonesia
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]

    username = session.get("username")
    return render_template(
        "iuran/manual_iuran.html",
        messages=message_list_to_display,
        username=username,
    )


@app.route("/kirim_manual_iuran", methods=["POST"])
def kirim_manual_iuran():
    if request.method == "POST":
        nama_keluarga = request.form.get("nama_keluarga")
        jumlah_iuran = request.form.get("jumlah")
        file = request.files.get("bukti_pembayaran")

        file_url = None
        if file:
            try:
                timestamp = int(time.time())
                original_filename = secure_filename(file.filename)
                filename = f"{timestamp}_{original_filename}"
                bucket_name = "digipan"
                file_path = f"bukti_pembayaran/{filename}"
                upload_response = supabase.storage.from_(bucket_name).upload(
                    file_path, file.read()
                )

                if upload_response.status_code == 200:
                    file_url = supabase.storage.from_(bucket_name).get_public_url(
                        file_path
                    )
            except Exception:
                pass

        try:
            jakarta_tz = pytz.timezone("Asia/Jakarta")
            now_jakarta = datetime.now(jakarta_tz).replace(tzinfo=None)

            iuran_baru = Iuran(
                nama_keluarga=nama_keluarga,
                jumlah_iuran=float(
                    jumlah_iuran.replace("Rp ", "").replace(".", "").replace(",", ".")
                ),
                bukti_pembayaran=file_url,
                status_pembayaran="Menunggu",
            )
            db.session.add(iuran_baru)
            db.session.commit()

            new_activity = Activity(
                user_id=session["user_id"],
                action=f"Menambahkan iuran manual atas nama {nama_keluarga}",
                timestamp=now_jakarta,
            )
            db.session.add(new_activity)
            db.session.commit()

            return jsonify({"message": "Iuran berhasil ditambahkan!"}), 200

        except:
            db.session.rollback()
            return jsonify({"error": "Terjadi kesalahan saat menambahkan iuran."}), 400

    return jsonify({"error": "Metode tidak valid."}), 400


@app.route("/pengeluaran")
def pengeluaran():
    # Periksa apakah pengguna sudah login melalui session
    if "user_id" not in session:
        # Jika pengguna belum login, arahkan ke halaman login
        return redirect(url_for("login"))
    all_messages = Message.query.order_by(Message.timestamp.desc()).all()

    # Batasi pesan yang ditampilkan
    messages_to_display = all_messages[:3]

    # Format pesan untuk template
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            # Ganti awalan '0' dengan '62' untuk nomor Indonesia
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]

    username = session.get("username")
    return render_template(
        "iuran/pengeluaran.html",
        messages=message_list_to_display,
        username=username,
    )


@app.route("/pengeluaran", methods=["POST"])
def tambah_pengeluaran():
    try:
        data = request.form
        nama_kegiatan = data.get("nama_kegiatan")
        jenis_pengeluaran = data.get("jenis_pengeluaran")
        jumlah = data.get("jumlah").replace(".", "")
        tanggal = data.get("tanggal")

        jakarta_tz = pytz.timezone("Asia/Jakarta")
        now_jakarta = datetime.now(jakarta_tz).replace(tzinfo=None)

        jumlah_float = float(jumlah)

        pengeluaran_baru = Pengeluaran(
            nama_kegiatan=nama_kegiatan,
            jenis_pengeluaran=jenis_pengeluaran,
            jumlah=jumlah_float,
            tanggal=tanggal,
        )

        db.session.add(pengeluaran_baru)
        db.session.commit()

        new_activity = Activity(
            user_id=session["user_id"],
            action=f"Menambahkan pengeluaran",
            timestamp=now_jakarta,
        )
        db.session.add(new_activity)
        db.session.commit()

        return jsonify({"message": "Pengeluaran berhasil ditambahkan!"}), 200

    except:
        return (
            jsonify({"error": "Terjadi kesalahan saat menambahkan pengeluaran."}),
            500,
        )


# Endpoint delete_user
@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    # Periksa role pengguna yang sedang login
    current_user_role = session.get("role")
    if current_user_role == "kader":
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Fitur ini hanya dapat diakses oleh Admin.",
                }
            ),
            403,
        )

    # Temukan pengguna berdasarkan ID
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "Pengguna tidak ditemukan."}), 404

    # Hapus pengguna dari database
    db.session.delete(user)
    db.session.commit()
    return jsonify({"status": "success", "message": "Pengguna berhasil dihapus."})


@app.route("/edit_user/<string:username>", methods=["POST"])
def edit_user(username):
    # Periksa role pengguna yang sedang login
    current_user_role = session.get("role")
    if current_user_role == "kader":
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Fitur ini hanya dapat diakses oleh Admin.",
                }
            ),
            403,
        )

    # Cari pengguna berdasarkan username
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"status": "error", "message": "Pengguna tidak ditemukan."}), 404

    # Ambil data baru dari request
    data = request.get_json()
    role = data.get("role")
    if not role:
        return jsonify({"status": "error", "message": "Role harus diisi."}), 400

    # Perbarui role pengguna
    user.role = role
    db.session.commit()

    return jsonify({"status": "success", "message": "Pengguna berhasil diperbarui."})


@app.route("/api/pengeluaran", methods=["GET"])
def get_pengeluaran():
    try:
        # Ambil parameter bulan dan tahun dari query string
        bulan = request.args.get("bulan", type=int)
        tahun = request.args.get("tahun", type=int)

        # Filter data pengeluaran berdasarkan bulan dan tahun jika diberikan
        query = Pengeluaran.query.with_entities(
            Pengeluaran.nama_kegiatan, Pengeluaran.jumlah, Pengeluaran.tanggal
        )

        if bulan and tahun:
            query = query.filter(
                extract("month", Pengeluaran.tanggal) == bulan,
                extract("year", Pengeluaran.tanggal) == tahun,
            )

        pengeluaran_data = query.all()

        # Hitung total pengeluaran
        total_pengeluaran = sum(pengeluaran.jumlah for pengeluaran in pengeluaran_data)

        # Hitung total iuran
        total_iuran = (
            db.session.query(func.sum(Iuran.jumlah_iuran))
            .filter(Iuran.status_pembayaran == "Diterima")
            .scalar()
        )
        total_iuran = total_iuran or 0
        total_pengeluaran = db.session.query(func.sum(Pengeluaran.jumlah)).scalar()
        total_pengeluaran = total_pengeluaran or 0
        net_iuran = total_iuran - total_pengeluaran
        net_iuran_formatted = format_rupiah(net_iuran)

        # Format data menjadi list of dicts
        result = [
            {"nama_kegiatan": pengeluaran.nama_kegiatan, "jumlah": pengeluaran.jumlah}
            for pengeluaran in pengeluaran_data
        ]

        # Mengembalikan data sebagai JSON, termasuk total pengeluaran dan total kas
        return (
            jsonify(
                {
                    "pengeluaran_data": result,
                    "total_pengeluaran": total_pengeluaran,
                    "total_iuran": net_iuran_formatted,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": "Error retrieving data", "error": str(e)}), 500


@app.route("/register", methods=["POST"])
def register_user():
    try:
        # Ambil data dari form
        data = request.form
        print(f"Data diterima: {data}")  # Tambahkan ini untuk debug
        nama_lengkap = data.get("nama_lengkap")
        nomor_whatsapp = data.get("nomor_whatsapp")
        kata_sandi = data.get("kata_sandi")

        # Validasi input
        if not nama_lengkap or not nomor_whatsapp or not kata_sandi:
            return jsonify({"error": "Semua field harus diisi!"}), 400

        # Hash kata sandi untuk keamanan
        from werkzeug.security import generate_password_hash

        kata_sandi_hashed = generate_password_hash(kata_sandi)

        # Buat objek registrasi dengan menambahkan tanggal_daftar
        user_baru = Register(
            nama_lengkap=nama_lengkap,
            nomor_whatsapp=nomor_whatsapp,
            kata_sandi=kata_sandi_hashed,
            tanggal_daftar=datetime.now(),  # Menambahkan tanggal pendaftaran
        )

        # Simpan ke database
        db.session.add(user_baru)
        db.session.commit()

        return (
            jsonify(
                {"message": "Pendaftaran berhasil ! Menunggu persetujuan pengurus RT"}
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500


@app.route("/loginusers", methods=["POST"])
def loginusers():
    try:
        data = request.form
        nama_lengkap = data.get("nama_lengkap")
        kata_sandi = data.get("kata_sandi")

        # Validasi input
        if not nama_lengkap or not kata_sandi:
            return jsonify({"error": "Nama lengkap dan kata sandi wajib diisi!"}), 400

        # Cari pengguna berdasarkan nama_lengkap
        user = Register.query.filter_by(nama_lengkap=nama_lengkap).first()

        if not user:

            return jsonify({"error": "Anda tidak terdaftar"}), 404

        # 🔹 Periksa kecocokan kata sandi terlebih dahulu
        if not check_password_hash(user.kata_sandi, kata_sandi):

            return jsonify({"error": "Nama dan Kata sandi tidak sesuai!"}), 401

        # 🔹 Periksa status pengguna setelah memastikan password benar
        if user.status != "Aktif":
            return jsonify({"error": "Akun belum aktif. Silakan hubungi admin!"}), 403

        # Simpan sesi login
        session["user_id"] = user.id
        session["nama_lengkap"] = user.nama_lengkap
        return jsonify({"message": "Login berhasil!", "user": user.nama_lengkap}), 200

    except Exception as e:
        return jsonify({"error": "Terjadi kesalahan server"}), 500


@app.route("/aktivasi")
def aktivasi():
    if "username" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("login"))

    all_messages = Message.query.order_by(Message.timestamp.desc()).all()

    # Batasi pesan yang ditampilkan
    messages_to_display = all_messages[:3]
    register_data = Register.query.all()
    # Format pesan untuk template
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            # Ganti awalan '0' dengan '62' untuk nomor Indonesia
            "nomor_whatsapp": (
                "62" + msg.nomor_whatsapp[1:]
                if msg.nomor_whatsapp.startswith("0")
                else msg.nomor_whatsapp
            ),
            "timestamp": msg.timestamp.astimezone(
                pytz.timezone("Asia/Jakarta")
            ).strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]

    username = session.get("username")
    return render_template(
        "aktivasi.html",
        register_data=register_data,
        messages=message_list_to_display,
        username=username,
    )


@app.route("/toggle_status/<nama_lengkap>", methods=["POST"])
def toggle_user_status(nama_lengkap):
    user = Register.query.filter_by(nama_lengkap=nama_lengkap).first()
    if user:
        # Jika user aktif, nonaktifkan; jika tidak aktif, aktifkan
        user.status = "Belum Aktif" if user.status == "Aktif" else "Aktif"
        db.session.commit()
        flash(
            f"Status akun {user.nama_lengkap} berhasil diubah menjadi {user.status}.",
            "success",
        )
    else:
        flash("Akun tidak ditemukan.", "danger")

    return redirect(url_for("aktivasi"))


# Route untuk menampilkan data Register
@app.route("/get_register", methods=["GET"])
def get_register():
    try:
        # Ambil parameter dari query string jika diperlukan (contoh: pencarian berdasarkan nomor whatsapp atau status)
        nomor_whatsapp = request.args.get("nomor_whatsapp", type=str)
        status = request.args.get("status", type=str)

        # Query untuk mengambil data dari tabel register
        query = Register.query.with_entities(
            Register.id,
            Register.nama_lengkap,
            Register.nomor_whatsapp,
            Register.tanggal_daftar,
            Register.status,
        )

        if nomor_whatsapp:
            query = query.filter(Register.nomor_whatsapp == nomor_whatsapp)

        if status:
            query = query.filter(Register.status == status)

        register_data = query.all()

        # Format data menjadi list of dicts
        result = [
            {
                "id": r.id,
                "nama_lengkap": r.nama_lengkap,
                "nomor_whatsapp": r.nomor_whatsapp,
                "tanggal_daftar": r.tanggal_daftar,
                "status": r.status,
            }
            for r in register_data
        ]

        return jsonify({"register_data": result}), 200
    except Exception as e:
        return jsonify({"message": "Error retrieving data", "error": str(e)}), 500


def send_whatsapp_message(nomor_whatsapp, message):
    url = "https://api.fonnte.com/send"

    headers = {"Authorization": "epNpDwe9gi9MabXMLZGG"}

    payload = {"target": nomor_whatsapp, "message": message, "countryCode": "62"}

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        print("Pesan berhasil dikirim!")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def format_nomor_whatsapp(nomor):
    if nomor.startswith("08"):
        nomor = "+62" + nomor[1:]
    return nomor


def generate_custom_password(nama_lengkap):
    # Menghilangkan spasi dan menggabungkan nama lengkap
    nama_bersih = nama_lengkap.replace(" ", "")

    # Mengambil 4 digit angka acak untuk menambah keamanan
    angka_acak = random.randint(1000, 9999)

    # Membuat password dengan format 'NamaLengkap + AngkaAcak'
    password = f"{nama_bersih}{angka_acak}"
    return password


@app.route("/reset-password", methods=["POST"])
def reset_password():
    nama_lengkap = request.form.get("nama_lengkap")
    kata_sandi = request.form.get("kata_sandi")
    konfirmasi_kata_sandi = request.form.get("konfirmasi_kata_sandi")

    if not nama_lengkap or not kata_sandi or not konfirmasi_kata_sandi:
        flash("Semua kolom harus diisi.", "danger")
        return redirect(url_for("index"))

    if kata_sandi != konfirmasi_kata_sandi:
        flash("Konfirmasi kata sandi tidak cocok.", "danger")
        return redirect(url_for("index"))

    user = Register.query.filter(
        func.lower(Register.nama_lengkap) == func.lower(nama_lengkap)
    ).first()

    if user:
        hashed_password = generate_password_hash(kata_sandi)
        user.kata_sandi = hashed_password
        db.session.commit()

        flash(
            "Password berhasil direset! Silakan login dengan password baru Anda.",
            "success",
        )
    else:
        flash("Nama lengkap tidak ditemukan. Silakan coba lagi.", "danger")

    return redirect(url_for("index"))


@app.route("/delete_warga/<nama_lengkap>", methods=["POST"])
def delete_warga(nama_lengkap):
    user = Register.query.filter_by(nama_lengkap=nama_lengkap).first()

    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User berhasil dihapus", "success")
    else:
        flash("User tidak ditemukan", "danger")

    return redirect(url_for("aktivasi"))


if __name__ == "__main__":
    app.run(debug=True)
