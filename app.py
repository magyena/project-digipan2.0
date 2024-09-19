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
from flask import current_app
from weasyprint import HTML
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from textwrap import fill, wrap
from werkzeug.exceptions import NotFound
from io import BytesIO
from urllib.parse import unquote
from sqlalchemy import func
from werkzeug.utils import secure_filename
from supabase import create_client, Client
import logging
import os
from werkzeug.security import check_password_hash
import re
from flask import Flask, send_from_directory, send_file, abort
import io
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import textwrap
import base64


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
    ktp = db.Column(db.String(255))
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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

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
        self.timestamp = timestamp if timestamp else datetime.now()


def __init__(self, username, password):
    self.username = username
    self.password = password  # Menyimpan password sebagai plaintext


# Route untuk halaman user
@app.route("/")
def index():
    return render_template("index.html")


# Route untuk login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username dan password harus diisi.", "warning")
            return render_template("login.html")

        # Mencari user di database berdasarkan username
        user = User.query.filter_by(username=username).first()

        # Validasi username dan password
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id  # Simpan user id di session
            session["username"] = user.username  # Simpan username di session
            return redirect(url_for("dashboard"))
        else:
            flash("Username atau password salah. Silakan coba lagi.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()  # Hapus semua data sesi
    flash("Anda telah keluar.", "info")
    return redirect(url_for("login"))


def format_rupiah(value):
    """Format nilai menjadi rupiah dengan pemisah ribuan (misalnya, 60000 menjadi '60.000')."""
    return f"{value:,.0f}".replace(
        ",", "."
    )  # Menggunakan format koma sebagai titik pemisah ribuan


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
            "nomor_whatsapp": msg.nomor_whatsapp,
            "timestamp": msg.timestamp.strftime("%d %b %Y · %H:%M"),
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

    current_datetime = datetime.now().strftime(
        "%m/%d/%Y, %I:%M %p"
    )  # Formatkan sesuai kebutuhan

    return render_template(
        "dashboard.html",
        family_count=family_count,
        surat_count=surat_count,
        warga_count=warga_count,
        total_iuran=total_iuran_diterima_formatted,
        current_datetime=current_datetime,
        messages=message_list_to_display,  # Tampilkan pesan yang dibatasi
        more_messages=message_list_more,  # Kirimkan pesan tambahan untuk View More
        selesai_count=selesai_count,
        none_count=none_count,
    )


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


@app.route("/input", methods=["GET", "POST"])
def input_data():
    if request.method == "POST":
        try:
            # Mengambil data dari formulir dan mengonversi nama keluarga ke huruf kapital
            nama_keluarga = request.form["nama_keluarga"].upper()

            family_data = Family(
                nama_keluarga=nama_keluarga,
                nama=request.form["nama"],
                tempat_lahir=request.form["tempat_lahir"],
                tanggal_lahir=request.form["tanggal_lahir"],
                nomor_keluarga=request.form["nomor_keluarga"],
                hubungan_keluarga=request.form["hubungan_keluarga"],
            )

            db.session.add(family_data)
            db.session.commit()
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Terjadi kesalahan: {e}")
            return (
                jsonify({"error": "Terjadi kesalahan saat memproses permintaan Anda."}),
                500,
            )

    return render_template("input.html")


@app.route("/surat_pengantar")
def surat_pengantar():
    return render_template("surat/surat_pengantar.html")


@app.route("/tentang")
def tentang():
    return render_template("tentang.html")


@app.route("/input_iuran", methods=["GET", "POST"])
def input_iuran():
    # Hilangkan spasi di awal dan akhir, dan ambil nama keluarga yang unik
    subquery = (
        db.session.query(func.trim(func.lower(Family.nama_keluarga)))
        .distinct()
        .subquery()
    )

    nama_keluarga = db.session.query(subquery.c["trim"]).all()
    return render_template("iuran/input_iuran.html", nama_keluarga=nama_keluarga)


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

                if upload_response.status_code == 200:
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

                    return redirect(url_for("input_iuran"))
                else:
                    logging.error(f"Upload failed: {upload_response.text}")
                    return redirect(
                        url_for(
                            "input_iuran", error="Gagal mengupload bukti pembayaran"
                        )
                    )

            except Exception as e:
                logging.error(f"Exception: {e}")
                db.session.rollback()
                return redirect(
                    url_for("input_iuran", error="Terjadi kesalahan saat mengupload")
                )
        else:
            return redirect(url_for("input_iuran", error="File tidak ditemukan"))

    return redirect(url_for("input_iuran"))


@app.route("/kirim-surat", methods=["POST"])
def kirim_surat():
    data = request.json
    # print(f"Received data: {data}")  # Logging data yang diterima

    try:
        # Validasi nomor KTP/KK hanya boleh angka
        ktp = data.get("ktp")
        if not re.fullmatch(r"\d+", ktp):
            return jsonify({"message": "Nomor KTP/KK hanya boleh berisi angka."}), 400

        # Cek apakah format tanggal benar
        tanggal_str = data.get("tanggal")
        tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d").date()
        # print(f"Parsed date: {tanggal}")  # Logging tanggal yang di-parse

        surat = SuratPengantar(
            nama=data["nama"],
            tanggal=tanggal,
            tempatlahir=data["tempatlahir"],
            jeniskelamin=data["jeniskelamin"],
            agama=data["agama"],
            pekerjaan=data["pekerjaan"],
            ktp=ktp,  # Menggunakan ktp yang sudah divalidasi
            alamatktp=data["alamatktp"],
            statusperkawinan=data["statusperkawinan"],
            tujuan=data["tujuan"],
            jenissurat=data["jenissurat"],
        )
        db.session.add(surat)
        db.session.commit()
        return jsonify({"message": "Surat berhasil dikirim!"}), 200
    except Exception as e:
        db.session.rollback()
        # print(f"Error: {str(e)}")  # Logging error
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


#  route menu keluarga
@app.route("/keluarga")
def keluarga():
    if "username" not in session:
        flash("Anda harus login terlebih dahulu.", "warning")
        return redirect(url_for("login"))

    # Mengambil nama keluarga unik (distinct) setelah mengabaikan spasi
    families = db.session.query(func.trim(Family.nama_keluarga)).distinct().all()

    all_messages = Message.query.order_by(Message.timestamp.desc()).all()

    # Batasi pesan yang ditampilkan
    messages_to_display = all_messages[:3]

    # Format pesan untuk template
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            "nomor_whatsapp": msg.nomor_whatsapp,
            "timestamp": msg.timestamp.strftime("%d %b %Y · %H:%M"),
        }
        for msg in messages_to_display
    ]

    return render_template(
        "datatables.html", families=families, messages=message_list_to_display
    )


