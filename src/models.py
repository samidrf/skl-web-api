from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Pengguna(db.Model):
    __tablename__ = 'pengguna'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    jabatan = db.Column(db.String(50))
    role = db.Column(db.String(50), nullable=False)  # 'admin' atau 'user'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class OrangTua(db.Model):
    __tablename__ = 'orang_tua'
    
    id = db.Column(db.Integer, primary_key=True)
    nik = db.Column(db.String(20), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    tempat_tanggal_lahir = db.Column(db.String(100))
    pekerjaan = db.Column(db.String(50))
    agama = db.Column(db.String(20))
    alamat = db.Column(db.Text)

    anak_ayah = db.relationship('Anak', backref='ayah', foreign_keys='Anak.id_ayah')
    anak_ibu = db.relationship('Anak', backref='ibu', foreign_keys='Anak.id_ibu')


class Anak(db.Model):
    __tablename__ = 'anak'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    jenis_kelamin = db.Column(db.Enum('Laki-laki', 'Perempuan'), nullable=False)
    anak_ke = db.Column(db.Integer)
    tempat_lahir = db.Column(db.String(100))
    tanggal_lahir = db.Column(db.DateTime)
    kewarganegaraan = db.Column(db.String(50))

    id_ayah = db.Column(db.Integer, db.ForeignKey('orang_tua.id'))
    id_ibu = db.Column(db.Integer, db.ForeignKey('orang_tua.id'))

    administrasi = db.relationship('AdministrasiSurat', backref='anak', uselist=False)
    dokumen = db.relationship('DokumenPendukung', backref='anak', lazy=True)


class AdministrasiSurat(db.Model):
    __tablename__ = 'administrasi_surat'
    
    id = db.Column(db.Integer, primary_key=True)
    id_anak = db.Column(db.Integer, db.ForeignKey('anak.id'), unique=True)
    nomor_surat = db.Column(db.String(50), unique=True, nullable=False)
    dibuat_di = db.Column(db.String(100))
    tanggal_surat = db.Column(db.Date)
    mengetahui = db.Column(db.String(100))
    tertanda = db.Column(db.String(100))


class DokumenPendukung(db.Model):
    __tablename__ = 'dokumen_pendukung'
    
    id = db.Column(db.Integer, primary_key=True)
    id_anak = db.Column(db.Integer, db.ForeignKey('anak.id'))
    jenis_dokumen = db.Column(db.Enum('KTP', 'Kartu Keluarga', 'Surat Nikah', 'Lainnya'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)