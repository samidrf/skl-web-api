# Sistem Pengelolaan Surat Keterangan Kelahiran (SKL)

Sistem ini adalah aplikasi berbasis Flask untuk mengelola formulir pembuatan SKL. Aplikasi ini memiliki fitur autentikasi pengguna dengan peran **admin** dan **user**, serta mendukung penyimpanan data menggunakan MySQL.

## Fitur Utama

- **Registrasi & Login** menggunakan JWT Authentication
- **Manajemen Formulir SKL** untuk administator
- **Validasi Input** menggunakan Pydantic
- **Role-Based Access Control** untuk membatasi akses fitur
- **Database MySQL** untuk penyimpanan data

## Instalasi

### 1. Clone Repository

```sh
git clone https://github.com/username/repository.git
cd repository
```

### 2. Buat Virtual Environment (Opsional)

```sh
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Konfigurasi Database

Pastikan MySQL sudah berjalan dan buat database dengan menjalankan file **dbdesa.sql**.

```sh
mysql -u root -p < dbdesa.sql
```

Lalu sesuaikan konfigurasi database pada **config.py**:

```python
class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/nama_database'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'supersecretkey'
```

### 5. Jalankan Aplikasi

```sh
flask run
```

Aplikasi akan berjalan di `http://127.0.0.1:5000/`.

---

## Cara Testing API

Gunakan **Postman** ntuk menguji endpoint.
Dokumen ini menjelaskan cara menguji API menggunakan Postman. Setiap endpoint memiliki deskripsi, metode HTTP, URL, headers, body request, dan respons yang diharapkan.