@app.route("/get_family_details/<nama_keluarga>")
def get_family_details(nama_keluarga):
    # Menghapus spasi tambahan di nama keluarga
    nama_keluarga = nama_keluarga.strip()

    # Query dengan menghapus spasi ekstra di database
    family_details = Family.query.filter(
        func.trim(Family.nama_keluarga) == nama_keluarga
    ).all()

    family_data = [
        {
            "id": member.id,  # Tambahkan ID untuk pengeditan
            "nama_keluarga": member.nama_keluarga,
            "nama": member.nama,
            "tempat_lahir": member.tempat_lahir,
            "tanggal_lahir": member.tanggal_lahir.strftime(
                "%Y-%m-%d"
            ),  # Formatkan tanggal
            "nomor_keluarga": member.nomor_keluarga,
            "hubungan_keluarga": member.hubungan_keluarga,
        }
        for member in family_details
    ]

    return jsonify(family_data)


@app.route("/delete_family_member/<int:member_id>", methods=["DELETE"])
def delete_family_member(member_id):
    try:
        # Menghapus anggota keluarga dari database
        member = db.session.query(Family).filter_by(id=member_id).first()
        if not member:
            return jsonify({"error": "Anggota keluarga tidak ditemukan."}), 404

        db.session.delete(member)
        db.session.commit()
        return jsonify({"message": "Anggota keluarga berhasil dihapus."}), 200

    except Exception as e:
        # Menangani kemungkinan kesalahan
        return jsonify({"error": str(e)}), 500


