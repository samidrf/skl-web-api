from flask import Flask, jsonify, request, send_file
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
)
from models import db, Pengguna, OrangTua, Anak, AdministrasiSurat
from pydantic import ValidationError
from datetime import datetime
from functools import wraps
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from sqlalchemy.orm import aliased
from schemas import PenggunaCreate, SKLCreate, SKLSearch, SKLSign

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
jwt = JWTManager(app)

# Helper functions
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims['role'] != role:
                return jsonify(msg=f"Akses ditolak. Hanya {role} yang dapat mengakses fitur ini."), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# Auth Routes
@app.route('/register', methods=['POST'])
def register():
    try:
        data = PenggunaCreate(**request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400
    
    if Pengguna.query.filter_by(username=data.username).first():
        return jsonify(msg="Username sudah terdaftar"), 400
    
    pengguna = Pengguna(
        username=data.username,
        nama_lengkap=data.nama_lengkap,
        jabatan=data.jabatan,
        role=data.role
    )
    pengguna.set_password(data.password)
    db.session.add(pengguna)
    db.session.commit()
    return jsonify(msg="Registrasi berhasil"), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    pengguna = Pengguna.query.filter_by(username=username).first()
    
    if pengguna and pengguna.check_password(password):
        access_token = create_access_token(
            identity=username,
            additional_claims={'role': pengguna.role}
        )
        return jsonify(access_token=access_token)
    return jsonify(msg="Username atau password salah"), 401

# SKL Routes
def generate_skl_pdf(anak, ayah, ibu, administrasi):
    folder_path = "temp"
    filename = f"SKL_{anak.nama}.pdf"
    filepath = os.path.join(folder_path, filename)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    c = canvas.Canvas(filepath, pagesize=letter)
    c.drawString(100, 750, f"SURAT KETERANGAN KELAHIRAN")
    c.drawString(100, 700, f"Nomor: {administrasi.nomor_surat}")
    
    # Data Anak
    c.drawString(100, 650, f"Nama Anak: {anak.nama}")
    c.drawString(100, 630, f"Jenis Kelamin: {anak.jenis_kelamin}")
    c.drawString(100, 610, f"Anak ke-: {anak.anak_ke}")
    c.drawString(100, 590, f"Tempat Lahir: {anak.tempat_lahir}")
    c.drawString(100, 570, f"Tanggal Lahir: {anak.tanggal_lahir.strftime('%d-%m-%Y')}")
    
    # Data Ayah
    c.drawString(100, 530, f"Data Ayah:")
    c.drawString(120, 510, f"NIK: {ayah.nik}")
    c.drawString(120, 490, f"Nama: {ayah.nama}")
    
    # Data Ibu
    c.drawString(100, 450, f"Data Ibu:")
    c.drawString(120, 430, f"NIK: {ibu.nik}")
    c.drawString(120, 410, f"Nama: {ibu.nama}")
    
    c.save()
    return filepath

def send_email(to_email, filepath, nama_anak):
    # Konfigurasi email
    sender_email = "your-email@gmail.com"
    password = "your-app-password"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = f"Surat Keterangan Kelahiran - {nama_anak}"
    
    body = f"Terlampir Surat Keterangan Kelahiran untuk {nama_anak}"
    msg.attach(MIMEText(body, 'plain'))
    
    with open(filepath, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="pdf")
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filepath))
        msg.attach(attachment)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/api/skl/form_skl', methods=['POST'])