## Daftar Isi
1. [Login untuk Mendapatkan Token](#1-login-untuk-mendapatkan-token)
2. [Registrasi Pengguna Baru](#2-registrasi-pengguna-baru)
3. [Membuat Formulir SKL Baru](#3-membuat-formulir-skl-baru)
4. [Mendapatkan Detail SKL Berdasarkan Nama Anak](#4-mendapatkan-detail-skl-berdasarkan-nama-anak)
5. [Mendapatkan Semua Riwayat SKL](#5-mendapatkan-semua-riwayat-skl)
6. [Mengunduh SKL dalam Format PDF](#6-mengunduh-skl-dalam-format-pdf)
7. [Menandatangani dan Mengirim SKL via Email](#7-menandatangani-dan-mengirim-skl-via-email)

---

## 1. Login untuk Mendapatkan Token

Gunakan Postman untuk mengirimkan request berikut:

**Metode:** POST  
**URL:** `http://127.0.0.1:5000/login`  
**Headers:**
- Content-Type: application/json

**Body:**
```json
{
    "username": "admin123",
    "password": "tes123"
}
```

**Response yang Diharapkan:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 2. Registrasi Pengguna Baru

**Metode:** POST  
**URL:** `http://127.0.0.1:5000/register`  
**Headers:**
- Content-Type: application/json

**Body:**
```json
{
    "username": "pengguna_baru",
    "password": "password123",
    "nama_lengkap": "Pengguna Test",
    "jabatan": "Warga",
    "role": "user"
}
```

**Response yang Diharapkan:**
```json
{
    "msg": "Registrasi berhasil"
}
```

---

## 3. Membuat Formulir SKL Baru

**Metode:** POST  
**URL:** `http://127.0.0.1:5000/api/skl/form_skl`  
**Headers:**
- Content-Type: application/json
- Authorization: Bearer <YOUR_ACCESS_TOKEN>

**Body:**
```json
{
    "nama_anak": "Bayi Contoh",
    "jenis_kelamin": "Laki-laki",
    "anak_ke": 1,
    "tempat_lahir": "Jakarta",
    "tanggal_lahir": "2025-01-15T00:00:00",
    "kewarganegaraan": "Indonesia",
    "nik_ayah": "1234567890123456",
    "nama_ayah": "Ayah Contoh",
    "email_ayah": "ayah@example.com",
    "tempat_tanggal_lahir_ayah": "Jakarta, 10 Januari 1990",
    "pekerjaan_ayah": "Karyawan Swasta",
    "agama_ayah": "Islam",
    "alamat_ayah": "Jl. Contoh No.123, Jakarta",
    "nik_ibu": "6543210987654321",
    "nama_ibu": "Ibu Contoh",
    "email_ibu": "ibu@example.com",
    "tempat_tanggal_lahir_ibu": "Bandung, 15 Februari 1992",
    "pekerjaan_ibu": "Ibu Rumah Tangga",
    "agama_ibu": "Islam",
    "alamat_ibu": "Jl. Contoh No.123, Jakarta"
}
```

**Response yang Diharapkan:**
```json
{
    "status": "success",
    "message": "Formulir SKL berhasil dibuat",
    "data": {
        "nomor_surat": "SKL/20250306/4",
        "nama_anak": "Bayi Contoh",
        "tanggal_pengajuan": "2025-03-06"
    }
}
```

---

## 4. Mendapatkan Detail SKL Berdasarkan Nama Anak

**Metode:** POST  
**URL:** `http://127.0.0.1:5000/api/skl/detail`  
**Headers:**
- Content-Type: application/json
- Authorization: Bearer <YOUR_ACCESS_TOKEN>

**Body:**
```json
{
    "nama_anak": "Anak Satu"
}
```

**Response yang Diharapkan:**
```json
{
    "id": 1,
    "nomor_surat": "SKL/20250305/1",
    "nama_anak": "Anak Satu",
    "tanggal_surat": "2025-03-05",
    "jenis_kelamin": "Laki-laki",
    "anak_ke": 1,
    "tempat_lahir": "Jakarta",
    "tanggal_lahir": "2024-01-15T00:00:00",
    "kewarganegaraan": "Indonesia",
    "nama_ayah": "Ayah Contoh",
    "nama_ibu": "Ibu Contoh",
    "status": "Menunggu"
}
```

---

## 5. Mendapatkan Semua Riwayat SKL

**Metode:** GET  
**URL:** `http://127.0.0.1:5000/api/skl/riwayat_skl`  
**Headers:**
- Authorization: Bearer <YOUR_ACCESS_TOKEN>

**Response yang Diharapkan:**
```json
[
    {
        "id": 1,
        "nomor_surat": "SKL/20250305/1",
        "nama_anak": "Anak Satu",
        "tanggal_surat": "2025-03-05",
        "status": "Menunggu"
    },
    {
        "id": 2,
        "nomor_surat": "SKL/20250306/2",
        "nama_anak": "Bayi Contoh",
        "tanggal_surat": "2025-03-06",
        "status": "Menunggu"
    }
]
```

---

## 6. Mengunduh SKL dalam Format PDF

**Metode:** POST  
**URL:** `http://127.0.0.1:5000/api/skl/download`  
**Headers:**
- Content-Type: application/json
- Authorization: Bearer <YOUR_ACCESS_TOKEN>

**Body:**
```json
{
    "nama_anak": "Anak Satu"
}
```

**Response yang Diharapkan:**
- File PDF yang diunduh (SKL_Anak Satu.pdf)

---

## 7. Menandatangani dan Mengirim SKL via Email

**Metode:** POST  
**URL:** `http://127.0.0.1:5000/api/skl/form_skl_sign`  
**Headers:**
- Content-Type: application/json
- Authorization: Bearer <YOUR_ACCESS_TOKEN>

**Body:**
```json
{
    "nama_anak": "Anak Satu",
    "email_orang_tua": "orangtua@example.com"
}
```

**Response yang Diharapkan:**
```json
{
    "status": "success",
    "message": "SKL berhasil ditandatangani dan dikirim via email"
}
```

---

## Struktur Direktori

```
repository
│-- src/                # Direktori utama kode sumber
│   │-- app.py          # Entry point aplikasi Flask dan definisi API endpoints
│   │-- config.py       # Konfigurasi aplikasi (database, JWT, dll)
│   │-- models.py       # Model database menggunakan SQLAlchemy
│   │-- schemas.py      # Validasi data menggunakan Pydantic
│   │-- temp/           # Direktori untuk file sementara
│   │   │-- SKL.pdf     # Contoh file PDF SKL yang dihasilkan
│   │-- test_api/       # Direktori untuk pengujian API
│       │-- reg.sh      # Script shell untuk pengujian registrasi
│       │-- tes.sh      # Script shell untuk pengujian umum
│-- venv/               # Virtual environment Python
│-- .gitignore          # Daftar file/direktori yang diabaikan oleh Git
│-- dbdesa.sql          # File SQL untuk inisialisasi database
│-- README.md           # Dokumentasi proyek
│-- requirements.txt    # Daftar dependensi Python yang diperlukan
```

---

## Contributor

1. Bahteramon Bintang 
2. Dimas Rifqi Firmansyah
3. Jonathan Sebastian
4. M. Rakhmat Dramaga