@app.route("/edit_family", methods=["POST"])
def edit_family():
    data = request.form
    member_id = data.get("member_id")
    nama_keluarga = data.get("nama_keluarga")
    nama = data.get("nama")
    tempat_lahir = data.get("tempat_lahir")
    tanggal_lahir_str = data.get("tanggal_lahir")
    nomor_keluarga = data.get("nomor_keluarga")
    hubungan_keluarga = data.get("hubungan_keluarga")

    # Validasi ID anggota keluarga
    if not member_id:
        return (
            jsonify(
                {"status": "error", "message": "ID anggota keluarga tidak diberikan."}
            ),
            400,
        )

    # Cari anggota keluarga yang sesuai berdasarkan ID
    family_member = Family.query.get(member_id)

    if family_member:
        try:
            # Parsing tanggal lahir dari string ke objek date
            tanggal_lahir = datetime.strptime(tanggal_lahir_str, "%Y-%m-%d").date()

            # Perbarui data anggota keluarga
            family_member.nama_keluarga = nama_keluarga
            family_member.nama = nama
            family_member.tempat_lahir = tempat_lahir
            family_member.tanggal_lahir = tanggal_lahir
            family_member.nomor_keluarga = nomor_keluarga
            family_member.hubungan_keluarga = hubungan_keluarga

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

    # Batasi pesan yang ditampilkan
    messages_to_display = all_messages[:3]

    # Format pesan untuk template
    message_list_to_display = [
        {
            "message": msg.message,
            "user": msg.user,
            "nomor_whatsapp": msg.nomor_whatsapp,
            "timestamp": msg.timestamp.strftime("%d %b %Y · %H:%M"),
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
            # Mengganti underscore dengan spasi
            "jenissurat": surat.jenissurat.replace("_", " "),
            "statussurat": surat.statussurat,
        }
        for surat in all_surat
    ]

    return render_template(
        "surat/list_surat.html",
        messages=message_list_to_display,
        surat_list=surat_list_to_display,
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


nomor_surat_counter = 1
nomor_surat_pengantar_counter = 1


@app.route("/download_surat_pdf/<int:surat_id>", methods=["GET"])
def download_surat_pdf(surat_id):
    # Ambil data surat berdasarkan surat_id
    surat = SuratPengantar.query.get(surat_id)
    if not surat:
        return "Surat tidak ditemukan", 404

    # Cetak nilai jenissurat untuk debugging
    # print(f"Jenis surat: {surat.jenissurat}")

    # Tentukan jalur absolut gambar
    logo_url = os.path.join(current_app.root_path, "static/img/logo/depok.png")
    ttd_url = os.path.join(current_app.root_path, "static/img/logo/ttd2.png")
    today = datetime.now().strftime("Pasir Gunung Selatan, %d %B %Y")
    global nomor_surat_counter
    global nomor_surat_pengantar_counter

    # Buat format nomor surat otomatis
    nomor_surat = f"SKD-{nomor_surat_counter:02d}/RT-08/01/2024"

    # Setelah nomor dibuat, increment counter
    nomor_surat_counter += 1

    nomor_surat_pengantar = f"SP-{nomor_surat_pengantar_counter:02d}/RT-08/01/2024"

    # Setelah nomor dibuat, increment counter
    nomor_surat_pengantar_counter += 1

    # Tentukan template berdasarkan jenis surat
    if surat.jenissurat == "surat_keterangan_domisili":
        template = "surat/template_surat_domisili.html"
    elif surat.jenissurat == "surat_pengantar":
        template = "surat/template_surat_pengantar.html"
    elif surat.jenissurat == "surat_pernyataan_tidak_mampu":
        template = "surat/template_surat_tidak_mampu.html"
    elif surat.jenissurat == "surat_pernyataan_belum_menikah":
        template = "surat/template_surat_belum_menikah.html"
    else:
        # app.logger.error(f"Jenis surat tidak dikenal: {surat.jenissurat}")
        return "Jenis surat tidak dikenal", 400

    # Cetak template yang akan digunakan
    # print(f"Template yang digunakan: {template}")

    try:
        # Render template HTML dengan data surat
        rendered_template = render_template(
            template,
            nama=surat.nama,
            tempat_lahir=surat.tempatlahir,
            tanggal=surat.tanggal,
            jeniskelamin=surat.jeniskelamin,
            agama=surat.agama,
            pekerjaan=surat.pekerjaan,
            ktp=surat.ktp,
            alamat=surat.alamatktp,
            statusperkawinan=surat.statusperkawinan,
            tujuan=surat.tujuan,
            logo_url=logo_url,
            ttd_url=ttd_url,
            today=today,
            nomor_surat=nomor_surat,
            nomor_surat_pengantar=nomor_surat_pengantar,
        )
    except NotFound:
        # app.logger.error(f"Template tidak ditemukan: {template}")
        return "Template tidak ditemukan", 500

    # Tentukan base_url
    base_url = os.path.abspath(current_app.root_path)

    # Konversi HTML ke PDF menggunakan WeasyPrint
    pdf_file = HTML(string=rendered_template, base_url=base_url).write_pdf()

    # Mengirim file sebagai unduhan, nama file mengikuti jenis surat
    response = make_response(pdf_file)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f"attachment; filename={surat.jenissurat}_{surat.nama}.pdf"
    )

    return response


if __name__ == "__main__":
    app.run(debug=True)