@jwt_required()
def create_skl():
    try:
        data = SKLCreate(**request.json)
        
        # Buat atau dapatkan data orang tua
        ayah = OrangTua.query.filter_by(nik=data.nik_ayah).first()
        if not ayah:
            ayah = OrangTua(
                nik=data.nik_ayah,
                nama=data.nama_ayah,
                email=data.email_ayah,
                tempat_tanggal_lahir=data.tempat_tanggal_lahir_ayah,
                pekerjaan=data.pekerjaan_ayah,
                agama=data.agama_ayah,
                alamat=data.alamat_ayah
            )
            db.session.add(ayah)
        
        ibu = OrangTua.query.filter_by(nik=data.nik_ibu).first()
        if not ibu:
            ibu = OrangTua(
                nik=data.nik_ibu,
                nama=data.nama_ibu,
                email=data.email_ibu,
                tempat_tanggal_lahir=data.tempat_tanggal_lahir_ibu,
                pekerjaan=data.pekerjaan_ibu,
                agama=data.agama_ibu,
                alamat=data.alamat_ibu
            )
            db.session.add(ibu)
        
        db.session.flush()
        
        # Buat data anak
        anak = Anak(
            nama=data.nama_anak,
            jenis_kelamin=data.jenis_kelamin,
            anak_ke=data.anak_ke,
            tempat_lahir=data.tempat_lahir,
            tanggal_lahir=data.tanggal_lahir,
            kewarganegaraan=data.kewarganegaraan,
            id_ayah=ayah.id,
            id_ibu=ibu.id
        )
        db.session.add(anak)
        db.session.flush()
        
        # Buat administrasi surat
        nomor_surat = f"SKL/{datetime.now().strftime('%Y%m%d')}/{anak.id}"
        administrasi = AdministrasiSurat(
            id_anak=anak.id,
            nomor_surat=nomor_surat,
            tanggal_surat=datetime.now().date()
        )
        db.session.add(administrasi)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Formulir SKL berhasil dibuat",
            "data": {
                "nomor_surat": nomor_surat,
                "nama_anak": data.nama_anak,
                "tanggal_pengajuan": datetime.now().strftime("%Y-%m-%d")
            }
        }), 201
        
    except ValidationError as e:
        return jsonify({
            "status": "error",
            "message": "Validasi gagal",
            "errors": e.errors()
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/skl/detail_skl', methods=['POST'])
@role_required('admin')
def get_skl_detail():
    data = request.json
    nama_anak = data.get('nama_anak')
    
    if not nama_anak:
        return jsonify({
            "status": "error",
            "message": "Nama anak harus diisi"
        }), 400
    
    ayah_alias = aliased(OrangTua)
    ibu_alias = aliased(OrangTua)
    
    skl = db.session.query(
        Anak, AdministrasiSurat, ayah_alias, ibu_alias
    ).join(
        AdministrasiSurat
    ).join(
        ayah_alias, Anak.id_ayah == ayah_alias.id
    ).join(
        ibu_alias, Anak.id_ibu == ibu_alias.id
    ).filter(
        Anak.nama == nama_anak
    ).first()
    
    if not skl:
        return jsonify({
            "status": "error",
            "message": "Data tidak ditemukan"
        }), 404
    
    result = {
        'id': skl.Anak.id,
        'nomor_surat': skl.AdministrasiSurat.nomor_surat,
        'nama_anak': skl.Anak.nama,
        'tanggal_surat': skl.AdministrasiSurat.tanggal_surat,
        'jenis_kelamin': skl.Anak.jenis_kelamin,
        'anak_ke': skl.Anak.anak_ke,
        'tempat_lahir': skl.Anak.tempat_lahir,
        'tanggal_lahir': skl.Anak.tanggal_lahir,
        'kewarganegaraan': skl.Anak.kewarganegaraan,
        'nama_ayah': skl[2].nama,
        'nama_ibu': skl[3].nama,
        'status': 'Ditandatangani' if skl.AdministrasiSurat.tertanda else 'Menunggu'
    }
    
    return jsonify(result)

@app.route('/api/skl/riwayat_skl', methods=['GET'])
@role_required('admin')
def get_all_skl():
    skl_list = db.session.query(
        Anak, AdministrasiSurat
    ).join(
        AdministrasiSurat
    ).all()
    
    result = [{
        'id': skl.Anak.id,
        'nomor_surat': skl.AdministrasiSurat.nomor_surat,
        'nama_anak': skl.Anak.nama,
        'tanggal_surat': skl.AdministrasiSurat.tanggal_surat,
        'status': 'Ditandatangani' if skl.AdministrasiSurat.tertanda else 'Menunggu'
    } for skl in skl_list]
    
    return jsonify(result)

@app.route('/api/skl/download_skl', methods=['POST'])
@role_required('admin')
def download_skl_form():
    try:
        data = request.json
        nama_anak = data.get('nama_anak')
        
        if not nama_anak:
            return jsonify({
                "status": "error",
                "message": "Nama anak harus diisi"
            }), 400
            
        ayah_alias = aliased(OrangTua)
        ibu_alias = aliased(OrangTua)

        skl = db.session.query(
            Anak, AdministrasiSurat, ayah_alias, ibu_alias
        ).join(
            AdministrasiSurat
        ).join(
            ayah_alias, Anak.id_ayah == ayah_alias.id
        ).join(
            ibu_alias, Anak.id_ibu == ibu_alias.id
        ).filter(
            Anak.nama == nama_anak
        ).first()
        
        if not skl:
            return jsonify({
                "status": "error",
                "message": "Data tidak ditemukan"
            }), 404

        filename_nama = skl.Anak.nama.replace("_", " ")    
        filepath = generate_skl_pdf(skl.Anak, skl[2], skl[3], skl.AdministrasiSurat)
        return send_file(filepath, as_attachment=True, download_name=f"SKL_{filename_nama}.pdf")
        
    except Exception as e:
        return jsonify({
            "status": "download error",
            "message": str(e)
        }), 500

@app.route('/api/skl/form_skl_sign', methods=['POST'])
@role_required('admin')
def sign_and_send_skl():
    try:
        
        ayah_alias = aliased(OrangTua)
        ibu_alias = aliased(OrangTua)

        data = SKLSign(**request.json)
        
        skl = db.session.query(
            Anak, AdministrasiSurat, ayah_alias, ibu_alias
        ).join(
            AdministrasiSurat
        ).join(
            ayah_alias, Anak.id_ayah == ayah_alias.id
        ).join(
            ibu_alias, Anak.id_ibu == ibu_alias.id
        ).filter(
            Anak.nama == data.nama_anak
        ).first()
        
        if not skl:
            return jsonify({
                "status": "error",
                "message": "Data tidak ditemukan"
            }), 404
            
        filepath = generate_skl_pdf(skl.Anak, skl[2], skl[3], skl.AdministrasiSurat)
        
        if send_email(data.email_orang_tua, filepath, data.nama_anak):
            skl.AdministrasiSurat.tertanda = get_jwt_identity()
            skl.AdministrasiSurat.tanggal_surat = datetime.now().date()
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "message": "SKL berhasil ditandatangani dan dikirim via email"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Gagal mengirim email"
            }), 500
            
    except ValidationError as e:
        return jsonify({
            "status": "error",
            "message": "Validasi gagal",
            "errors": e.errors()
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)